"""Orchestrator Agent for coordinating meal planning workflow."""

from typing import Optional
import structlog
from pydantic import BaseModel
from pydantic_ai import Agent

from app.config import settings
from app.agents.researcher import ResearcherAgent
from app.agents.optimizer import OptimizerAgent
from app.api.schemas import PriceResult, OptimizerResult
from app.db.repository import PriceRepository

logger = structlog.get_logger()


class OrchestratorRequest(BaseModel):
    """Request model for orchestrator."""

    budget: float
    currency: str
    city: str
    preferences: Optional[dict] = None


class OrchestratorResponse(BaseModel):
    """Response model for orchestrator (Week 2: includes optimizer results)."""

    prices: list[PriceResult]
    optimizer_result: OptimizerResult | None = None
    total_products: int
    city: str


class OrchestratorAgent:
    """Main orchestrator agent that coordinates sub-agents."""

    def __init__(self):
        """Initialize Orchestrator Agent."""
        self.agent = Agent(
            'openai:gpt-5.1-mini',
            system_prompt="""You are the orchestrator for a budget-first meal planning system. 
            Your role is to coordinate between different agents to gather price data and generate meal plans.
            Week 2: Coordinate Researcher Agent to fetch prices, then Optimizer Agent to optimize ingredient selection.""",
        )
        self.researcher = ResearcherAgent()
        self.optimizer = OptimizerAgent()
        self.repository = PriceRepository()

    async def process_request(
        self, request: OrchestratorRequest
    ) -> OrchestratorResponse:
        """
        Process a meal planning request.
        
        Week 2: Coordinates Researcher Agent to fetch prices, then Optimizer Agent to optimize.
        
        Args:
            request: Orchestrator request with budget, city, preferences
            
        Returns:
            OrchestratorResponse with price data and optimizer results
        """
        logger.info(
            "orchestrator_request_start",
            budget=request.budget,
            currency=request.currency,
            city=request.city,
        )

        # Step 1: Get prices from database (cached) or fetch fresh
        prices = await self.repository.get_prices(
            city=request.city,
            category=None,
            store=None,
        )

        # If no cached prices, try fetching fresh (fallback to Researcher)
        if not prices:
            logger.info("orchestrator_no_cached_prices", city=request.city)
            # Try fetching a sample product
            sample_price = await self.researcher.fetch_price(
                product_name="chicken breast",
                city=request.city,
                store="spar",
            )
            if sample_price:
                prices.append(sample_price)

        # Step 2: Optimize ingredient selection
        optimizer_result = None
        if prices:
            try:
                optimizer_result = self.optimizer.optimize(
                    prices=prices,
                    budget=request.budget,
                    currency=request.currency,
                    min_protein_variety=3,
                    max_per_item_units=2.0,
                )
                logger.info(
                    "orchestrator_optimizer_complete",
                    status=optimizer_result.status,
                    ingredients_count=len(optimizer_result.ingredients),
                )
            except Exception as e:
                logger.error("orchestrator_optimizer_error", error=str(e))
                # Return partial results without optimizer data

        logger.info(
            "orchestrator_request_complete",
            prices_fetched=len(prices),
            optimizer_status=optimizer_result.status if optimizer_result else None,
        )

        return OrchestratorResponse(
            prices=prices,
            optimizer_result=optimizer_result,
            total_products=len(prices),
            city=request.city,
        )

