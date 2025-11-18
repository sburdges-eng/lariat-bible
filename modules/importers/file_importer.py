"""
File Import System
Import data from CSV, Excel, and Google Sheets
No API needed - just upload files!
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime
import numpy as np
import os


class FileImporter:
    """Import data from various file formats"""

    def __init__(self):
        self.supported_formats = ['.csv', '.xlsx', '.xls', '.ods']
        self.import_history = []

    # ==================== CORE IMPORT FUNCTIONS ====================

    def read_file(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        Read file and return DataFrame
        Automatically detects file format

        Args:
            file_path: Path to file
            sheet_name: Sheet name for Excel files (default: first sheet)

        Returns:
            pandas DataFrame with cleaned column names
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Get file extension
        ext = file_path.suffix.lower()

        if ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {ext}. Supported: {self.supported_formats}")

        # Read based on format
        if ext == '.csv':
            df = pd.read_csv(file_path)
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path, sheet_name=sheet_name or 0)
        elif ext == '.ods':
            df = pd.read_excel(file_path, engine='odf', sheet_name=sheet_name or 0)

        # Clean column names (remove spaces, lowercase)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

        # Remove empty rows
        df = df.dropna(how='all')

        return df

    def validate_columns(self, df: pd.DataFrame, required_columns: List[str]) -> Dict:
        """
        Check if DataFrame has required columns

        Args:
            df: DataFrame to validate
            required_columns: List of required column names

        Returns:
            Dict with validation results
        """
        # Normalize column names
        df_cols = set(df.columns)
        required = set(col.lower().replace(' ', '_') for col in required_columns)

        missing = required - df_cols
        extra = df_cols - required

        return {
            'valid': len(missing) == 0,
            'missing_columns': list(missing),
            'extra_columns': list(extra),
            'message': f"Missing columns: {missing}" if missing else "All required columns present"
        }

    # ==================== VENDOR ORDER GUIDE IMPORT ====================

    def import_vendor_order_guide(
        self,
        file_path: str,
        vendor: str,
        sheet_name: Optional[str] = None,
        validate_only: bool = False
    ) -> Dict:
        """
        Import vendor order guide from CSV or Excel

        Args:
            file_path: Path to file
            vendor: 'SYSCO' or 'Shamrock Foods'
            sheet_name: Sheet name for Excel files
            validate_only: If True, only validate, don't import

        Returns:
            Dict with import results
        """
        print(f"📁 Importing {vendor} order guide from {file_path}")

        # Read file
        df = self.read_file(file_path, sheet_name)

        # Required columns
        required = ['item_code', 'description', 'pack_size', 'case_price']

        # Validate
        validation = self.validate_columns(df, required)

        if not validation['valid']:
            return {
                'success': False,
                'error': validation['message'],
                'missing_columns': validation['missing_columns']
            }

        if validate_only:
            return {
                'success': True,
                'message': 'Validation passed',
                'rows': len(df)
            }

        # Process each row
        products = []
        errors = []

        for idx, row in df.iterrows():
            try:
                product = {
                    'vendor': vendor,
                    'item_code': str(row['item_code']).strip(),
                    'description': str(row['description']).strip().upper(),
                    'pack_size': str(row['pack_size']).strip(),
                    'case_price': float(row['case_price']),
                    'unit_price': float(row.get('unit_price', 0)) if 'unit_price' in row and pd.notna(row.get('unit_price')) else None,
                    'unit': str(row.get('unit', 'EACH')).strip().upper() if 'unit' in row and pd.notna(row.get('unit')) else 'EACH',
                    'category': str(row.get('category', 'UNCATEGORIZED')).strip().upper() if 'category' in row and pd.notna(row.get('category')) else 'UNCATEGORIZED',
                    'last_updated': datetime.now()
                }

                # Validate price
                if product['case_price'] <= 0:
                    errors.append(f"Row {idx+2}: Invalid price ${product['case_price']}")
                    continue

                products.append(product)

            except Exception as e:
                errors.append(f"Row {idx+2}: {str(e)}")

        # Save to database or return results
        result = {
            'success': True,
            'vendor': vendor,
            'total_rows': len(df),
            'products_imported': len(products),
            'errors': errors,
            'error_count': len(errors),
            'products': products
        }

        # Record import
        self.import_history.append({
            'timestamp': datetime.now(),
            'type': 'vendor_order_guide',
            'vendor': vendor,
            'file': str(file_path),
            'rows_imported': len(products)
        })

        print(f"✅ Imported {len(products)} products")
        if errors:
            print(f"⚠️  {len(errors)} errors occurred")

        return result

    # ==================== INVOICE IMPORT ====================

    def import_invoice(
        self,
        file_path: str,
        vendor: str,
        sheet_name: Optional[str] = None
    ) -> Dict:
        """
        Import invoice from CSV or Excel

        Args:
            file_path: Path to invoice file
            vendor: Vendor name
            sheet_name: Sheet name for Excel

        Returns:
            Dict with invoice data and totals
        """
        print(f"📄 Importing invoice from {file_path}")

        df = self.read_file(file_path, sheet_name)

        # Required columns for invoice
        required = ['item_code', 'description', 'quantity', 'unit_price', 'extension']

        validation = self.validate_columns(df, required)

        if not validation['valid']:
            return {
                'success': False,
                'error': validation['message']
            }

        # Extract invoice metadata if present
        invoice_number = df['invoice_number'].iloc[0] if 'invoice_number' in df.columns else None
        order_date = df['order_date'].iloc[0] if 'order_date' in df.columns else datetime.now()

        # Process line items
        line_items = []
        total = 0

        for idx, row in df.iterrows():
            try:
                item = {
                    'item_code': str(row['item_code']).strip(),
                    'description': str(row['description']).strip(),
                    'quantity': int(row['quantity']),
                    'unit_price': float(row['unit_price']),
                    'extension': float(row['extension']),
                    'pack_size': str(row.get('pack_size', '')) if 'pack_size' in row and pd.notna(row.get('pack_size')) else ''
                }

                line_items.append(item)
                total += item['extension']

            except Exception as e:
                print(f"⚠️  Row {idx+2} error: {e}")

        result = {
            'success': True,
            'vendor': vendor,
            'invoice_number': invoice_number,
            'order_date': order_date,
            'line_items': line_items,
            'item_count': len(line_items),
            'total_amount': total
        }

        print(f"✅ Imported invoice: {len(line_items)} items, Total: ${total:,.2f}")

        return result

    # ==================== RECIPE IMPORT ====================

    def import_recipes(
        self,
        file_path: str,
        sheet_name: Optional[str] = None
    ) -> Dict:
        """
        Import recipes from CSV or Excel

        Format: Each row is one ingredient in a recipe
        Rows with same Recipe Name are grouped together
        """
        print(f"📖 Importing recipes from {file_path}")

        df = self.read_file(file_path, sheet_name)

        required = ['recipe_name', 'ingredient', 'quantity', 'unit']

        validation = self.validate_columns(df, required)

        if not validation['valid']:
            return {
                'success': False,
                'error': validation['message']
            }

        # Group by recipe
        recipes = {}

        for idx, row in df.iterrows():
            recipe_name = str(row['recipe_name']).strip()

            if recipe_name not in recipes:
                recipes[recipe_name] = {
                    'name': recipe_name,
                    'category': str(row.get('category', 'Uncategorized')) if 'category' in row and pd.notna(row.get('category')) else 'Uncategorized',
                    'yield_amount': float(row.get('yield_amount', 1)) if 'yield_amount' in row and pd.notna(row.get('yield_amount')) else 1,
                    'yield_unit': str(row.get('yield_unit', 'servings')) if 'yield_unit' in row and pd.notna(row.get('yield_unit')) else 'servings',
                    'ingredients': []
                }

            # Add ingredient
            ingredient = {
                'name': str(row['ingredient']).strip(),
                'quantity': float(row['quantity']),
                'unit': str(row['unit']).strip(),
                'prep_instruction': str(row.get('prep_instruction', '')) if 'prep_instruction' in row and pd.notna(row.get('prep_instruction')) else ''
            }

            recipes[recipe_name]['ingredients'].append(ingredient)

        result = {
            'success': True,
            'recipes_imported': len(recipes),
            'recipes': list(recipes.values())
        }

        print(f"✅ Imported {len(recipes)} recipes")

        return result

    # ==================== MENU ITEMS IMPORT ====================

    def import_menu_items(
        self,
        file_path: str,
        sheet_name: Optional[str] = None
    ) -> Dict:
        """Import menu items from CSV or Excel"""
        print(f"🍽️  Importing menu items from {file_path}")

        df = self.read_file(file_path, sheet_name)

        required = ['item_name', 'category', 'menu_price']

        validation = self.validate_columns(df, required)

        if not validation['valid']:
            return {
                'success': False,
                'error': validation['message']
            }

        menu_items = []

        for idx, row in df.iterrows():
            try:
                item = {
                    'name': str(row['item_name']).strip(),
                    'category': str(row['category']).strip(),
                    'subcategory': str(row.get('subcategory', '')) if 'subcategory' in row and pd.notna(row.get('subcategory')) else '',
                    'menu_price': float(row['menu_price']),
                    'recipe_name': str(row.get('recipe_name', '')) if 'recipe_name' in row and pd.notna(row.get('recipe_name')) else '',
                    'portion_size': str(row.get('portion_size', '')) if 'portion_size' in row and pd.notna(row.get('portion_size')) else '',
                    'target_margin': float(row.get('target_margin', 0.45)) if 'target_margin' in row and pd.notna(row.get('target_margin')) else 0.45,
                    'description': str(row.get('description', '')) if 'description' in row and pd.notna(row.get('description')) else ''
                }

                menu_items.append(item)

            except Exception as e:
                print(f"⚠️  Row {idx+2} error: {e}")

        result = {
            'success': True,
            'items_imported': len(menu_items),
            'menu_items': menu_items
        }

        print(f"✅ Imported {len(menu_items)} menu items")

        return result

    # ==================== EXPORT TEMPLATES ====================

    def create_import_templates(self, output_dir: str = 'data/templates'):
        """
        Create template CSV files for importing data

        Saves to output_dir:
        - vendor_order_guide_template.csv
        - invoice_template.csv
        - recipe_template.csv
        - menu_items_template.csv
        """
        os.makedirs(output_dir, exist_ok=True)

        # Vendor Order Guide Template
        order_guide_template = pd.DataFrame({
            'Item Code': ['SYS001', 'SYS002', 'SYS003'],
            'Description': ['GROUND BEEF 80/20', 'BLACK PEPPER COARSE', 'ONION POWDER'],
            'Pack Size': ['10 LB', '6/1LB', '6/1LB'],
            'Case Price': [45.99, 298.95, 148.95],
            'Unit Price': [4.599, 49.83, 24.83],
            'Unit': ['LB', 'LB', 'LB'],
            'Category': ['MEAT', 'SPICES', 'SPICES']
        })
        order_guide_template.to_csv(f'{output_dir}/vendor_order_guide_template.csv', index=False)

        # Invoice Template
        invoice_template = pd.DataFrame({
            'Order Date': ['2025-01-18', '2025-01-18'],
            'Invoice Number': ['INV-12345', 'INV-12345'],
            'Item Code': ['SYS001', 'SYS002'],
            'Description': ['GROUND BEEF 80/20', 'BLACK PEPPER COARSE'],
            'Quantity': [5, 2],
            'Unit Price': [45.99, 298.95],
            'Extension': [229.95, 597.90],
            'Pack Size': ['10 LB', '6/1LB']
        })
        invoice_template.to_csv(f'{output_dir}/invoice_template.csv', index=False)

        # Recipe Template
        recipe_template = pd.DataFrame({
            'Recipe Name': ['BBQ Sauce', 'BBQ Sauce', 'BBQ Sauce', 'Green Chile', 'Green Chile'],
            'Ingredient': ['Tomato Paste', 'Brown Sugar', 'Apple Cider Vinegar', 'Pork Shoulder', 'Green Chiles'],
            'Quantity': [2, 1, 0.5, 5, 3],
            'Unit': ['cups', 'cup', 'cup', 'lbs', 'cans'],
            'Yield Amount': [1, 1, 1, 50, 50],
            'Yield Unit': ['gallon', 'gallon', 'gallon', 'servings', 'servings'],
            'Category': ['Sauce', 'Sauce', 'Sauce', 'Entree', 'Entree']
        })
        recipe_template.to_csv(f'{output_dir}/recipe_template.csv', index=False)

        # Menu Items Template
        menu_template = pd.DataFrame({
            'Item Name': ['Smothered Burrito', 'BBQ Pulled Pork', 'Green Chile Bowl'],
            'Category': ['Entree', 'Entree', 'Entree'],
            'Subcategory': ['Mexican', 'BBQ', 'Mexican'],
            'Menu Price': [12.99, 10.99, 9.99],
            'Recipe Name': ['Green Chile', 'BBQ Sauce', 'Green Chile'],
            'Portion Size': ['12 oz', '8 oz', '10 oz'],
            'Target Margin': [0.45, 0.45, 0.45]
        })
        menu_template.to_csv(f'{output_dir}/menu_items_template.csv', index=False)

        print(f"✅ Created templates in {output_dir}/")
        print(f"   - vendor_order_guide_template.csv")
        print(f"   - invoice_template.csv")
        print(f"   - recipe_template.csv")
        print(f"   - menu_items_template.csv")

        return output_dir


# ==================== CLI USAGE ====================

if __name__ == "__main__":
    import sys

    importer = FileImporter()

    if len(sys.argv) == 1:
        # No arguments - create templates
        print("Creating import templates...")
        importer.create_import_templates('data/templates')
        print("\n📝 Templates created! Fill them out and import with:")
        print("   python -m modules.importers.file_importer import vendor data/sysco.csv SYSCO")
        sys.exit(0)

    command = sys.argv[1]

    if command == 'import':
        import_type = sys.argv[2]
        file_path = sys.argv[3]

        if import_type == 'vendor':
            vendor = sys.argv[4] if len(sys.argv) > 4 else 'SYSCO'
            result = importer.import_vendor_order_guide(file_path, vendor)

        elif import_type == 'invoice':
            vendor = sys.argv[4] if len(sys.argv) > 4 else 'SYSCO'
            result = importer.import_invoice(file_path, vendor)

        elif import_type == 'recipes':
            result = importer.import_recipes(file_path)

        elif import_type == 'menu':
            result = importer.import_menu_items(file_path)

        else:
            print(f"Unknown import type: {import_type}")
            print("Usage: python file_importer.py import [vendor|invoice|recipes|menu] <file_path> [vendor_name]")
            sys.exit(1)

        if result['success']:
            print(f"\n✅ Import successful!")
            print(f"Results: {result}")
        else:
            print(f"\n❌ Import failed: {result.get('error')}")
