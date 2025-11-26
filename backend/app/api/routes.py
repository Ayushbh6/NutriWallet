"""FastAPI route handlers."""

import structlog
from fastapi import APIRouter, Query
from datetime import datetime, timedelta

from app.api.schemas import (
    MealPlanRequest,
    MealPlanResponse,
    PriceResponse,
    PriceResult,
    HealthResponse,
)
from app.db.repository import PriceRepository

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
    fresh_only: bool = Query(True, description="Only return prices within SLA window"),
):
    """
    Get prices for products in a given city with freshness tracking.
    """
    logger.info(
        "price_query",
        city=city,
        category=category,
        store=store,
        fresh_only=fresh_only,
    )
    
    repository = PriceRepository()
    prices = await repository.get_prices(city=city, category=category, store=store)
    
    # Add freshness fields
    now = datetime.utcnow()
    enhanced_prices = []
    
    for price in prices:
        # Determine SLA window based on store
        sla_days = _get_sla_days_for_store(price.store)
        is_fresh = (now - price.scraped_at).days <= sla_days
        
        # Filter out stale prices if fresh_only is True
        if fresh_only and not is_fresh:
            continue
        
        # Create enhanced PriceResult with freshness fields
        enhanced_price = PriceResult(
            product_name=price.product_name,
            normalized_name=price.normalized_name,
            price=price.price,
            currency=price.currency,
            unit=price.unit,
            price_per_unit=price.price_per_unit,
            store=price.store,
            city=price.city,
            url=price.url,
            scraped_at=price.scraped_at,
            last_updated=price.scraped_at,
            source_type="cache",
            confidence=1.0 if is_fresh else 0.5,
            is_fresh=is_fresh,
        )
        enhanced_prices.append(enhanced_price)
    
    return PriceResponse(
        prices=enhanced_prices,
        total_count=len(enhanced_prices),
        city=city,
        category=category,
    )


@router.get("/api/prices/compare")
async def compare_prices(
    product: str = Query(..., description="Product name to compare"),
    city: str = Query(..., description="City name"),
):
    """
    Compare prices for a product across all stores.
    Returns prices sorted by price_per_unit (cheapest first).
    """
    logger.info("price_compare", product=product, city=city)
    
    repository = PriceRepository()
    prices = await repository.get_prices(city=city, store=None)
    
    # Filter by product name (normalized)
    product_lower = product.lower()
    matching_prices = [
        p for p in prices
        if product_lower in p.normalized_name.lower() or product_lower in p.product_name.lower()
    ]
    
    # Add freshness fields
    now = datetime.utcnow()
    enhanced_prices = []
    
    for price in matching_prices:
        sla_days = _get_sla_days_for_store(price.store)
        is_fresh = (now - price.scraped_at).days <= sla_days
        
        enhanced_price = PriceResult(
            product_name=price.product_name,
            normalized_name=price.normalized_name,
            price=price.price,
            currency=price.currency,
            unit=price.unit,
            price_per_unit=price.price_per_unit,
            store=price.store,
            city=price.city,
            url=price.url,
            scraped_at=price.scraped_at,
            last_updated=price.scraped_at,
            source_type="cache",
            confidence=1.0 if is_fresh else 0.5,
            is_fresh=is_fresh,
        )
        enhanced_prices.append(enhanced_price)
    
    # Sort by price_per_unit (cheapest first)
    enhanced_prices.sort(
        key=lambda p: float(p.price_per_unit) if p.price_per_unit else float('inf')
    )
    
    return {
        "product": product,
        "city": city,
        "prices": enhanced_prices,
        "cheapest": enhanced_prices[0].store if enhanced_prices else None,
    }


def _get_sla_days_for_store(store: str) -> int:
    """Get SLA freshness window in days for a store."""
    store_lower = store.lower()
    if store_lower == "spar":
        return 7  # Weekly scraping
    elif store_lower in ["tesco", "bigbasket"]:
        return 3  # Bi-weekly scraping (3 days buffer)
    else:
        return 7  # Default


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

