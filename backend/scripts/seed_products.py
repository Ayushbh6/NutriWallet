"""Seed script for MVP product list."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.client import get_supabase_client


MVP_PRODUCTS = {
    "protein": [
        "chicken breast",
        "eggs",
        "greek yogurt",
        "cottage cheese",
        "tofu",
        "lentils",
        "chickpeas",
        "tuna",
        "ground beef",
        "milk",
    ],
    "carbs": [
        "rice",
        "oats",
        "bread",
        "pasta",
        "potatoes",
        "bananas",
    ],
    "vegetables": [
        "broccoli",
        "spinach",
        "carrots",
        "onions",
        "tomatoes",
    ],
    "fats": [
        "olive oil",
        "peanut butter",
        "butter",
    ],
}


async def seed_products():
    """Seed products table with MVP product list."""
    client = get_supabase_client()

    print("Starting product seeding...")

    products_inserted = 0

    for category, products in MVP_PRODUCTS.items():
        print(f"\nSeeding {category} products...")

        for product_name in products:
            # Use lowercase normalized name
            normalized_name = product_name.lower().strip()

            # Check if product already exists
            existing = (
                client.table("products")
                .select("id")
                .eq("normalized_name", normalized_name)
                .execute()
            )

            if existing.data:
                print(f"  ✓ {product_name} already exists, skipping")
                continue

            # Insert product
            product_data = {
                "name": product_name,
                "normalized_name": normalized_name,
                "category": category,
            }

            try:
                response = client.table("products").insert(product_data).execute()
                if response.data:
                    products_inserted += 1
                    print(f"  ✓ Inserted: {product_name}")
                else:
                    print(f"  ✗ Failed to insert: {product_name}")
            except Exception as e:
                print(f"  ✗ Error inserting {product_name}: {e}")

    print(f"\n✅ Seeding complete! Inserted {products_inserted} new products.")


if __name__ == "__main__":
    asyncio.run(seed_products())

