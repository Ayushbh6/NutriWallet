"""Tests for price service normalization."""

import pytest
from decimal import Decimal

from app.services.price_service import PriceService


class TestPriceService:
    """Test price service normalization."""

    def test_parse_price_european_format(self):
        """Test parsing European price format (comma decimal)."""
        service = PriceService()
        
        assert service.parse_price("8,99") == Decimal("8.99")
        assert service.parse_price("12,50") == Decimal("12.50")
        assert service.parse_price("€8,99") == Decimal("8.99")

    def test_parse_price_american_format(self):
        """Test parsing American price format (dot decimal)."""
        service = PriceService()
        
        assert service.parse_price("8.99") == Decimal("8.99")
        assert service.parse_price("$12.50") == Decimal("12.50")

    def test_parse_price_with_currency_symbols(self):
        """Test parsing prices with currency symbols."""
        service = PriceService()
        
        assert service.parse_price("€8,99") == Decimal("8.99")
        assert service.parse_price("$12.50") == Decimal("12.50")
        assert service.parse_price("£9.99") == Decimal("9.99")

    def test_parse_unit_weight(self):
        """Test parsing weight units."""
        service = PriceService()
        
        unit, factor = service.parse_unit("kg")
        assert unit == "kg"
        assert factor == Decimal("1.0")
        
        unit, factor = service.parse_unit("g")
        assert unit == "g"
        assert factor == Decimal("0.001")
        
        # 100g returns the full string as unit name
        unit, factor = service.parse_unit("100g")
        assert unit == "100g"
        assert factor == Decimal("0.1")

    def test_parse_unit_volume(self):
        """Test parsing volume units."""
        service = PriceService()
        
        unit, factor = service.parse_unit("L")
        assert unit == "l"
        assert factor == Decimal("1.0")
        
        unit, factor = service.parse_unit("ml")
        assert unit == "ml"
        assert factor == Decimal("0.001")

    def test_parse_unit_count(self):
        """Test parsing count units."""
        service = PriceService()
        
        unit, factor = service.parse_unit("piece")
        assert unit == "piece"
        assert factor == Decimal("1.0")
        
        unit, factor = service.parse_unit("Stück")
        assert unit == "stück"
        assert factor == Decimal("1.0")

    def test_calculate_price_per_unit_weight(self):
        """Test calculating price per kg."""
        service = PriceService()
        
        # 8.99 EUR for 500g = 17.98 EUR per kg
        price_per_kg = service.calculate_price_per_unit(Decimal("8.99"), "500g")
        assert price_per_kg == Decimal("17.98")
        
        # 5.50 EUR per kg
        price_per_kg = service.calculate_price_per_unit(Decimal("5.50"), "kg")
        assert price_per_kg == Decimal("5.50")

    def test_calculate_price_per_unit_volume(self):
        """Test calculating price per L."""
        service = PriceService()
        
        # 2.50 EUR for 500ml = 5.00 EUR per L
        price_per_l = service.calculate_price_per_unit(Decimal("2.50"), "500ml")
        assert price_per_l == Decimal("5.00")

    def test_calculate_price_per_unit_count_returns_none(self):
        """Test that count units return None for price_per_unit."""
        service = PriceService()
        
        assert service.calculate_price_per_unit(Decimal("5.00"), "piece") is None
        assert service.calculate_price_per_unit(Decimal("3.50"), "pack") is None

    def test_normalize_price_data(self):
        """Test full normalization workflow."""
        service = PriceService()
        
        price, price_per_unit, unit = service.normalize_price_data("8,99", "500g")
        
        assert price == Decimal("8.99")
        assert price_per_unit == Decimal("17.98")
        assert unit == "500g"  # Returns full unit string

