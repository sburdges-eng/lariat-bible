"""
Shared pytest fixtures for The Lariat Bible test suite
"""

import pytest
from datetime import datetime
from modules.recipes.recipe import Ingredient, RecipeIngredient, Recipe
from modules.vendor_analysis.comparator import VendorComparator
from modules.vendor_analysis.corrected_comparison import CorrectedVendorComparison


# ========================
# Ingredient Fixtures
# ========================

@pytest.fixture
def sample_ingredient_sysco_cheaper():
    """Ingredient where SYSCO has better pricing"""
    return Ingredient(
        ingredient_id="ING-001",
        name="Chicken Breast",
        category="Protein",
        unit_of_measure="lb",
        case_size="4/10#",
        sysco_item_code="SYS-12345",
        sysco_price=85.00,
        sysco_unit_price=2.125,  # 85 / 40 lbs
        shamrock_item_code="SHM-67890",
        shamrock_price=96.00,
        shamrock_unit_price=2.40,  # 96 / 40 lbs
        storage_location="Walk-in Cooler",
        shelf_life_days=3
    )


@pytest.fixture
def sample_ingredient_shamrock_cheaper():
    """Ingredient where Shamrock has better pricing"""
    return Ingredient(
        ingredient_id="ING-002",
        name="Garlic Powder",
        category="Spice",
        unit_of_measure="lb",
        case_size="6 LB",
        sysco_item_code="SYS-54321",
        sysco_price=213.19,
        sysco_unit_price=11.84,  # 213.19 / 18 lbs (3/6LB = 3 containers × 6 lbs)
        shamrock_item_code="SHM-98765",
        shamrock_price=54.26,
        shamrock_unit_price=9.04,  # 54.26 / 6 lbs (1/6/LB = 1 × 6 lbs)
        storage_location="Dry Storage",
        shelf_life_days=365
    )


@pytest.fixture
def sample_ingredient_no_pricing():
    """Ingredient with missing pricing data"""
    return Ingredient(
        ingredient_id="ING-003",
        name="Exotic Mushrooms",
        category="Produce",
        unit_of_measure="lb",
        case_size="5 lb",
        storage_location="Walk-in Cooler",
        shelf_life_days=5
    )


@pytest.fixture
def sample_ingredient_sysco_only():
    """Ingredient with only SYSCO pricing"""
    return Ingredient(
        ingredient_id="ING-004",
        name="Specialty Cheese",
        category="Dairy",
        unit_of_measure="lb",
        case_size="10 lb",
        sysco_item_code="SYS-11111",
        sysco_price=75.00,
        sysco_unit_price=7.50,
        storage_location="Walk-in Cooler",
        shelf_life_days=14
    )


# ========================
# Recipe Fixtures
# ========================

@pytest.fixture
def sample_recipe(sample_ingredient_shamrock_cheaper, sample_ingredient_sysco_cheaper):
    """Sample recipe with multiple ingredients"""
    # Calculate best prices for ingredients
    sample_ingredient_shamrock_cheaper.calculate_best_price()
    sample_ingredient_sysco_cheaper.calculate_best_price()

    recipe = Recipe(
        recipe_id="RCP-001",
        name="Garlic Chicken",
        category="Entree",
        yield_amount=10,
        yield_unit="portions",
        portion_size="8 oz",
        prep_time_minutes=15,
        cook_time_minutes=25,
        created_by="Chef Test"
    )

    recipe.ingredients = [
        RecipeIngredient(
            ingredient=sample_ingredient_sysco_cheaper,
            quantity=5.0,  # 5 lbs chicken
            unit="lb",
            prep_instruction="diced"
        ),
        RecipeIngredient(
            ingredient=sample_ingredient_shamrock_cheaper,
            quantity=0.25,  # 4 oz garlic powder
            unit="lb",
            prep_instruction="as needed"
        )
    ]

    return recipe


@pytest.fixture
def sample_recipe_zero_yield():
    """Recipe with zero yield (edge case)"""
    return Recipe(
        recipe_id="RCP-002",
        name="Invalid Recipe",
        category="Test",
        yield_amount=0,  # Invalid!
        yield_unit="portions",
        portion_size="N/A"
    )


# ========================
# Vendor Comparator Fixtures
# ========================

@pytest.fixture
def vendor_comparator():
    """Fresh VendorComparator instance"""
    return VendorComparator()


@pytest.fixture
def corrected_vendor_comparison():
    """Fresh CorrectedVendorComparison instance"""
    return CorrectedVendorComparison()


# ========================
# Sample Product Data Fixtures
# ========================

@pytest.fixture
def sample_products_for_comparison():
    """Sample products with vendor pricing for comparison tests"""
    return [
        {
            'name': 'Black Pepper Ground',
            'sysco_price': 295.89,
            'shamrock_price': 95.88,
            'category': 'Spice'
        },
        {
            'name': 'Onion Powder',
            'sysco_price': 148.95,
            'shamrock_price': 39.80,
            'category': 'Spice'
        },
        {
            'name': 'Chicken Wings',
            'sysco_price': 85.00,
            'shamrock_price': 78.50,
            'category': 'Protein'
        },
        {
            'name': 'Olive Oil',
            'sysco_price': 45.00,
            'shamrock_price': 42.00,
            'category': 'Dry Goods'
        }
    ]


@pytest.fixture
def sample_spice_comparisons():
    """Actual spice comparison data from the codebase"""
    return [
        ("Garlic Powder", "3/6LB", 213.19, "1/6/LB", 54.26),
        ("Black Pepper Ground", "6/1LB", 295.89, "25 LB", 95.88),
        ("Black Pepper Coarse", "6/1LB", 298.95, "25 LB", 79.71),
        ("Black Pepper Cracked", "6/1LB", 269.99, "25 LB", 76.90),
        ("Onion Powder", "6/1LB", 148.95, "25 LB", 39.80),
        ("Garlic Granulated", "5/1LB", 165.99, "25 LB", 67.47),
    ]


# ========================
# Pack Size Test Data
# ========================

@pytest.fixture
def pack_size_test_cases():
    """Comprehensive pack size test cases with expected results"""
    return [
        # (pack_string, expected_total_pounds, expected_total_ounces, expected_containers)
        ("1/6/LB", 6, 96, 1),           # Shamrock: 1 × 6 lbs
        ("3/6LB", 18, 288, 3),          # SYSCO: 3 × 6 lbs
        ("6/1LB", 6, 96, 6),            # SYSCO: 6 × 1 lb
        ("25 LB", 25, 400, 1),          # Simple: 25 lbs
        ("50 LB", 50, 800, 1),          # Simple: 50 lbs
        ("6/#10", 40.875, 654, 6),      # 6 × #10 cans (109 oz each)
        ("2/1GAL", None, 256, 2),       # 2 × 1 gallon (128 oz each)
    ]


@pytest.fixture
def malformed_pack_sizes():
    """Edge cases and malformed pack size strings"""
    return [
        "",                              # Empty string
        "INVALID",                       # No recognizable format
        "10",                           # Just a number
        "/6/LB",                        # Missing containers
        "3/LB",                         # Missing pounds
        "ABC/DEF",                      # Letters instead of numbers
    ]
