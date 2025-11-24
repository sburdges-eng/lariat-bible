"""
Cost Calculator
================
Calculate recipe and ingredient costs.
"""

from decimal import Decimal
from typing import Optional, List, Dict, Any
from datetime import datetime
from .models import (
    Recipe, RecipeIngredient, Ingredient, MenuItem,
    CostSnapshot, CostingResult, Unit
)
from .unit_converter import UnitConverter


class CostCalculator:
    """
    Calculate costs for recipes and ingredients.
    """

    def __init__(self, ingredients: Dict[str, Ingredient] = None):
        """
        Initialize calculator with ingredient library.

        Args:
            ingredients: Dict mapping ingredient_id to Ingredient
        """
        self.ingredients = ingredients or {}

    def set_ingredients(self, ingredients: Dict[str, Ingredient]):
        """Update ingredient library"""
        self.ingredients = ingredients

    def cost_recipe(
        self,
        recipe: Recipe,
        create_snapshot: bool = True
    ) -> CostingResult:
        """
        Calculate full cost for a recipe.

        Args:
            recipe: Recipe to cost
            create_snapshot: Whether to create a cost snapshot

        Returns:
            CostingResult with full breakdown
        """
        warnings = []
        uncosted = []
        ingredient_costs = []
        total_cost = Decimal('0')

        for recipe_ing in recipe.ingredients:
            ing_cost = self._cost_recipe_ingredient(recipe_ing)

            if ing_cost is None:
                uncosted.append(recipe_ing.ingredient_id)
                warnings.append(f"No cost found for: {recipe_ing.ingredient_id}")
                continue

            recipe_ing.unit_cost = ing_cost['unit_cost']
            recipe_ing.extended_cost = ing_cost['extended_cost']

            total_cost += ing_cost['extended_cost']
            ingredient_costs.append(ing_cost)

        # Calculate per-portion cost
        portions = max(recipe.portions, 1)
        cost_per_portion = total_cost / Decimal(str(portions))

        # Calculate suggested price
        target_pct = recipe.target_food_cost_pct
        if target_pct > 0:
            suggested_price = cost_per_portion / target_pct
        else:
            suggested_price = cost_per_portion / Decimal('0.28')

        # Update recipe
        recipe.total_cost = total_cost
        recipe.cost_per_portion = cost_per_portion
        recipe.suggested_price = suggested_price
        recipe.last_costed_at = datetime.now()

        # Create result
        result = CostingResult(
            recipe_id=recipe.id,
            recipe_name=recipe.name,
            costed_at=datetime.now(),
            total_cost=total_cost,
            cost_per_portion=cost_per_portion,
            portions=portions,
            target_food_cost_pct=target_pct,
            suggested_price=suggested_price,
            ingredient_costs=ingredient_costs,
            warnings=warnings,
            uncosted_ingredients=uncosted
        )

        # Create snapshot
        if create_snapshot:
            result.snapshot = self._create_snapshot(recipe, ingredient_costs)

        return result

    def _cost_recipe_ingredient(
        self,
        recipe_ing: RecipeIngredient
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate cost for a single recipe ingredient.
        """
        # Get ingredient from library
        ingredient = recipe_ing.ingredient or self.ingredients.get(recipe_ing.ingredient_id)

        if not ingredient:
            return None

        # Get cost per unit from ingredient
        cost_per_unit = ingredient.current_cost_per_unit

        if not cost_per_unit:
            return None

        # Convert units if needed
        if recipe_ing.unit != ingredient.default_unit:
            conversion = UnitConverter.convert(
                Decimal('1'),
                recipe_ing.unit,
                ingredient.default_unit,
                ingredient.name
            )
            if conversion:
                # Adjust cost per unit for the recipe's unit
                cost_per_unit = cost_per_unit * conversion
            else:
                # Can't convert, use as-is with warning
                pass

        # Calculate extended cost
        extended_cost = recipe_ing.quantity * cost_per_unit

        # Apply waste factor
        if ingredient.waste_factor > 0:
            waste_multiplier = Decimal('1') / (Decimal('1') - Decimal(str(ingredient.waste_factor)))
            extended_cost = extended_cost * waste_multiplier

        return {
            'ingredient_id': recipe_ing.ingredient_id,
            'ingredient_name': ingredient.name,
            'quantity': float(recipe_ing.quantity),
            'unit': recipe_ing.unit.value if isinstance(recipe_ing.unit, Unit) else recipe_ing.unit,
            'unit_cost': cost_per_unit,
            'extended_cost': extended_cost,
            'vendor': ingredient.preferred_vendor,
            'waste_factor': ingredient.waste_factor
        }

    def _create_snapshot(
        self,
        recipe: Recipe,
        ingredient_costs: List[Dict]
    ) -> CostSnapshot:
        """Create a cost snapshot for historical tracking"""
        import uuid

        snapshot = CostSnapshot(
            id=str(uuid.uuid4()),
            snapshot_date=datetime.now(),
            snapshot_type='recipe',
            recipe_id=recipe.id,
            cost=recipe.total_cost or Decimal('0'),
            cost_per_portion=recipe.cost_per_portion,
            ingredient_costs={
                ic['ingredient_id']: ic['extended_cost']
                for ic in ingredient_costs
            }
        )

        return snapshot

    def cost_menu_item(
        self,
        menu_item: MenuItem,
        recipes: Dict[str, Recipe]
    ) -> Dict[str, Any]:
        """
        Calculate total food cost for a menu item.

        Args:
            menu_item: MenuItem to cost
            recipes: Dict of recipe_id to Recipe

        Returns:
            Cost breakdown for menu item
        """
        total_cost = Decimal('0')
        recipe_costs = []

        # Main recipe
        if menu_item.recipe_id and menu_item.recipe_id in recipes:
            main_recipe = recipes[menu_item.recipe_id]
            if main_recipe.cost_per_portion:
                total_cost += main_recipe.cost_per_portion
                recipe_costs.append({
                    'recipe_id': main_recipe.id,
                    'recipe_name': main_recipe.name,
                    'cost': main_recipe.cost_per_portion
                })

        # Component recipes
        for comp_id in menu_item.component_recipes:
            if comp_id in recipes:
                comp = recipes[comp_id]
                if comp.cost_per_portion:
                    total_cost += comp.cost_per_portion
                    recipe_costs.append({
                        'recipe_id': comp.id,
                        'recipe_name': comp.name,
                        'cost': comp.cost_per_portion
                    })

        # Update menu item
        menu_item.total_food_cost = total_cost

        if menu_item.menu_price and menu_item.menu_price > 0:
            menu_item.food_cost_pct = total_cost / menu_item.menu_price
            menu_item.gross_profit = menu_item.menu_price - total_cost

        return {
            'menu_item_id': menu_item.id,
            'menu_item_name': menu_item.name,
            'total_food_cost': total_cost,
            'menu_price': menu_item.menu_price,
            'food_cost_pct': menu_item.food_cost_pct,
            'gross_profit': menu_item.gross_profit,
            'recipe_breakdown': recipe_costs
        }

    def calculate_suggested_price(
        self,
        cost: Decimal,
        target_food_cost_pct: Decimal = Decimal('0.28')
    ) -> Decimal:
        """
        Calculate suggested menu price based on target food cost %.

        Args:
            cost: Food cost
            target_food_cost_pct: Target food cost percentage (e.g., 0.28 for 28%)

        Returns:
            Suggested menu price
        """
        if target_food_cost_pct <= 0:
            target_food_cost_pct = Decimal('0.28')
        return cost / target_food_cost_pct

    def calculate_food_cost_pct(
        self,
        cost: Decimal,
        price: Decimal
    ) -> Decimal:
        """Calculate food cost percentage"""
        if price <= 0:
            return Decimal('0')
        return cost / price

    def get_cost_variance(
        self,
        current: CostSnapshot,
        previous: CostSnapshot
    ) -> Dict[str, Any]:
        """
        Calculate variance between two cost snapshots.
        """
        variance = current.cost - previous.cost
        variance_pct = Decimal('0')

        if previous.cost > 0:
            variance_pct = variance / previous.cost

        # Find ingredient-level variances
        ingredient_variances = []
        all_ingredients = set(current.ingredient_costs.keys()) | set(previous.ingredient_costs.keys())

        for ing_id in all_ingredients:
            curr_cost = current.ingredient_costs.get(ing_id, Decimal('0'))
            prev_cost = previous.ingredient_costs.get(ing_id, Decimal('0'))
            ing_variance = curr_cost - prev_cost

            if ing_variance != 0:
                ingredient_variances.append({
                    'ingredient_id': ing_id,
                    'previous_cost': prev_cost,
                    'current_cost': curr_cost,
                    'variance': ing_variance,
                    'variance_pct': (ing_variance / prev_cost * 100) if prev_cost > 0 else None
                })

        return {
            'recipe_id': current.recipe_id,
            'previous_date': previous.snapshot_date,
            'current_date': current.snapshot_date,
            'previous_cost': previous.cost,
            'current_cost': current.cost,
            'variance': variance,
            'variance_pct': variance_pct * 100,  # As percentage
            'ingredient_variances': sorted(
                ingredient_variances,
                key=lambda x: abs(x['variance']),
                reverse=True
            )
        }
