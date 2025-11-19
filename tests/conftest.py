"""
Shared pytest fixtures for all tests
"""

import pytest
from datetime import datetime, timedelta
from modules.recipes.recipe import Recipe, Ingredient, RecipeIngredient
from modules.menu.menu_item import MenuItem
from modules.equipment.equipment_manager import Equipment, EquipmentStatus, MaintenanceRecord, MaintenanceType
from modules.vendor_analysis.accurate_matcher import ProductMatch


@pytest.fixture
def sample_ingredient_pepper():
    """Sample black pepper ingredient with vendor pricing"""
    return Ingredient(
        ingredient_id="pepper_001",
        name="Black Pepper Coarse",
        category="Spices",
        unit_of_measure="lb",
        case_size="25 LB",
        sysco_item_code="SYSCO_COARSE",
        sysco_price=298.95,
        sysco_unit_price=49.825,  # per lb
        sysco_last_updated=datetime.now(),
        shamrock_item_code="SHAM_COARSE",
        shamrock_price=79.71,
        shamrock_unit_price=3.19,  # per lb
        shamrock_last_updated=datetime.now(),
        preferred_vendor="Shamrock Foods",
        price_difference=46.635,
        price_difference_percent=175.6
    )


@pytest.fixture
def sample_ingredient_garlic():
    """Sample garlic powder ingredient"""
    return Ingredient(
        ingredient_id="garlic_001",
        name="Garlic Powder",
        category="Spices",
        unit_of_measure="lb",
        case_size="6 LB",
        sysco_item_code="SYSCO_GARLIC",
        sysco_price=213.19,
        sysco_unit_price=11.84,
        shamrock_item_code="SHAM_GARLIC",
        shamrock_price=54.26,
        shamrock_unit_price=9.04,
        preferred_vendor="Shamrock Foods"
    )


@pytest.fixture
def sample_recipe(sample_ingredient_pepper, sample_ingredient_garlic):
    """Sample recipe with ingredients"""
    recipe = Recipe(
        recipe_id="recipe_001",
        name="Seasoned Steak Rub",
        category="Seasoning",
        yield_amount=10,
        yield_unit="portions",
        portion_size="2 oz",
        prep_time_minutes=10,
        cook_time_minutes=0
    )

    recipe.ingredients = [
        RecipeIngredient(
            ingredient=sample_ingredient_pepper,
            quantity=1.0,
            unit="lb",
            prep_instruction="Use coarse grind"
        ),
        RecipeIngredient(
            ingredient=sample_ingredient_garlic,
            quantity=0.5,
            unit="lb",
            prep_instruction="Mix well"
        )
    ]

    return recipe


@pytest.fixture
def sample_menu_item():
    """Sample menu item"""
    return MenuItem(
        item_id="menu_001",
        name="Ribeye Steak",
        category="Entree",
        subcategory="Beef",
        description="12 oz ribeye with garlic butter",
        menu_price=32.99,
        food_cost=12.50,
        target_margin=0.45,
        recipe_id="recipe_steak_001",
        portion_size="12 oz",
        available=True,
        popularity_score=9,
        monthly_sales=120
    )


@pytest.fixture
def sample_equipment():
    """Sample kitchen equipment"""
    return Equipment(
        equipment_id="eq_001",
        name="Commercial Range",
        category="Cooking",
        brand="Vulcan",
        model="V6B",
        serial_number="V6B-12345",
        location="Kitchen",
        station="Hot Line",
        purchase_date=datetime(2020, 1, 15),
        purchase_price=8500.00,
        vendor="Restaurant Depot",
        warranty_end_date=datetime(2023, 1, 15),
        service_company="Kitchen Pro Services",
        service_phone="970-555-1234",
        status=EquipmentStatus.OPERATIONAL,
        last_maintenance_date=datetime(2024, 10, 1),
        next_maintenance_due=datetime(2024, 12, 1)
    )


@pytest.fixture
def sample_maintenance_record():
    """Sample maintenance record"""
    return MaintenanceRecord(
        record_id="maint_001",
        equipment_id="eq_001",
        date_performed=datetime.now(),
        maintenance_type=MaintenanceType.MONTHLY_INSPECTION,
        performed_by="John Smith",
        tasks_completed=[
            "Cleaned burners",
            "Checked gas connections",
            "Calibrated temperature"
        ],
        labor_hours=2.0,
        labor_cost=150.00,
        parts_cost=25.00,
        next_maintenance_date=datetime.now() + timedelta(days=30),
        notes="All systems operational"
    )


@pytest.fixture
def sample_product_match():
    """Sample product match for vendor comparison"""
    return ProductMatch(
        product_name="Black Pepper",
        specification="Coarse Grind",
        sysco_code="SYSCO_COARSE",
        sysco_description="BLACK PEPPER COARSE",
        sysco_pack="6/1LB",
        sysco_case_price=298.95,
        sysco_split_price=None,
        shamrock_code="SHAM_COARSE",
        shamrock_description="PEPPER BLACK COARSE GRIND",
        shamrock_pack="25 LB",
        shamrock_price=79.71,
        notes="For steaks and robust dishes"
    )


@pytest.fixture
def sysco_order_guide_data():
    """Sample SYSCO order guide data"""
    return [
        {
            'item_code': 'SYS001',
            'description': 'BEEF GROUND 80/20',
            'pack_size': '10 LB',
            'case_price': 45.99,
            'unit_price': 4.599,
            'unit': 'LB',
            'category': 'MEAT'
        },
        {
            'item_code': 'SYS002',
            'description': 'CHICKEN BREAST BONELESS',
            'pack_size': '40 LB',
            'case_price': 89.99,
            'unit_price': 2.249,
            'unit': 'LB',
            'category': 'POULTRY'
        },
        {
            'item_code': 'SYS003',
            'description': 'PEPPER BLACK COARSE',
            'pack_size': '6/1LB',
            'case_price': 298.95,
            'unit_price': 49.825,
            'unit': 'LB',
            'category': 'SPICES'
        }
    ]


@pytest.fixture
def shamrock_order_guide_data():
    """Sample Shamrock order guide data"""
    return [
        {
            'item_code': 'SHA001',
            'description': 'GROUND BEEF 80/20',
            'pack_size': '10 LB',
            'case_price': 32.50,
            'unit_price': 3.25,
            'unit': 'LB',
            'category': 'MEAT'
        },
        {
            'item_code': 'SHA002',
            'description': 'CHICKEN BREAST BNLS',
            'pack_size': '40 LB',
            'case_price': 63.50,
            'unit_price': 1.587,
            'unit': 'LB',
            'category': 'POULTRY'
        },
        {
            'item_code': 'SHA003',
            'description': 'PEPPER BLACK COARSE GRIND',
            'pack_size': '25 LB',
            'case_price': 79.71,
            'unit_price': 3.19,
            'unit': 'LB',
            'category': 'SPICES'
        }
    ]
