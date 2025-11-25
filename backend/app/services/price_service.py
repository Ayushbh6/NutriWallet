"""Price normalization and unit conversion service."""

import re
from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple


class PriceService:
    """Service for normalizing prices and units."""

    # Unit conversion factors to base units (kg for weight, L for volume)
    UNIT_CONVERSIONS = {
        # Weight units (to kg)
        "kg": Decimal("1.0"),
        "g": Decimal("0.001"),
        "mg": Decimal("0.000001"),
        "100g": Decimal("0.1"),
        "500g": Decimal("0.5"),
        # Volume units (to L)
        "l": Decimal("1.0"),
        "L": Decimal("1.0"),
        "ml": Decimal("0.001"),
        "mL": Decimal("0.001"),
        "cl": Decimal("0.01"),
        "cL": Decimal("0.01"),
        # Count units (no conversion, price per piece)
        "piece": Decimal("1.0"),
        "stück": Decimal("1.0"),  # German
        "pack": Decimal("1.0"),
        "packung": Decimal("1.0"),  # German
    }

    @classmethod
    def parse_price(cls, price_str: str) -> Optional[Decimal]:
        """
        Parse price string, handling European formats (comma decimals).
        
        Args:
            price_str: Price string (e.g., "8,99" or "8.99")
            
        Returns:
            Decimal price or None if parsing fails
        """
        if not price_str:
            return None

        # Remove currency symbols and whitespace
        cleaned = re.sub(r'[€$£₹\s]', '', price_str.strip())

        # Handle European format (comma as decimal separator)
        if ',' in cleaned and '.' in cleaned:
            # Both comma and dot: assume comma is decimal (e.g., "1.234,56")
            cleaned = cleaned.replace('.', '').replace(',', '.')
        elif ',' in cleaned:
            # Only comma: could be decimal separator or thousands separator
            # Check if it's likely a decimal (e.g., "8,99" vs "1,234")
            parts = cleaned.split(',')
            if len(parts) == 2 and len(parts[1]) <= 2:
                # Likely decimal separator
                cleaned = cleaned.replace(',', '.')
            else:
                # Likely thousands separator
                cleaned = cleaned.replace(',', '')
        elif '.' in cleaned:
            # Only dot: could be decimal or thousands separator
            # Assume decimal if there are 1-2 digits after dot
            parts = cleaned.split('.')
            if len(parts) == 2 and len(parts[1]) <= 2:
                # Likely decimal separator
                pass
            else:
                # Likely thousands separator
                cleaned = cleaned.replace('.', '')

        try:
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return None

    @classmethod
    def parse_unit(cls, unit_str: str) -> Tuple[str, Decimal]:
        """
        Parse unit string and return normalized unit name and conversion factor.
        
        Args:
            unit_str: Unit string (e.g., "kg", "100g", "L", "piece", "pro kg")
            
        Returns:
            Tuple of (normalized_unit_name, conversion_factor)
        """
        if not unit_str:
            return "piece", Decimal("1.0")

        unit_lower = unit_str.strip().lower()

        # Handle German "pro" prefix (e.g., "pro kg", "pro 100g")
        if unit_lower.startswith("pro "):
            unit_lower = unit_lower[4:].strip()

        # Handle "per" prefix (e.g., "per kg")
        if unit_lower.startswith("per "):
            unit_lower = unit_lower[4:].strip()

        # Check for exact matches first
        if unit_lower in cls.UNIT_CONVERSIONS:
            return unit_lower, cls.UNIT_CONVERSIONS[unit_lower]

        # Check for numeric prefixes (e.g., "100g", "500g")
        match = re.match(r'^(\d+)(g|kg|ml|l|cl)$', unit_lower)
        if match:
            number = Decimal(match.group(1))
            base_unit = match.group(2)
            if base_unit in ["g", "kg"]:
                # Weight unit
                if base_unit == "g":
                    conversion = number * cls.UNIT_CONVERSIONS["g"]
                    return "g", conversion
                else:
                    conversion = number * cls.UNIT_CONVERSIONS["kg"]
                    return "kg", conversion
            else:
                # Volume unit
                if base_unit == "ml":
                    conversion = number * cls.UNIT_CONVERSIONS["ml"]
                    return "ml", conversion
                elif base_unit == "l":
                    conversion = number * cls.UNIT_CONVERSIONS["l"]
                    return "l", conversion
                elif base_unit == "cl":
                    conversion = number * cls.UNIT_CONVERSIONS["cl"]
                    return "cl", conversion

        # Default to piece if unknown
        return "piece", Decimal("1.0")

    @classmethod
    def calculate_price_per_unit(
        cls, price: Decimal, unit: str
    ) -> Optional[Decimal]:
        """
        Calculate normalized price per kg/L.
        
        Args:
            price: Product price
            unit: Unit string
            
        Returns:
            Price per kg (for weight) or per L (for volume), or None if not applicable
        """
        normalized_unit, conversion_factor = cls.parse_unit(unit)

        # For count units (piece, pack), return None (no normalization)
        if normalized_unit in ["piece", "stück", "pack", "packung"]:
            return None

        if conversion_factor == Decimal("0"):
            return None

        try:
            price_per_base_unit = price / conversion_factor
            return price_per_base_unit.quantize(Decimal("0.01"))
        except (InvalidOperation, ZeroDivisionError):
            return None

    @classmethod
    def normalize_price_data(
        cls,
        price_str: str,
        unit_str: str,
    ) -> Tuple[Optional[Decimal], Optional[Decimal], str]:
        """
        Normalize price and unit data.
        
        Args:
            price_str: Price string
            unit_str: Unit string
            
        Returns:
            Tuple of (parsed_price, price_per_unit, normalized_unit)
        """
        price = cls.parse_price(price_str)
        normalized_unit, _ = cls.parse_unit(unit_str)
        price_per_unit = cls.calculate_price_per_unit(price, unit_str) if price else None

        return price, price_per_unit, normalized_unit

