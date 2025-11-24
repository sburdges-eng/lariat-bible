"""
Costing Service
================
Manages all costing operations.
"""

from typing import Optional, List, Dict, Any
from decimal import Decimal
import uuid
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from modules.kitchen_core import (
    CostingEngine, Ingredient, Recipe, RecipeIngredient, MenuItem,
    VendorProduct, CostSnapshot, Unit, RecipeType
)


class CostingService:
    """
    Singleton service for recipe costing operations.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.engine = CostingEngine()
        self._initialized = True

        # Load sample data for demo
        self._load_sample_data()

    def _load_sample_data(self):
        """Load sample ingredients for demo"""
        samples = [
            ("black_pepper", "Black Pepper", "Spices", Unit.OZ, Decimal("3.07")),
            ("garlic_powder", "Garlic Powder", "Spices", Unit.LB, Decimal("9.04")),
            ("onion_powder", "Onion Powder", "Spices", Unit.LB, Decimal("1.59")),
            ("chicken_breast", "Chicken Breast", "Protein", Unit.LB, Decimal("3.99")),
            ("ground_beef", "Ground Beef 80/20", "Protein", Unit.LB, Decimal("4.49")),
            ("olive_oil", "Olive Oil", "Oils", Unit.GALLON, Decimal("28.99")),
            ("butter", "Butter", "Dairy", Unit.LB, Decimal("4.29")),
            ("cheddar_cheese", "Cheddar Cheese", "Dairy", Unit.LB, Decimal("5.99")),
            ("lettuce", "Romaine Lettuce", "Produce", Unit.HEAD, Decimal("2.49")),
            ("tomato", "Tomatoes", "Produce", Unit.LB, Decimal("2.99")),
        ]

        for id, name, category, unit, cost in samples:
            ing = Ingredient(
                id=id,
                name=name,
                category=category,
                default_unit=unit,
                current_cost_per_unit=cost,
                preferred_vendor="Shamrock"
            )
            self.engine.add_ingredient(ing)

    # =========================================================================
    # Ingredient Operations
    # =========================================================================

    def get_all_ingredients(self) -> List[Dict]:
        """Get all ingredients"""
        return [self._ingredient_to_dict(ing) for ing in self.engine.get_all_ingredients()]

    def get_ingredient(self, ingredient_id: str) -> Optional[Dict]:
        """Get ingredient by ID"""
        ing = self.engine.get_ingredient(ingredient_id)
        return self._ingredient_to_dict(ing) if ing else None

    def create_ingredient(self, data: Dict) -> Dict:
        """Create new ingredient"""
        ing = Ingredient(
            id=data.get('id') or str(uuid.uuid4()),
            name=data['name'],
            category=data.get('category', 'Other'),
            default_unit=Unit(data.get('default_unit', 'oz')),
            current_cost_per_unit=Decimal(str(data.get('current_cost_per_unit', 0))) if data.get('current_cost_per_unit') else None,
            preferred_vendor=data.get('preferred_vendor'),
            waste_factor=float(data.get('waste_factor', 0)),
            aliases=data.get('aliases', [])
        )
        self.engine.add_ingredient(ing)
        return self._ingredient_to_dict(ing)

    def update_ingredient(self, ingredient_id: str, data: Dict) -> Optional[Dict]:
        """Update ingredient"""
        ing = self.engine.get_ingredient(ingredient_id)
        if not ing:
            return None

        if 'name' in data:
            ing.name = data['name']
        if 'category' in data:
            ing.category = data['category']
        if 'default_unit' in data:
            ing.default_unit = Unit(data['default_unit'])
        if 'current_cost_per_unit' in data:
            ing.current_cost_per_unit = Decimal(str(data['current_cost_per_unit'])) if data['current_cost_per_unit'] else None
        if 'preferred_vendor' in data:
            ing.preferred_vendor = data['preferred_vendor']
        if 'waste_factor' in data:
            ing.waste_factor = float(data['waste_factor'])

        return self._ingredient_to_dict(ing)

    def auto_link_ingredients(self) -> Dict:
        """Auto-link ingredients to vendor products"""
        return self.engine.auto_link_ingredients()

    def _ingredient_to_dict(self, ing: Ingredient) -> Dict:
        """Convert Ingredient to dict"""
        return {
            'id': ing.id,
            'name': ing.name,
            'category': ing.category,
            'default_unit': ing.default_unit.value if hasattr(ing.default_unit, 'value') else ing.default_unit,
            'current_cost_per_unit': float(ing.current_cost_per_unit) if ing.current_cost_per_unit else None,
            'preferred_vendor': ing.preferred_vendor,
            'preferred_product_id': ing.preferred_product_id,
            'waste_factor': ing.waste_factor,
            'aliases': ing.aliases,
            'is_active': ing.is_active
        }

    # =========================================================================
    # Recipe Operations
    # =========================================================================

    def get_all_recipes(self) -> List[Dict]:
        """Get all recipes"""
        return [self._recipe_to_dict(r) for r in self.engine.recipes.values()]

    def get_recipe(self, recipe_id: str) -> Optional[Dict]:
        """Get recipe by ID"""
        recipe = self.engine.get_recipe(recipe_id)
        return self._recipe_to_dict(recipe) if recipe else None

    def create_recipe(self, data: Dict) -> Dict:
        """Create new recipe"""
        recipe = Recipe(
            id=data.get('id') or str(uuid.uuid4()),
            name=data['name'],
            recipe_type=RecipeType(data.get('recipe_type', 'menu_item')),
            category=data.get('category'),
            portions=int(data.get('portions', 1)),
            yield_quantity=Decimal(str(data.get('yield_quantity', 1))),
            yield_unit=data.get('yield_unit', 'portion'),
            target_food_cost_pct=Decimal(str(data.get('target_food_cost_pct', 0.28))),
            instructions=data.get('instructions')
        )

        # Add ingredients
        for ing_data in data.get('ingredients', []):
            recipe_ing = RecipeIngredient(
                id=str(uuid.uuid4()),
                recipe_id=recipe.id,
                ingredient_id=ing_data['ingredient_id'],
                quantity=Decimal(str(ing_data['quantity'])),
                unit=Unit(ing_data.get('unit', 'oz')),
                prep_notes=ing_data.get('prep_notes')
            )
            recipe.ingredients.append(recipe_ing)

        self.engine.add_recipe(recipe)
        return self._recipe_to_dict(recipe)

    def update_recipe(self, recipe_id: str, data: Dict) -> Optional[Dict]:
        """Update recipe"""
        recipe = self.engine.get_recipe(recipe_id)
        if not recipe:
            return None

        if 'name' in data:
            recipe.name = data['name']
        if 'category' in data:
            recipe.category = data['category']
        if 'portions' in data:
            recipe.portions = int(data['portions'])
        if 'target_food_cost_pct' in data:
            recipe.target_food_cost_pct = Decimal(str(data['target_food_cost_pct']))
        if 'instructions' in data:
            recipe.instructions = data['instructions']

        return self._recipe_to_dict(recipe)

    def cost_recipe(self, recipe_id: str) -> Optional[Dict]:
        """Cost a single recipe"""
        result = self.engine.cost_recipe(recipe_id)
        if not result:
            return None

        return {
            'recipe_id': result.recipe_id,
            'recipe_name': result.recipe_name,
            'total_cost': float(result.total_cost),
            'cost_per_portion': float(result.cost_per_portion),
            'portions': result.portions,
            'suggested_price': float(result.suggested_price),
            'target_food_cost_pct': float(result.target_food_cost_pct),
            'ingredient_costs': result.ingredient_costs,
            'warnings': result.warnings,
            'uncosted_ingredients': result.uncosted_ingredients
        }

    def cost_all_recipes(self) -> Dict:
        """Cost all recipes"""
        results = self.engine.cost_all_recipes()
        return {
            recipe_id: {
                'total_cost': float(r.total_cost),
                'cost_per_portion': float(r.cost_per_portion)
            }
            for recipe_id, r in results.items()
        }

    def get_cost_history(self, recipe_id: str) -> List[Dict]:
        """Get cost history for a recipe"""
        return self.engine.get_cost_history(recipe_id)

    def parse_recipes(self, text: str, source: str = "text") -> List[Dict]:
        """Parse recipes from text"""
        recipes = self.engine.parse_recipes_from_text(text, source)
        return [self._recipe_to_dict(r) for r in recipes]

    def _recipe_to_dict(self, recipe: Recipe) -> Dict:
        """Convert Recipe to dict"""
        return {
            'id': recipe.id,
            'name': recipe.name,
            'recipe_type': recipe.recipe_type.value if hasattr(recipe.recipe_type, 'value') else recipe.recipe_type,
            'category': recipe.category,
            'portions': recipe.portions,
            'yield_quantity': float(recipe.yield_quantity),
            'yield_unit': recipe.yield_unit,
            'total_cost': float(recipe.total_cost) if recipe.total_cost else None,
            'cost_per_portion': float(recipe.cost_per_portion) if recipe.cost_per_portion else None,
            'target_food_cost_pct': float(recipe.target_food_cost_pct),
            'suggested_price': float(recipe.suggested_price) if recipe.suggested_price else None,
            'instructions': recipe.instructions,
            'ingredients': [
                {
                    'id': ing.id,
                    'ingredient_id': ing.ingredient_id,
                    'ingredient_name': ing.ingredient.name if ing.ingredient else ing.ingredient_id,
                    'quantity': float(ing.quantity),
                    'unit': ing.unit.value if hasattr(ing.unit, 'value') else ing.unit,
                    'unit_cost': float(ing.unit_cost) if ing.unit_cost else None,
                    'extended_cost': float(ing.extended_cost) if ing.extended_cost else None,
                    'prep_notes': ing.prep_notes
                }
                for ing in recipe.ingredients
            ],
            'last_costed_at': recipe.last_costed_at.isoformat() if recipe.last_costed_at else None,
            'is_active': recipe.is_active
        }

    # =========================================================================
    # Menu Item Operations
    # =========================================================================

    def get_all_menu_items(self) -> List[Dict]:
        """Get all menu items"""
        return [self._menu_item_to_dict(m) for m in self.engine.menu_items.values()]

    def create_menu_item(self, data: Dict) -> Dict:
        """Create menu item"""
        item = MenuItem(
            id=data.get('id') or str(uuid.uuid4()),
            name=data['name'],
            description=data.get('description'),
            category=data.get('category', 'Entrees'),
            recipe_id=data.get('recipe_id'),
            menu_price=Decimal(str(data['menu_price'])) if data.get('menu_price') else None
        )
        self.engine.add_menu_item(item)
        return self._menu_item_to_dict(item)

    def cost_menu_item(self, menu_item_id: str) -> Optional[Dict]:
        """Cost a menu item"""
        return self.engine.cost_menu_item(menu_item_id)

    def _menu_item_to_dict(self, item: MenuItem) -> Dict:
        """Convert MenuItem to dict"""
        return {
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'category': item.category,
            'recipe_id': item.recipe_id,
            'menu_price': float(item.menu_price) if item.menu_price else None,
            'total_food_cost': float(item.total_food_cost) if item.total_food_cost else None,
            'food_cost_pct': float(item.food_cost_pct) if item.food_cost_pct else None,
            'gross_profit': float(item.gross_profit) if item.gross_profit else None,
            'monthly_sales': item.monthly_sales,
            'is_active': item.is_active
        }

    # =========================================================================
    # Summary
    # =========================================================================

    def get_costing_summary(self) -> Dict:
        """Get overall costing summary"""
        return self.engine.get_costing_summary()
