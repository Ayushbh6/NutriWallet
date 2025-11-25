"""Database repository for price and product operations."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.db.client import get_supabase_client
from app.api.schemas import PriceResult


class PriceRepository:
    """Repository for price-related database operations."""

    def __init__(self):
        self.client = get_supabase_client()

    async def get_prices(
        self,
        city: str,
        category: Optional[str] = None,
        store: Optional[str] = None,
    ) -> list[PriceResult]:
        """
        Fetch cached prices from database.
        
        Args:
            city: City name
            category: Optional product category filter
            store: Optional store name filter
            
        Returns:
            List of PriceResult objects
        """
        query = self.client.table("prices").select(
            """
            id,
            product_id,
            store,
            city,
            country,
            price,
            currency,
            unit,
            price_per_unit,
            original_url,
            scraped_at,
            is_on_sale,
            sale_price,
            products!inner(
                name,
                normalized_name,
                category
            )
            """
        ).eq("city", city.lower())

        if category:
            query = query.eq("products.category", category.lower())

        if store:
            query = query.eq("store", store.lower())

        # Get most recent prices (last 7 days)
        seven_days_ago = datetime.utcnow().isoformat()
        query = query.gte("scraped_at", seven_days_ago).order("scraped_at", desc=True)

        response = query.execute()

        prices = []
        for row in response.data:
            product = row.get("products", {})
            prices.append(
                PriceResult(
                    product_name=product.get("name", ""),
                    normalized_name=product.get("normalized_name", ""),
                    price=Decimal(str(row["price"])),
                    currency=row["currency"],
                    unit=row["unit"],
                    price_per_unit=Decimal(str(row["price_per_unit"])) if row.get("price_per_unit") else None,
                    store=row["store"],
                    city=row["city"],
                    url=row.get("original_url"),
                    scraped_at=datetime.fromisoformat(row["scraped_at"].replace("Z", "+00:00")),
                )
            )

        return prices

    async def upsert_price(self, price_data: dict) -> dict:
        """
        Insert or update a price record.
        
        Args:
            price_data: Dictionary with price information
            
        Returns:
            Created/updated record
        """
        response = (
            self.client.table("prices")
            .upsert(price_data, on_conflict="product_id,store,city")
            .execute()
        )
        return response.data[0] if response.data else {}

    async def get_products_by_category(self, category: str) -> list[dict]:
        """
        Get products by category.
        
        Args:
            category: Product category
            
        Returns:
            List of product dictionaries
        """
        response = (
            self.client.table("products")
            .select("*")
            .eq("category", category.lower())
            .execute()
        )
        return response.data

    async def create_scrape_job(self, store: str, city: str) -> dict:
        """
        Create a new scrape job record.
        
        Args:
            store: Store name
            city: City name
            
        Returns:
            Created job record
        """
        job_data = {
            "store": store.lower(),
            "city": city.lower(),
            "status": "pending",
            "started_at": datetime.utcnow().isoformat(),
        }
        response = self.client.table("scrape_jobs").insert(job_data).execute()
        return response.data[0] if response.data else {}

    async def update_scrape_job(
        self,
        job_id: UUID,
        status: str,
        items_scraped: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> dict:
        """
        Update a scrape job record.
        
        Args:
            job_id: Job UUID
            status: New status
            items_scraped: Optional count of scraped items
            error_message: Optional error message
            
        Returns:
            Updated job record
        """
        update_data = {
            "status": status,
            "completed_at": datetime.utcnow().isoformat(),
        }
        if items_scraped is not None:
            update_data["items_scraped"] = items_scraped
        if error_message:
            update_data["error_message"] = error_message

        response = (
            self.client.table("scrape_jobs")
            .update(update_data)
            .eq("id", str(job_id))
            .execute()
        )
        return response.data[0] if response.data else {}

