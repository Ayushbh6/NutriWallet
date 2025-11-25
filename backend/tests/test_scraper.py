"""Tests for scrapers."""

import pytest
from pathlib import Path

from app.scrapers.stores.spar import SPARParser


class TestSPARParser:
    """Test SPAR store parser."""

    @pytest.fixture
    def parser(self):
        """Create SPAR parser instance."""
        return SPARParser()

    @pytest.fixture
    def golden_html(self):
        """Load golden page HTML."""
        fixture_path = Path(__file__).parent / "fixtures" / "spar_golden.html"
        return fixture_path.read_text(encoding="utf-8")

    def test_parse_golden_page(self, parser, golden_html):
        """Test parsing golden page fixture."""
        result = parser.parse(golden_html, url="https://spar.at/test")

        assert result is not None
        assert "hühnerbrust" in result["product_name"].lower() or "chicken" in result["product_name"].lower()
        assert result["price"] is not None
        assert result["currency"] == "EUR"
        assert result["unit"] in ["kg", "g"]

    def test_parse_with_css_selectors(self, parser):
        """Test parsing with CSS selectors."""
        html = """
        <html>
            <h1 class="product-title">Test Product</h1>
            <div class="price">9,99</div>
            <span class="unit">pro kg</span>
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
            <title>SPAR Test Product - SPAR</title>
            <body>
                <p>Price: 12,50 € per kg</p>
            </body>
        </html>
        """
        
        result = parser.parse(html)
        
        assert result is not None
        assert "test product" in result["product_name"].lower()
        assert result["price"] is not None

