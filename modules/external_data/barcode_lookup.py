"""
Barcode/UPC Lookup Integration
===============================
FREE product lookup by barcode/UPC.

Data Sources:
- Open Food Facts (FREE, no key required)
- UPC Database (FREE tier with key)
- Barcode Lookup (FREE tier with key)
- Open Product Data (FREE, no key required)

Features:
- Product information by UPC/EAN barcode
- Brand and manufacturer data
- Product descriptions
- Pricing information
"""

from typing import Any, Dict, List, Optional
from .base_client import BaseClient, cached


class BarcodeLookupClient(BaseClient):
    """
    Client for barcode/UPC product lookup

    Multiple data sources for comprehensive product coverage.
    Primary: Open Food Facts (FREE, no key required)
    """

    def __init__(self):
        super().__init__()
        # Open Product Data is the primary free source
        self.open_product_url = self.config.OPEN_PRODUCT_DATA_BASE_URL
        self.upc_database_url = self.config.UPC_DATABASE_BASE_URL
        self.barcode_lookup_url = self.config.BARCODE_LOOKUP_BASE_URL

        # API keys (optional)
        self.upc_key = self.config.UPC_DATABASE_API_KEY
        self.barcode_key = self.config.BARCODE_LOOKUP_API_KEY

    def health_check(self) -> Dict[str, Any]:
        """Check if barcode lookup services are accessible"""
        # Check Open Food Facts (always free)
        try:
            result = self._get(
                "https://world.openfoodfacts.org/api/v0/product/737628064502.json"
            )
            available = result and result.get('status') == 1
        except Exception:
            available = False

        sources = ['Open Food Facts (FREE)']
        if self.upc_key:
            sources.append('UPC Database')
        if self.barcode_key:
            sources.append('Barcode Lookup')

        return {
            'available': available,
            'source': 'Barcode Lookup',
            'message': f'Available sources: {", ".join(sources)}',
            'configured_sources': sources
        }

    @cached(ttl=86400)
    def search(self, query: str, **kwargs) -> List[Dict]:
        """Search products by name (uses Open Food Facts)"""
        result = self._get(
            "https://world.openfoodfacts.org/cgi/search.pl",
            params={
                'search_terms': query,
                'search_simple': 1,
                'action': 'process',
                'json': 1,
                'page_size': kwargs.get('limit', 20)
            }
        )

        if result and result.get('products'):
            return [self._format_product(p) for p in result['products']]

        return []

    @cached(ttl=86400)
    def lookup(self, barcode: str) -> Optional[Dict]:
        """
        Look up product by barcode/UPC

        Tries multiple sources in order of preference.

        Args:
            barcode: Product barcode (UPC, EAN, etc.)

        Returns:
            Product information or None if not found
        """
        # Clean barcode
        barcode = barcode.strip().replace('-', '').replace(' ', '')

        # Try sources in order
        product = self._lookup_open_food_facts(barcode)
        if product:
            return product

        if self.upc_key:
            product = self._lookup_upc_database(barcode)
            if product:
                return product

        if self.barcode_key:
            product = self._lookup_barcode_api(barcode)
            if product:
                return product

        return None

    @cached(ttl=86400)
    def lookup_batch(self, barcodes: List[str]) -> Dict[str, Optional[Dict]]:
        """
        Look up multiple products by barcode

        Args:
            barcodes: List of barcodes to look up

        Returns:
            Dict mapping barcode to product info
        """
        results = {}
        for barcode in barcodes:
            results[barcode] = self.lookup(barcode)
        return results

    def _lookup_open_food_facts(self, barcode: str) -> Optional[Dict]:
        """Look up product in Open Food Facts database"""
        result = self._get(
            f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        )

        if result and result.get('status') == 1:
            product = result.get('product', {})
            return self._format_product(product)

        return None

    def _lookup_upc_database(self, barcode: str) -> Optional[Dict]:
        """Look up product in UPC Database (requires API key)"""
        if not self.upc_key:
            return None

        result = self._get(
            f"{self.upc_database_url}/product/{barcode}",
            headers={'Authorization': f'Bearer {self.upc_key}'}
        )

        if result and not result.get('error'):
            return {
                'barcode': barcode,
                'name': result.get('title'),
                'brand': result.get('brand'),
                'description': result.get('description'),
                'category': result.get('category'),
                'msrp': result.get('msrp'),
                'image_url': result.get('images', [None])[0] if result.get('images') else None,
                'source': 'UPC Database'
            }

        return None

    def _lookup_barcode_api(self, barcode: str) -> Optional[Dict]:
        """Look up product in Barcode Lookup API (requires API key)"""
        if not self.barcode_key:
            return None

        result = self._get(
            f"{self.barcode_lookup_url}/products",
            params={
                'barcode': barcode,
                'formatted': 'y',
                'key': self.barcode_key
            }
        )

        if result and result.get('products'):
            product = result['products'][0]
            return {
                'barcode': barcode,
                'name': product.get('product_name') or product.get('title'),
                'brand': product.get('brand'),
                'description': product.get('description'),
                'category': product.get('category'),
                'manufacturer': product.get('manufacturer'),
                'msrp': product.get('msrp'),
                'image_url': product.get('images', [None])[0] if product.get('images') else None,
                'stores': product.get('stores', []),
                'source': 'Barcode Lookup API'
            }

        return None

    def get_vendor_product_match(
        self,
        barcode: str,
        vendor_name: str
    ) -> Optional[Dict]:
        """
        Match barcode to vendor product

        Useful for matching SYSCO/Shamrock products to standard UPCs.

        Args:
            barcode: Product barcode
            vendor_name: Vendor name (e.g., 'SYSCO', 'Shamrock')

        Returns:
            Product match info
        """
        product = self.lookup(barcode)

        if product:
            return {
                'barcode': barcode,
                'product_name': product.get('name'),
                'brand': product.get('brand'),
                'vendor': vendor_name,
                'matched': True,
                'product_data': product,
                'source': product.get('source')
            }

        return {
            'barcode': barcode,
            'vendor': vendor_name,
            'matched': False,
            'message': 'Product not found in database'
        }

    def _format_product(self, product: Dict) -> Dict:
        """Format product data from Open Food Facts"""
        nutriments = product.get('nutriments', {})

        return {
            'barcode': product.get('code'),
            'name': product.get('product_name'),
            'brand': product.get('brands'),
            'brand_owner': product.get('brand_owner'),
            'categories': product.get('categories'),
            'quantity': product.get('quantity'),
            'serving_size': product.get('serving_size'),

            # Nutrition per 100g
            'nutrition': {
                'calories': nutriments.get('energy-kcal_100g'),
                'fat': nutriments.get('fat_100g'),
                'saturated_fat': nutriments.get('saturated-fat_100g'),
                'carbohydrates': nutriments.get('carbohydrates_100g'),
                'sugars': nutriments.get('sugars_100g'),
                'fiber': nutriments.get('fiber_100g'),
                'proteins': nutriments.get('proteins_100g'),
                'sodium': nutriments.get('sodium_100g'),
                'salt': nutriments.get('salt_100g'),
            },

            # Additional info
            'ingredients_text': product.get('ingredients_text'),
            'allergens': product.get('allergens'),
            'nutriscore': product.get('nutriscore_grade'),
            'nova_group': product.get('nova_group'),

            # Images
            'image_url': product.get('image_url'),
            'image_small_url': product.get('image_small_url'),

            # Origin
            'countries': product.get('countries'),
            'origins': product.get('origins'),

            'source': 'Open Food Facts'
        }

    def validate_barcode(self, barcode: str) -> Dict:
        """
        Validate barcode format

        Args:
            barcode: Barcode string to validate

        Returns:
            Validation result with barcode type
        """
        barcode = barcode.strip().replace('-', '').replace(' ', '')

        # Check format
        if not barcode.isdigit():
            return {'valid': False, 'error': 'Barcode must contain only digits'}

        length = len(barcode)
        barcode_types = {
            8: 'EAN-8',
            12: 'UPC-A',
            13: 'EAN-13',
            14: 'GTIN-14'
        }

        if length not in barcode_types:
            return {
                'valid': False,
                'error': f'Invalid barcode length: {length}. Expected 8, 12, 13, or 14 digits'
            }

        # Validate check digit
        if not self._validate_check_digit(barcode):
            return {
                'valid': False,
                'error': 'Invalid check digit',
                'type': barcode_types[length]
            }

        return {
            'valid': True,
            'barcode': barcode,
            'type': barcode_types[length],
            'length': length
        }

    def _validate_check_digit(self, barcode: str) -> bool:
        """Validate barcode check digit using standard algorithm"""
        digits = [int(d) for d in barcode]
        check = digits[-1]

        # Calculate expected check digit
        total = 0
        for i, digit in enumerate(digits[:-1]):
            if (len(barcode) - i) % 2 == 0:
                total += digit * 3
            else:
                total += digit

        expected_check = (10 - (total % 10)) % 10
        return check == expected_check
