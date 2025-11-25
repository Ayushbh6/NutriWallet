"""SPAR Vienna store parser with CSS selector-first approach."""

import re
from typing import Optional, Dict
import structlog
from bs4 import BeautifulSoup

from app.scrapers.base import BaseScraper
from app.services.price_service import PriceService

logger = structlog.get_logger()


class SPARParser:
    """Parser for SPAR.at product pages."""

    # CSS selectors for SPAR product pages (to be updated based on actual page structure)
    SELECTORS = {
        "product_name": [
            "h1.product-title",
            ".product-name",
            "[data-testid='product-title']",
            "h1",
        ],
        "price": [
            ".price",
            ".product-price",
            "[data-testid='price']",
            ".current-price",
        ],
        "unit": [
            ".unit",
            ".product-unit",
            "[data-testid='unit']",
            ".price-per-unit",
        ],
    }

    def __init__(self):
        """Initialize SPAR parser."""
        self.price_service = PriceService()

    def parse(self, html_content: str, url: Optional[str] = None) -> Optional[Dict]:
        """
        Parse SPAR product page HTML.
        
        Args:
            html_content: HTML content of the product page
            url: Optional URL for reference
            
        Returns:
            Dictionary with product data or None if parsing fails
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Try CSS selector approach first
            product_name = self._extract_with_selectors(soup, self.SELECTORS["product_name"])
            price_str = self._extract_with_selectors(soup, self.SELECTORS["price"])
            unit_str = self._extract_with_selectors(soup, self.SELECTORS["unit"])

            # If selectors fail, try text-based extraction
            if not product_name:
                product_name = self._extract_product_name_fallback(soup)

            if not price_str:
                price_str = self._extract_price_fallback(soup)

            if not unit_str:
                unit_str = self._extract_unit_fallback(soup, price_str)

            if not product_name or not price_str:
                logger.warning("spar_parser_failed", url=url)
                return None

            # Normalize price and unit
            price, price_per_unit, normalized_unit = self.price_service.normalize_price_data(
                price_str, unit_str or "piece"
            )

            if not price:
                logger.warning("spar_parser_price_normalization_failed", price_str=price_str)
                return None

            result = {
                "product_name": product_name.strip(),
                "price": price,
                "price_str": price_str,
                "unit": normalized_unit,
                "unit_str": unit_str or "piece",
                "price_per_unit": price_per_unit,
                "currency": "EUR",  # SPAR is Austrian, default to EUR
            }

            logger.debug("spar_parser_success", product=product_name, price=price)
            return result

        except Exception as e:
            logger.error("spar_parser_error", error=str(e), url=url)
            return None

    def _extract_with_selectors(self, soup: BeautifulSoup, selectors: list[str]) -> Optional[str]:
        """Try multiple CSS selectors to extract text."""
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if text:
                        return text
            except Exception:
                continue
        return None

    def _extract_product_name_fallback(self, soup: BeautifulSoup) -> Optional[str]:
        """Fallback method to extract product name from page."""
        # Try h1 tag
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)

        # Try title tag
        title = soup.find("title")
        if title:
            title_text = title.get_text(strip=True)
            # Remove common suffixes
            title_text = re.sub(r'\s*-\s*SPAR.*$', '', title_text, flags=re.IGNORECASE)
            return title_text

        return None

    def _extract_price_fallback(self, soup: BeautifulSoup) -> Optional[str]:
        """Fallback method to extract price from page."""
        # Look for price patterns in text
        price_patterns = [
            r'€\s*(\d+[.,]\d{2})',
            r'(\d+[.,]\d{2})\s*€',
            r'(\d+[.,]\d{2})',
        ]

        page_text = soup.get_text()

        for pattern in price_patterns:
            matches = re.findall(pattern, page_text)
            if matches:
                # Return the first reasonable match (likely the main price)
                for match in matches:
                    try:
                        price_val = float(match.replace(',', '.'))
                        if 0.01 <= price_val <= 1000:  # Reasonable price range
                            return match
                    except ValueError:
                        continue

        return None

    def _extract_unit_fallback(self, soup: BeautifulSoup, price_str: Optional[str]) -> Optional[str]:
        """Fallback method to extract unit from page."""
        # Look for common unit patterns near the price
        unit_patterns = [
            r'(\d+)\s*(kg|g|L|l|ml|mL|Stück|stück|piece)',
            r'per\s*(kg|g|L|l|ml|mL|piece)',
            r'/\s*(kg|g|L|l|ml|mL|piece)',
        ]

        page_text = soup.get_text()

        for pattern in unit_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                # Return the first match
                if isinstance(matches[0], tuple):
                    return matches[0][1] if len(matches[0]) > 1 else matches[0][0]
                return matches[0]

        return None

