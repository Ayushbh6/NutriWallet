"""Researcher Agent for price discovery using PydanticAI."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
import structlog
from pydantic import BaseModel, Field
from pydantic_ai import Agent

from app.config import settings
from app.scrapers.crawl4ai_scraper import Crawl4AIScraper
from app.services.price_service import PriceService
from app.api.schemas import PriceResult

logger = structlog.get_logger()


class ExtractedPriceData(BaseModel):
    """Structured output for LLM price extraction."""

    product_name: str = Field(..., description="Product name as it appears on the page")
    price: str = Field(..., description="Price string (e.g., '8.99' or '8,99')")
    currency: str = Field(..., description="Currency code (EUR, USD, etc.)")
    unit: str = Field(..., description="Unit (kg, L, piece, 100g, etc.)")
    store: Optional[str] = Field(default=None, description="Store name if mentioned")


class ResearcherAgent:
    """Agent for researching product prices from web sources."""

    def __init__(self):
        """Initialize Researcher Agent with PydanticAI."""
        self.agent = Agent(
            'openai:gpt-5.1-mini',
            output_type=ExtractedPriceData,
            system_prompt="""You are a price extraction assistant. Your task is to extract product price information 
            from markdown content scraped from grocery store websites. Extract the product name, price, currency, 
            and unit. Be precise with price extraction - handle both dot and comma decimal separators. 
            Return structured data in the ExtractedPriceData format.""",
        )
        self.scraper = Crawl4AIScraper()
        self.price_service = PriceService()

    async def fetch_price(
        self,
        product_name: str,
        city: str,
        store: Optional[str] = None,
        url: Optional[str] = None,
    ) -> Optional[PriceResult]:
        """
        Fetch price for a product using dual-source strategy.
        
        Args:
            product_name: Product name to search for
            city: City name
            store: Optional store name
            url: Optional direct URL to product page
            
        Returns:
            PriceResult or None if extraction fails
        """
        logger.info(
            "researcher_fetch_start",
            product=product_name,
            city=city,
            store=store,
            url=url,
        )

        # If URL provided, use it directly
        if url:
            markdown = await self._scrape(url)
        else:
            # TODO: Week 2 - Implement web search to find product URLs
            logger.warning("researcher_no_url", product=product_name)
            return None

        if not markdown:
            logger.warning("researcher_no_markdown", product=product_name)
            return None

        # Extract structured data using LLM
        try:
            result = await self.agent.run(
                f"""Extract price information from this grocery store page content:
                
{markdown[:5000]}  # Limit to first 5000 chars to avoid token limits

Product we're looking for: {product_name}
Store: {store or 'unknown'}
City: {city}

Extract the product name, price, currency, and unit."""
            )

            # Parse the agent output (PydanticAI returns structured output)
            try:
                if hasattr(result, 'output') and result.output:
                    extracted = result.output
                elif hasattr(result, 'data') and result.data:
                    extracted = result.data
                else:
                    logger.error("researcher_no_output", result=str(result))
                    return None
                
                # Ensure it's an ExtractedPriceData instance
                if not isinstance(extracted, ExtractedPriceData):
                    extracted = ExtractedPriceData.model_validate(extracted)
            except Exception as e:
                logger.error("researcher_parse_error", error=str(e), output=str(result.output) if hasattr(result, 'output') else str(result))
                return None

            # Normalize price and unit
            price, price_per_unit, normalized_unit = self.price_service.normalize_price_data(
                extracted.price,
                extracted.unit,
            )

            if not price:
                logger.warning("researcher_price_parse_failed", price_str=extracted.price)
                return None

            return PriceResult(
                product_name=extracted.product_name,
                normalized_name=product_name.lower(),  # Use search term as normalized name
                price=price,
                currency=extracted.currency.upper(),
                unit=normalized_unit,
                price_per_unit=price_per_unit,
                store=extracted.store or store or "unknown",
                city=city.lower(),
                url=url,
                scraped_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error("researcher_extraction_error", error=str(e), product=product_name)
            return None

    async def _scrape(self, url: str) -> Optional[str]:
        """
        Scrape URL using Crawl4AI.
        
        Args:
            url: URL to scrape
            
        Returns:
            Markdown content or None
        """
        logger.debug("researcher_scraping", url=url)
        markdown = await self.scraper.scrape(url)

        if markdown:
            logger.debug("researcher_scrape_success", url=url, content_length=len(markdown))
            return markdown

        logger.warning("researcher_scrape_failed", url=url)
        return None

