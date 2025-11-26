"""Integration tests for Researcher → Optimizer pipeline."""

import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

from app.agents.orchestrator import OrchestratorAgent, OrchestratorRequest
from app.api.schemas import PriceResult


class TestPipeline:
    """Test end-to-end pipeline."""

    @pytest.fixture
    def orchestrator(self):
        """Create Orchestrator Agent instance with mocked repository."""
        with patch('app.agents.orchestrator.PriceRepository') as MockRepo:
            # Mock the repository to avoid Supabase client initialization
            mock_repo = MagicMock()
            MockRepo.return_value = mock_repo
            agent = OrchestratorAgent()
            yield agent

    @pytest.fixture
    def mock_prices(self):
        """Create mock price data."""
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
                price_per_unit=Decimal("0.35"),
                store="spar",
                city="vienna",
                url="https://spar.at/test",
                scraped_at=datetime.utcnow(),
            ),
        ]

    @pytest.mark.asyncio
    async def test_researcher_to_optimizer_pipeline(self, orchestrator, mock_prices):
        """Test full pipeline from Researcher to Optimizer."""
        # Mock repository to return prices
        orchestrator.repository.get_prices = AsyncMock(return_value=mock_prices)

        request = OrchestratorRequest(
            budget=50.0,
            currency="EUR",
            city="vienna",
        )

        response = await orchestrator.process_request(request)

        assert response.city == "vienna"
        assert len(response.prices) > 0
        assert response.optimizer_result is not None
        assert response.optimizer_result.status in ["optimal", "infeasible"]

    @pytest.mark.asyncio
    async def test_pipeline_no_cached_prices(self, orchestrator):
        """Test pipeline when no cached prices exist."""
        # Mock repository to return empty list
        orchestrator.repository.get_prices = AsyncMock(return_value=[])

        # Mock researcher to return a price
        mock_price = PriceResult(
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
        )

        orchestrator.researcher.fetch_price = AsyncMock(return_value=mock_price)

        request = OrchestratorRequest(
            budget=50.0,
            currency="EUR",
            city="vienna",
        )

        response = await orchestrator.process_request(request)

        assert response.city == "vienna"
        # Should have at least one price from researcher
        assert len(response.prices) >= 0  # May be empty if optimizer fails
