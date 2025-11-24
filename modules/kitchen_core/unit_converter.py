"""
Unit Conversion System
=======================
Handles conversions between all kitchen units.
"""

from decimal import Decimal
from typing import Optional, Dict, Tuple
from .models import Unit


class UnitConverter:
    """
    Convert between kitchen units.

    Supports:
    - Weight: oz, lb, g, kg
    - Volume: tsp, tbsp, fl_oz, cup, pint, quart, gallon, ml, liter
    - Count: each, dozen
    - Special: can, jar, bag, case, bunch, etc.
    """

    # Base conversions (to smallest unit in category)
    # Weight base: grams
    WEIGHT_TO_GRAMS = {
        Unit.G: Decimal('1'),
        Unit.KG: Decimal('1000'),
        Unit.OZ: Decimal('28.3495'),
        Unit.LB: Decimal('453.592'),
    }

    # Volume base: milliliters
    VOLUME_TO_ML = {
        Unit.ML: Decimal('1'),
        Unit.LITER: Decimal('1000'),
        Unit.TSP: Decimal('4.92892'),
        Unit.TBSP: Decimal('14.7868'),
        Unit.FL_OZ: Decimal('29.5735'),
        Unit.CUP: Decimal('236.588'),
        Unit.PINT: Decimal('473.176'),
        Unit.QUART: Decimal('946.353'),
        Unit.GALLON: Decimal('3785.41'),
    }

    # Count conversions
    COUNT_CONVERSIONS = {
        Unit.EACH: Decimal('1'),
        Unit.DOZEN: Decimal('12'),
    }

    # Common ingredient densities (g/ml) for weight/volume conversions
    # Used when converting between weight and volume
    DENSITIES = {
        # Default (water)
        'default': Decimal('1.0'),
        # Liquids
        'water': Decimal('1.0'),
        'milk': Decimal('1.03'),
        'cream': Decimal('0.99'),
        'oil': Decimal('0.92'),
        'olive oil': Decimal('0.92'),
        'vegetable oil': Decimal('0.92'),
        'honey': Decimal('1.42'),
        'maple syrup': Decimal('1.37'),
        'soy sauce': Decimal('1.15'),
        'vinegar': Decimal('1.01'),
        # Dry goods
        'flour': Decimal('0.53'),
        'all purpose flour': Decimal('0.53'),
        'bread flour': Decimal('0.55'),
        'sugar': Decimal('0.85'),
        'granulated sugar': Decimal('0.85'),
        'brown sugar': Decimal('0.93'),
        'powdered sugar': Decimal('0.56'),
        'salt': Decimal('1.22'),
        'kosher salt': Decimal('1.12'),
        'baking powder': Decimal('0.90'),
        'baking soda': Decimal('0.69'),
        'cocoa powder': Decimal('0.52'),
        'cornstarch': Decimal('0.54'),
        # Fats
        'butter': Decimal('0.96'),
        'shortening': Decimal('0.88'),
        'lard': Decimal('0.92'),
        # Grains
        'rice': Decimal('0.85'),
        'oats': Decimal('0.41'),
        # Nuts/Seeds
        'almonds': Decimal('0.46'),
        'peanuts': Decimal('0.53'),
        # Dairy
        'cheese': Decimal('0.45'),
        'parmesan': Decimal('0.42'),
        'cream cheese': Decimal('1.02'),
        'sour cream': Decimal('1.00'),
        'yogurt': Decimal('1.03'),
    }

    # Pack size patterns for parsing vendor pack sizes
    PACK_SIZE_PATTERNS = [
        # Pattern: "6/5 LB" -> 6 units of 5 lb each
        (r'(\d+)\s*/\s*(\d+(?:\.\d+)?)\s*(LB|OZ|GAL|QT)', 'multi'),
        # Pattern: "1/CASE" -> 1 case
        (r'(\d+)\s*/\s*CASE', 'case'),
        # Pattern: "50 LB" -> 50 lb
        (r'(\d+(?:\.\d+)?)\s*(LB|OZ|GAL|QT|EA)', 'single'),
    ]

    @classmethod
    def convert(
        cls,
        value: Decimal,
        from_unit: Unit,
        to_unit: Unit,
        ingredient_name: Optional[str] = None
    ) -> Optional[Decimal]:
        """
        Convert a value from one unit to another.

        Args:
            value: Amount to convert
            from_unit: Source unit
            to_unit: Target unit
            ingredient_name: Optional ingredient name for density lookup

        Returns:
            Converted value or None if conversion not possible
        """
        if from_unit == to_unit:
            return value

        # Same category conversions
        if cls._is_weight(from_unit) and cls._is_weight(to_unit):
            return cls._convert_weight(value, from_unit, to_unit)

        if cls._is_volume(from_unit) and cls._is_volume(to_unit):
            return cls._convert_volume(value, from_unit, to_unit)

        if cls._is_count(from_unit) and cls._is_count(to_unit):
            return cls._convert_count(value, from_unit, to_unit)

        # Cross-category conversions (weight <-> volume)
        if cls._is_weight(from_unit) and cls._is_volume(to_unit):
            return cls._weight_to_volume(value, from_unit, to_unit, ingredient_name)

        if cls._is_volume(from_unit) and cls._is_weight(to_unit):
            return cls._volume_to_weight(value, from_unit, to_unit, ingredient_name)

        return None

    @classmethod
    def _is_weight(cls, unit: Unit) -> bool:
        return unit in cls.WEIGHT_TO_GRAMS

    @classmethod
    def _is_volume(cls, unit: Unit) -> bool:
        return unit in cls.VOLUME_TO_ML

    @classmethod
    def _is_count(cls, unit: Unit) -> bool:
        return unit in cls.COUNT_CONVERSIONS

    @classmethod
    def _convert_weight(cls, value: Decimal, from_unit: Unit, to_unit: Unit) -> Decimal:
        """Convert between weight units"""
        # Convert to grams, then to target
        grams = value * cls.WEIGHT_TO_GRAMS[from_unit]
        return grams / cls.WEIGHT_TO_GRAMS[to_unit]

    @classmethod
    def _convert_volume(cls, value: Decimal, from_unit: Unit, to_unit: Unit) -> Decimal:
        """Convert between volume units"""
        # Convert to ml, then to target
        ml = value * cls.VOLUME_TO_ML[from_unit]
        return ml / cls.VOLUME_TO_ML[to_unit]

    @classmethod
    def _convert_count(cls, value: Decimal, from_unit: Unit, to_unit: Unit) -> Decimal:
        """Convert between count units"""
        base = value * cls.COUNT_CONVERSIONS[from_unit]
        return base / cls.COUNT_CONVERSIONS[to_unit]

    @classmethod
    def _get_density(cls, ingredient_name: Optional[str]) -> Decimal:
        """Get density for ingredient (g/ml)"""
        if not ingredient_name:
            return cls.DENSITIES['default']

        name_lower = ingredient_name.lower().strip()

        # Exact match
        if name_lower in cls.DENSITIES:
            return cls.DENSITIES[name_lower]

        # Partial match
        for key, density in cls.DENSITIES.items():
            if key in name_lower or name_lower in key:
                return density

        return cls.DENSITIES['default']

    @classmethod
    def _weight_to_volume(
        cls,
        value: Decimal,
        from_unit: Unit,
        to_unit: Unit,
        ingredient_name: Optional[str]
    ) -> Decimal:
        """Convert weight to volume using density"""
        density = cls._get_density(ingredient_name)

        # Convert weight to grams
        grams = value * cls.WEIGHT_TO_GRAMS[from_unit]

        # Convert grams to ml using density (ml = g / density)
        ml = grams / density

        # Convert ml to target volume unit
        return ml / cls.VOLUME_TO_ML[to_unit]

    @classmethod
    def _volume_to_weight(
        cls,
        value: Decimal,
        from_unit: Unit,
        to_unit: Unit,
        ingredient_name: Optional[str]
    ) -> Decimal:
        """Convert volume to weight using density"""
        density = cls._get_density(ingredient_name)

        # Convert volume to ml
        ml = value * cls.VOLUME_TO_ML[from_unit]

        # Convert ml to grams using density (g = ml * density)
        grams = ml * density

        # Convert grams to target weight unit
        return grams / cls.WEIGHT_TO_GRAMS[to_unit]

    @classmethod
    def parse_unit(cls, unit_str: str) -> Optional[Unit]:
        """Parse unit string to Unit enum"""
        unit_map = {
            # Weight
            'oz': Unit.OZ, 'ounce': Unit.OZ, 'ounces': Unit.OZ,
            'lb': Unit.LB, 'lbs': Unit.LB, 'pound': Unit.LB, 'pounds': Unit.LB,
            'g': Unit.G, 'gram': Unit.G, 'grams': Unit.G,
            'kg': Unit.KG, 'kilogram': Unit.KG, 'kilograms': Unit.KG,
            # Volume
            'tsp': Unit.TSP, 'teaspoon': Unit.TSP, 'teaspoons': Unit.TSP,
            'tbsp': Unit.TBSP, 'tablespoon': Unit.TBSP, 'tablespoons': Unit.TBSP,
            'fl oz': Unit.FL_OZ, 'fluid ounce': Unit.FL_OZ,
            'cup': Unit.CUP, 'cups': Unit.CUP, 'c': Unit.CUP,
            'pint': Unit.PINT, 'pints': Unit.PINT, 'pt': Unit.PINT,
            'quart': Unit.QUART, 'quarts': Unit.QUART, 'qt': Unit.QUART,
            'gallon': Unit.GALLON, 'gallons': Unit.GALLON, 'gal': Unit.GALLON,
            'ml': Unit.ML, 'milliliter': Unit.ML, 'milliliters': Unit.ML,
            'liter': Unit.LITER, 'liters': Unit.LITER, 'l': Unit.LITER,
            # Count
            'each': Unit.EACH, 'ea': Unit.EACH, 'pc': Unit.EACH, 'piece': Unit.EACH,
            'dozen': Unit.DOZEN, 'dz': Unit.DOZEN,
            # Packaging
            'can': Unit.CAN, 'cans': Unit.CAN,
            'jar': Unit.JAR, 'jars': Unit.JAR,
            'bag': Unit.BAG, 'bags': Unit.BAG,
            'case': Unit.CASE, 'cases': Unit.CASE,
            'box': Unit.BOX, 'boxes': Unit.BOX,
            # Special
            'bunch': Unit.BUNCH, 'bunches': Unit.BUNCH,
            'head': Unit.HEAD, 'heads': Unit.HEAD,
            'clove': Unit.CLOVE, 'cloves': Unit.CLOVE,
            'slice': Unit.SLICE, 'slices': Unit.SLICE,
            'portion': Unit.PORTION, 'portions': Unit.PORTION,
        }

        normalized = unit_str.lower().strip()
        return unit_map.get(normalized)

    @classmethod
    def parse_pack_size(cls, pack_size: str) -> Tuple[Decimal, Unit]:
        """
        Parse vendor pack size string.

        Examples:
            "6/5 LB" -> (30, Unit.LB)  # 6 units of 5 lb = 30 lb total
            "50 LB" -> (50, Unit.LB)
            "1/GAL" -> (1, Unit.GALLON)

        Returns:
            Tuple of (quantity, unit)
        """
        import re

        pack_size = pack_size.upper().strip()

        # Pattern: "6/5 LB" -> 6 * 5 = 30 lb
        match = re.match(r'(\d+)\s*/\s*(\d+(?:\.\d+)?)\s*(LB|OZ|GAL|QT|PT)', pack_size)
        if match:
            count = Decimal(match.group(1))
            unit_qty = Decimal(match.group(2))
            unit_str = match.group(3)
            total = count * unit_qty

            unit_map = {
                'LB': Unit.LB, 'OZ': Unit.OZ, 'GAL': Unit.GALLON,
                'QT': Unit.QUART, 'PT': Unit.PINT
            }
            return (total, unit_map.get(unit_str, Unit.EACH))

        # Pattern: "50 LB"
        match = re.match(r'(\d+(?:\.\d+)?)\s*(LB|OZ|GAL|QT|PT|EA)', pack_size)
        if match:
            qty = Decimal(match.group(1))
            unit_str = match.group(2)
            unit_map = {
                'LB': Unit.LB, 'OZ': Unit.OZ, 'GAL': Unit.GALLON,
                'QT': Unit.QUART, 'PT': Unit.PINT, 'EA': Unit.EACH
            }
            return (qty, unit_map.get(unit_str, Unit.EACH))

        # Pattern: "1/CASE"
        match = re.match(r'(\d+)\s*/\s*CASE', pack_size)
        if match:
            return (Decimal(match.group(1)), Unit.CASE)

        # Default
        return (Decimal('1'), Unit.EACH)

    @classmethod
    def get_conversion_factor(
        cls,
        from_unit: Unit,
        to_unit: Unit,
        ingredient_name: Optional[str] = None
    ) -> Optional[Decimal]:
        """Get conversion factor to multiply by"""
        return cls.convert(Decimal('1'), from_unit, to_unit, ingredient_name)
