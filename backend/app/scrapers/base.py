"""Base scraper class."""

from abc import ABC, abstractmethod
from typing import Optional


class BaseScraper(ABC):
    """Base class for web scrapers."""

    @abstractmethod
    async def scrape(self, url: str) -> Optional[str]:
        """
        Scrape content from a URL.
        
        Args:
            url: URL to scrape
            
        Returns:
            Markdown content or None if scraping fails
        """
        pass

