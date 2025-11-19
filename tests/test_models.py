"""
Database Model Tests.

Tests for SQLAlchemy models.
"""

import pytest
from datetime import datetime
from models import Vendor, VendorItem, Recipe, RecipeIngredient, CateringEvent


@pytest.mark.database
class TestVendorModel:
    """Test Vendor model."""

    def test_create_vendor(self, database):
        """Test creating a vendor."""
        vendor = Vendor(
            name='Test Vendor',
            category='broadline',
            contact_name='John Doe',
            email='john@test.com',
            phone='555-1234',
            status='active'
        )
        database.session.add(vendor)
        database.session.commit()

        assert vendor.id is not None
        assert vendor.name == 'Test Vendor'
        assert vendor.category == 'broadline'

    def test_vendor_repr(self, vendor):
        """Test vendor string representation."""
        assert 'Test Vendor' in str(vendor)

    def test_vendor_to_dict(self, vendor):
        """Test vendor to_dict method."""
        data = vendor.to_dict()

        assert data['id'] == vendor.id
        assert data['name'] == vendor.name
        assert data['category'] == vendor.category
        assert 'created_at' in data
        assert 'updated_at' in data

    def test_vendor_timestamps(self, vendor):
        """Test vendor timestamps are set."""
        assert vendor.created_at is not None
        assert vendor.updated_at is not None
        assert isinstance(vendor.created_at, datetime)

    def test_vendor_unique_name(self, database, vendor):
        """Test vendor name must be unique."""
        duplicate = Vendor(
            name='Test Vendor',  # Same name as fixture
            category='specialty',
            status='active'
        )
        database.session.add(duplicate)

        with pytest.raises(Exception):  # Should raise IntegrityError
            database.session.commit()


@pytest.mark.database
class TestVendorItemModel:
    """Test VendorItem model."""

    def test_create_vendor_item(self, database, vendor):
        """Test creating a vendor item."""
        item = VendorItem(
            vendor_id=vendor.id,
            item_name='Test Item',
            item_code='TEST001',
            unit_price=10.50,
            unit_type='case'
        )
        database.session.add(item)
        database.session.commit()

        assert item.id is not None
        assert item.vendor_id == vendor.id
        assert item.unit_price == 10.50

    def test_vendor_item_relationship(self, vendor_item, vendor):
        """Test relationship between vendor and items."""
        assert vendor_item.vendor.id == vendor.id
        assert vendor_item in vendor.items

    def test_vendor_item_to_dict(self, vendor_item):
        """Test vendor item to_dict method."""
        data = vendor_item.to_dict()

        assert data['id'] == vendor_item.id
        assert data['item_name'] == vendor_item.item_name
        assert data['unit_price'] == vendor_item.unit_price


@pytest.mark.database
class TestRecipeModel:
    """Test Recipe model."""

    def test_create_recipe(self, database):
        """Test creating a recipe."""
        recipe = Recipe(
            name='Test Recipe',
            description='Test description',
            category='entree',
            serving_size=4,
            prep_time=15,
            cook_time=30,
            instructions='Test instructions',
            is_active=True
        )
        database.session.add(recipe)
        database.session.commit()

        assert recipe.id is not None
        assert recipe.name == 'Test Recipe'
        assert recipe.is_active is True

    def test_recipe_defaults(self, database):
        """Test recipe default values."""
        recipe = Recipe(name='Simple Recipe')
        database.session.add(recipe)
        database.session.commit()

        assert recipe.is_active is True
        assert recipe.created_at is not None

    def test_recipe_to_dict(self, recipe):
        """Test recipe to_dict method."""
        data = recipe.to_dict()

        assert data['id'] == recipe.id
        assert data['name'] == recipe.name
        assert data['category'] == recipe.category


@pytest.mark.database
class TestRecipeIngredientModel:
    """Test RecipeIngredient model."""

    def test_create_ingredient(self, database, recipe):
        """Test creating a recipe ingredient."""
        ingredient = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_name='Test Ingredient',
            quantity=2.5,
            unit='cup'
        )
        database.session.add(ingredient)
        database.session.commit()

        assert ingredient.id is not None
        assert ingredient.recipe_id == recipe.id

    def test_ingredient_relationship(self, recipe_ingredient, recipe):
        """Test relationship between recipe and ingredients."""
        assert recipe_ingredient.recipe.id == recipe.id
        assert recipe_ingredient in recipe.ingredients


@pytest.mark.database
class TestCateringEventModel:
    """Test CateringEvent model."""

    def test_create_catering_event(self, database):
        """Test creating a catering event."""
        event = CateringEvent(
            event_name='Test Event',
            client_name='Test Client',
            event_date=datetime(2025, 12, 31),
            guest_count=100,
            total_quote=5000.00,
            status='pending'
        )
        database.session.add(event)
        database.session.commit()

        assert event.id is not None
        assert event.event_name == 'Test Event'

    def test_catering_event_defaults(self, database):
        """Test catering event default values."""
        event = CateringEvent(
            event_name='Simple Event',
            client_name='Client',
            event_date=datetime(2025, 6, 1)
        )
        database.session.add(event)
        database.session.commit()

        assert event.status == 'pending'

    def test_catering_event_to_dict(self, catering_event):
        """Test catering event to_dict method."""
        data = catering_event.to_dict()

        assert data['id'] == catering_event.id
        assert data['event_name'] == catering_event.event_name
        assert data['guest_count'] == catering_event.guest_count


@pytest.mark.database
class TestCascadeDeletes:
    """Test cascade delete behavior."""

    def test_vendor_delete_cascades_to_items(self, database, vendor, vendor_item):
        """Test deleting vendor deletes associated items."""
        vendor_id = vendor.id
        item_id = vendor_item.id

        database.session.delete(vendor)
        database.session.commit()

        # Vendor should be deleted
        assert Vendor.query.get(vendor_id) is None

        # Item should also be deleted (cascade)
        assert VendorItem.query.get(item_id) is None

    def test_recipe_delete_cascades_to_ingredients(
        self, database, recipe, recipe_ingredient
    ):
        """Test deleting recipe deletes associated ingredients."""
        recipe_id = recipe.id
        ingredient_id = recipe_ingredient.id

        database.session.delete(recipe)
        database.session.commit()

        # Recipe should be deleted
        assert Recipe.query.get(recipe_id) is None

        # Ingredient should also be deleted (cascade)
        assert RecipeIngredient.query.get(ingredient_id) is None
