"""
Unit tests for Recipe and Ingredient costing
Tests critical calculation logic for food cost and pricing
"""

import pytest
from datetime import datetime
from modules.recipes.recipe import Ingredient, RecipeIngredient, Recipe


class TestIngredientCalculateBestPrice:
    """Tests for Ingredient.calculate_best_price() method"""

    def test_shamrock_cheaper(self, sample_ingredient_shamrock_cheaper):
        """Test when Shamrock has better pricing"""
        result = sample_ingredient_shamrock_cheaper.calculate_best_price()

        assert result['ingredient'] == 'Garlic Powder'
        assert result['preferred_vendor'] == 'Shamrock Foods'
        assert sample_ingredient_shamrock_cheaper.preferred_vendor == 'Shamrock Foods'
        assert sample_ingredient_shamrock_cheaper.price_difference > 0
        assert result['savings_per_unit'] > 0

    def test_sysco_cheaper(self, sample_ingredient_sysco_cheaper):
        """Test when SYSCO has better pricing"""
        result = sample_ingredient_sysco_cheaper.calculate_best_price()

        assert result['preferred_vendor'] == 'SYSCO'
        assert sample_ingredient_sysco_cheaper.preferred_vendor == 'SYSCO'
        assert sample_ingredient_sysco_cheaper.price_difference > 0

    def test_price_difference_calculation(self, sample_ingredient_shamrock_cheaper):
        """Test that price difference is calculated correctly"""
        result = sample_ingredient_shamrock_cheaper.calculate_best_price()

        # Shamrock: $9.04/lb, SYSCO: $11.84/lb
        # Difference: $11.84 - $9.04 = $2.80
        expected_diff = 11.84 - 9.04
        assert abs(sample_ingredient_shamrock_cheaper.price_difference - expected_diff) < 0.1

    def test_price_difference_percent_calculation(self, sample_ingredient_shamrock_cheaper):
        """Test percentage difference calculation"""
        result = sample_ingredient_shamrock_cheaper.calculate_best_price()

        # Average: (9.04 + 11.84) / 2 = 10.44
        # Difference: 2.80
        # Percentage: (2.80 / 10.44) × 100 = 26.8%
        assert sample_ingredient_shamrock_cheaper.price_difference_percent > 20
        assert sample_ingredient_shamrock_cheaper.price_difference_percent < 30

    def test_insufficient_data(self, sample_ingredient_no_pricing):
        """Test when pricing data is insufficient"""
        result = sample_ingredient_no_pricing.calculate_best_price()

        assert result['preferred_vendor'] == 'Insufficient data'
        assert 'message' in result
        assert result['message'] == 'Need pricing from both vendors'

    def test_sysco_only_pricing(self, sample_ingredient_sysco_only):
        """Test when only SYSCO pricing is available"""
        result = sample_ingredient_sysco_only.calculate_best_price()

        # Should return insufficient data message
        assert result['preferred_vendor'] == 'Insufficient data'

    def test_equal_pricing(self):
        """Test when both vendors have identical pricing"""
        ingredient = Ingredient(
            ingredient_id="ING-EQ",
            name="Equal Price Item",
            category="Test",
            unit_of_measure="lb",
            case_size="10 lb",
            sysco_unit_price=5.00,
            shamrock_unit_price=5.00
        )

        result = ingredient.calculate_best_price()

        # When equal, Shamrock should win (second condition)
        assert result['preferred_vendor'] == 'Shamrock Foods'
        assert abs(ingredient.price_difference) < 0.01  # Should be ~0

    def test_result_structure(self, sample_ingredient_shamrock_cheaper):
        """Test that result has expected structure"""
        result = sample_ingredient_shamrock_cheaper.calculate_best_price()

        assert 'ingredient' in result
        assert 'preferred_vendor' in result
        assert 'sysco_price' in result
        assert 'shamrock_price' in result
        assert 'savings_per_unit' in result
        assert 'savings_percent' in result


class TestRecipeIngredientCost:
    """Tests for RecipeIngredient.cost property"""

    def test_cost_with_preferred_vendor_sysco(self, sample_ingredient_sysco_cheaper):
        """Test cost calculation when SYSCO is preferred"""
        sample_ingredient_sysco_cheaper.calculate_best_price()

        recipe_ing = RecipeIngredient(
            ingredient=sample_ingredient_sysco_cheaper,
            quantity=5.0,
            unit="lb"
        )

        # Cost = 5 lbs × $2.125/lb = $10.625
        expected_cost = 5.0 * 2.125
        assert abs(recipe_ing.cost - expected_cost) < 0.01

    def test_cost_with_preferred_vendor_shamrock(self, sample_ingredient_shamrock_cheaper):
        """Test cost calculation when Shamrock is preferred"""
        sample_ingredient_shamrock_cheaper.calculate_best_price()

        recipe_ing = RecipeIngredient(
            ingredient=sample_ingredient_shamrock_cheaper,
            quantity=0.5,
            unit="lb"
        )

        # Cost = 0.5 lbs × $9.04/lb = $4.52
        expected_cost = 0.5 * 9.04
        assert abs(recipe_ing.cost - expected_cost) < 0.01

    def test_cost_fallback_to_sysco(self, sample_ingredient_sysco_only):
        """Test cost fallback when only SYSCO pricing available"""
        recipe_ing = RecipeIngredient(
            ingredient=sample_ingredient_sysco_only,
            quantity=2.0,
            unit="lb"
        )

        # Should use SYSCO price: 2 × $7.50 = $15.00
        assert recipe_ing.cost == 15.00

    def test_cost_fallback_to_shamrock(self):
        """Test cost fallback when only Shamrock pricing available"""
        ingredient = Ingredient(
            ingredient_id="SHM-ONLY",
            name="Shamrock Only",
            category="Test",
            unit_of_measure="lb",
            case_size="10 lb",
            shamrock_unit_price=3.50
        )

        recipe_ing = RecipeIngredient(
            ingredient=ingredient,
            quantity=4.0,
            unit="lb"
        )

        # Should use Shamrock price: 4 × $3.50 = $14.00
        assert recipe_ing.cost == 14.00

    def test_cost_no_pricing_available(self, sample_ingredient_no_pricing):
        """Test cost when no pricing is available"""
        recipe_ing = RecipeIngredient(
            ingredient=sample_ingredient_no_pricing,
            quantity=1.0,
            unit="lb"
        )

        assert recipe_ing.cost == 0.0

    def test_cost_with_zero_quantity(self, sample_ingredient_sysco_cheaper):
        """Test cost calculation with zero quantity"""
        recipe_ing = RecipeIngredient(
            ingredient=sample_ingredient_sysco_cheaper,
            quantity=0.0,
            unit="lb"
        )

        assert recipe_ing.cost == 0.0

    def test_cost_with_large_quantity(self, sample_ingredient_shamrock_cheaper):
        """Test cost calculation with large quantity"""
        sample_ingredient_shamrock_cheaper.calculate_best_price()

        recipe_ing = RecipeIngredient(
            ingredient=sample_ingredient_shamrock_cheaper,
            quantity=100.0,
            unit="lb"
        )

        # 100 lbs × $9.04 = $904
        expected_cost = 100.0 * 9.04
        assert abs(recipe_ing.cost - expected_cost) < 0.1


class TestRecipeTotalCost:
    """Tests for Recipe.total_cost property"""

    def test_total_cost_multiple_ingredients(self, sample_recipe):
        """Test total cost with multiple ingredients"""
        total = sample_recipe.total_cost

        # Chicken: 5 lbs × $2.125 = $10.625
        # Garlic Powder: 0.25 lbs × $9.04 = $2.26
        # Total: $12.885
        assert total > 12.0
        assert total < 13.5

    def test_total_cost_single_ingredient(self, sample_ingredient_sysco_cheaper):
        """Test total cost with single ingredient"""
        sample_ingredient_sysco_cheaper.calculate_best_price()

        recipe = Recipe(
            recipe_id="RCP-SINGLE",
            name="Single Ingredient Recipe",
            category="Test",
            yield_amount=4,
            yield_unit="portions",
            portion_size="1 cup"
        )

        recipe.ingredients = [
            RecipeIngredient(
                ingredient=sample_ingredient_sysco_cheaper,
                quantity=2.0,
                unit="lb"
            )
        ]

        # 2 lbs × $2.125 = $4.25
        assert abs(recipe.total_cost - 4.25) < 0.01

    def test_total_cost_no_ingredients(self):
        """Test total cost with no ingredients"""
        recipe = Recipe(
            recipe_id="RCP-EMPTY",
            name="Empty Recipe",
            category="Test",
            yield_amount=1,
            yield_unit="portions",
            portion_size="N/A"
        )

        assert recipe.total_cost == 0.0

    def test_total_cost_updates_with_ingredient_changes(self, sample_recipe):
        """Test that total cost updates when ingredient quantities change"""
        original_cost = sample_recipe.total_cost

        # Double the chicken quantity
        sample_recipe.ingredients[0].quantity = 10.0

        new_cost = sample_recipe.total_cost

        # Cost should increase by roughly $10.625 (5 lbs × $2.125)
        assert new_cost > original_cost
        assert abs((new_cost - original_cost) - 10.625) < 0.1


class TestRecipeCostPerPortion:
    """Tests for Recipe.cost_per_portion property"""

    def test_cost_per_portion_basic(self, sample_recipe):
        """Test basic cost per portion calculation"""
        cost_per_portion = sample_recipe.cost_per_portion

        # Total cost ~$12.89, Yield: 10 portions
        # Cost per portion: ~$1.29
        assert cost_per_portion > 1.0
        assert cost_per_portion < 1.5

    def test_cost_per_portion_calculation_accuracy(self):
        """Test cost per portion calculation precision"""
        ingredient = Ingredient(
            ingredient_id="TEST",
            name="Test",
            category="Test",
            unit_of_measure="lb",
            case_size="10 lb",
            sysco_unit_price=10.00
        )
        ingredient.preferred_vendor = "SYSCO"

        recipe = Recipe(
            recipe_id="PRECISE",
            name="Precise Recipe",
            category="Test",
            yield_amount=8,
            yield_unit="portions",
            portion_size="1 cup"
        )

        recipe.ingredients = [
            RecipeIngredient(ingredient=ingredient, quantity=2.0, unit="lb")
        ]

        # Total: 2 × $10 = $20, Per portion: $20 / 8 = $2.50
        assert recipe.cost_per_portion == 2.50

    def test_cost_per_portion_zero_yield(self, sample_recipe_zero_yield):
        """Test cost per portion with zero yield (edge case)"""
        cost_per_portion = sample_recipe_zero_yield.cost_per_portion

        # Should return 0 to avoid division by zero
        assert cost_per_portion == 0

    def test_cost_per_portion_large_yield(self, sample_recipe):
        """Test cost per portion with large yield"""
        sample_recipe.yield_amount = 100

        cost_per_portion = sample_recipe.cost_per_portion

        # Should be much smaller
        assert cost_per_portion < 0.50

    def test_cost_per_portion_small_yield(self, sample_recipe):
        """Test cost per portion with small yield"""
        sample_recipe.yield_amount = 1

        cost_per_portion = sample_recipe.cost_per_portion

        # Should equal total cost
        assert abs(cost_per_portion - sample_recipe.total_cost) < 0.01


class TestRecipeGetShoppingList:
    """Tests for Recipe.get_shopping_list() method"""

    def test_shopping_list_basic(self, sample_recipe):
        """Test basic shopping list generation"""
        shopping_list = sample_recipe.get_shopping_list()

        assert 'Chicken Breast' in shopping_list
        assert 'Garlic Powder' in shopping_list

    def test_shopping_list_structure(self, sample_recipe):
        """Test shopping list item structure"""
        shopping_list = sample_recipe.get_shopping_list()
        chicken = shopping_list['Chicken Breast']

        assert 'quantity_needed' in chicken
        assert 'unit' in chicken
        assert 'preferred_vendor' in chicken
        assert 'vendor_item_code' in chicken
        assert 'estimated_cost' in chicken
        assert 'savings_vs_other' in chicken

    def test_shopping_list_quantities(self, sample_recipe):
        """Test shopping list quantities are correct"""
        shopping_list = sample_recipe.get_shopping_list()

        assert shopping_list['Chicken Breast']['quantity_needed'] == 5.0
        assert shopping_list['Garlic Powder']['quantity_needed'] == 0.25

    def test_shopping_list_with_multiplier(self, sample_recipe):
        """Test shopping list with quantity multiplier"""
        shopping_list = sample_recipe.get_shopping_list(multiplier=2.0)

        # Quantities should be doubled
        assert shopping_list['Chicken Breast']['quantity_needed'] == 10.0
        assert shopping_list['Garlic Powder']['quantity_needed'] == 0.5

    def test_shopping_list_cost_with_multiplier(self, sample_recipe):
        """Test that costs scale with multiplier"""
        list_1x = sample_recipe.get_shopping_list(multiplier=1.0)
        list_2x = sample_recipe.get_shopping_list(multiplier=2.0)

        chicken_cost_1x = list_1x['Chicken Breast']['estimated_cost']
        chicken_cost_2x = list_2x['Chicken Breast']['estimated_cost']

        assert abs(chicken_cost_2x - (chicken_cost_1x * 2)) < 0.01

    def test_shopping_list_vendor_item_codes(self, sample_recipe):
        """Test that vendor item codes are included"""
        shopping_list = sample_recipe.get_shopping_list()

        # Chicken is SYSCO preferred
        assert shopping_list['Chicken Breast']['vendor_item_code'] == 'SYS-12345'
        # Garlic is Shamrock preferred
        assert shopping_list['Garlic Powder']['vendor_item_code'] == 'SHM-98765'

    def test_shopping_list_savings_calculation(self, sample_recipe):
        """Test savings vs other vendor calculation"""
        shopping_list = sample_recipe.get_shopping_list()

        # Should have savings values for ingredients with both vendors
        assert 'savings_vs_other' in shopping_list['Chicken Breast']
        assert shopping_list['Chicken Breast']['savings_vs_other'] != 0


class TestRecipeAnalyzeVendorImpact:
    """Tests for Recipe.analyze_vendor_impact() method"""

    def test_vendor_impact_analysis_structure(self, sample_recipe):
        """Test vendor impact analysis result structure"""
        analysis = sample_recipe.analyze_vendor_impact()

        assert 'recipe' in analysis
        assert 'sysco_only_cost' in analysis
        assert 'shamrock_only_cost' in analysis
        assert 'optimized_cost' in analysis
        assert 'savings_vs_sysco' in analysis
        assert 'savings_vs_shamrock' in analysis
        assert 'recommendation' in analysis

    def test_vendor_impact_sysco_only(self, sample_recipe):
        """Test SYSCO-only cost calculation"""
        analysis = sample_recipe.analyze_vendor_impact()

        # Chicken: 5 × $2.125 = $10.625
        # Garlic: 0.25 × $11.84 = $2.96
        # Total: ~$13.585
        assert analysis['sysco_only_cost'] > 13.0
        assert analysis['sysco_only_cost'] < 14.0

    def test_vendor_impact_shamrock_only(self, sample_recipe):
        """Test Shamrock-only cost calculation"""
        analysis = sample_recipe.analyze_vendor_impact()

        # Chicken: 5 × $2.40 = $12.00
        # Garlic: 0.25 × $9.04 = $2.26
        # Total: ~$14.26
        assert analysis['shamrock_only_cost'] > 14.0
        assert analysis['shamrock_only_cost'] < 15.0

    def test_vendor_impact_optimized_cost(self, sample_recipe):
        """Test optimized (mixed vendor) cost"""
        analysis = sample_recipe.analyze_vendor_impact()

        # Should use best price for each ingredient
        # Chicken from SYSCO: 5 × $2.125 = $10.625
        # Garlic from Shamrock: 0.25 × $9.04 = $2.26
        # Total: ~$12.885
        assert analysis['optimized_cost'] > 12.5
        assert analysis['optimized_cost'] < 13.5

    def test_vendor_impact_savings_calculations(self, sample_recipe):
        """Test savings calculations are correct"""
        analysis = sample_recipe.analyze_vendor_impact()

        # Optimized should be cheaper than both single-vendor options
        assert analysis['optimized_cost'] <= analysis['sysco_only_cost']
        assert analysis['optimized_cost'] <= analysis['shamrock_only_cost']

        # Savings should be non-negative
        assert analysis['savings_vs_sysco'] >= 0
        assert analysis['savings_vs_shamrock'] >= 0

    def test_vendor_impact_recommendation(self, sample_recipe):
        """Test that recommendation is provided"""
        analysis = sample_recipe.analyze_vendor_impact()

        assert 'recommendation' in analysis
        assert len(analysis['recommendation']) > 0

    def test_vendor_impact_single_vendor_cheaper(self):
        """Test when single vendor is actually cheaper overall"""
        # Create ingredient where Shamrock is much cheaper
        ingredient = Ingredient(
            ingredient_id="SHM-BEST",
            name="Shamrock Best",
            category="Test",
            unit_of_measure="lb",
            case_size="10 lb",
            sysco_unit_price=10.00,
            shamrock_unit_price=5.00
        )
        ingredient.calculate_best_price()

        recipe = Recipe(
            recipe_id="SIMPLE",
            name="Simple Recipe",
            category="Test",
            yield_amount=4,
            yield_unit="portions",
            portion_size="1 cup"
        )

        recipe.ingredients = [
            RecipeIngredient(ingredient=ingredient, quantity=2.0, unit="lb")
        ]

        analysis = recipe.analyze_vendor_impact()

        # Shamrock should be cheapest
        assert analysis['shamrock_only_cost'] <= analysis['sysco_only_cost']
        assert analysis['optimized_cost'] == analysis['shamrock_only_cost']


class TestRecipeInitialization:
    """Tests for Recipe initialization and defaults"""

    def test_recipe_initialization(self):
        """Test basic recipe initialization"""
        recipe = Recipe(
            recipe_id="TEST",
            name="Test Recipe",
            category="Test",
            yield_amount=5,
            yield_unit="portions",
            portion_size="8 oz"
        )

        assert recipe.recipe_id == "TEST"
        assert recipe.name == "Test Recipe"
        assert recipe.ingredients == []
        assert recipe.prep_instructions == []
        assert recipe.cooking_instructions == []

    def test_recipe_default_dates(self):
        """Test that dates are set automatically"""
        recipe = Recipe(
            recipe_id="TEST",
            name="Test",
            category="Test",
            yield_amount=1,
            yield_unit="portions",
            portion_size="1 cup"
        )

        assert recipe.created_date is not None
        assert recipe.last_modified is not None
        assert isinstance(recipe.created_date, datetime)
        assert isinstance(recipe.last_modified, datetime)

    def test_recipe_custom_dates(self):
        """Test recipe with custom dates"""
        custom_date = datetime(2024, 1, 1, 12, 0, 0)

        recipe = Recipe(
            recipe_id="TEST",
            name="Test",
            category="Test",
            yield_amount=1,
            yield_unit="portions",
            portion_size="1 cup",
            created_date=custom_date,
            last_modified=custom_date
        )

        assert recipe.created_date == custom_date
        assert recipe.last_modified == custom_date


class TestEdgeCases:
    """Tests for edge cases and error conditions"""

    def test_ingredient_with_none_prices(self):
        """Test ingredient with None prices"""
        ingredient = Ingredient(
            ingredient_id="NONE",
            name="No Prices",
            category="Test",
            unit_of_measure="lb",
            case_size="10 lb",
            sysco_unit_price=None,
            shamrock_unit_price=None
        )

        result = ingredient.calculate_best_price()
        assert result['preferred_vendor'] == 'Insufficient data'

    def test_recipe_ingredient_with_fractional_quantity(self, sample_ingredient_sysco_cheaper):
        """Test recipe ingredient with small fractional quantity"""
        sample_ingredient_sysco_cheaper.calculate_best_price()

        recipe_ing = RecipeIngredient(
            ingredient=sample_ingredient_sysco_cheaper,
            quantity=0.001,  # 1 gram
            unit="lb"
        )

        # Should still calculate correctly
        expected = 0.001 * 2.125
        assert abs(recipe_ing.cost - expected) < 0.0001

    def test_recipe_with_very_large_yield(self):
        """Test recipe with extremely large yield"""
        ingredient = Ingredient(
            ingredient_id="TEST",
            name="Test",
            category="Test",
            unit_of_measure="lb",
            case_size="10 lb",
            sysco_unit_price=1.00
        )
        ingredient.preferred_vendor = "SYSCO"

        recipe = Recipe(
            recipe_id="LARGE",
            name="Large Batch",
            category="Test",
            yield_amount=10000,
            yield_unit="portions",
            portion_size="1 oz"
        )

        recipe.ingredients = [
            RecipeIngredient(ingredient=ingredient, quantity=100.0, unit="lb")
        ]

        # Total: $100, Per portion: $0.01
        assert recipe.cost_per_portion == 0.01
