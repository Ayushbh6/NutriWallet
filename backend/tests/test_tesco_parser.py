"""Tests for Tesco parser."""

import pytest
from pathlib import Path

from app.scrapers.stores.tesco import TescoParser


class TestTescoParser:
    """Test Tesco store parser."""

    @pytest.fixture
    def parser(self):
        """Create Tesco parser instance."""
        return TescoParser()

    @pytest.fixture
    def golden_html(self):
        """Load golden page HTML."""
        fixture_path = Path(__file__).parent / "fixtures" / "tesco_golden.html"
        return fixture_path.read_text(encoding="utf-8")

    def test_parse_golden_page(self, parser, golden_html):
        """Test parsing golden page fixture."""
        result = parser.parse(golden_html, url="https://tesco.com/test")

        assert result is not None
        assert "chicken" in result["product_name"].lower()
        assert result["price"] is not None
        assert result["currency"] == "GBP"
        assert result["unit"] in ["kg", "g"]

    def test_parse_with_css_selectors(self, parser):
        """Test parsing with CSS selectors."""
        html = """
        <html>
            <h1 data-testid="product-title">Test Product</h1>
            <span data-testid="price">£5.50</span>
            <span class="unit-price">per kg</span>
        </html>
        """
        
        result = parser.parse(html)
        
        assert result is not None
        assert result["product_name"] == "Test Product"
        assert result["price"] is not None

    def test_parse_fallback_extraction(self, parser):
        """Test fallback text extraction when selectors fail."""
        html = """
        <html>
            <title>Tesco Test Product - Tesco Groceries</title>
            <body>
                <p>Price: £12.50 per kg</p>
            </body>
        </html>
        """
        
        result = parser.parse(html)
        
        assert result is not None
        assert "test product" in result["product_name"].lower()
        assert result["price"] is not None

