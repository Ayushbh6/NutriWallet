"""Tests for Optimizer Agent."""

import pytest
from decimal import Decimal
from datetime import datetime

from app.agents.optimizer import OptimizerAgent
from app.api.schemas import PriceResult


class TestOptimizerAgent:
    """Test Optimizer Agent."""

    @pytest.fixture
    def optimizer(self):
        """Create Optimizer Agent instance."""
        return OptimizerAgent()

    @pytest.fixture
    def sample_prices(self):
        """Create sample price data for testing."""
        return [
            PriceResult(
                product_name="Chicken Breast",
                normalized_name="chicken breast",
                price=Decimal("8.99"),
                currency="EUR",
                unit="kg",
                price_per_unit=Decimal("8.99"),
                store="spar",
                city="vienna",
                url="https://spar.at/test",
                scraped_at=datetime.utcnow(),
            ),
            PriceResult(
                product_name="Eggs",
                normalized_name="eggs",
                price=Decimal("3.50"),
                currency="EUR",
                unit="piece",
                price_per_unit=Decimal("0.35"),  # 10 eggs
                store="spar",
                city="vienna",
                url="https://spar.at/test",
                scraped_at=datetime.utcnow(),
            ),
            PriceResult(
                product_name="Rice",
                normalized_name="rice",
                price=Decimal("2.50"),
                currency="EUR",
                unit="kg",
                price_per_unit=Decimal("2.50"),
                store="spar",
                city="vienna",
                url="https://spar.at/test",
                scraped_at=datetime.utcnow(),
            ),
        ]

    def test_optimize_feasible_budget(self, optimizer, sample_prices):
        """Test optimizer with feasible budget."""
        result = optimizer.optimize(
            prices=sample_prices,
            budget=50.0,
            currency="EUR",
            min_protein_variety=2,
            max_per_item_units=2.0,
        )

        assert result.status == "optimal"
        assert len(result.ingredients) > 0
        assert float(result.total_cost) <= 50.0 * 1.02  # Within budget tolerance
        assert result.total_protein > 0
        assert result.budget_utilization > 0

    def test_optimize_infeasible_budget(self, optimizer, sample_prices):
        """Test optimizer with infeasible budget (too low)."""
        result = optimizer.optimize(
            prices=sample_prices,
            budget=0.50,  # Too low
            currency="EUR",
        )

        assert result.status in ["infeasible", "budget_too_low"]
        assert len(result.ingredients) == 0

    def test_optimize_empty_prices(self, optimizer):
        """Test optimizer with empty price list."""
        result = optimizer.optimize(
            prices=[],
            budget=50.0,
            currency="EUR",
        )

        assert result.status == "infeasible"
        assert len(result.ingredients) == 0

    def test_optimize_wrong_currency(self, optimizer, sample_prices):
        """Test optimizer with mismatched currency."""
        result = optimizer.optimize(
            prices=sample_prices,
            budget=50.0,
            currency="USD",  # Mismatch
        )

        assert result.status == "infeasible"
        assert len(result.ingredients) == 0

    def test_optimize_budget_too_low(self, optimizer, sample_prices):
        """Test optimizer detects budget too low."""
        result = optimizer.optimize(
            prices=sample_prices,
            budget=0.01,  # Below minimum price
            currency="EUR",
        )

        assert result.status == "budget_too_low"

    def test_optimize_variety_constraint(self, optimizer, sample_prices):
        """Test optimizer enforces variety constraint."""
        result = optimizer.optimize(
            prices=sample_prices,
            budget=50.0,
            currency="EUR",
            min_protein_variety=3,
            max_per_item_units=1.0,  # Limit variety
        )

        # Should still find a solution
        assert result.status == "optimal"
        assert len(result.ingredients) > 0

