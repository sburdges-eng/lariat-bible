"""
Unit Converter Module
Handles conversion between different units of measurement for vendor products
"""

import re
from typing import Dict, Optional, Tuple


class UnitConverter:
    """Convert between different units of measurement for food products"""

    # Conversion factors to base units (ounces for weight, fluid ounces for volume)
    WEIGHT_TO_OZ = {
        'OZ': 1.0,
        'LB': 16.0,
        'KG': 35.274,
        'G': 0.03527,
        'LBS': 16.0,
        'POUND': 16.0,
        'POUNDS': 16.0,
        'OUNCE': 1.0,
        'OUNCES': 1.0,
    }

    VOLUME_TO_FLOZ = {
        'FLOZ': 1.0,
        'FL OZ': 1.0,
        'GAL': 128.0,
        'GALLON': 128.0,
        'QT': 32.0,
        'QUART': 32.0,
        'PT': 16.0,
        'PINT': 16.0,
        'CUP': 8.0,
        'ML': 0.03381,
        'L': 33.814,
        'LITER': 33.814,
    }

    # Standard can sizes in ounces
    CAN_SIZES = {
        '#10': 109.0,
        '#5': 56.0,
        '#2.5': 28.0,
        '#2': 20.0,
        '#1': 10.0,
        '#300': 15.0,
        '#303': 16.0,
    }

    def __init__(self):
        self.parsed_cache: Dict[str, dict] = {}

    def parse_pack_size(self, pack_str: str) -> dict:
        """
        Parse a pack size string into components

        Formats handled:
        - Shamrock: 1/6/LB (containers/pounds/LB)
        - SYSCO: 3/6LB, 6/1LB (containers/pounds each)
        - Simple: 25 LB, 50 OZ
        - Can: 6/#10 (6 x #10 cans)
        - Each: 12 EA, 24 CT

        Args:
            pack_str: Pack size string from vendor

        Returns:
            Dictionary with parsed components
        """
        if pack_str in self.parsed_cache:
            return self.parsed_cache[pack_str]

        original = pack_str
        pack_str = str(pack_str).upper().strip()

        result = {
            'original': original,
            'total_ounces': None,
            'total_pounds': None,
            'total_fluid_ounces': None,
            'containers': 1,
            'quantity_per_container': None,
            'unit_type': None,
            'parse_success': False,
        }

        # Shamrock format: 1/6/LB (containers/amount/unit)
        shamrock_match = re.match(r'(\d+)/(\d+(?:\.\d+)?)/LB', pack_str)
        if shamrock_match:
            containers = int(shamrock_match.group(1))
            pounds_per = float(shamrock_match.group(2))
            result['containers'] = containers
            result['quantity_per_container'] = pounds_per
            result['unit_type'] = 'LB'
            result['total_pounds'] = containers * pounds_per
            result['total_ounces'] = containers * pounds_per * 16
            result['parse_success'] = True
            self.parsed_cache[original] = result
            return result

        # SYSCO format: 3/6LB or 6/1# (containers/amount unit)
        sysco_match = re.match(r'(\d+)/(\d+(?:\.\d+)?)(LB|#)', pack_str)
        if sysco_match:
            containers = int(sysco_match.group(1))
            pounds_per = float(sysco_match.group(2))
            result['containers'] = containers
            result['quantity_per_container'] = pounds_per
            result['unit_type'] = 'LB'
            result['total_pounds'] = containers * pounds_per
            result['total_ounces'] = containers * pounds_per * 16
            result['parse_success'] = True
            self.parsed_cache[original] = result
            return result

        # Can format: 6/#10
        can_match = re.match(r'(\d+)/(#\d+(?:\.\d+)?)', pack_str)
        if can_match:
            count = int(can_match.group(1))
            can_size = can_match.group(2)
            if can_size in self.CAN_SIZES:
                oz_per_can = self.CAN_SIZES[can_size]
                result['containers'] = count
                result['quantity_per_container'] = oz_per_can
                result['unit_type'] = 'CAN'
                result['total_ounces'] = count * oz_per_can
                result['total_pounds'] = (count * oz_per_can) / 16
                result['parse_success'] = True
                self.parsed_cache[original] = result
                return result

        # Simple weight: 25 LB, 50 OZ
        simple_weight = re.match(r'(\d+(?:\.\d+)?)\s*(LB|LBS|OZ|POUND|POUNDS|OUNCE|OUNCES)', pack_str)
        if simple_weight:
            amount = float(simple_weight.group(1))
            unit = simple_weight.group(2)
            result['containers'] = 1
            result['quantity_per_container'] = amount
            result['unit_type'] = unit

            if unit in self.WEIGHT_TO_OZ:
                result['total_ounces'] = amount * self.WEIGHT_TO_OZ[unit]
                result['total_pounds'] = result['total_ounces'] / 16
                result['parse_success'] = True

            self.parsed_cache[original] = result
            return result

        # Volume: 4/1 GAL
        volume_match = re.match(r'(\d+)/(\d+(?:\.\d+)?)\s*(GAL|QT|PT)', pack_str)
        if volume_match:
            containers = int(volume_match.group(1))
            amount = float(volume_match.group(2))
            unit = volume_match.group(3)
            result['containers'] = containers
            result['quantity_per_container'] = amount
            result['unit_type'] = unit

            if unit in self.VOLUME_TO_FLOZ:
                result['total_fluid_ounces'] = containers * amount * self.VOLUME_TO_FLOZ[unit]
                result['parse_success'] = True

            self.parsed_cache[original] = result
            return result

        # Simple volume: 1 GAL, 2 QT
        simple_volume = re.match(r'(\d+(?:\.\d+)?)\s*(GAL|GALLON|QT|QUART|PT|PINT)', pack_str)
        if simple_volume:
            amount = float(simple_volume.group(1))
            unit = simple_volume.group(2)
            result['containers'] = 1
            result['quantity_per_container'] = amount
            result['unit_type'] = unit

            if unit in self.VOLUME_TO_FLOZ:
                result['total_fluid_ounces'] = amount * self.VOLUME_TO_FLOZ[unit]
                result['parse_success'] = True

            self.parsed_cache[original] = result
            return result

        # Count: 12 EA, 24 CT, 100 COUNT
        count_match = re.match(r'(\d+)\s*(EA|EACH|CT|COUNT|PK|PKG|PACK)', pack_str)
        if count_match:
            count = int(count_match.group(1))
            result['containers'] = count
            result['quantity_per_container'] = 1
            result['unit_type'] = 'EACH'
            result['parse_success'] = True
            self.parsed_cache[original] = result
            return result

        # Complex count: 4/6 CT (4 packs of 6)
        complex_count = re.match(r'(\d+)/(\d+)\s*(EA|EACH|CT|COUNT|PK|PKG)', pack_str)
        if complex_count:
            packs = int(complex_count.group(1))
            per_pack = int(complex_count.group(2))
            result['containers'] = packs * per_pack
            result['quantity_per_container'] = 1
            result['unit_type'] = 'EACH'
            result['parse_success'] = True
            self.parsed_cache[original] = result
            return result

        self.parsed_cache[original] = result
        return result

    def calculate_price_per_unit(
        self,
        pack_size: str,
        case_price: float,
        target_unit: str = 'LB'
    ) -> Optional[float]:
        """
        Calculate price per target unit

        Args:
            pack_size: Pack size string
            case_price: Total case price
            target_unit: Target unit (LB, OZ, FLOZ, EACH)

        Returns:
            Price per target unit, or None if conversion not possible
        """
        parsed = self.parse_pack_size(pack_size)

        if not parsed['parse_success']:
            return None

        if target_unit == 'LB' and parsed['total_pounds']:
            return case_price / parsed['total_pounds']
        elif target_unit == 'OZ' and parsed['total_ounces']:
            return case_price / parsed['total_ounces']
        elif target_unit == 'FLOZ' and parsed['total_fluid_ounces']:
            return case_price / parsed['total_fluid_ounces']
        elif target_unit == 'EACH' and parsed['containers']:
            return case_price / parsed['containers']

        return None

    def convert(
        self,
        value: float,
        from_unit: str,
        to_unit: str
    ) -> Optional[float]:
        """
        Convert a value from one unit to another

        Args:
            value: Value to convert
            from_unit: Source unit
            to_unit: Target unit

        Returns:
            Converted value, or None if conversion not possible
        """
        from_unit = from_unit.upper()
        to_unit = to_unit.upper()

        # Same unit, no conversion needed
        if from_unit == to_unit:
            return value

        # Weight conversions
        if from_unit in self.WEIGHT_TO_OZ and to_unit in self.WEIGHT_TO_OZ:
            oz_value = value * self.WEIGHT_TO_OZ[from_unit]
            return oz_value / self.WEIGHT_TO_OZ[to_unit]

        # Volume conversions
        if from_unit in self.VOLUME_TO_FLOZ and to_unit in self.VOLUME_TO_FLOZ:
            floz_value = value * self.VOLUME_TO_FLOZ[from_unit]
            return floz_value / self.VOLUME_TO_FLOZ[to_unit]

        return None

    def normalize_unit(self, unit: str) -> str:
        """
        Normalize unit to standard form

        Args:
            unit: Unit string to normalize

        Returns:
            Normalized unit string
        """
        unit = unit.upper().strip()

        # Weight normalizations
        if unit in ('LBS', 'POUND', 'POUNDS'):
            return 'LB'
        if unit in ('OUNCE', 'OUNCES'):
            return 'OZ'

        # Volume normalizations
        if unit in ('GALLON',):
            return 'GAL'
        if unit in ('QUART',):
            return 'QT'
        if unit in ('PINT',):
            return 'PT'

        # Count normalizations
        if unit in ('EA', 'EACH', 'COUNT'):
            return 'EA'
        if unit in ('CT', 'PK', 'PKG', 'PACK'):
            return 'CT'

        return unit

    def are_comparable(self, pack1: str, pack2: str) -> Tuple[bool, str]:
        """
        Check if two pack sizes are comparable (same unit type)

        Args:
            pack1: First pack size string
            pack2: Second pack size string

        Returns:
            Tuple of (comparable, common_unit or error_message)
        """
        parsed1 = self.parse_pack_size(pack1)
        parsed2 = self.parse_pack_size(pack2)

        if not parsed1['parse_success']:
            return False, f"Cannot parse: {pack1}"
        if not parsed2['parse_success']:
            return False, f"Cannot parse: {pack2}"

        # Both weight-based
        if parsed1['total_ounces'] and parsed2['total_ounces']:
            return True, 'LB'

        # Both volume-based
        if parsed1['total_fluid_ounces'] and parsed2['total_fluid_ounces']:
            return True, 'FLOZ'

        # Both count-based
        if parsed1['unit_type'] == 'EACH' and parsed2['unit_type'] == 'EACH':
            return True, 'EACH'

        return False, "Incompatible unit types"


# Singleton instance
_converter = None


def get_unit_converter() -> UnitConverter:
    """Get the singleton unit converter instance"""
    global _converter
    if _converter is None:
        _converter = UnitConverter()
    return _converter
