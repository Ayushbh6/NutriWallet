"""Pytest configuration and shared fixtures."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.db.client import get_supabase_client
from app.scrapers.crawl4ai_scraper import Crawl4AIScraper


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client."""
    client = MagicMock()
    client.table.return_value = MagicMock()
    return client


@pytest.fixture
def mock_crawl4ai_scraper():
    """Mock Crawl4AI scraper."""
    scraper = AsyncMock(spec=Crawl4AIScraper)
    scraper.scrape = AsyncMock(return_value="# Product Page\n\nPrice: 8.99 EUR per kg")
    return scraper


@pytest.fixture
def sample_spar_html():
    """Sample SPAR HTML content."""
    return """
    <html>
        <head><title>SPAR Hühnerbrust - SPAR</title></head>
        <body>
            <h1 class="product-title">SPAR Hühnerbrustfilet</h1>
            <div class="price">8,99 €</div>
            <div class="unit">pro kg</div>
        </body>
    </html>
    """

