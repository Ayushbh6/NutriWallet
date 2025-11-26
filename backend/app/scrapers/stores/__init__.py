"""Store-specific scrapers registry."""

from typing import Optional, Type
from urllib.parse import urlparse

from app.scrapers.stores.spar import SPARParser
from app.scrapers.stores.tesco import TescoParser
from app.scrapers.stores.bigbasket import BigBasketParser


# Store parser registry
STORE_PARSERS = {
    "spar": SPARParser,
    "tesco": TescoParser,
    "bigbasket": BigBasketParser,
}

# Domain to store name mapping
DOMAIN_TO_STORE = {
    "spar.at": "spar",
    "www.spar.at": "spar",
    "tesco.com": "tesco",
    "www.tesco.com": "tesco",
    "bigbasket.com": "bigbasket",
    "www.bigbasket.com": "bigbasket",
}


def get_parser_for_store(store_name: str):
    """
    Get parser class for a store name.
    
    Args:
        store_name: Store name (e.g., "spar", "tesco", "bigbasket")
        
    Returns:
        Parser class or None if not found
    """
    store_lower = store_name.lower()
    return STORE_PARSERS.get(store_lower)


def get_parser_for_url(url: str):
    """
    Auto-select parser based on URL domain.
    
    Args:
        url: Product page URL
        
    Returns:
        Parser class or None if domain not recognized
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www. prefix for matching
        if domain.startswith("www."):
            domain = domain[4:]
        
        store_name = DOMAIN_TO_STORE.get(domain)
        if store_name:
            return STORE_PARSERS.get(store_name)
        
        # Try matching with www prefix
        store_name = DOMAIN_TO_STORE.get(f"www.{domain}")
        if store_name:
            return STORE_PARSERS.get(store_name)
            
        return None
    except Exception:
        return None


__all__ = [
    "SPARParser",
    "TescoParser",
    "BigBasketParser",
    "get_parser_for_store",
    "get_parser_for_url",
    "STORE_PARSERS",
]
