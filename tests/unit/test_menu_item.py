"""
P1 HIGH PRIORITY: Tests for menu item margin calculations
These tests ensure accurate pricing and margin management
"""

import pytest
from datetime import datetime
from modules.menu.menu_item import MenuItem


@pytest.mark.high
class TestMenuItemMargins:
    """Test margin calculations for menu items"""

    def test_margin_calculation(self, sample_menu_item):
        """Test margin property calculation"""
        # Menu price: $32.99, Food cost: $12.50
        # Margin = ($32.99 - $12.50) / $32.99 = 0.621
        expected_margin = (32.99 - 12.50) / 32.99
        assert abs(sample_menu_item.margin - expected_margin) < 0.01

    def test_margin_zero_menu_price(self):
        """Test margin calculation with zero menu price"""
        menu_item = MenuItem(
            item_id="test_001",
            name="Test Item",
            category="Test",
            menu_price=0.0,
            food_cost=5.0
        )

        assert menu_item.margin == 0

    def test_margin_variance(self, sample_menu_item):
        """Test margin variance from target"""
        # Current margin: ~62.1%, Target: 45%
        # Variance: 62.1% - 45% = 17.1%
        expected_variance = sample_menu_item.margin - 0.45
        assert abs(sample_menu_item.margin_variance - expected_variance) < 0.01

    def test_suggested_price_calculation(self, sample_menu_item):
        """Test suggested price based on target margin"""
        # Food cost: $12.50, Target margin: 45%
        # Suggested price = $12.50 / (1 - 0.45) = $12.50 / 0.55 = $22.73
        expected_price = 12.50 / (1 - 0.45)
        assert abs(sample_menu_item.suggested_price - expected_price) < 0.01

    def test_suggested_price_invalid_margin(self):
        """Test suggested price with invalid margin (>=1)"""
        menu_item = MenuItem(
            item_id="test_001",
            name="Test Item",
            category="Test",
            menu_price=10.0,
            food_cost=5.0,
            target_margin=1.0  # 100% margin - invalid
        )

        # Should return 0 for invalid margin
        assert menu_item.suggested_price == 0

    def test_suggested_price_high_margin_target(self):
        """Test suggested price with high margin target (catering)"""
        menu_item = MenuItem(
            item_id="cater_001",
            name="Catering Item",
            category="Catering",
            menu_price=50.0,
            food_cost=20.0,
            target_margin=0.45  # 45% for catering
        )

        # $20 / (1 - 0.45) = $36.36
        expected_price = 20.0 / 0.55
        assert abs(menu_item.suggested_price - expected_price) < 0.01

    def test_suggested_price_low_margin_target(self):
        """Test suggested price with low margin target (restaurant)"""
        menu_item = MenuItem(
            item_id="rest_001",
            name="Restaurant Item",
            category="Entree",
            menu_price=15.0,
            food_cost=10.0,
            target_margin=0.04  # 4% for restaurant
        )

        # $10 / (1 - 0.04) = $10.42
        expected_price = 10.0 / 0.96
        assert abs(menu_item.suggested_price - expected_price) < 0.01


@pytest.mark.high
class TestMenuItemFoodCostUpdate:
    """Test food cost update functionality"""

    def test_update_food_cost(self, sample_menu_item):
        """Test updating food cost and analysis"""
        old_cost = sample_menu_item.food_cost
        new_cost = 15.00

        result = sample_menu_item.update_food_cost(new_cost)

        assert result['old_cost'] == old_cost
        assert result['new_cost'] == new_cost
        assert result['cost_change'] == new_cost - old_cost
        assert result['current_price'] == sample_menu_item.menu_price
        assert 'current_margin' in result
        assert 'suggested_price' in result
        assert 'price_adjustment_needed' in result

    def test_update_food_cost_increases_margin(self):
        """Test that decreasing food cost increases margin"""
        menu_item = MenuItem(
            item_id="test_001",
            name="Test Item",
            category="Test",
            menu_price=20.0,
            food_cost=10.0,
            target_margin=0.30
        )

        old_margin = menu_item.margin

        # Decrease food cost
        menu_item.update_food_cost(8.0)

        new_margin = menu_item.margin
        assert new_margin > old_margin

    def test_update_food_cost_flags_adjustment_needed(self):
        """Test that significant margin variance flags adjustment needed"""
        menu_item = MenuItem(
            item_id="test_001",
            name="Test Item",
            category="Test",
            menu_price=20.0,
            food_cost=10.0,
            target_margin=0.30
        )

        # Current margin: 50%, Target: 30%
        # Variance: 20% > 5% threshold
        result = menu_item.update_food_cost(10.0)
        assert result['price_adjustment_needed'] is True

    def test_update_food_cost_no_adjustment_needed(self):
        """Test that small margin variance doesn't flag adjustment"""
        menu_item = MenuItem(
            item_id="test_001",
            name="Test Item",
            category="Test",
            menu_price=20.0,
            food_cost=13.0,  # Results in ~35% margin
            target_margin=0.30
        )

        # Margin variance: 5% exactly
        result = menu_item.update_food_cost(13.0)
        # Should not need adjustment if within 5%
        # (20 - 13) / 20 = 0.35, target 0.30, variance 0.05
        assert result['price_adjustment_needed'] is False

    def test_update_food_cost_updates_timestamp(self, sample_menu_item):
        """Test that updating food cost updates last_modified timestamp"""
        old_timestamp = sample_menu_item.last_modified

        # Wait a tiny bit to ensure timestamp changes
        import time
        time.sleep(0.01)

        sample_menu_item.update_food_cost(15.0)

        assert sample_menu_item.last_modified > old_timestamp


@pytest.mark.high
class TestMenuItemSerialization:
    """Test menu item serialization and deserialization"""

    def test_to_dict(self, sample_menu_item):
        """Test converting menu item to dictionary"""
        data = sample_menu_item.to_dict()

        assert data['item_id'] == sample_menu_item.item_id
        assert data['name'] == sample_menu_item.name
        assert data['category'] == sample_menu_item.category
        assert data['menu_price'] == sample_menu_item.menu_price
        assert data['food_cost'] == sample_menu_item.food_cost
        assert data['margin'] == sample_menu_item.margin
        assert 'created_date' in data
        assert 'last_modified' in data

    def test_from_dict(self, sample_menu_item):
        """Test creating menu item from dictionary"""
        data = sample_menu_item.to_dict()
        restored_item = MenuItem.from_dict(data)

        assert restored_item.item_id == sample_menu_item.item_id
        assert restored_item.name == sample_menu_item.name
        assert restored_item.menu_price == sample_menu_item.menu_price
        assert restored_item.food_cost == sample_menu_item.food_cost

    def test_to_dict_from_dict_roundtrip(self, sample_menu_item):
        """Test complete roundtrip conversion"""
        # Convert to dict and back
        data = sample_menu_item.to_dict()
        restored = MenuItem.from_dict(data)
        data2 = restored.to_dict()

        # Should be identical (except datetime precision)
        assert data['item_id'] == data2['item_id']
        assert data['name'] == data2['name']
        assert data['menu_price'] == data2['menu_price']
        assert data['food_cost'] == data2['food_cost']

    def test_from_dict_datetime_parsing(self):
        """Test that datetime strings are properly parsed"""
        data = {
            'item_id': 'test_001',
            'name': 'Test Item',
            'category': 'Test',
            'menu_price': 10.0,
            'food_cost': 5.0,
            'created_date': '2024-01-01T12:00:00',
            'last_modified': '2024-01-02T12:00:00'
        }

        item = MenuItem.from_dict(data)

        assert isinstance(item.created_date, datetime)
        assert isinstance(item.last_modified, datetime)
        assert item.created_date.year == 2024
        assert item.created_date.month == 1


@pytest.mark.high
class TestMenuItemDefaults:
    """Test default values and initialization"""

    def test_defaults_initialization(self):
        """Test that defaults are properly set"""
        menu_item = MenuItem(
            item_id="test_001",
            name="Test Item",
            category="Test"
        )

        assert menu_item.menu_price == 0.0
        assert menu_item.food_cost == 0.0
        assert menu_item.target_margin == 0.30
        assert menu_item.available is True
        assert menu_item.seasonal is False
        assert len(menu_item.days_available) == 7  # All days
        assert len(menu_item.meal_periods) == 2  # Lunch and Dinner
        assert menu_item.dietary_flags == []
        assert menu_item.allergens == []

    def test_display_name_defaults_to_name(self):
        """Test that display_name defaults to name if not provided"""
        menu_item = MenuItem(
            item_id="test_001",
            name="Regular Name",
            category="Test"
        )

        assert menu_item.display_name == "Regular Name"

    def test_display_name_can_be_different(self):
        """Test that display_name can be set differently from name"""
        menu_item = MenuItem(
            item_id="test_001",
            name="Internal Name",
            category="Test",
            display_name="Fancy Menu Name"
        )

        assert menu_item.name == "Internal Name"
        assert menu_item.display_name == "Fancy Menu Name"

    def test_timestamps_auto_set(self):
        """Test that timestamps are automatically set"""
        menu_item = MenuItem(
            item_id="test_001",
            name="Test Item",
            category="Test"
        )

        assert menu_item.created_date is not None
        assert menu_item.last_modified is not None
        assert isinstance(menu_item.created_date, datetime)
        assert isinstance(menu_item.last_modified, datetime)


@pytest.mark.high
class TestMenuItemEdgeCases:
    """Test edge cases and error conditions"""

    def test_negative_food_cost(self):
        """Test handling of negative food cost"""
        menu_item = MenuItem(
            item_id="test_001",
            name="Test Item",
            category="Test",
            menu_price=10.0,
            food_cost=-5.0  # Negative cost
        )

        # Margin would be > 100%, which is unusual but mathematically valid
        margin = (10.0 - (-5.0)) / 10.0
        assert abs(menu_item.margin - margin) < 0.01

    def test_food_cost_exceeds_menu_price(self):
        """Test when food cost is higher than menu price (negative margin)"""
        menu_item = MenuItem(
            item_id="test_001",
            name="Test Item",
            category="Test",
            menu_price=10.0,
            food_cost=15.0  # Losing money!
        )

        # Margin: (10 - 15) / 10 = -0.5 = -50%
        assert menu_item.margin < 0

        # Suggested price should still work
        suggested = menu_item.suggested_price
        assert suggested > food_cost  # Should be > $15

    def test_very_high_margin_target(self):
        """Test with very high margin target close to 100%"""
        menu_item = MenuItem(
            item_id="test_001",
            name="Test Item",
            category="Test",
            menu_price=100.0,
            food_cost=10.0,
            target_margin=0.99  # 99% margin
        )

        # Suggested price = $10 / (1 - 0.99) = $10 / 0.01 = $1000
        assert menu_item.suggested_price == 1000.0

    def test_zero_target_margin(self):
        """Test with zero target margin (non-profit)"""
        menu_item = MenuItem(
            item_id="test_001",
            name="Test Item",
            category="Test",
            menu_price=10.0,
            food_cost=10.0,
            target_margin=0.0  # No profit margin
        )

        # Suggested price = cost / (1 - 0) = cost
        assert menu_item.suggested_price == 10.0
