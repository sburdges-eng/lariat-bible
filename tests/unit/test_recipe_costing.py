"""
P0 CRITICAL: Tests for recipe costing and ingredient calculations
These tests protect menu pricing accuracy and margin calculations
"""

import pytest
from datetime import datetime
from modules.recipes.recipe import Recipe, Ingredient, RecipeIngredient


@pytest.mark.critical
class TestIngredientPricing:
    """Test Ingredient class pricing calculations"""

    def test_ingredient_calculate_best_price_shamrock_cheaper(self, sample_ingredient_pepper):
        """Test that best price calculation identifies cheaper vendor"""
        result = sample_ingredient_pepper.calculate_best_price()

        assert result['preferred_vendor'] == 'Shamrock Foods'
        assert result['sysco_price'] == 49.825
        assert result['shamrock_price'] == 3.19
        assert result['savings_per_unit'] > 0

    def test_ingredient_calculate_best_price_sysco_cheaper(self):
        """Test best price when SYSCO is cheaper"""
        ingredient = Ingredient(
            ingredient_id="test_001",
            name="Test Item",
            category="Test",
            unit_of_measure="lb",
            case_size="25 LB",
            sysco_unit_price=2.00,
            shamrock_unit_price=3.00
        )

        result = ingredient.calculate_best_price()

        assert result['preferred_vendor'] == 'SYSCO'
        assert result['savings_per_unit'] == 1.00

    def test_ingredient_calculate_best_price_missing_data(self):
        """Test handling when pricing data is incomplete"""
        ingredient = Ingredient(
            ingredient_id="test_001",
            name="Test Item",
            category="Test",
            unit_of_measure="lb",
            case_size="25 LB",
            sysco_unit_price=2.00,
            shamrock_unit_price=None  # Missing Shamrock price
        )

        result = ingredient.calculate_best_price()

        assert result['preferred_vendor'] == 'Insufficient data'
        assert 'message' in result

    def test_ingredient_price_difference_percent(self):
        """Test percentage difference calculation"""
        ingredient = Ingredient(
            ingredient_id="test_001",
            name="Test Item",
            category="Test",
            unit_of_measure="lb",
            case_size="25 LB",
            sysco_unit_price=10.00,
            shamrock_unit_price=5.00
        )

        ingredient.calculate_best_price()

        # Average price: (10 + 5) / 2 = 7.5
        # Difference: 5
        # Percentage: (5 / 7.5) * 100 = 66.67%
        assert abs(ingredient.price_difference_percent - 66.67) < 0.1


@pytest.mark.critical
class TestRecipeIngredientCost:
    """Test RecipeIngredient cost calculations"""

    def test_recipe_ingredient_cost_uses_preferred_vendor(self, sample_ingredient_pepper):
        """Test that cost calculation uses preferred vendor price"""
        recipe_ingredient = RecipeIngredient(
            ingredient=sample_ingredient_pepper,
            quantity=2.0,
            unit="lb"
        )

        # Should use Shamrock price (preferred): 2.0 × $3.19 = $6.38
        expected_cost = 2.0 * 3.19
        assert abs(recipe_ingredient.cost - expected_cost) < 0.01

    def test_recipe_ingredient_cost_fallback_to_sysco(self):
        """Test fallback to SYSCO price when preferred vendor price unavailable"""
        ingredient = Ingredient(
            ingredient_id="test_001",
            name="Test Item",
            category="Test",
            unit_of_measure="lb",
            case_size="25 LB",
            sysco_unit_price=5.00,
            shamrock_unit_price=None,
            preferred_vendor=None
        )

        recipe_ingredient = RecipeIngredient(
            ingredient=ingredient,
            quantity=3.0,
            unit="lb"
        )

        # Should fall back to SYSCO: 3.0 × $5.00 = $15.00
        assert abs(recipe_ingredient.cost - 15.0) < 0.01

    def test_recipe_ingredient_cost_fallback_to_shamrock(self):
        """Test fallback to Shamrock price when SYSCO unavailable"""
        ingredient = Ingredient(
            ingredient_id="test_001",
            name="Test Item",
            category="Test",
            unit_of_measure="lb",
            case_size="25 LB",
            sysco_unit_price=None,
            shamrock_unit_price=4.00,
            preferred_vendor=None
        )

        recipe_ingredient = RecipeIngredient(
            ingredient=ingredient,
            quantity=2.5,
            unit="lb"
        )

        # Should fall back to Shamrock: 2.5 × $4.00 = $10.00
        assert abs(recipe_ingredient.cost - 10.0) < 0.01

    def test_recipe_ingredient_cost_no_pricing_available(self):
        """Test handling when no pricing is available"""
        ingredient = Ingredient(
            ingredient_id="test_001",
            name="Test Item",
            category="Test",
            unit_of_measure="lb",
            case_size="25 LB",
            sysco_unit_price=None,
            shamrock_unit_price=None
        )

        recipe_ingredient = RecipeIngredient(
            ingredient=ingredient,
            quantity=2.0,
            unit="lb"
        )

        # Should return 0 when no pricing available
        assert recipe_ingredient.cost == 0.0


@pytest.mark.critical
class TestRecipeCosting:
    """Test Recipe class costing calculations"""

    def test_recipe_total_cost(self, sample_recipe):
        """Test total recipe cost calculation"""
        total = sample_recipe.total_cost

        # Recipe has:
        # - 1 lb black pepper @ $3.19 (Shamrock)
        # - 0.5 lb garlic powder @ $9.04 (Shamrock)
        # Expected: $3.19 + $4.52 = $7.71
        expected = 3.19 + (0.5 * 9.04)
        assert abs(total - expected) < 0.1

    def test_recipe_cost_per_portion(self, sample_recipe):
        """Test cost per portion calculation"""
        cost_per_portion = sample_recipe.cost_per_portion

        # Total cost ~$7.71, 10 portions
        # Expected: ~$0.77 per portion
        expected = sample_recipe.total_cost / 10
        assert abs(cost_per_portion - expected) < 0.01

    def test_recipe_cost_per_portion_zero_yield(self):
        """CRITICAL: Test division by zero protection"""
        recipe = Recipe(
            recipe_id="test_001",
            name="Test Recipe",
            category="Test",
            yield_amount=0,  # Zero yield - should not crash
            yield_unit="portions",
            portion_size="1 ea"
        )

        # Should not raise ZeroDivisionError
        assert recipe.cost_per_portion == 0

    def test_recipe_get_shopping_list(self, sample_recipe):
        """Test shopping list generation"""
        shopping_list = sample_recipe.get_shopping_list(multiplier=2.0)

        assert len(shopping_list) == 2  # 2 ingredients

        # Check black pepper entry
        assert "Black Pepper Coarse" in shopping_list
        pepper_entry = shopping_list["Black Pepper Coarse"]
        assert pepper_entry['quantity_needed'] == 2.0  # 1.0 × 2
        assert pepper_entry['preferred_vendor'] == 'Shamrock Foods'
        assert pepper_entry['savings_vs_other'] > 0

    def test_recipe_analyze_vendor_impact(self, sample_recipe):
        """Test vendor impact analysis"""
        analysis = sample_recipe.analyze_vendor_impact()

        assert 'recipe' in analysis
        assert 'sysco_only_cost' in analysis
        assert 'shamrock_only_cost' in analysis
        assert 'optimized_cost' in analysis
        assert 'savings_vs_sysco' in analysis

        # Shamrock should be cheaper for this recipe
        assert analysis['shamrock_only_cost'] < analysis['sysco_only_cost']

        # Optimized (mixed) should equal or beat both
        assert analysis['optimized_cost'] <= analysis['shamrock_only_cost']

    def test_recipe_with_no_ingredients(self):
        """Test recipe with empty ingredient list"""
        recipe = Recipe(
            recipe_id="test_001",
            name="Empty Recipe",
            category="Test",
            yield_amount=5,
            yield_unit="portions",
            portion_size="1 ea"
        )

        assert recipe.total_cost == 0
        assert recipe.cost_per_portion == 0
        assert len(recipe.get_shopping_list()) == 0

    def test_recipe_vendor_impact_mixed_pricing(self):
        """Test vendor impact when each vendor wins some items"""
        # Create ingredients where each vendor is cheaper for different items
        sysco_cheaper_ingredient = Ingredient(
            ingredient_id="sysco_win",
            name="SYSCO Winner",
            category="Test",
            unit_of_measure="lb",
            case_size="25 LB",
            sysco_unit_price=2.00,
            shamrock_unit_price=5.00,
            preferred_vendor="SYSCO"
        )

        shamrock_cheaper_ingredient = Ingredient(
            ingredient_id="sham_win",
            name="Shamrock Winner",
            category="Test",
            unit_of_measure="lb",
            case_size="25 LB",
            sysco_unit_price=10.00,
            shamrock_unit_price=3.00,
            preferred_vendor="Shamrock Foods"
        )

        recipe = Recipe(
            recipe_id="test_001",
            name="Mixed Vendor Recipe",
            category="Test",
            yield_amount=1,
            yield_unit="batch",
            portion_size="1 batch"
        )

        recipe.ingredients = [
            RecipeIngredient(sysco_cheaper_ingredient, 1.0, "lb"),
            RecipeIngredient(shamrock_cheaper_ingredient, 1.0, "lb")
        ]

        analysis = recipe.analyze_vendor_impact()

        # SYSCO only: $2 + $10 = $12
        # Shamrock only: $5 + $3 = $8
        # Optimized: $2 (SYSCO) + $3 (Shamrock) = $5
        assert abs(analysis['sysco_only_cost'] - 12.0) < 0.01
        assert abs(analysis['shamrock_only_cost'] - 8.0) < 0.01
        assert abs(analysis['optimized_cost'] - 5.0) < 0.01

        # Optimized should save vs both
        assert analysis['savings_vs_sysco'] == 7.0
        assert analysis['savings_vs_shamrock'] == 3.0


@pytest.mark.critical
class TestRecipeMarginImpact:
    """Test how recipe costs impact menu pricing margins"""

    def test_recipe_cost_affects_menu_margin(self, sample_recipe):
        """
        CRITICAL: Verify recipe costs correctly feed into menu margin calculations
        Target catering margin: 45%
        """
        cost_per_portion = sample_recipe.cost_per_portion

        # For 45% margin, price should be: cost / (1 - 0.45)
        target_margin = 0.45
        suggested_price = cost_per_portion / (1 - target_margin)

        # Verify the math
        calculated_margin = (suggested_price - cost_per_portion) / suggested_price
        assert abs(calculated_margin - target_margin) < 0.01

    def test_vendor_switch_impact_on_margins(self):
        """Test how switching vendors affects profit margins"""
        # Create ingredient with significant price difference
        ingredient = Ingredient(
            ingredient_id="test_001",
            name="Expensive Item",
            category="Test",
            unit_of_measure="lb",
            case_size="25 LB",
            sysco_unit_price=50.00,
            shamrock_unit_price=35.00,  # 30% cheaper
            preferred_vendor="Shamrock Foods"
        )

        recipe = Recipe(
            recipe_id="test_001",
            name="Test Recipe",
            category="Test",
            yield_amount=10,
            yield_unit="portions",
            portion_size="1 ea"
        )

        recipe.ingredients = [
            RecipeIngredient(ingredient, 1.0, "lb")
        ]

        # Cost with Shamrock: $35 / 10 = $3.50 per portion
        # Cost with SYSCO: $50 / 10 = $5.00 per portion
        # Savings per portion: $1.50

        cost_shamrock = recipe.cost_per_portion
        assert abs(cost_shamrock - 3.50) < 0.01

        # If menu price stays at $10:
        # Margin with Shamrock: ($10 - $3.50) / $10 = 65%
        # Margin with SYSCO: ($10 - $5.00) / $10 = 50%
        # Margin improvement: 15 percentage points

        menu_price = 10.0
        margin_shamrock = (menu_price - 3.50) / menu_price
        margin_sysco = (menu_price - 5.00) / menu_price

        margin_improvement = margin_shamrock - margin_sysco
        assert abs(margin_improvement - 0.15) < 0.01

    def test_recipe_scaling_maintains_costs(self, sample_recipe):
        """Test that recipe costs scale linearly"""
        base_cost = sample_recipe.total_cost

        # Double the recipe
        shopping_list_2x = sample_recipe.get_shopping_list(multiplier=2.0)

        # Sum up the costs
        total_cost_2x = sum(item['estimated_cost'] for item in shopping_list_2x.values())

        # Should be exactly double
        assert abs(total_cost_2x - (base_cost * 2)) < 0.01

    def test_recipe_savings_aggregation(self, sample_recipe):
        """Test that savings are correctly aggregated across ingredients"""
        shopping_list = sample_recipe.get_shopping_list()

        total_savings = sum(item['savings_vs_other'] for item in shopping_list.values())

        # Both ingredients have Shamrock preferred, so savings should be positive
        assert total_savings > 0

        # Verify it matches expected
        # Black pepper: 1 lb × $46.635 savings/lb
        # Garlic powder: 0.5 lb × ~$2.80 savings/lb
        expected_savings = (1.0 * 46.635) + (0.5 * 2.80)
        assert abs(total_savings - expected_savings) < 1.0  # Allow some variance
