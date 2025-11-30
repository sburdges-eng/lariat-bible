"""
Order Calculator Module
Calculates ingredient quantities needed for banquet events
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

from modules.core.models import BanquetEvent, MenuItem, IngredientQuantity, VendorProduct

logger = logging.getLogger(__name__)


@dataclass
class RecipeIngredient:
    """An ingredient in a recipe with quantity per serving"""
    name: str
    quantity_per_serving: float
    unit: str
    vendor_product: Optional[VendorProduct] = None


@dataclass
class Recipe:
    """A recipe with ingredients"""
    name: str
    servings_per_batch: int
    ingredients: List[RecipeIngredient]


class OrderCalculator:
    """Calculate ingredient quantities needed for events"""

    def __init__(self):
        self.recipes: Dict[str, Recipe] = {}
        self.waste_factor = 1.1  # 10% waste allowance

    def add_recipe(self, recipe: Recipe):
        """Add a recipe to the calculator"""
        self.recipes[recipe.name.upper()] = recipe

    def calculate_for_event(
        self,
        event: BanquetEvent,
        recipes: Optional[Dict[str, Recipe]] = None
    ) -> List[IngredientQuantity]:
        """
        Calculate ingredient quantities needed for an event

        Args:
            event: The banquet event
            recipes: Optional recipe dictionary (uses internal if not provided)

        Returns:
            List of ingredient quantities needed
        """
        recipes = recipes or self.recipes
        ingredient_totals: Dict[str, IngredientQuantity] = {}

        for menu_item in event.menu_items:
            recipe = recipes.get(menu_item.name.upper())

            if not recipe:
                logger.warning(f"No recipe found for menu item: {menu_item.name}")
                continue

            # Calculate servings needed
            servings_needed = menu_item.quantity * event.guest_count

            for ingredient in recipe.ingredients:
                total_qty = (
                    ingredient.quantity_per_serving *
                    servings_needed *
                    self.waste_factor
                )

                key = f"{ingredient.name}|{ingredient.unit}"

                if key in ingredient_totals:
                    ingredient_totals[key].quantity += total_qty
                else:
                    ingredient_totals[key] = IngredientQuantity(
                        ingredient_name=ingredient.name,
                        quantity=total_qty,
                        unit=ingredient.unit,
                        vendor_product=ingredient.vendor_product
                    )

        # Update event with calculated ingredients
        event.ingredients_needed = list(ingredient_totals.values())

        return list(ingredient_totals.values())

    def calculate_from_guest_count(
        self,
        guest_count: int,
        menu_items: List[str],
        recipes: Optional[Dict[str, Recipe]] = None
    ) -> List[IngredientQuantity]:
        """
        Calculate ingredients needed for a guest count and menu

        Args:
            guest_count: Number of guests
            menu_items: List of menu item names
            recipes: Optional recipe dictionary

        Returns:
            List of ingredient quantities needed
        """
        recipes = recipes or self.recipes
        ingredient_totals: Dict[str, IngredientQuantity] = {}

        for item_name in menu_items:
            recipe = recipes.get(item_name.upper())

            if not recipe:
                logger.warning(f"No recipe found for: {item_name}")
                continue

            servings_needed = guest_count

            for ingredient in recipe.ingredients:
                total_qty = (
                    ingredient.quantity_per_serving *
                    servings_needed *
                    self.waste_factor
                )

                key = f"{ingredient.name}|{ingredient.unit}"

                if key in ingredient_totals:
                    ingredient_totals[key].quantity += total_qty
                else:
                    ingredient_totals[key] = IngredientQuantity(
                        ingredient_name=ingredient.name,
                        quantity=total_qty,
                        unit=ingredient.unit,
                        vendor_product=ingredient.vendor_product
                    )

        return list(ingredient_totals.values())

    def set_waste_factor(self, factor: float):
        """Set the waste factor (e.g., 1.1 for 10% waste)"""
        if factor < 1.0:
            raise ValueError("Waste factor must be >= 1.0")
        self.waste_factor = factor

    def estimate_cost(
        self,
        ingredients: List[IngredientQuantity]
    ) -> float:
        """
        Estimate cost for a list of ingredients

        Args:
            ingredients: List of ingredient quantities

        Returns:
            Total estimated cost
        """
        total = 0.0

        for ing in ingredients:
            if ing.vendor_product:
                # Use vendor pricing
                unit_cost = ing.vendor_product.unit_price
                total += unit_cost * ing.quantity

        return total


# Sample recipes for testing
def get_sample_recipes() -> Dict[str, Recipe]:
    """Get sample recipes for testing"""
    return {
        "GRILLED CHICKEN BREAST": Recipe(
            name="Grilled Chicken Breast",
            servings_per_batch=1,
            ingredients=[
                RecipeIngredient("Chicken Breast", 0.5, "LB"),
                RecipeIngredient("Olive Oil", 0.25, "OZ"),
                RecipeIngredient("Salt", 0.1, "OZ"),
                RecipeIngredient("Black Pepper", 0.05, "OZ"),
                RecipeIngredient("Garlic Powder", 0.05, "OZ"),
            ]
        ),
        "MIXED GREEN SALAD": Recipe(
            name="Mixed Green Salad",
            servings_per_batch=1,
            ingredients=[
                RecipeIngredient("Mixed Greens", 0.25, "LB"),
                RecipeIngredient("Cherry Tomatoes", 0.1, "LB"),
                RecipeIngredient("Cucumber", 0.1, "LB"),
                RecipeIngredient("Ranch Dressing", 1.0, "OZ"),
            ]
        ),
        "MASHED POTATOES": Recipe(
            name="Mashed Potatoes",
            servings_per_batch=1,
            ingredients=[
                RecipeIngredient("Russet Potatoes", 0.5, "LB"),
                RecipeIngredient("Butter", 0.5, "OZ"),
                RecipeIngredient("Heavy Cream", 1.0, "OZ"),
                RecipeIngredient("Salt", 0.1, "OZ"),
                RecipeIngredient("Black Pepper", 0.02, "OZ"),
            ]
        ),
    }
