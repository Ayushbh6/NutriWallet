"""Optimizer Agent using PuLP linear programming for meal optimization."""

from decimal import Decimal
from typing import Optional, Dict, List
import structlog
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, LpStatus

from app.api.schemas import PriceResult, OptimizerResult, OptimizedIngredient

logger = structlog.get_logger()


# Default nutrition values per 100g (fallback if not in DB)
DEFAULT_NUTRITION = {
    "chicken breast": {"protein": 31.0, "carbs": 0.0, "fat": 3.6, "calories": 165},
    "eggs": {"protein": 13.0, "carbs": 1.1, "fat": 11.0, "calories": 155},
    "greek yogurt": {"protein": 10.0, "carbs": 3.6, "fat": 0.4, "calories": 59},
    "cottage cheese": {"protein": 11.0, "carbs": 3.4, "fat": 4.3, "calories": 98},
    "tofu": {"protein": 8.0, "carbs": 1.9, "fat": 4.8, "calories": 76},
    "lentils": {"protein": 9.0, "carbs": 20.0, "fat": 0.4, "calories": 116},
    "chickpeas": {"protein": 8.9, "carbs": 27.0, "fat": 2.6, "calories": 164},
    "tuna": {"protein": 30.0, "carbs": 0.0, "fat": 1.0, "calories": 144},
    "ground beef": {"protein": 26.0, "carbs": 0.0, "fat": 15.0, "calories": 250},
    "milk": {"protein": 3.4, "carbs": 5.0, "fat": 3.3, "calories": 61},
    "rice": {"protein": 2.7, "carbs": 28.0, "fat": 0.3, "calories": 130},
    "oats": {"protein": 17.0, "carbs": 66.0, "fat": 7.0, "calories": 389},
    "bread": {"protein": 9.0, "carbs": 49.0, "fat": 3.2, "calories": 265},
    "pasta": {"protein": 5.0, "carbs": 25.0, "fat": 1.1, "calories": 131},
    "potatoes": {"protein": 2.0, "carbs": 17.0, "fat": 0.1, "calories": 77},
    "bananas": {"protein": 1.1, "carbs": 23.0, "fat": 0.3, "calories": 89},
    "broccoli": {"protein": 2.8, "carbs": 7.0, "fat": 0.4, "calories": 34},
    "spinach": {"protein": 2.9, "carbs": 3.6, "fat": 0.4, "calories": 23},
    "carrots": {"protein": 0.9, "carbs": 10.0, "fat": 0.2, "calories": 41},
    "onions": {"protein": 1.1, "carbs": 9.0, "fat": 0.1, "calories": 40},
    "tomatoes": {"protein": 0.9, "carbs": 3.9, "fat": 0.2, "calories": 18},
    "olive oil": {"protein": 0.0, "carbs": 0.0, "fat": 100.0, "calories": 884},
    "peanut butter": {"protein": 25.0, "carbs": 20.0, "fat": 50.0, "calories": 588},
    "butter": {"protein": 0.9, "carbs": 0.1, "fat": 81.0, "calories": 717},
}


class OptimizerAgent:
    """Agent for optimizing ingredient selection using linear programming."""

    def __init__(self):
        """Initialize Optimizer Agent."""
        pass

    def optimize(
        self,
        prices: List[PriceResult],
        budget: float,
        currency: str,
        min_protein_variety: int = 3,
        max_per_item_units: float = 2.0,
        category_max: Optional[Dict[str, float]] = None,
        calorie_bounds: Optional[tuple] = None,
    ) -> OptimizerResult:
        """
        Optimize ingredient selection using linear programming.
        
        Args:
            prices: List of PriceResult objects with product prices
            budget: Weekly budget amount
            currency: Currency code (must match prices)
            min_protein_variety: Minimum number of different proteins required
            max_per_item_units: Maximum units per item (for variety)
            category_max: Optional dict of category -> max quantity (e.g., {"protein": 3.0})
            calorie_bounds: Optional tuple (min_calories_per_day, max_calories_per_day)
            
        Returns:
            OptimizerResult with optimized ingredients or error status
        """
        logger.info(
            "optimizer_start",
            budget=budget,
            currency=currency,
            num_prices=len(prices),
        )

        if not prices:
            logger.warning("optimizer_no_prices")
            return OptimizerResult(
                status="infeasible",
                ingredients=[],
                total_cost=Decimal("0"),
                total_protein=0.0,
                total_calories=0.0,
                budget_utilization=0.0,
            )

        # Filter prices by currency
        filtered_prices = [p for p in prices if p.currency.upper() == currency.upper()]
        if not filtered_prices:
            logger.warning("optimizer_no_matching_currency", currency=currency)
            return OptimizerResult(
                status="infeasible",
                ingredients=[],
                total_cost=Decimal("0"),
                total_protein=0.0,
                total_calories=0.0,
                budget_utilization=0.0,
            )

        # Check if budget is too low
        min_price = min(float(p.price) for p in filtered_prices)
        if budget < min_price:
            logger.warning("optimizer_budget_too_low", budget=budget, min_price=min_price)
            return OptimizerResult(
                status="budget_too_low",
                ingredients=[],
                total_cost=Decimal("0"),
                total_protein=0.0,
                total_calories=0.0,
                budget_utilization=0.0,
            )

        # Create LP problem
        prob = LpProblem("MealOptimization", LpMaximize)

        # Create decision variables: quantity of each product
        # Key: (product_name, store), Value: LpVariable
        variables = {}
        product_info = {}

        for price in filtered_prices:
            key = (price.normalized_name, price.store)
            if key not in variables:
                # Variable represents quantity in base unit (kg for weight, L for volume, pieces for count)
                var = LpVariable(f"{price.normalized_name}_{price.store}", lowBound=0, cat="Continuous")
                variables[key] = var
                product_info[key] = {
                    "price": price,
                    "price_per_unit": float(price.price_per_unit) if price.price_per_unit else float(price.price),
                    "unit": price.unit,
                }

        # Get nutrition data for each product
        nutrition_data = {}
        for key, info in product_info.items():
            product_name = info["price"].normalized_name
            nutrition_data[key] = self._get_nutrition(product_name)

        # Objective: Maximize protein per € spent (weighted by protein content)
        # We maximize total protein, but normalize by cost efficiency
        objective_terms = []
        for key, var in variables.items():
            nutrition = nutrition_data[key]
            price_per_unit = product_info[key]["price_per_unit"]
            # Protein per € spent
            if price_per_unit > 0:
                protein_efficiency = nutrition["protein"] / price_per_unit
                objective_terms.append(protein_efficiency * var)
            else:
                objective_terms.append(0)

        prob += lpSum(objective_terms), "Maximize_Protein_Per_Euro"

        # Constraint 1: Budget constraint (±2% tolerance)
        budget_constraint = lpSum(
            product_info[key]["price_per_unit"] * var
            for key, var in variables.items()
        )
        prob += budget_constraint <= budget * 1.02, "Budget_Constraint"

        # Constraint 2: Per-item max units (variety enforcement)
        for key, var in variables.items():
            prob += var <= max_per_item_units, f"Max_Units_{key[0]}_{key[1]}"

        # Constraint 3: Per-category max (if specified)
        if category_max:
            # Group products by category (simplified: use normalized_name prefix)
            for category, max_qty in category_max.items():
                category_items = [
                    var for key, var in variables.items()
                    if category.lower() in product_info[key]["price"].normalized_name.lower()
                ]
                if category_items:
                    prob += lpSum(category_items) <= max_qty, f"Category_Max_{category}"

        # Constraint 4: Minimum protein variety
        # Create binary variables for each unique protein product
        protein_products = {}
        for key, info in product_info.items():
            product_name = info["price"].normalized_name
            # Check if it's a protein source (simplified check)
            if nutrition_data[key]["protein"] > 15.0:  # High protein threshold
                if product_name not in protein_products:
                    protein_products[product_name] = []
                protein_products[product_name].append(key)

        # For variety, ensure at least min_protein_variety different proteins are selected
        # Simplified: ensure total quantity of proteins is distributed across at least N products
        if protein_products:
            protein_vars = []
            for product_name, keys in protein_products.items():
                product_vars = [variables[key] for key in keys]
                protein_vars.extend(product_vars)
            
            if len(protein_products) >= min_protein_variety:
                # Ensure at least min_protein_variety products have non-zero quantity
                # This is a simplified constraint - full implementation would use binary variables
                prob += lpSum(protein_vars) >= 0.1 * min_protein_variety, "Protein_Variety"

        # Constraint 5: Optional calorie bounds
        if calorie_bounds:
            min_cal, max_cal = calorie_bounds
            weekly_min = min_cal * 7
            weekly_max = max_cal * 7
            
            calorie_sum = lpSum(
                nutrition_data[key]["calories"] * var / 100.0 * self._unit_to_grams(product_info[key]["unit"])
                for key, var in variables.items()
            )
            prob += calorie_sum >= weekly_min, "Min_Calories"
            prob += calorie_sum <= weekly_max, "Max_Calories"

        # Solve the problem
        prob.solve()

        # Check solution status
        status_code = LpStatus[prob.status]
        logger.info("optimizer_solve_status", status=status_code)

        if status_code == "Optimal":
            # Extract solution
            ingredients = []
            total_cost = Decimal("0")
            total_protein = 0.0
            total_calories = 0.0

            for key, var in variables.items():
                quantity = var.varValue
                if quantity and quantity > 0.001:  # Ignore very small values
                    info = product_info[key]
                    price = info["price"]
                    nutrition = nutrition_data[key]
                    unit = info["unit"]
                    
                    # Calculate total cost
                    cost = Decimal(str(info["price_per_unit"] * quantity))
                    total_cost += cost
                    
                    # Calculate nutrition totals
                    # Convert quantity to grams for nutrition calculation
                    quantity_grams = self._unit_to_grams(unit) * quantity
                    total_protein += nutrition["protein"] * quantity_grams / 100.0
                    total_calories += nutrition["calories"] * quantity_grams / 100.0
                    
                    ingredients.append(
                        OptimizedIngredient(
                            product_name=price.product_name,
                            quantity=round(quantity, 2),
                            unit=unit,
                            total_cost=cost,
                            store=price.store,
                            nutrition={
                                "protein": round(nutrition["protein"] * quantity_grams / 100.0, 1),
                                "carbs": round(nutrition["carbs"] * quantity_grams / 100.0, 1),
                                "fat": round(nutrition["fat"] * quantity_grams / 100.0, 1),
                                "calories": round(nutrition["calories"] * quantity_grams / 100.0, 0),
                            },
                        )
                    )

            budget_utilization = (float(total_cost) / budget * 100) if budget > 0 else 0.0

            logger.info(
                "optimizer_success",
                ingredients_count=len(ingredients),
                total_cost=float(total_cost),
                total_protein=total_protein,
            )

            return OptimizerResult(
                status="optimal",
                ingredients=ingredients,
                total_cost=total_cost,
                total_protein=round(total_protein, 1),
                total_calories=round(total_calories, 0),
                budget_utilization=round(budget_utilization, 1),
            )
        else:
            logger.warning("optimizer_infeasible", status=status_code)
            return OptimizerResult(
                status="infeasible",
                ingredients=[],
                total_cost=Decimal("0"),
                total_protein=0.0,
                total_calories=0.0,
                budget_utilization=0.0,
            )

    def _get_nutrition(self, product_name: str) -> Dict[str, float]:
        """Get nutrition data for a product (fallback to defaults)."""
        normalized = product_name.lower()
        return DEFAULT_NUTRITION.get(normalized, {
            "protein": 10.0,
            "carbs": 20.0,
            "fat": 5.0,
            "calories": 150,
        })

    def _unit_to_grams(self, unit: str) -> float:
        """Convert unit to grams for nutrition calculation."""
        unit_lower = unit.lower()
        if unit_lower == "kg":
            return 1000.0
        elif unit_lower == "g":
            return 1.0
        elif unit_lower == "l" or unit_lower == "l":
            return 1000.0  # Assume 1L ≈ 1000g for liquids
        elif unit_lower == "ml" or unit_lower == "ml":
            return 1.0
        elif "100g" in unit_lower:
            return 100.0
        else:
            # For pieces, assume average weight
            return 50.0  # Default: 50g per piece

