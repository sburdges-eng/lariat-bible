"""
Vendor Import Module
Handles importing product data from SYSCO and Shamrock Foods using standardized templates
"""

import csv
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VendorImportError(Exception):
    """Custom exception for vendor import errors"""
    pass


class VendorImporter:
    """
    Handles importing vendor product data using standardized CSV templates
    """

    SUPPORTED_VENDORS = ['SYSCO', 'SHAMROCK']
    TEMPLATE_DIR = 'data/templates'

    def __init__(self):
        self.sysco_schema = self._load_schema('SYSCO_SCHEMA.json')
        self.shamrock_schema = self._load_schema('SHAMROCK_SCHEMA.json')

    def _load_schema(self, schema_file: str) -> Dict[str, Any]:
        """Load JSON schema for vendor"""
        schema_path = os.path.join(self.TEMPLATE_DIR, schema_file)
        try:
            with open(schema_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Schema file not found: {schema_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing schema {schema_file}: {e}")
            return {}

    def import_sysco_products(self, csv_file_path: str) -> Dict[str, Any]:
        """
        Import SYSCO products from CSV file

        Args:
            csv_file_path: Path to SYSCO CSV file

        Returns:
            Dict containing import statistics and any errors
        """
        return self._import_vendor_products(csv_file_path, 'SYSCO')

    def import_shamrock_products(self, csv_file_path: str) -> Dict[str, Any]:
        """
        Import Shamrock Foods products from CSV file

        Args:
            csv_file_path: Path to Shamrock CSV file

        Returns:
            Dict containing import statistics and any errors
        """
        return self._import_vendor_products(csv_file_path, 'SHAMROCK')

    def _import_vendor_products(self, csv_file_path: str, vendor: str) -> Dict[str, Any]:
        """
        Generic vendor product import function

        Args:
            csv_file_path: Path to CSV file
            vendor: Vendor name (SYSCO or SHAMROCK)

        Returns:
            Import results dictionary
        """
        if vendor not in self.SUPPORTED_VENDORS:
            raise VendorImportError(f"Unsupported vendor: {vendor}")

        if not os.path.exists(csv_file_path):
            raise VendorImportError(f"CSV file not found: {csv_file_path}")

        logger.info(f"Starting {vendor} product import from {csv_file_path}")

        products = []
        errors = []
        row_count = 0

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row_num, row in enumerate(reader, start=2):  # Start at 2 to account for header
                    row_count += 1

                    try:
                        # Validate and clean the row data
                        validated_product = self._validate_product_row(row, vendor)
                        products.append(validated_product)

                    except Exception as e:
                        error_msg = f"Row {row_num}: {str(e)}"
                        errors.append(error_msg)
                        logger.warning(error_msg)

        except Exception as e:
            raise VendorImportError(f"Error reading CSV file: {str(e)}")

        # Calculate statistics
        success_count = len(products)
        error_count = len(errors)

        result = {
            'vendor': vendor,
            'file': csv_file_path,
            'timestamp': datetime.now().isoformat(),
            'total_rows': row_count,
            'successful_imports': success_count,
            'failed_imports': error_count,
            'success_rate': (success_count / row_count * 100) if row_count > 0 else 0,
            'products': products,
            'errors': errors
        }

        logger.info(f"{vendor} import complete: {success_count}/{row_count} products imported successfully")

        return result

    def _validate_product_row(self, row: Dict[str, str], vendor: str) -> Dict[str, Any]:
        """
        Validate and convert a product row

        Args:
            row: Raw CSV row data
            vendor: Vendor name

        Returns:
            Validated and typed product dictionary
        """
        product = {}

        # Define required fields by vendor
        if vendor == 'SYSCO':
            required_fields = ['sysco_product_code', 'product_name', 'category', 'pack_size', 'unit_of_measure', 'case_price']
            code_field = 'sysco_product_code'
        else:  # SHAMROCK
            required_fields = ['shamrock_product_code', 'product_name', 'category', 'pack_size', 'unit_of_measure', 'case_price']
            code_field = 'shamrock_product_code'

        # Check required fields
        for field in required_fields:
            if field not in row or not row[field].strip():
                raise ValueError(f"Missing required field: {field}")

        # Convert and validate numeric fields
        numeric_fields = ['case_price', 'unit_price', 'price_per_lb', 'price_per_oz', 'each_weight_lb']
        integer_fields = ['case_quantity', 'shelf_life_days']

        for key, value in row.items():
            if not value or not value.strip():
                continue

            value = value.strip()

            try:
                if key in numeric_fields:
                    product[key] = float(value) if value else None
                elif key in integer_fields:
                    product[key] = int(value) if value else None
                else:
                    product[key] = value
            except ValueError as e:
                raise ValueError(f"Invalid value for {key}: {value}")

        # Validate product code format
        if vendor == 'SYSCO' and not row[code_field].isdigit():
            raise ValueError(f"Invalid SYSCO product code format: {row[code_field]}")
        elif vendor == 'SHAMROCK' and not row[code_field].startswith('SF-'):
            raise ValueError(f"Invalid Shamrock product code format: {row[code_field]}")

        # Validate price consistency
        if 'case_price' in product and 'unit_price' in product and 'case_quantity' in product:
            if product['case_price'] and product['unit_price'] and product['case_quantity']:
                expected_case_price = product['unit_price'] * product['case_quantity']
                if abs(product['case_price'] - expected_case_price) > 0.02:
                    logger.warning(
                        f"Price mismatch for {row[code_field]}: "
                        f"case_price={product['case_price']}, "
                        f"expected={expected_case_price}"
                    )

        # Add metadata
        product['vendor'] = vendor
        product['import_date'] = datetime.now().isoformat()

        return product

    def compare_vendor_pricing(self, sysco_products: List[Dict], shamrock_products: List[Dict]) -> List[Dict]:
        """
        Compare pricing between SYSCO and Shamrock products

        Args:
            sysco_products: List of SYSCO products
            shamrock_products: List of Shamrock products

        Returns:
            List of price comparisons
        """
        comparisons = []

        # Create lookup dict by product name for Shamrock
        shamrock_lookup = {p['product_name'].lower(): p for p in shamrock_products}

        for sysco_product in sysco_products:
            product_name = sysco_product['product_name'].lower()

            if product_name in shamrock_lookup:
                shamrock_product = shamrock_lookup[product_name]

                sysco_price = sysco_product.get('price_per_lb') or sysco_product.get('unit_price', 0)
                shamrock_price = shamrock_product.get('price_per_lb') or shamrock_product.get('unit_price', 0)

                if sysco_price and shamrock_price:
                    savings = sysco_price - shamrock_price
                    savings_percent = (savings / sysco_price * 100) if sysco_price > 0 else 0

                    comparison = {
                        'product_name': sysco_product['product_name'],
                        'sysco_price': sysco_price,
                        'shamrock_price': shamrock_price,
                        'savings': savings,
                        'savings_percent': savings_percent,
                        'preferred_vendor': 'Shamrock' if shamrock_price < sysco_price else 'SYSCO',
                        'category': sysco_product.get('category', 'Unknown')
                    }

                    comparisons.append(comparison)

        # Sort by savings amount (descending)
        comparisons.sort(key=lambda x: x['savings'], reverse=True)

        return comparisons

    def export_comparison_to_csv(self, comparisons: List[Dict], output_file: str):
        """
        Export price comparisons to CSV file

        Args:
            comparisons: List of comparison dictionaries
            output_file: Path to output CSV file
        """
        if not comparisons:
            logger.warning("No comparisons to export")
            return

        fieldnames = ['product_name', 'sysco_price', 'shamrock_price', 'savings',
                     'savings_percent', 'preferred_vendor', 'category']

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(comparisons)

        logger.info(f"Comparison exported to {output_file}")

    def get_template_path(self, vendor: str) -> str:
        """
        Get the path to a vendor's import template

        Args:
            vendor: Vendor name (SYSCO or SHAMROCK)

        Returns:
            Path to template CSV file
        """
        if vendor not in self.SUPPORTED_VENDORS:
            raise VendorImportError(f"Unsupported vendor: {vendor}")

        template_file = f"{vendor}_IMPORT_TEMPLATE.csv"
        return os.path.join(self.TEMPLATE_DIR, template_file)

    def validate_import_file(self, csv_file_path: str, vendor: str) -> Dict[str, Any]:
        """
        Validate an import file without actually importing

        Args:
            csv_file_path: Path to CSV file
            vendor: Vendor name

        Returns:
            Validation results dictionary
        """
        logger.info(f"Validating {vendor} import file: {csv_file_path}")

        errors = []
        warnings = []
        row_count = 0

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames

                # Check for required headers
                if vendor == 'SYSCO':
                    required_headers = ['sysco_product_code', 'product_name', 'category', 'case_price']
                else:
                    required_headers = ['shamrock_product_code', 'product_name', 'category', 'case_price']

                missing_headers = [h for h in required_headers if h not in headers]
                if missing_headers:
                    errors.append(f"Missing required columns: {', '.join(missing_headers)}")

                # Validate rows
                for row_num, row in enumerate(reader, start=2):
                    row_count += 1

                    try:
                        self._validate_product_row(row, vendor)
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")

        except Exception as e:
            errors.append(f"Error reading file: {str(e)}")

        is_valid = len(errors) == 0

        return {
            'valid': is_valid,
            'file': csv_file_path,
            'vendor': vendor,
            'row_count': row_count,
            'errors': errors,
            'warnings': warnings
        }


# Example usage
if __name__ == "__main__":
    importer = VendorImporter()

    # Example: Import SYSCO products
    sysco_template = importer.get_template_path('SYSCO')
    print(f"SYSCO template path: {sysco_template}")

    # Example: Validate a file before import
    validation = importer.validate_import_file(sysco_template, 'SYSCO')
    print(f"Validation result: {validation['valid']}")

    if validation['valid']:
        # Import the products
        result = importer.import_sysco_products(sysco_template)
        print(f"Imported {result['successful_imports']} SYSCO products")
