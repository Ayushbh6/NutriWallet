"""Tests for Researcher Agent."""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime

from app.agents.researcher import ResearcherAgent, ExtractedPriceData
from app.api.schemas import PriceResult


class TestResearcherAgent:
    """Test Researcher Agent."""

    @pytest.fixture
    def researcher(self):
        """Create Researcher Agent instance."""
        return ResearcherAgent()

    @pytest.mark.asyncio
    async def test_scrape_success(self, researcher):
        """Test scraping with Crawl4AI success."""
        researcher.scraper.scrape = AsyncMock(return_value="# Product\n\nPrice: 8.99 EUR")
        
        markdown = await researcher._scrape("https://test.com")
        
        assert markdown == "# Product\n\nPrice: 8.99 EUR"
        researcher.scraper.scrape.assert_called_once()

    @pytest.mark.asyncio
    async def test_scrape_fail(self, researcher):
        """Test scraping when Crawl4AI fails."""
        researcher.scraper.scrape = AsyncMock(return_value=None)
        
        markdown = await researcher._scrape("https://test.com")
        
        assert markdown is None

    @pytest.mark.asyncio
    @patch('app.agents.researcher.ResearcherAgent._scrape')
    async def test_fetch_price_success(self, mock_scrape, researcher):
        """Test successful price fetching."""
        # Mock scraping
        mock_scrape.return_value = """
        # SPAR Hühnerbrustfilet
        
        Price: 8,99 €
        Unit: pro kg
        """
        
        # Mock LLM agent response
        mock_result = AsyncMock()
        mock_result.data = ExtractedPriceData(
            product_name="SPAR Hühnerbrustfilet",
            price="8,99",
            currency="EUR",
            unit="kg",
            store="spar",
        )
        researcher.agent.run = AsyncMock(return_value=mock_result)
        
        # Mock result.output for fallback parsing
        mock_result.output = mock_result.data
        
        result = await researcher.fetch_price(
            product_name="chicken breast",
            city="vienna",
            store="spar",
            url="https://spar.at/test",
        )
        
        assert result is not None
        assert isinstance(result, PriceResult)
        assert result.product_name == "SPAR Hühnerbrustfilet"
        assert float(result.price) == pytest.approx(8.99, abs=0.01)
        assert result.currency == "EUR"
        assert result.city == "vienna"

    @pytest.mark.asyncio
    async def test_fetch_price_no_url(self, researcher):
        """Test price fetching without URL (should return None in Week 1)."""
        result = await researcher.fetch_price(
            product_name="chicken breast",
            city="vienna",
        )
        
        assert result is None

