"""Orchestrator Agent for coordinating meal planning workflow."""

from typing import Optional
import structlog
from pydantic import BaseModel
from pydantic_ai import Agent

from app.config import settings
from app.agents.researcher import ResearcherAgent
from app.api.schemas import PriceResult

logger = structlog.get_logger()


class OrchestratorRequest(BaseModel):
    """Request model for orchestrator."""

    budget: float
    currency: str
    city: str
    preferences: Optional[dict] = None


class OrchestratorResponse(BaseModel):
    """Response model for orchestrator (Week 1: price data only)."""

    prices: list[PriceResult]
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
            For Week 1, focus on coordinating price research. In later weeks, you'll coordinate meal optimization.""",
        )
        self.researcher = ResearcherAgent()

    async def process_request(
        self, request: OrchestratorRequest
    ) -> OrchestratorResponse:
        """
        Process a meal planning request.
        
        Week 1: Coordinates price fetching via Researcher Agent.
        Week 2+: Will coordinate full meal plan generation.
        
        Args:
            request: Orchestrator request with budget, city, preferences
            
        Returns:
            OrchestratorResponse with price data (Week 1)
        """
        logger.info(
            "orchestrator_request_start",
            budget=request.budget,
            currency=request.currency,
            city=request.city,
        )

        # Week 1: Simple price fetching demonstration
        # Fetch a sample product price (chicken breast from SPAR Vienna)
        prices = []

        # Example: Fetch chicken breast price
        # TODO: Week 2 - Fetch prices for all products in MVP product list
        sample_price = await self.researcher.fetch_price(
            product_name="chicken breast",
            city=request.city,
            store="spar",
        )

        if sample_price:
            prices.append(sample_price)
            logger.info(
                "orchestrator_price_fetched",
                product=sample_price.product_name,
                price=sample_price.price,
            )

        logger.info(
            "orchestrator_request_complete",
            prices_fetched=len(prices),
        )

        return OrchestratorResponse(
            prices=prices,
            total_products=len(prices),
            city=request.city,
        )

