"""
Edamam API Integration
=======================
FREE tier: 1,000 API calls/month.

Get your free key at: https://developer.edamam.com

Features:
- Recipe search and analysis
- Nutritional analysis
- Food database
- Diet and health labels
- Meal type classification
"""

from typing import Any, Dict, List, Optional
from .base_client import BaseClient, cached


class EdamamClient(BaseClient):
    """
    Client for Edamam Food and Recipe API

    FREE tier: 1,000 API calls/month
    Comprehensive recipe and nutrition database.
    """

    DIET_LABELS = [
        'balanced', 'high-fiber', 'high-protein', 'low-carb',
        'low-fat', 'low-sodium'
    ]

    HEALTH_LABELS = [
        'alcohol-cocktail', 'alcohol-free', 'celery-free', 'crustacean-free',
        'dairy-free', 'DASH', 'egg-free', 'fish-free', 'fodmap-free',
        'gluten-free', 'immuno-supportive', 'keto-friendly', 'kidney-friendly',
        'kosher', 'low-fat-abs', 'low-potassium', 'low-sugar', 'lupine-free',
        'Mediterranean', 'mollusk-free', 'mustard-free', 'no-oil-added',
        'paleo', 'peanut-free', 'pescatarian', 'pork-free', 'red-meat-free',
        'sesame-free', 'shellfish-free', 'soy-free', 'sugar-conscious',
        'sulfite-free', 'tree-nut-free', 'vegan', 'vegetarian', 'wheat-free'
    ]

    MEAL_TYPES = ['Breakfast', 'Lunch', 'Dinner', 'Snack', 'Teatime']

    DISH_TYPES = [
        'Biscuits and cookies', 'Bread', 'Cereals', 'Condiments and sauces',
        'Desserts', 'Drinks', 'Main course', 'Pancake', 'Preps', 'Preserve',
        'Salad', 'Sandwiches', 'Side dish', 'Soup', 'Starter', 'Sweets'
    ]

    def __init__(self):
        super().__init__()
        self.base_url = self.config.EDAMAM_BASE_URL
        self.app_id = self.config.EDAMAM_APP_ID
        self.app_key = self.config.EDAMAM_APP_KEY

    def _get_params(self, extra_params: Optional[Dict] = None) -> Dict:
        """Get request parameters with API credentials"""
        params = {}
        if self.app_id and self.app_key:
            params['app_id'] = self.app_id
            params['app_key'] = self.app_key
        if extra_params:
            params.update(extra_params)
        return params

    def health_check(self) -> Dict[str, Any]:
        """Check if Edamam API is accessible"""
        if not self.app_id or not self.app_key:
            return {
                'available': False,
                'source': 'Edamam',
                'message': 'API credentials not configured. Get free key at: https://developer.edamam.com'
            }

        # Try a simple search
        result = self._get(
            f"{self.base_url}/recipes/v2",
            params=self._get_params({'q': 'test', 'type': 'public'})
        )

        if result and not result.get('error'):
            return {
                'available': True,
                'source': 'Edamam',
                'message': 'API is accessible (1,000 calls/month free)'
            }

        return {
            'available': False,
            'source': 'Edamam',
            'message': result.get('message', 'API unavailable')
        }

    @cached(ttl=3600)
    def search(self, query: str, **kwargs) -> List[Dict]:
        """Search for recipes (alias for search_recipes)"""
        return self.search_recipes(query, **kwargs)

    @cached(ttl=3600)
    def search_recipes(
        self,
        query: str,
        diet: Optional[List[str]] = None,
        health: Optional[List[str]] = None,
        cuisine_type: Optional[List[str]] = None,
        meal_type: Optional[List[str]] = None,
        dish_type: Optional[List[str]] = None,
        calories: Optional[str] = None,
        time: Optional[str] = None,
        num_results: int = 20
    ) -> List[Dict]:
        """
        Search for recipes

        Args:
            query: Search term
            diet: Diet labels (see DIET_LABELS)
            health: Health labels (see HEALTH_LABELS)
            cuisine_type: Cuisine types (e.g., 'American', 'Mexican')
            meal_type: Meal types (see MEAL_TYPES)
            dish_type: Dish types (see DISH_TYPES)
            calories: Calorie range (e.g., '100-500')
            time: Time range in minutes (e.g., '1-60')
            num_results: Number of results to return

        Returns:
            List of matching recipes
        """
        if not self.app_id or not self.app_key:
            return []

        params = self._get_params({
            'q': query,
            'type': 'public'
        })

        if diet:
            params['diet'] = diet
        if health:
            params['health'] = health
        if cuisine_type:
            params['cuisineType'] = cuisine_type
        if meal_type:
            params['mealType'] = meal_type
        if dish_type:
            params['dishType'] = dish_type
        if calories:
            params['calories'] = calories
        if time:
            params['time'] = time

        result = self._get(f"{self.base_url}/recipes/v2", params=params)

        if result and not result.get('error'):
            hits = result.get('hits', [])[:num_results]
            return [self._format_recipe(h.get('recipe', {})) for h in hits]

        return []

    @cached(ttl=3600)
    def analyze_nutrition(
        self,
        ingredients: List[str],
        title: str = "Recipe Analysis"
    ) -> Optional[Dict]:
        """
        Analyze nutrition for a list of ingredients

        Args:
            ingredients: List of ingredient strings (e.g., ['1 cup flour', '2 eggs'])
            title: Recipe title

        Returns:
            Nutritional analysis
        """
        if not self.app_id or not self.app_key:
            return None

        data = {
            'title': title,
            'ingr': ingredients
        }

        result = self._post(
            f"{self.base_url}/nutrition-details",
            data=data
        )

        if result and not result.get('error'):
            return self._format_nutrition_analysis(result)

        return None

    @cached(ttl=3600)
    def search_food(
        self,
        query: str,
        category: Optional[str] = None,
        health: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Search food database

        Args:
            query: Search term
            category: Food category filter
            health: Health labels

        Returns:
            List of matching foods
        """
        if not self.app_id or not self.app_key:
            return []

        params = self._get_params({
            'ingr': query
        })

        if category:
            params['category'] = category
        if health:
            params['health'] = health

        result = self._get(f"{self.base_url}/food-database/v2/parser", params=params)

        if result and not result.get('error'):
            hints = result.get('hints', [])
            return [self._format_food(h.get('food', {})) for h in hints[:20]]

        return []

    @cached(ttl=86400)
    def get_food_nutrients(self, food_id: str, measure_uri: Optional[str] = None) -> Optional[Dict]:
        """
        Get detailed nutrients for a food item

        Args:
            food_id: Edamam food ID
            measure_uri: Specific measure URI

        Returns:
            Detailed nutrient information
        """
        if not self.app_id or not self.app_key:
            return None

        data = {
            'ingredients': [
                {
                    'quantity': 1,
                    'foodId': food_id
                }
            ]
        }

        if measure_uri:
            data['ingredients'][0]['measureURI'] = measure_uri

        result = self._post(
            f"{self.base_url}/food-database/v2/nutrients",
            data=data
        )

        if result and not result.get('error'):
            return self._format_nutrient_response(result)

        return None

    def _format_recipe(self, recipe: Dict) -> Dict:
        """Format recipe data"""
        return {
            'uri': recipe.get('uri'),
            'label': recipe.get('label'),
            'image': recipe.get('image'),
            'source': recipe.get('source'),
            'url': recipe.get('url'),
            'yield': recipe.get('yield'),
            'calories': recipe.get('calories'),
            'calories_per_serving': recipe.get('calories', 0) / max(recipe.get('yield', 1), 1),
            'total_time': recipe.get('totalTime'),
            'cuisine_type': recipe.get('cuisineType', []),
            'meal_type': recipe.get('mealType', []),
            'dish_type': recipe.get('dishType', []),
            'diet_labels': recipe.get('dietLabels', []),
            'health_labels': recipe.get('healthLabels', []),
            'cautions': recipe.get('cautions', []),
            'ingredients': [
                {
                    'text': ing.get('text'),
                    'quantity': ing.get('quantity'),
                    'measure': ing.get('measure'),
                    'food': ing.get('food'),
                    'weight': ing.get('weight'),
                    'food_id': ing.get('foodId')
                }
                for ing in recipe.get('ingredients', [])
            ],
            'nutrients': self._extract_nutrients(recipe.get('totalNutrients', {})),
            'daily_values': self._extract_nutrients(recipe.get('totalDaily', {})),
            'data_source': 'Edamam'
        }

    def _format_food(self, food: Dict) -> Dict:
        """Format food item data"""
        nutrients = food.get('nutrients', {})

        return {
            'food_id': food.get('foodId'),
            'label': food.get('label'),
            'known_as': food.get('knownAs'),
            'category': food.get('category'),
            'category_label': food.get('categoryLabel'),
            'brand': food.get('brand'),
            'image': food.get('image'),
            'nutrients': {
                'calories': nutrients.get('ENERC_KCAL'),
                'protein': nutrients.get('PROCNT'),
                'fat': nutrients.get('FAT'),
                'carbs': nutrients.get('CHOCDF'),
                'fiber': nutrients.get('FIBTG'),
            },
            'data_source': 'Edamam'
        }

    def _format_nutrition_analysis(self, result: Dict) -> Dict:
        """Format nutrition analysis response"""
        return {
            'uri': result.get('uri'),
            'yield': result.get('yield'),
            'calories': result.get('calories'),
            'total_weight': result.get('totalWeight'),
            'diet_labels': result.get('dietLabels', []),
            'health_labels': result.get('healthLabels', []),
            'cautions': result.get('cautions', []),
            'nutrients': self._extract_nutrients(result.get('totalNutrients', {})),
            'daily_values': self._extract_nutrients(result.get('totalDaily', {})),
            'ingredients': [
                {
                    'text': ing.get('text'),
                    'parsed': [
                        {
                            'quantity': p.get('quantity'),
                            'measure': p.get('measure'),
                            'food': p.get('food'),
                            'weight': p.get('weight'),
                            'nutrients': p.get('nutrients', {})
                        }
                        for p in ing.get('parsed', [])
                    ]
                }
                for ing in result.get('ingredients', [])
            ],
            'data_source': 'Edamam'
        }

    def _format_nutrient_response(self, result: Dict) -> Dict:
        """Format nutrient response"""
        return {
            'calories': result.get('calories'),
            'total_weight': result.get('totalWeight'),
            'diet_labels': result.get('dietLabels', []),
            'health_labels': result.get('healthLabels', []),
            'nutrients': self._extract_nutrients(result.get('totalNutrients', {})),
            'daily_values': self._extract_nutrients(result.get('totalDaily', {})),
            'data_source': 'Edamam'
        }

    def _extract_nutrients(self, nutrients: Dict) -> Dict:
        """Extract and format nutrient data"""
        return {
            key.lower(): {
                'label': val.get('label'),
                'quantity': val.get('quantity'),
                'unit': val.get('unit')
            }
            for key, val in nutrients.items()
        }
