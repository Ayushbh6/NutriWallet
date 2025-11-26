"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict
from pydantic import BaseModel, Field


# Request Schemas
class MealPlanRequest(BaseModel):
    """Request schema for meal plan generation."""

    budget: float = Field(..., gt=0, description="Weekly budget amount")
    currency: str = Field(..., min_length=3, max_length=3, description="Currency code (EUR, USD, etc.)")
    city: str = Field(..., min_length=1, description="City name")
    preferences: Optional[dict] = Field(default=None, description="Dietary preferences and restrictions")


class PriceQueryParams(BaseModel):
    """Query parameters for price lookup."""

    city: str = Field(..., description="City name")
    category: Optional[str] = Field(default=None, description="Product category (protein, carbs, vegetables, fats)")
    store: Optional[str] = Field(default=None, description="Store name (spar, billa, etc.)")


# Response Schemas
class PriceResult(BaseModel):
    """Price data result from scraping."""

    product_name: str = Field(..., description="Original product name")
    normalized_name: str = Field(..., description="Normalized product name")
    price: Decimal = Field(..., description="Product price")
    currency: str = Field(..., description="Currency code")
    unit: str = Field(..., description="Unit (kg, L, piece, etc.)")
    price_per_unit: Optional[Decimal] = Field(default=None, description="Normalized price per kg/L")
    store: str = Field(..., description="Store name")
    city: str = Field(..., description="City name")
    url: Optional[str] = Field(default=None, description="Product URL")
    scraped_at: datetime = Field(..., description="When price was scraped")
    last_updated: Optional[datetime] = Field(default=None, description="Last update timestamp")
    source_type: Optional[str] = Field(default="crawl4ai", description="Source type (crawl4ai, cache)")
    confidence: Optional[float] = Field(default=1.0, description="Confidence score (0.0-1.0)")
    is_fresh: Optional[bool] = Field(default=True, description="Whether price is within SLA window")


class PriceResponse(BaseModel):
    """API response for price queries."""

    prices: list[PriceResult]
    total_count: int
    city: str
    category: Optional[str] = None


class MealPlanResponse(BaseModel):
    """Response schema for meal plan (stub for Week 1)."""

    message: str = "Meal plan generation coming in Week 2"
    budget: float
    currency: str
    city: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Optimizer Schemas
class OptimizedIngredient(BaseModel):
    """Optimized ingredient with quantity and cost."""

    product_name: str = Field(..., description="Product name")
    quantity: float = Field(..., description="Quantity in kg/L/pieces")
    unit: str = Field(..., description="Unit (kg, L, piece, etc.)")
    total_cost: Decimal = Field(..., description="Total cost for this quantity")
    store: str = Field(..., description="Store name")
    nutrition: Dict[str, float] = Field(..., description="Nutrition per quantity (protein, carbs, fat, calories)")


class OptimizerResult(BaseModel):
    """Result from optimizer agent."""

    status: str = Field(..., description="Status: optimal, infeasible, budget_too_low")
    ingredients: list[OptimizedIngredient] = Field(default_factory=list, description="Optimized ingredient list")
    total_cost: Decimal = Field(..., description="Total cost of all ingredients")
    total_protein: float = Field(..., description="Total protein in grams")
    total_calories: float = Field(..., description="Total calories")
    budget_utilization: float = Field(..., description="Budget utilization percentage")

