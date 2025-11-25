"""Supabase client setup with singleton pattern."""

from functools import lru_cache
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

from app.config import settings


@lru_cache()
def get_supabase_client() -> Client:
    """
    Get Supabase client instance (singleton).
    
    Uses LRU cache to ensure only one client instance is created.
    """
    return create_client(
        settings.supabase_url_value,
        settings.supabase_secret_key_value,
        options=ClientOptions(
            auto_refresh_token=False,
            persist_session=False,
        ),
    )

