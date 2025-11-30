"""
Vendor Parser Module
Parses SYSCO and Shamrock Foods vendor spreadsheets/invoices
"""

import re
import pandas as pd
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

from modules.core.models import VendorProduct, Vendor
from .unit_converter import get_unit_converter

logger = logging.getLogger(__name__)


# Major brands to identify in product names
MAJOR_BRANDS = [
    "HEINZ", "TURANO", "HELLMANN", "COCA COLA", "PEPSI",
    "NESTLE", "HORMEL", "KRAFT", "TYSON", "PILLSBURY",
    "MCCORMICK", "SYSCO", "SHAMROCK", "IMPERIAL", "BADIA",
    "TONY CHACHERE", "OLD BAY", "LAWRY", "LOUISIANA",
]

# Stopwords to remove when normalizing product names
STOPWORDS = {
    "AND", "THE", "OF", "WITH", "IN", "ON", "PK", "CS",
    "CASE", "EA", "CT", "LB", "OZ", "GAL", "QT", "PT",
    "EACH", "PER", "BOX", "BAG", "CAN", "JAR", "BTL",
    "BOTTLE", "PKG", "PACKAGE", "SLEEVE", "TRAY", "FOR",
    "TO", "A", "AN", "IS", "AT", "BY", "FROM", "OR",
}


class VendorParser:
    """Parse vendor spreadsheets and extract product information"""

    def __init__(self):
        self.unit_converter = get_unit_converter()
        self.products: List[VendorProduct] = []

    def parse_file(
        self,
        file_path: str,
        vendor: str,
        **kwargs
    ) -> List[VendorProduct]:
        """
        Parse a vendor spreadsheet file

        Args:
            file_path: Path to the Excel file
            vendor: Vendor name ("SYSCO" or "Shamrock")
            **kwargs: Additional parsing options

        Returns:
            List of VendorProduct objects
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        vendor_upper = vendor.upper()

        if vendor_upper == "SYSCO":
            return self.parse_sysco(file_path, **kwargs)
        elif vendor_upper in ("SHAMROCK", "SHAMROCK FOODS"):
            return self.parse_shamrock(file_path, **kwargs)
        else:
            raise ValueError(f"Unsupported vendor: {vendor}")

    def parse_sysco(
        self,
        file_path: str,
        sheet_name: Optional[str] = None,
        header_row: int = 0,
        **kwargs
    ) -> List[VendorProduct]:
        """
        Parse a SYSCO spreadsheet

        Expected columns (flexible matching):
        - Product Code / Item Number / SKU
        - Description / Product Name
        - Pack Size / Pack
        - Case Price / Price
        - Split Price (optional)
        - Category (optional)

        Args:
            file_path: Path to the Excel file
            sheet_name: Optional specific sheet name
            header_row: Row number for column headers (0-indexed)

        Returns:
            List of VendorProduct objects
        """
        products = []

        try:
            # Read Excel file
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name or 0,
                header=header_row,
                engine='openpyxl' if file_path.endswith('.xlsx') else None
            )

            # Clean column names
            df.columns = [str(c).strip().upper() for c in df.columns]

            # Map column names
            column_map = self._map_columns(df.columns, 'SYSCO')

            if not column_map.get('product_code') or not column_map.get('description'):
                logger.warning("Could not identify required columns in SYSCO file")
                return products

            for _, row in df.iterrows():
                try:
                    product_code = str(row.get(column_map['product_code'], '')).strip()
                    if not product_code or product_code == 'nan':
                        continue

                    description = str(row.get(column_map['description'], '')).strip()
                    pack_size = str(row.get(column_map.get('pack_size', ''), '')).strip()

                    # Parse prices
                    case_price = self._parse_price(row.get(column_map.get('case_price', ''), 0))
                    # Split price is parsed but stored in product if available
                    _ = self._parse_price(row.get(column_map.get('split_price', ''), 0))

                    if case_price <= 0:
                        continue

                    # Extract brand and normalize name
                    brand = self._extract_brand(description)
                    normalized_name = self.normalize_product_name(description)

                    # Calculate unit price
                    unit_price = self.unit_converter.calculate_price_per_unit(
                        pack_size, case_price, 'LB'
                    ) or case_price

                    # Parse case quantity
                    parsed = self.unit_converter.parse_pack_size(pack_size)
                    case_quantity = parsed.get('containers', 1)

                    # Get category if available
                    category = None
                    if column_map.get('category'):
                        category = str(row.get(column_map['category'], '')).strip()
                        if category == 'nan':
                            category = None

                    product = VendorProduct(
                        vendor=Vendor.SYSCO.value,
                        product_code=product_code,
                        product_name=normalized_name,
                        brand=brand,
                        unit_size=pack_size,
                        unit_price=unit_price,
                        case_price=case_price,
                        case_quantity=case_quantity,
                        category=category
                    )
                    products.append(product)

                except Exception as e:
                    logger.debug(f"Error parsing SYSCO row: {e}")
                    continue

            logger.info(f"Parsed {len(products)} products from SYSCO file")

        except Exception as e:
            logger.error(f"Error reading SYSCO file: {e}")
            raise

        self.products.extend(products)
        return products

    def parse_shamrock(
        self,
        file_path: str,
        sheet_name: Optional[str] = None,
        header_row: int = 0,
        **kwargs
    ) -> List[VendorProduct]:
        """
        Parse a Shamrock Foods spreadsheet

        Expected columns (flexible matching):
        - Item Number / Product Code / SKU
        - Description / Product Name
        - Pack / Pack Size
        - Price / Case Price
        - Category (optional)

        Args:
            file_path: Path to the Excel file
            sheet_name: Optional specific sheet name
            header_row: Row number for column headers (0-indexed)

        Returns:
            List of VendorProduct objects
        """
        products = []

        try:
            # Read Excel file
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name or 0,
                header=header_row,
                engine='openpyxl' if file_path.endswith('.xlsx') else None
            )

            # Clean column names
            df.columns = [str(c).strip().upper() for c in df.columns]

            # Map column names
            column_map = self._map_columns(df.columns, 'SHAMROCK')

            if not column_map.get('product_code') or not column_map.get('description'):
                logger.warning("Could not identify required columns in Shamrock file")
                return products

            for _, row in df.iterrows():
                try:
                    product_code = str(row.get(column_map['product_code'], '')).strip()
                    if not product_code or product_code == 'nan':
                        continue

                    description = str(row.get(column_map['description'], '')).strip()
                    pack_size = str(row.get(column_map.get('pack_size', ''), '')).strip()

                    # Parse price
                    case_price = self._parse_price(row.get(column_map.get('case_price', ''), 0))

                    if case_price <= 0:
                        continue

                    # Extract brand and normalize name
                    brand = self._extract_brand(description)
                    normalized_name = self.normalize_product_name(description)

                    # Calculate unit price
                    unit_price = self.unit_converter.calculate_price_per_unit(
                        pack_size, case_price, 'LB'
                    ) or case_price

                    # Parse case quantity
                    parsed = self.unit_converter.parse_pack_size(pack_size)
                    case_quantity = parsed.get('containers', 1)

                    # Get category if available
                    category = None
                    if column_map.get('category'):
                        category = str(row.get(column_map['category'], '')).strip()
                        if category == 'nan':
                            category = None

                    product = VendorProduct(
                        vendor=Vendor.SHAMROCK.value,
                        product_code=product_code,
                        product_name=normalized_name,
                        brand=brand,
                        unit_size=pack_size,
                        case_price=case_price,
                        unit_price=unit_price,
                        case_quantity=case_quantity,
                        category=category
                    )
                    products.append(product)

                except Exception as e:
                    logger.debug(f"Error parsing Shamrock row: {e}")
                    continue

            logger.info(f"Parsed {len(products)} products from Shamrock file")

        except Exception as e:
            logger.error(f"Error reading Shamrock file: {e}")
            raise

        self.products.extend(products)
        return products

    def _map_columns(self, columns: List[str], vendor: str) -> Dict[str, str]:
        """
        Map detected column names to standard field names

        Args:
            columns: List of column names from the spreadsheet
            vendor: Vendor name for vendor-specific mappings

        Returns:
            Dictionary mapping standard field names to actual column names
        """
        column_map = {}

        # Product code patterns
        code_patterns = ['ITEM', 'CODE', 'SKU', 'NUMBER', 'PRODUCT CODE', 'ITEM NUMBER']
        for col in columns:
            if any(p in col for p in code_patterns):
                if 'description' not in col.lower():
                    column_map['product_code'] = col
                    break

        # Description patterns
        desc_patterns = ['DESCRIPTION', 'NAME', 'PRODUCT NAME', 'ITEM DESC']
        for col in columns:
            if any(p in col for p in desc_patterns):
                column_map['description'] = col
                break

        # Pack size patterns
        pack_patterns = ['PACK', 'SIZE', 'PACK SIZE', 'UNIT SIZE']
        for col in columns:
            if any(p in col for p in pack_patterns):
                if 'price' not in col.lower():
                    column_map['pack_size'] = col
                    break

        # Price patterns - case price
        price_patterns = ['PRICE', 'CASE PRICE', 'COST', 'CASE COST', 'TOTAL']
        for col in columns:
            if any(p in col for p in price_patterns):
                if 'split' not in col.lower() and 'unit' not in col.lower():
                    column_map['case_price'] = col
                    break

        # Split price (SYSCO specific)
        if vendor == 'SYSCO':
            for col in columns:
                if 'SPLIT' in col and 'PRICE' in col:
                    column_map['split_price'] = col
                    break

        # Category patterns
        cat_patterns = ['CATEGORY', 'CLASS', 'TYPE', 'GROUP']
        for col in columns:
            if any(p in col for p in cat_patterns):
                column_map['category'] = col
                break

        return column_map

    def _parse_price(self, value) -> float:
        """Parse a price value from various formats"""
        if pd.isna(value):
            return 0.0

        if isinstance(value, (int, float)):
            return float(value)

        # Handle string prices like "$123.45" or "123.45"
        price_str = str(value).strip()
        price_str = re.sub(r'[^\d.]', '', price_str)

        try:
            return float(price_str) if price_str else 0.0
        except ValueError:
            return 0.0

    def _extract_brand(self, description: str) -> Optional[str]:
        """Extract brand name from product description"""
        description_upper = description.upper()

        for brand in MAJOR_BRANDS:
            if brand in description_upper:
                return brand

        return None

    def normalize_product_name(self, name: str) -> str:
        """
        Normalize a product name for matching

        - Converts to uppercase
        - Removes stopwords
        - Removes extra whitespace
        - Removes special characters

        Args:
            name: Product name to normalize

        Returns:
            Normalized product name
        """
        # Convert to uppercase
        name = name.upper()

        # Remove special characters but keep spaces
        name = re.sub(r'[^\w\s]', ' ', name)

        # Split into words and filter stopwords
        words = name.split()
        words = [w for w in words if w not in STOPWORDS]

        # Rejoin and normalize whitespace
        return ' '.join(words)

    def get_products_by_vendor(self, vendor: str) -> List[VendorProduct]:
        """Get all parsed products for a specific vendor"""
        vendor_upper = vendor.upper()
        return [
            p for p in self.products
            if p.vendor.upper() == vendor_upper or
               (vendor_upper == 'SHAMROCK' and p.vendor == Vendor.SHAMROCK.value)
        ]

    def clear(self):
        """Clear all parsed products"""
        self.products = []


# Convenience functions
def parse_sysco_file(file_path: str, **kwargs) -> List[VendorProduct]:
    """Parse a SYSCO spreadsheet file"""
    parser = VendorParser()
    return parser.parse_sysco(file_path, **kwargs)


def parse_shamrock_file(file_path: str, **kwargs) -> List[VendorProduct]:
    """Parse a Shamrock Foods spreadsheet file"""
    parser = VendorParser()
    return parser.parse_shamrock(file_path, **kwargs)
