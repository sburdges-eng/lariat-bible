"""
USDA FoodData Central API Integration
======================================
FREE API for comprehensive food and nutrition data.

Get your free API key at: https://fdc.nal.usda.gov/api-key-signup.html

Features:
- Search foods by name or keyword
- Get detailed nutritional information
- Access branded food products
- Foundation foods (raw ingredients)
- Survey foods (NHANES data)
"""

from typing import Any, Dict, List, Optional
from .base_client import BaseClient, cached


class USDAFoodDataClient(BaseClient):
    """
    Client for USDA FoodData Central API

    Free API providing:
    - Nutritional data for 300,000+ foods
    - Branded products with UPC codes
    - Foundation foods (raw ingredients)
    - Nutrient analysis
    """

    FOOD_TYPES = {
        'foundation': 'Foundation',      # Raw agricultural commodities
        'sr_legacy': 'SR Legacy',        # Standard Reference Legacy
        'survey_fndds': 'Survey (FNDDS)', # NHANES survey foods
        'branded': 'Branded',            # Branded food products
    }

    NUTRIENTS = {
        'energy': 1008,           # Calories (kcal)
        'protein': 1003,          # Protein (g)
        'fat': 1004,              # Total fat (g)
        'carbs': 1005,            # Carbohydrates (g)
        'fiber': 1079,            # Dietary fiber (g)
        'sugar': 2000,            # Total sugars (g)
        'sodium': 1093,           # Sodium (mg)
        'cholesterol': 1253,      # Cholesterol (mg)
        'saturated_fat': 1258,    # Saturated fat (g)
        'vitamin_a': 1106,        # Vitamin A (IU)
        'vitamin_c': 1162,        # Vitamin C (mg)
        'calcium': 1087,          # Calcium (mg)
        'iron': 1089,             # Iron (mg)
        'potassium': 1092,        # Potassium (mg)
    }

    def __init__(self):
        super().__init__()
        self.base_url = self.config.USDA_FOODDATA_BASE_URL
        self.api_key = self.config.USDA_FOODDATA_API_KEY

    def _get_params(self, extra_params: Optional[Dict] = None) -> Dict:
        """Get request parameters with API key"""
        params = {'api_key': self.api_key} if self.api_key else {}
        if extra_params:
            params.update(extra_params)
        return params

    def health_check(self) -> Dict[str, Any]:
        """Check if USDA FoodData Central API is accessible"""
        if not self.api_key:
            return {
                'available': False,
                'source': 'USDA FoodData Central',
                'message': 'API key not configured. Get free key at: https://fdc.nal.usda.gov/api-key-signup.html'
            }

        # Try a simple search to verify connectivity
        result = self._get(
            f"{self.base_url}/foods/search",
            params=self._get_params({'query': 'test', 'pageSize': 1})
        )

        if result and not result.get('error'):
            return {
                'available': True,
                'source': 'USDA FoodData Central',
                'message': 'API is accessible',
                'total_foods': result.get('totalHits', 0)
            }

        return {
            'available': False,
            'source': 'USDA FoodData Central',
            'message': result.get('message', 'API unavailable')
        }

    @cached(ttl=3600)
    def search(
        self,
        query: str,
        food_types: Optional[List[str]] = None,
        page_size: int = 25,
        page_number: int = 1,
        sort_by: str = 'dataType.keyword',
        sort_order: str = 'asc',
        brand_owner: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for foods by keyword

        Args:
            query: Search term (e.g., 'black pepper', 'chicken breast')
            food_types: Filter by type ['foundation', 'branded', 'sr_legacy', 'survey_fndds']
            page_size: Results per page (max 200)
            page_number: Page number for pagination
            sort_by: Field to sort by
            sort_order: 'asc' or 'desc'
            brand_owner: Filter by brand owner name

        Returns:
            List of matching food items with basic info
        """
        if not self.api_key:
            return []

        params = self._get_params({
            'query': query,
            'pageSize': min(page_size, 200),
            'pageNumber': page_number,
            'sortBy': sort_by,
            'sortOrder': sort_order
        })

        if food_types:
            params['dataType'] = ','.join([
                self.FOOD_TYPES.get(ft, ft) for ft in food_types
            ])

        if brand_owner:
            params['brandOwner'] = brand_owner

        result = self._get(f"{self.base_url}/foods/search", params=params)

        if result and not result.get('error'):
            foods = result.get('foods', [])
            return [self._format_food_item(food) for food in foods]

        return []

    @cached(ttl=86400)
    def get_food(self, fdc_id: int, nutrients: Optional[List[int]] = None) -> Optional[Dict]:
        """
        Get detailed information for a specific food item

        Args:
            fdc_id: FoodData Central ID
            nutrients: List of nutrient IDs to include (default: all)

        Returns:
            Detailed food information including nutrients
        """
        if not self.api_key:
            return None

        params = self._get_params()
        if nutrients:
            params['nutrients'] = ','.join(map(str, nutrients))

        result = self._get(f"{self.base_url}/food/{fdc_id}", params=params)

        if result and not result.get('error'):
            return self._format_food_detail(result)

        return None

    @cached(ttl=86400)
    def get_foods(self, fdc_ids: List[int], nutrients: Optional[List[int]] = None) -> List[Dict]:
        """
        Get detailed information for multiple foods at once

        Args:
            fdc_ids: List of FoodData Central IDs
            nutrients: List of nutrient IDs to include

        Returns:
            List of detailed food information
        """
        if not self.api_key or not fdc_ids:
            return []

        data = {'fdcIds': fdc_ids}
        if nutrients:
            data['nutrients'] = nutrients

        params = self._get_params()
        result = self._post(f"{self.base_url}/foods", data=data)

        if result and not result.get('error') and isinstance(result, list):
            return [self._format_food_detail(food) for food in result]

        return []

    @cached(ttl=3600)
    def search_ingredients(self, ingredient_name: str) -> List[Dict]:
        """
        Search for raw ingredients (foundation foods)

        Best for matching recipe ingredients to nutritional data.

        Args:
            ingredient_name: Name of ingredient (e.g., 'garlic powder')

        Returns:
            List of matching foundation foods
        """
        return self.search(
            query=ingredient_name,
            food_types=['foundation', 'sr_legacy'],
            page_size=10
        )

    @cached(ttl=3600)
    def search_branded_products(
        self,
        product_name: str,
        brand: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for branded food products

        Args:
            product_name: Product name or description
            brand: Brand owner name filter

        Returns:
            List of matching branded products
        """
        return self.search(
            query=product_name,
            food_types=['branded'],
            brand_owner=brand,
            page_size=25
        )

    def get_nutrition_facts(self, fdc_id: int) -> Optional[Dict]:
        """
        Get nutrition facts label data for a food

        Args:
            fdc_id: FoodData Central ID

        Returns:
            Nutrition facts in label format
        """
        food = self.get_food(fdc_id, nutrients=list(self.NUTRIENTS.values()))

        if not food:
            return None

        nutrients = food.get('nutrients', {})

        return {
            'food_name': food.get('description'),
            'serving_size': food.get('serving_size', '100g'),
            'calories': nutrients.get('energy', 0),
            'total_fat': nutrients.get('fat', 0),
            'saturated_fat': nutrients.get('saturated_fat', 0),
            'cholesterol': nutrients.get('cholesterol', 0),
            'sodium': nutrients.get('sodium', 0),
            'total_carbohydrates': nutrients.get('carbs', 0),
            'dietary_fiber': nutrients.get('fiber', 0),
            'sugars': nutrients.get('sugar', 0),
            'protein': nutrients.get('protein', 0),
            'vitamin_a': nutrients.get('vitamin_a', 0),
            'vitamin_c': nutrients.get('vitamin_c', 0),
            'calcium': nutrients.get('calcium', 0),
            'iron': nutrients.get('iron', 0),
            'potassium': nutrients.get('potassium', 0),
        }

    def _format_food_item(self, food: Dict) -> Dict:
        """Format food search result"""
        return {
            'fdc_id': food.get('fdcId'),
            'description': food.get('description'),
            'data_type': food.get('dataType'),
            'brand_owner': food.get('brandOwner'),
            'brand_name': food.get('brandName'),
            'gtin_upc': food.get('gtinUpc'),
            'ingredients': food.get('ingredients'),
            'serving_size': food.get('servingSize'),
            'serving_unit': food.get('servingSizeUnit'),
            'source': 'USDA FoodData Central'
        }

    def _format_food_detail(self, food: Dict) -> Dict:
        """Format detailed food information"""
        nutrients = {}
        for nutrient in food.get('foodNutrients', []):
            nutrient_data = nutrient.get('nutrient', nutrient)
            nutrient_id = nutrient_data.get('id') or nutrient_data.get('nutrientId')
            nutrient_name = nutrient_data.get('name', '').lower().replace(' ', '_')
            value = nutrient.get('amount') or nutrient.get('value', 0)

            if nutrient_id:
                # Map by ID to our standard names
                for name, nid in self.NUTRIENTS.items():
                    if nid == nutrient_id:
                        nutrients[name] = value
                        break
                else:
                    nutrients[nutrient_name] = value

        return {
            'fdc_id': food.get('fdcId'),
            'description': food.get('description'),
            'data_type': food.get('dataType'),
            'brand_owner': food.get('brandOwner'),
            'brand_name': food.get('brandName'),
            'gtin_upc': food.get('gtinUpc'),
            'ingredients': food.get('ingredients'),
            'serving_size': food.get('servingSize'),
            'serving_unit': food.get('servingSizeUnit'),
            'nutrients': nutrients,
            'source': 'USDA FoodData Central'
        }
