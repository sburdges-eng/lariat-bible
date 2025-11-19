"""
P2 MEDIUM PRIORITY: Integration tests for LariatBible main class
Tests end-to-end workflows and component integration
"""

import pytest
from modules.core.lariat_bible import LariatBible
from modules.recipes.recipe import Recipe, Ingredient, RecipeIngredient
from modules.menu.menu_item import MenuItem


@pytest.mark.integration
class TestLariatBibleIngredientWorkflow:
    """Test ingredient management workflow"""

    def test_add_ingredient_workflow(self):
        """Test complete workflow of adding ingredient with pricing"""
        lariat = LariatBible()

        ingredient = Ingredient(
            ingredient_id="test_001",
            name="Test Spice",
            category="Spices",
            unit_of_measure="lb",
            case_size="25 LB",
            sysco_price=100.0,
            sysco_unit_price=4.0,
            shamrock_price=75.0,
            shamrock_unit_price=3.0
        )

        result = lariat.add_ingredient(ingredient)

        assert "Added ingredient" in result
        assert ingredient.ingredient_id in lariat.ingredients
        assert ingredient.preferred_vendor == "Shamrock Foods"

    def test_update_ingredient_pricing_workflow(self):
        """Test updating ingredient pricing from vendor"""
        lariat = LariatBible()

        # Add initial ingredient
        ingredient = Ingredient(
            ingredient_id="test_001",
            name="Test Item",
            category="Test",
            unit_of_measure="lb",
            case_size="25 LB",
            sysco_price=100.0,
            sysco_unit_price=4.0
        )
        lariat.add_ingredient(ingredient)

        # Update pricing
        result = lariat.update_ingredient_pricing("test_001", "SYSCO", 90.0)

        assert result['vendor_updated'] == "SYSCO"
        assert result['new_price'] == 90.0
        assert 'preferred_vendor' in result


@pytest.mark.integration
class TestLariatBibleRecipeWorkflow:
    """Test recipe creation and costing workflow"""

    def test_create_recipe_with_costing_workflow(self, sample_recipe):
        """Test complete recipe creation with cost analysis"""
        lariat = LariatBible()

        # Add ingredients to lariat first
        for recipe_ing in sample_recipe.ingredients:
            lariat.add_ingredient(recipe_ing.ingredient)

        # Create recipe
        result = lariat.create_recipe_with_costing(sample_recipe)

        assert 'recipe' in result
        assert 'total_cost' in result
        assert 'cost_per_portion' in result
        assert 'vendor_analysis' in result
        assert 'suggested_menu_price' in result

        # Recipe should be stored
        assert sample_recipe.recipe_id in lariat.recipes

    def test_link_recipe_to_menu_workflow(self, sample_recipe, sample_menu_item):
        """Test linking recipe to menu item"""
        lariat = LariatBible()

        # Add ingredients
        for recipe_ing in sample_recipe.ingredients:
            lariat.add_ingredient(recipe_ing.ingredient)

        # Create recipe
        lariat.create_recipe_with_costing(sample_recipe)

        # Add menu item
        lariat.menu_items[sample_menu_item.item_id] = sample_menu_item

        # Link recipe to menu
        result = lariat.link_recipe_to_menu(sample_recipe.recipe_id, sample_menu_item.item_id)

        assert 'menu_item' in result
        assert 'recipe' in result
        assert sample_menu_item.recipe_id == sample_recipe.recipe_id


@pytest.mark.integration
class TestLariatBibleOrderGuideWorkflow:
    """Test order guide comparison workflow"""

    def test_import_order_guides_workflow(self):
        """Test importing order guides from both vendors"""
        lariat = LariatBible()

        result = lariat.import_order_guides()

        assert 'sysco' in result
        assert 'shamrock' in result
        assert result['sysco'] > 0
        assert result['shamrock'] > 0

    def test_run_comprehensive_comparison_workflow(self):
        """Test complete vendor comparison workflow"""
        lariat = LariatBible()

        # Import order guides
        lariat.import_order_guides()

        # Run comparison
        result = lariat.run_comprehensive_comparison()

        assert 'items_compared' in result
        assert 'category_analysis' in result
        assert 'recommendations' in result
        assert 'margin_impact' in result


@pytest.mark.integration
class TestLariatBibleMenuOptimization:
    """Test menu pricing optimization workflow"""

    def test_optimize_menu_pricing_workflow(self):
        """Test menu pricing optimization"""
        lariat = LariatBible()

        # Add menu items with different margins
        item1 = MenuItem(
            item_id="item_001",
            name="Overpriced Item",
            category="Catering",
            menu_price=50.0,
            food_cost=10.0,  # 80% margin - too high
            target_margin=0.45
        )

        item2 = MenuItem(
            item_id="item_002",
            name="Underpriced Item",
            category="Catering",
            menu_price=20.0,
            food_cost=18.0,  # 10% margin - too low
            target_margin=0.45
        )

        lariat.menu_items[item1.item_id] = item1
        lariat.menu_items[item2.item_id] = item2

        results = lariat.optimize_menu_pricing()

        # Should identify items needing price adjustment
        assert len(results) > 0

        # Results should be sorted by price change
        if len(results) > 1:
            assert abs(results[0]['price_change']) >= abs(results[1]['price_change'])


@pytest.mark.integration
class TestLariatBibleReporting:
    """Test reporting and data export functionality"""

    def test_generate_executive_summary(self):
        """Test generating executive summary report"""
        lariat = LariatBible()

        summary = lariat.generate_executive_summary()

        assert "LARIAT BIBLE" in summary
        assert "EXECUTIVE SUMMARY" in summary
        assert "FINANCIAL OVERVIEW" in summary
        assert "VENDOR OPTIMIZATION" in summary
        assert "MENU ANALYSIS" in summary
        assert "EQUIPMENT STATUS" in summary
        assert "RECOMMENDATIONS" in summary

    def test_export_all_data(self, tmp_path):
        """Test exporting all data to files"""
        lariat = LariatBible()

        # Add some test data
        menu_item = MenuItem(
            item_id="test_001",
            name="Test Item",
            category="Test",
            menu_price=10.0
        )
        lariat.menu_items[menu_item.item_id] = menu_item

        # Export to temp directory
        export_dir = tmp_path / "exports"
        result = lariat.export_all_data(str(export_dir))

        assert 'menu' in result
        assert 'recipes' in result
        assert 'summary' in result

        # Files should exist
        import os
        assert os.path.exists(result['summary'])


@pytest.mark.integration
class TestLariatBibleEndToEnd:
    """End-to-end integration tests"""

    def test_complete_workflow_new_menu_item(self):
        """Test complete workflow: ingredient → recipe → menu item → pricing"""
        lariat = LariatBible()

        # Step 1: Add ingredients
        pepper = Ingredient(
            ingredient_id="pepper_001",
            name="Black Pepper",
            category="Spices",
            unit_of_measure="lb",
            case_size="25 LB",
            sysco_unit_price=49.82,
            shamrock_unit_price=3.19
        )
        lariat.add_ingredient(pepper)

        # Step 2: Create recipe
        recipe = Recipe(
            recipe_id="recipe_001",
            name="Spice Blend",
            category="Seasoning",
            yield_amount=10,
            yield_unit="portions",
            portion_size="2 oz"
        )
        recipe.ingredients = [
            RecipeIngredient(pepper, 1.0, "lb")
        ]
        lariat.create_recipe_with_costing(recipe)

        # Step 3: Create menu item
        menu_item = MenuItem(
            item_id="menu_001",
            name="Spiced Steak",
            category="Catering",
            target_margin=0.45
        )
        lariat.menu_items[menu_item.item_id] = menu_item

        # Step 4: Link recipe to menu
        result = lariat.link_recipe_to_menu(recipe.recipe_id, menu_item.item_id)

        # Verify complete workflow
        assert result['menu_item'] == menu_item.name
        assert result['food_cost'] == recipe.cost_per_portion
        assert menu_item.food_cost > 0
        assert menu_item.suggested_price > menu_item.food_cost

        # Step 5: Verify suggested pricing maintains target margin
        suggested = menu_item.suggested_price
        cost = menu_item.food_cost
        calculated_margin = (suggested - cost) / suggested

        assert abs(calculated_margin - 0.45) < 0.01

    def test_vendor_switch_impact_on_margins(self):
        """Test how switching vendors impacts overall profit margins"""
        lariat = LariatBible()

        # Import order guides with significant price differences
        lariat.import_order_guides()

        # Run comparison
        comparison = lariat.run_comprehensive_comparison()

        # Verify margin impact calculations
        margin_impact = comparison['margin_impact']

        assert 'catering' in margin_impact
        assert 'restaurant' in margin_impact
        assert margin_impact['catering']['margin_increase'] >= 0
        assert margin_impact['restaurant']['margin_increase'] >= 0
