"""
Spoonacular API Integration
============================
FREE tier: 150 requests/day with API key.

Get your free key at: https://spoonacular.com/food-api/console

Features:
- Recipe search and analysis
- Ingredient information
- Nutritional data
- Cost estimation
- Meal planning
- Food trivia
"""

from typing import Any, Dict, List, Optional
from .base_client import BaseClient, cached


class SpoonacularClient(BaseClient):
    """
    Client for Spoonacular Food API

    FREE tier: 150 requests/day
    Comprehensive food and recipe database.
    """

    CUISINES = [
        'African', 'American', 'British', 'Cajun', 'Caribbean', 'Chinese',
        'Eastern European', 'European', 'French', 'German', 'Greek', 'Indian',
        'Irish', 'Italian', 'Japanese', 'Jewish', 'Korean', 'Latin American',
        'Mediterranean', 'Mexican', 'Middle Eastern', 'Nordic', 'Southern',
        'Spanish', 'Thai', 'Vietnamese'
    ]

    DIETS = [
        'gluten free', 'ketogenic', 'vegetarian', 'lacto-vegetarian',
        'ovo-vegetarian', 'vegan', 'pescetarian', 'paleo', 'primal', 'whole30'
    ]

    def __init__(self):
        super().__init__()
        self.base_url = self.config.SPOONACULAR_BASE_URL
        self.api_key = self.config.SPOONACULAR_API_KEY

    def _get_params(self, extra_params: Optional[Dict] = None) -> Dict:
        """Get request parameters with API key"""
        params = {'apiKey': self.api_key} if self.api_key else {}
        if extra_params:
            params.update(extra_params)
        return params

    def health_check(self) -> Dict[str, Any]:
        """Check if Spoonacular API is accessible"""
        if not self.api_key:
            return {
                'available': False,
                'source': 'Spoonacular',
                'message': 'API key not configured. Get free key at: https://spoonacular.com/food-api/console'
            }

        # Try a simple search
        result = self._get(
            f"{self.base_url}/food/ingredients/search",
            params=self._get_params({'query': 'pepper', 'number': 1})
        )

        if result and not result.get('error'):
            return {
                'available': True,
                'source': 'Spoonacular',
                'message': 'API is accessible (150 requests/day free)'
            }

        return {
            'available': False,
            'source': 'Spoonacular',
            'message': result.get('message', 'API unavailable')
        }

    @cached(ttl=3600)
    def search(self, query: str, **kwargs) -> List[Dict]:
        """Search for ingredients (alias for search_ingredients)"""
        return self.search_ingredients(query, **kwargs)

    @cached(ttl=3600)
    def search_ingredients(
        self,
        query: str,
        number: int = 10,
        sort: str = 'calories',
        sort_direction: str = 'asc',
        meta_information: bool = True
    ) -> List[Dict]:
        """
        Search for ingredients

        Args:
            query: Search term (e.g., 'garlic', 'olive oil')
            number: Number of results (1-100)
            sort: Sort by (calories, protein, fat, carbs, etc.)
            sort_direction: 'asc' or 'desc'
            meta_information: Include metadata

        Returns:
            List of matching ingredients
        """
        if not self.api_key:
            return []

        params = self._get_params({
            'query': query,
            'number': min(number, 100),
            'sort': sort,
            'sortDirection': sort_direction,
            'metaInformation': meta_information
        })

        result = self._get(f"{self.base_url}/food/ingredients/search", params=params)

        if result and not result.get('error'):
            ingredients = result.get('results', [])
            return [self._format_ingredient(ing) for ing in ingredients]

        return []

    @cached(ttl=86400)
    def get_ingredient_info(self, ingredient_id: int, amount: float = 100, unit: str = 'grams') -> Optional[Dict]:
        """
        Get detailed ingredient information

        Args:
            ingredient_id: Spoonacular ingredient ID
            amount: Amount of ingredient
            unit: Unit of measurement

        Returns:
            Detailed ingredient info with nutrients
        """
        if not self.api_key:
            return None

        params = self._get_params({
            'amount': amount,
            'unit': unit
        })

        result = self._get(f"{self.base_url}/food/ingredients/{ingredient_id}/information", params=params)

        if result and not result.get('error'):
            return self._format_ingredient_detail(result)

        return None

    @cached(ttl=3600)
    def search_recipes(
        self,
        query: str,
        cuisine: Optional[str] = None,
        diet: Optional[str] = None,
        number: int = 10,
        max_ready_time: Optional[int] = None,
        min_calories: Optional[int] = None,
        max_calories: Optional[int] = None
    ) -> List[Dict]:
        """
        Search for recipes

        Args:
            query: Search term
            cuisine: Cuisine type (see CUISINES)
            diet: Diet type (see DIETS)
            number: Number of results
            max_ready_time: Maximum preparation time in minutes
            min_calories: Minimum calories per serving
            max_calories: Maximum calories per serving

        Returns:
            List of matching recipes
        """
        if not self.api_key:
            return []

        params = self._get_params({
            'query': query,
            'number': min(number, 100),
            'addRecipeNutrition': True
        })

        if cuisine:
            params['cuisine'] = cuisine
        if diet:
            params['diet'] = diet
        if max_ready_time:
            params['maxReadyTime'] = max_ready_time
        if min_calories:
            params['minCalories'] = min_calories
        if max_calories:
            params['maxCalories'] = max_calories

        result = self._get(f"{self.base_url}/recipes/complexSearch", params=params)

        if result and not result.get('error'):
            recipes = result.get('results', [])
            return [self._format_recipe(r) for r in recipes]

        return []

    @cached(ttl=86400)
    def get_recipe_info(self, recipe_id: int) -> Optional[Dict]:
        """
        Get detailed recipe information

        Args:
            recipe_id: Spoonacular recipe ID

        Returns:
            Detailed recipe info with ingredients and nutrition
        """
        if not self.api_key:
            return None

        params = self._get_params({'includeNutrition': True})

        result = self._get(f"{self.base_url}/recipes/{recipe_id}/information", params=params)

        if result and not result.get('error'):
            return self._format_recipe_detail(result)

        return None

    @cached(ttl=86400)
    def get_recipe_price_breakdown(self, recipe_id: int) -> Optional[Dict]:
        """
        Get price breakdown for a recipe

        Args:
            recipe_id: Spoonacular recipe ID

        Returns:
            Cost breakdown by ingredient
        """
        if not self.api_key:
            return None

        result = self._get(
            f"{self.base_url}/recipes/{recipe_id}/priceBreakdownWidget.json",
            params=self._get_params()
        )

        if result and not result.get('error'):
            ingredients = result.get('ingredients', [])
            return {
                'recipe_id': recipe_id,
                'total_cost': result.get('totalCost', 0) / 100,  # Convert cents to dollars
                'cost_per_serving': result.get('totalCostPerServing', 0) / 100,
                'ingredients': [
                    {
                        'name': ing.get('name'),
                        'amount': ing.get('amount', {}).get('us', {}).get('value'),
                        'unit': ing.get('amount', {}).get('us', {}).get('unit'),
                        'price': ing.get('price', 0) / 100
                    }
                    for ing in ingredients
                ],
                'source': 'Spoonacular'
            }

        return None

    @cached(ttl=3600)
    def convert_amounts(
        self,
        ingredient_name: str,
        source_amount: float,
        source_unit: str,
        target_unit: str
    ) -> Optional[Dict]:
        """
        Convert ingredient amounts between units

        Args:
            ingredient_name: Name of ingredient
            source_amount: Amount to convert
            source_unit: Source unit
            target_unit: Target unit

        Returns:
            Converted amount
        """
        if not self.api_key:
            return None

        params = self._get_params({
            'ingredientName': ingredient_name,
            'sourceAmount': source_amount,
            'sourceUnit': source_unit,
            'targetUnit': target_unit
        })

        result = self._get(f"{self.base_url}/recipes/convert", params=params)

        if result and not result.get('error'):
            return {
                'ingredient': ingredient_name,
                'source_amount': source_amount,
                'source_unit': source_unit,
                'target_amount': result.get('targetAmount'),
                'target_unit': target_unit,
                'answer': result.get('answer'),
                'source': 'Spoonacular'
            }

        return None

    @cached(ttl=86400)
    def get_ingredient_substitutes(self, ingredient_name: str) -> Optional[Dict]:
        """
        Get substitutes for an ingredient

        Args:
            ingredient_name: Name of ingredient

        Returns:
            List of possible substitutes
        """
        if not self.api_key:
            return None

        params = self._get_params({'ingredientName': ingredient_name})

        result = self._get(f"{self.base_url}/food/ingredients/substitutes", params=params)

        if result and not result.get('error'):
            return {
                'ingredient': ingredient_name,
                'substitutes': result.get('substitutes', []),
                'message': result.get('message'),
                'source': 'Spoonacular'
            }

        return None

    def _format_ingredient(self, ingredient: Dict) -> Dict:
        """Format ingredient search result"""
        return {
            'id': ingredient.get('id'),
            'name': ingredient.get('name'),
            'image': f"https://spoonacular.com/cdn/ingredients_100x100/{ingredient.get('image')}" if ingredient.get('image') else None,
            'aisle': ingredient.get('aisle'),
            'possible_units': ingredient.get('possibleUnits', []),
            'source': 'Spoonacular'
        }

    def _format_ingredient_detail(self, ingredient: Dict) -> Dict:
        """Format detailed ingredient info"""
        nutrition = ingredient.get('nutrition', {})
        nutrients = {
            n.get('name', '').lower().replace(' ', '_'): {
                'amount': n.get('amount'),
                'unit': n.get('unit'),
                'percent_daily': n.get('percentOfDailyNeeds')
            }
            for n in nutrition.get('nutrients', [])
        }

        return {
            'id': ingredient.get('id'),
            'name': ingredient.get('name'),
            'original_name': ingredient.get('originalName'),
            'image': f"https://spoonacular.com/cdn/ingredients_100x100/{ingredient.get('image')}" if ingredient.get('image') else None,
            'aisle': ingredient.get('aisle'),
            'consistency': ingredient.get('consistency'),
            'possible_units': ingredient.get('possibleUnits', []),
            'estimated_cost': {
                'value': ingredient.get('estimatedCost', {}).get('value', 0) / 100,
                'unit': ingredient.get('estimatedCost', {}).get('unit')
            },
            'nutrients': nutrients,
            'category_path': ingredient.get('categoryPath', []),
            'source': 'Spoonacular'
        }

    def _format_recipe(self, recipe: Dict) -> Dict:
        """Format recipe search result"""
        nutrition = recipe.get('nutrition', {})

        return {
            'id': recipe.get('id'),
            'title': recipe.get('title'),
            'image': recipe.get('image'),
            'image_type': recipe.get('imageType'),
            'servings': recipe.get('servings'),
            'ready_in_minutes': recipe.get('readyInMinutes'),
            'source_url': recipe.get('sourceUrl'),
            'calories': next(
                (n.get('amount') for n in nutrition.get('nutrients', [])
                 if n.get('name') == 'Calories'),
                None
            ),
            'source': 'Spoonacular'
        }

    def _format_recipe_detail(self, recipe: Dict) -> Dict:
        """Format detailed recipe info"""
        return {
            'id': recipe.get('id'),
            'title': recipe.get('title'),
            'image': recipe.get('image'),
            'servings': recipe.get('servings'),
            'ready_in_minutes': recipe.get('readyInMinutes'),
            'prep_minutes': recipe.get('preparationMinutes'),
            'cook_minutes': recipe.get('cookingMinutes'),
            'source_url': recipe.get('sourceUrl'),
            'source_name': recipe.get('sourceName'),
            'cuisines': recipe.get('cuisines', []),
            'dish_types': recipe.get('dishTypes', []),
            'diets': recipe.get('diets', []),
            'instructions': recipe.get('instructions'),
            'analyzed_instructions': recipe.get('analyzedInstructions', []),
            'ingredients': [
                {
                    'id': ing.get('id'),
                    'name': ing.get('name'),
                    'original': ing.get('original'),
                    'amount': ing.get('amount'),
                    'unit': ing.get('unit'),
                    'aisle': ing.get('aisle')
                }
                for ing in recipe.get('extendedIngredients', [])
            ],
            'nutrition': recipe.get('nutrition'),
            'price_per_serving': recipe.get('pricePerServing', 0) / 100,
            'source': 'Spoonacular'
        }
