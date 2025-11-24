"""
Costing Export Module
======================
Export costing data in various formats.
"""

import csv
import json
from io import StringIO
from decimal import Decimal
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import Recipe, Ingredient, MenuItem, CostSnapshot, CostingResult


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal types"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class CostingExporter:
    """
    Export costing data to various formats.

    Supports:
    - CSV per recipe
    - Summary costing sheet
    - Portion pricing
    - Full costing book
    """

    def __init__(self):
        self.date_format = '%Y-%m-%d'

    # =========================================================================
    # Recipe Exports
    # =========================================================================

    def export_recipe_csv(self, recipe: Recipe) -> str:
        """
        Export single recipe to CSV.

        Returns CSV string with ingredient breakdown.
        """
        output = StringIO()
        writer = csv.writer(output)

        # Header info
        writer.writerow(['Recipe Name', recipe.name])
        writer.writerow(['Type', recipe.recipe_type.value if hasattr(recipe.recipe_type, 'value') else recipe.recipe_type])
        writer.writerow(['Yield', f"{recipe.yield_quantity} {recipe.yield_unit}"])
        writer.writerow(['Portions', recipe.portions])
        writer.writerow(['Total Cost', f"${recipe.total_cost:.2f}" if recipe.total_cost else 'Not costed'])
        writer.writerow(['Cost per Portion', f"${recipe.cost_per_portion:.2f}" if recipe.cost_per_portion else 'N/A'])
        writer.writerow(['Target Food Cost %', f"{float(recipe.target_food_cost_pct) * 100:.1f}%"])
        writer.writerow(['Suggested Price', f"${recipe.suggested_price:.2f}" if recipe.suggested_price else 'N/A'])
        writer.writerow([])

        # Ingredients header
        writer.writerow(['Ingredient', 'Quantity', 'Unit', 'Unit Cost', 'Extended Cost', 'Prep Notes'])

        # Ingredient rows
        for ing in recipe.ingredients:
            writer.writerow([
                ing.ingredient.name if ing.ingredient else ing.ingredient_id,
                float(ing.quantity),
                ing.unit.value if hasattr(ing.unit, 'value') else ing.unit,
                f"${ing.unit_cost:.4f}" if ing.unit_cost else 'N/A',
                f"${ing.extended_cost:.2f}" if ing.extended_cost else 'N/A',
                ing.prep_notes or ''
            ])

        return output.getvalue()

    def export_recipe_json(self, recipe: Recipe) -> str:
        """Export recipe to JSON format"""
        data = {
            'id': recipe.id,
            'name': recipe.name,
            'type': recipe.recipe_type.value if hasattr(recipe.recipe_type, 'value') else recipe.recipe_type,
            'category': recipe.category,
            'yield': {
                'quantity': float(recipe.yield_quantity),
                'unit': recipe.yield_unit,
                'portions': recipe.portions
            },
            'costing': {
                'total_cost': float(recipe.total_cost) if recipe.total_cost else None,
                'cost_per_portion': float(recipe.cost_per_portion) if recipe.cost_per_portion else None,
                'target_food_cost_pct': float(recipe.target_food_cost_pct),
                'suggested_price': float(recipe.suggested_price) if recipe.suggested_price else None,
                'last_costed': recipe.last_costed_at.isoformat() if recipe.last_costed_at else None
            },
            'ingredients': [
                {
                    'ingredient_id': ing.ingredient_id,
                    'name': ing.ingredient.name if ing.ingredient else ing.ingredient_id,
                    'quantity': float(ing.quantity),
                    'unit': ing.unit.value if hasattr(ing.unit, 'value') else ing.unit,
                    'unit_cost': float(ing.unit_cost) if ing.unit_cost else None,
                    'extended_cost': float(ing.extended_cost) if ing.extended_cost else None,
                    'prep_notes': ing.prep_notes
                }
                for ing in recipe.ingredients
            ],
            'instructions': recipe.instructions,
            'source': recipe.source
        }

        return json.dumps(data, indent=2, cls=DecimalEncoder)

    # =========================================================================
    # Summary Exports
    # =========================================================================

    def export_summary_sheet(
        self,
        recipes: List[Recipe],
        title: str = "The Lariat - Recipe Costing Summary"
    ) -> str:
        """
        Export summary costing sheet for all recipes.
        """
        output = StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([title])
        writer.writerow([f"Generated: {datetime.now().strftime(self.date_format)}"])
        writer.writerow([])

        # Column headers
        writer.writerow([
            'Recipe Name',
            'Category',
            'Type',
            'Portions',
            'Total Cost',
            'Cost/Portion',
            'Target COGS %',
            'Suggested Price',
            'Ingredient Count',
            'Last Costed'
        ])

        # Sort by category then name
        sorted_recipes = sorted(recipes, key=lambda r: (r.category or 'ZZZ', r.name))

        for recipe in sorted_recipes:
            writer.writerow([
                recipe.name,
                recipe.category or 'Uncategorized',
                recipe.recipe_type.value if hasattr(recipe.recipe_type, 'value') else recipe.recipe_type,
                recipe.portions,
                f"${recipe.total_cost:.2f}" if recipe.total_cost else 'Not costed',
                f"${recipe.cost_per_portion:.2f}" if recipe.cost_per_portion else 'N/A',
                f"{float(recipe.target_food_cost_pct) * 100:.0f}%",
                f"${recipe.suggested_price:.2f}" if recipe.suggested_price else 'N/A',
                len(recipe.ingredients),
                recipe.last_costed_at.strftime(self.date_format) if recipe.last_costed_at else 'Never'
            ])

        # Summary stats
        costed = [r for r in recipes if r.total_cost]
        if costed:
            writer.writerow([])
            writer.writerow(['SUMMARY'])
            writer.writerow(['Total Recipes', len(recipes)])
            writer.writerow(['Costed Recipes', len(costed)])
            writer.writerow(['Average Cost/Portion', f"${sum(r.cost_per_portion for r in costed) / len(costed):.2f}"])

        return output.getvalue()

    def export_portion_pricing(
        self,
        recipes: List[Recipe],
        target_cogs_options: List[float] = None
    ) -> str:
        """
        Export portion pricing analysis with multiple COGS targets.
        """
        if target_cogs_options is None:
            target_cogs_options = [0.25, 0.28, 0.30, 0.32, 0.35]

        output = StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(['Portion Pricing Analysis'])
        writer.writerow([f"Generated: {datetime.now().strftime(self.date_format)}"])
        writer.writerow([])

        # Column headers
        headers = ['Recipe Name', 'Cost/Portion']
        for target in target_cogs_options:
            headers.append(f"Price @ {target*100:.0f}% COGS")
        writer.writerow(headers)

        for recipe in sorted(recipes, key=lambda r: r.name):
            if not recipe.cost_per_portion:
                continue

            row = [recipe.name, f"${recipe.cost_per_portion:.2f}"]
            for target in target_cogs_options:
                price = recipe.cost_per_portion / Decimal(str(target))
                row.append(f"${price:.2f}")
            writer.writerow(row)

        return output.getvalue()

    # =========================================================================
    # Menu Item Exports
    # =========================================================================

    def export_menu_costing(self, menu_items: List[MenuItem]) -> str:
        """Export menu item costing summary"""
        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(['Menu Item Costing Analysis'])
        writer.writerow([f"Generated: {datetime.now().strftime(self.date_format)}"])
        writer.writerow([])

        writer.writerow([
            'Menu Item',
            'Category',
            'Menu Price',
            'Food Cost',
            'COGS %',
            'Gross Profit',
            'Monthly Sales',
            'Monthly Profit'
        ])

        for item in sorted(menu_items, key=lambda m: (m.category, m.name)):
            monthly_profit = (item.gross_profit or Decimal('0')) * item.monthly_sales

            writer.writerow([
                item.name,
                item.category,
                f"${item.menu_price:.2f}" if item.menu_price else 'N/A',
                f"${item.total_food_cost:.2f}" if item.total_food_cost else 'N/A',
                f"{float(item.food_cost_pct) * 100:.1f}%" if item.food_cost_pct else 'N/A',
                f"${item.gross_profit:.2f}" if item.gross_profit else 'N/A',
                item.monthly_sales,
                f"${monthly_profit:.2f}"
            ])

        return output.getvalue()

    # =========================================================================
    # Full Costing Book
    # =========================================================================

    def export_costing_book(
        self,
        recipes: List[Recipe],
        ingredients: List[Ingredient],
        menu_items: List[MenuItem] = None
    ) -> Dict[str, str]:
        """
        Export complete costing book as multiple CSV files.

        Returns dict of filename -> CSV content
        """
        files = {}

        # 1. Summary sheet
        files['summary.csv'] = self.export_summary_sheet(recipes)

        # 2. Portion pricing
        files['portion_pricing.csv'] = self.export_portion_pricing(recipes)

        # 3. Individual recipe sheets
        for recipe in recipes:
            safe_name = recipe.name.replace(' ', '_').replace('/', '-')[:50]
            files[f'recipes/{safe_name}.csv'] = self.export_recipe_csv(recipe)

        # 4. Ingredient master list
        files['ingredients.csv'] = self._export_ingredient_list(ingredients)

        # 5. Menu items (if provided)
        if menu_items:
            files['menu_costing.csv'] = self.export_menu_costing(menu_items)

        return files

    def _export_ingredient_list(self, ingredients: List[Ingredient]) -> str:
        """Export ingredient master list"""
        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(['Ingredient Master List'])
        writer.writerow([f"Generated: {datetime.now().strftime(self.date_format)}"])
        writer.writerow([])

        writer.writerow([
            'Ingredient',
            'Category',
            'Default Unit',
            'Cost/Unit',
            'Preferred Vendor',
            'Waste Factor',
            'Aliases',
            'Linked'
        ])

        for ing in sorted(ingredients, key=lambda i: (i.category or 'ZZZ', i.name)):
            writer.writerow([
                ing.name,
                ing.category,
                ing.default_unit.value if hasattr(ing.default_unit, 'value') else ing.default_unit,
                f"${ing.current_cost_per_unit:.4f}" if ing.current_cost_per_unit else 'Not linked',
                ing.preferred_vendor or 'None',
                f"{ing.waste_factor * 100:.0f}%",
                ', '.join(ing.aliases) if ing.aliases else '',
                'Yes' if ing.preferred_vendor else 'No'
            ])

        return output.getvalue()

    # =========================================================================
    # Cost History Exports
    # =========================================================================

    def export_cost_history(
        self,
        snapshots: List[CostSnapshot],
        recipe_name: str = "Recipe"
    ) -> str:
        """Export cost history for a recipe"""
        output = StringIO()
        writer = csv.writer(output)

        writer.writerow([f'Cost History: {recipe_name}'])
        writer.writerow([])

        writer.writerow([
            'Date',
            'Total Cost',
            'Cost/Portion',
            'Variance',
            'Variance %'
        ])

        sorted_snapshots = sorted(snapshots, key=lambda s: s.snapshot_date)
        prev_cost = None

        for snap in sorted_snapshots:
            variance = ''
            variance_pct = ''

            if prev_cost is not None:
                v = snap.cost - prev_cost
                variance = f"${v:+.2f}"
                if prev_cost > 0:
                    variance_pct = f"{float(v / prev_cost * 100):+.1f}%"

            writer.writerow([
                snap.snapshot_date.strftime(self.date_format),
                f"${snap.cost:.2f}",
                f"${snap.cost_per_portion:.2f}" if snap.cost_per_portion else 'N/A',
                variance,
                variance_pct
            ])

            prev_cost = snap.cost

        return output.getvalue()
