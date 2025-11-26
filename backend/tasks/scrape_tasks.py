"""Celery tasks for scraping stores."""

import sys
import asyncio
from pathlib import Path
from uuid import UUID
import structlog

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tasks.celery_app import app
from app.db.repository import PriceRepository
from app.agents.researcher import ResearcherAgent
from app.scrapers.stores import get_parser_for_store

logger = structlog.get_logger()

# MVP products to scrape
MVP_PRODUCTS = {
    "protein": [
        "chicken breast",
        "eggs",
        "greek yogurt",
        "cottage cheese",
        "tofu",
        "lentils",
        "chickpeas",
        "tuna",
        "ground beef",
        "milk",
    ],
    "carbs": [
        "rice",
        "oats",
        "bread",
        "pasta",
        "potatoes",
        "bananas",
    ],
    "vegetables": [
        "broccoli",
        "spinach",
        "carrots",
        "onions",
        "tomatoes",
    ],
    "fats": [
        "olive oil",
        "peanut butter",
        "butter",
    ],
}


@app.task(bind=True, name="tasks.scrape_tasks.scrape_store")
def scrape_store(self, store: str, city: str):
    """
    Scrape products from a store and save to database.
    
    Args:
        store: Store name (spar, tesco, bigbasket)
        city: City name
    """
    logger.info("scrape_task_start", store=store, city=city, task_id=self.request.id)
    
    repository = PriceRepository()
    researcher = ResearcherAgent()
    
    # Create scrape job record
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        job_record = loop.run_until_complete(
            repository.create_scrape_job(store=store, city=city)
        )
        job_id = UUID(job_record["id"])
        
        # Get all products to scrape
        all_products = []
        for category, products in MVP_PRODUCTS.items():
            all_products.extend(products)
        
        items_scraped = 0
        errors = []
        
        # Scrape each product
        for product_name in all_products:
            try:
                # Fetch price using Researcher Agent
                # Note: This requires URLs - for MVP, we'll need to implement web search
                # For now, this is a placeholder that will be enhanced in Week 3
                price_result = loop.run_until_complete(
                    researcher.fetch_price(
                        product_name=product_name,
                        city=city,
                        store=store,
                    )
                )
                
                if price_result:
                    # Save to database
                    price_data = {
                        "product_name": price_result.product_name,
                        "normalized_name": price_result.normalized_name,
                        "store": price_result.store,
                        "city": price_result.city,
                        "country": _get_country_for_store(store),
                        "price": float(price_result.price),
                        "currency": price_result.currency,
                        "unit": price_result.unit,
                        "price_per_unit": float(price_result.price_per_unit) if price_result.price_per_unit else None,
                        "original_url": price_result.url,
                        "scraped_at": price_result.scraped_at.isoformat(),
                    }
                    
                    loop.run_until_complete(repository.upsert_price(price_data))
                    items_scraped += 1
                    logger.debug("scrape_task_item_saved", product=product_name, store=store)
                else:
                    logger.warning("scrape_task_item_failed", product=product_name, store=store)
                    errors.append(f"Failed to fetch {product_name}")
                    
            except Exception as e:
                logger.error("scrape_task_item_error", product=product_name, error=str(e))
                errors.append(f"Error scraping {product_name}: {str(e)}")
        
        # Update job status
        status = "completed" if not errors else "completed_with_errors"
        error_message = "; ".join(errors) if errors else None
        
        loop.run_until_complete(
            repository.update_scrape_job(
                job_id=job_id,
                status=status,
                items_scraped=items_scraped,
                error_message=error_message,
            )
        )
        
        logger.info(
            "scrape_task_complete",
            store=store,
            city=city,
            items_scraped=items_scraped,
            errors=len(errors),
        )
        
        return {
            "status": status,
            "items_scraped": items_scraped,
            "errors": errors,
        }
        
    except Exception as e:
        logger.error("scrape_task_failed", store=store, city=city, error=str(e))
        
        # Update job status to failed
        if 'job_id' in locals():
            loop.run_until_complete(
                repository.update_scrape_job(
                    job_id=job_id,
                    status="failed",
                    error_message=str(e),
                )
            )
        
        raise
    
    finally:
        loop.close()


def _get_country_for_store(store: str) -> str:
    """Get country code for store."""
    store_lower = store.lower()
    if store_lower == "spar":
        return "AT"
    elif store_lower == "tesco":
        return "UK"
    elif store_lower == "bigbasket":
        return "IN"
    else:
        return "UNKNOWN"

