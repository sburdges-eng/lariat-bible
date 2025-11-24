"""
Open Food Facts API Integration
================================
FREE open-source food product database - NO API KEY REQUIRED.

Website: https://world.openfoodfacts.org

Features:
- 3+ million food products worldwide
- Barcode/UPC lookup
- Nutritional information
- Ingredients lists
- Allergen information
- Nutri-Score ratings
- Open data - completely free
"""

from typing import Any, Dict, List, Optional
from .base_client import BaseClient, cached


class OpenFoodFactsClient(BaseClient):
    """
    Client for Open Food Facts API

    Completely FREE, no API key required.
    Open-source database with 3+ million products.
    """

    NUTRI_SCORE_GRADES = ['a', 'b', 'c', 'd', 'e']

    def __init__(self):
        super().__init__()
        self.base_url = self.config.OPEN_FOOD_FACTS_BASE_URL
        self.session.headers.update({
            'User-Agent': self.config.OPEN_FOOD_FACTS_USER_AGENT
        })

    def health_check(self) -> Dict[str, Any]:
        """Check if Open Food Facts API is accessible"""
        # Try a simple search to verify connectivity
        result = self._get(
            f"{self.base_url}/search",
            params={'search_terms': 'test', 'page_size': 1, 'json': 1}
        )

        if result and not result.get('error'):
            return {
                'available': True,
                'source': 'Open Food Facts',
                'message': 'API is accessible (no key required)',
                'product_count': result.get('count', 0)
            }

        return {
            'available': False,
            'source': 'Open Food Facts',
            'message': result.get('message', 'API unavailable') if result else 'Connection failed'
        }

    @cached(ttl=86400)
    def search(
        self,
        query: str,
        page: int = 1,
        page_size: int = 25,
        sort_by: str = 'unique_scans_n',
        countries: Optional[str] = 'united-states',
        categories: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for food products

        Args:
            query: Search term
            page: Page number
            page_size: Results per page (max 100)
            sort_by: Sort field (unique_scans_n, product_name, created_t)
            countries: Filter by country tag
            categories: Filter by category tag

        Returns:
            List of matching products
        """
        params = {
            'search_terms': query,
            'page': page,
            'page_size': min(page_size, 100),
            'sort_by': sort_by,
            'json': 1
        }

        if countries:
            params['countries_tags_en'] = countries

        if categories:
            params['categories_tags_en'] = categories

        result = self._get(f"{self.base_url}/search", params=params)

        if result and not result.get('error'):
            products = result.get('products', [])
            return [self._format_product(p) for p in products]

        return []

    @cached(ttl=86400)
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict]:
        """
        Get product information by barcode/UPC

        Args:
            barcode: Product barcode (UPC, EAN, etc.)

        Returns:
            Product information or None if not found
        """
        result = self._get(f"{self.base_url}/product/{barcode}")

        if result and result.get('status') == 1:
            return self._format_product(result.get('product', {}))

        return None

    @cached(ttl=3600)
    def search_by_category(self, category: str, page: int = 1) -> List[Dict]:
        """
        Search products by category

        Args:
            category: Category name (e.g., 'spices', 'sauces', 'meats')
            page: Page number

        Returns:
            List of products in category
        """
        result = self._get(
            f"https://world.openfoodfacts.org/category/{category}.json",
            params={'page': page}
        )

        if result and not result.get('error'):
            products = result.get('products', [])
            return [self._format_product(p) for p in products]

        return []

    @cached(ttl=3600)
    def search_by_brand(self, brand: str, page: int = 1) -> List[Dict]:
        """
        Search products by brand

        Args:
            brand: Brand name
            page: Page number

        Returns:
            List of products from brand
        """
        brand_tag = brand.lower().replace(' ', '-')
        result = self._get(
            f"https://world.openfoodfacts.org/brand/{brand_tag}.json",
            params={'page': page}
        )

        if result and not result.get('error'):
            products = result.get('products', [])
            return [self._format_product(p) for p in products]

        return []

    def get_allergens(self, barcode: str) -> Optional[Dict]:
        """
        Get allergen information for a product

        Args:
            barcode: Product barcode

        Returns:
            Allergen information
        """
        product = self.get_product_by_barcode(barcode)

        if product:
            return {
                'barcode': barcode,
                'product_name': product.get('product_name'),
                'allergens': product.get('allergens', []),
                'allergens_tags': product.get('allergens_tags', []),
                'traces': product.get('traces', []),
                'traces_tags': product.get('traces_tags', [])
            }

        return None

    def get_ingredients(self, barcode: str) -> Optional[Dict]:
        """
        Get ingredient list for a product

        Args:
            barcode: Product barcode

        Returns:
            Ingredient information
        """
        product = self.get_product_by_barcode(barcode)

        if product:
            return {
                'barcode': barcode,
                'product_name': product.get('product_name'),
                'ingredients_text': product.get('ingredients_text'),
                'ingredients': product.get('ingredients', []),
                'additives': product.get('additives', []),
                'ingredients_from_palm_oil': product.get('ingredients_from_palm_oil', [])
            }

        return None

    @cached(ttl=86400)
    def get_categories(self) -> List[Dict]:
        """
        Get list of all product categories

        Returns:
            List of categories with product counts
        """
        result = self._get("https://world.openfoodfacts.org/categories.json")

        if result and not result.get('error'):
            return [
                {
                    'name': cat.get('name'),
                    'id': cat.get('id'),
                    'products': cat.get('products', 0),
                    'url': cat.get('url')
                }
                for cat in result.get('tags', [])[:100]  # Top 100 categories
            ]

        return []

    def _format_product(self, product: Dict) -> Dict:
        """Format product data"""
        nutriments = product.get('nutriments', {})

        return {
            'barcode': product.get('code'),
            'product_name': product.get('product_name'),
            'brand': product.get('brands'),
            'categories': product.get('categories'),
            'quantity': product.get('quantity'),
            'serving_size': product.get('serving_size'),
            'image_url': product.get('image_url'),
            'image_small_url': product.get('image_small_url'),

            # Nutrition per 100g
            'nutrition_per_100g': {
                'energy_kcal': nutriments.get('energy-kcal_100g'),
                'fat': nutriments.get('fat_100g'),
                'saturated_fat': nutriments.get('saturated-fat_100g'),
                'carbohydrates': nutriments.get('carbohydrates_100g'),
                'sugars': nutriments.get('sugars_100g'),
                'fiber': nutriments.get('fiber_100g'),
                'proteins': nutriments.get('proteins_100g'),
                'salt': nutriments.get('salt_100g'),
                'sodium': nutriments.get('sodium_100g'),
            },

            # Scores and grades
            'nutriscore_grade': product.get('nutriscore_grade'),
            'nutriscore_score': product.get('nutriscore_score'),
            'nova_group': product.get('nova_group'),
            'ecoscore_grade': product.get('ecoscore_grade'),

            # Allergens and labels
            'allergens': product.get('allergens', '').split(',') if product.get('allergens') else [],
            'allergens_tags': product.get('allergens_tags', []),
            'traces': product.get('traces', '').split(',') if product.get('traces') else [],
            'labels': product.get('labels'),
            'labels_tags': product.get('labels_tags', []),

            # Ingredients
            'ingredients_text': product.get('ingredients_text'),
            'ingredients_count': len(product.get('ingredients', [])),

            # Origin
            'countries': product.get('countries'),
            'origins': product.get('origins'),
            'manufacturing_places': product.get('manufacturing_places'),

            'source': 'Open Food Facts'
        }
