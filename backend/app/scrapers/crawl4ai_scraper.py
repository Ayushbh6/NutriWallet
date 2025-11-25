"""Crawl4AI integration for full page scraping with LLM extraction."""

import structlog
from typing import Optional
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

from app.scrapers.base import BaseScraper

logger = structlog.get_logger()


class Crawl4AIScraper(BaseScraper):
    """Crawl4AI scraper for full page scraping with JS rendering."""

    def __init__(self, headless: bool = True, timeout: int = 30000):
        """
        Initialize Crawl4AI scraper.
        
        Args:
            headless: Run browser in headless mode
            timeout: Page timeout in milliseconds
        """
        self.headless = headless
        self.timeout = timeout
        self.browser_config = BrowserConfig(headless=headless)

    async def scrape(self, url: str) -> Optional[str]:
        """
        Scrape content using Crawl4AI.
        
        Args:
            url: URL to scrape
            
        Returns:
            Markdown content or None if scraping fails
        """
        try:
            logger.debug("crawl4ai_scrape_start", url=url)

            config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                page_timeout=self.timeout,
                word_count_threshold=1,
            )

            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                result = await crawler.arun(url=url, config=config)

                if result.success and result.markdown:
                    markdown = result.markdown.raw_markdown if hasattr(result.markdown, 'raw_markdown') else str(result.markdown)
                    logger.debug(
                        "crawl4ai_scrape_success",
                        url=url,
                        content_length=len(markdown),
                    )
                    return markdown
                else:
                    error_msg = result.error_message if hasattr(result, 'error_message') else "Unknown error"
                    logger.warning("crawl4ai_scrape_failed", url=url, error=error_msg)
                    return None

        except Exception as e:
            logger.error("crawl4ai_scrape_unexpected_error", url=url, error=str(e))
            return None

