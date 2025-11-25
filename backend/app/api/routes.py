"""FastAPI route handlers."""

import structlog
from fastapi import APIRouter, Query
from datetime import datetime

from app.api.schemas import (
    MealPlanRequest,
    MealPlanResponse,
    PriceResponse,
    HealthResponse,
)

logger = structlog.get_logger()

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", timestamp=datetime.utcnow())


@router.get("/api/prices", response_model=PriceResponse)
async def get_prices(
    city: str = Query(..., description="City name"),
    category: str | None = Query(None, description="Product category"),
    store: str | None = Query(None, description="Store name"),
):
    """
    Get prices for products in a given city.
    
    Week 1: Returns empty list - will be implemented with Researcher Agent.
    """
    logger.info(
        "price_query",
        city=city,
        category=category,
        store=store,
    )
    
    # TODO: Week 1 - Integrate with Researcher Agent and DB repository
    # For now, return empty response
    return PriceResponse(
        prices=[],
        total_count=0,
        city=city,
        category=category,
    )


@router.post("/api/meal-plan", response_model=MealPlanResponse)
async def create_meal_plan(request: MealPlanRequest):
    """
    Generate a meal plan based on budget and preferences.
    
    Week 1: Stub endpoint - full implementation in Week 2.
    """
    logger.info(
        "meal_plan_request",
        budget=request.budget,
        currency=request.currency,
        city=request.city,
    )
    
    # TODO: Week 2 - Integrate with Orchestrator Agent
    return MealPlanResponse(
        message="Meal plan generation coming in Week 2",
        budget=request.budget,
        currency=request.currency,
        city=request.city,
    )

