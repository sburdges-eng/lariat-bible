"""
Pytest Configuration and Fixtures.

This module provides shared fixtures and configuration for all tests.
"""

import pytest
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Vendor, VendorItem, Recipe, RecipeIngredient, CateringEvent


@pytest.fixture(scope='session')
def app():
    """
    Create application for testing.

    Yields:
        Flask application configured for testing
    """
    # Create app with testing configuration
    test_app = create_app('testing')

    # Push application context
    ctx = test_app.app_context()
    ctx.push()

    yield test_app

    # Cleanup
    ctx.pop()


@pytest.fixture(scope='function')
def client(app):
    """
    Create test client for making requests.

    Args:
        app: Flask application fixture

    Returns:
        Flask test client
    """
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """
    Create CLI test runner.

    Args:
        app: Flask application fixture

    Returns:
        Flask CLI test runner
    """
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def database(app):
    """
    Create clean database for each test.

    Args:
        app: Flask application fixture

    Yields:
        Database instance
    """
    # Create all tables
    db.create_all()

    yield db

    # Drop all tables
    db.session.remove()
    db.drop_all()


# ==================== Model Fixtures ====================

@pytest.fixture
def vendor(database):
    """
    Create a test vendor.

    Args:
        database: Database fixture

    Returns:
        Vendor instance
    """
    vendor = Vendor(
        name='Test Vendor',
        category='broadline',
        contact_name='John Doe',
        email='john@testvendor.com',
        phone='555-123-4567',
        status='active'
    )
    database.session.add(vendor)
    database.session.commit()
    return vendor


@pytest.fixture
def vendor_item(database, vendor):
    """
    Create a test vendor item.

    Args:
        database: Database fixture
        vendor: Vendor fixture

    Returns:
        VendorItem instance
    """
    item = VendorItem(
        vendor_id=vendor.id,
        item_name='Test Item',
        item_code='TEST001',
        unit_price=10.50,
        unit_type='case'
    )
    database.session.add(item)
    database.session.commit()
    return item


@pytest.fixture
def recipe(database):
    """
    Create a test recipe.

    Args:
        database: Database fixture

    Returns:
        Recipe instance
    """
    recipe = Recipe(
        name='Test Recipe',
        description='A delicious test recipe',
        category='entree',
        serving_size=4,
        prep_time=15,
        cook_time=30,
        instructions='Cook it well',
        is_active=True
    )
    database.session.add(recipe)
    database.session.commit()
    return recipe


@pytest.fixture
def recipe_ingredient(database, recipe):
    """
    Create a test recipe ingredient.

    Args:
        database: Database fixture
        recipe: Recipe fixture

    Returns:
        RecipeIngredient instance
    """
    ingredient = RecipeIngredient(
        recipe_id=recipe.id,
        ingredient_name='Test Ingredient',
        quantity=2.5,
        unit='cup',
        notes='Fresh ingredients preferred'
    )
    database.session.add(ingredient)
    database.session.commit()
    return ingredient


@pytest.fixture
def catering_event(database):
    """
    Create a test catering event.

    Args:
        database: Database fixture

    Returns:
        CateringEvent instance
    """
    event = CateringEvent(
        event_name='Test Event',
        client_name='Test Client',
        client_contact='client@test.com',
        event_date=datetime(2025, 12, 31, 18, 0, 0),
        guest_count=50,
        total_quote=1500.00,
        status='confirmed',
        notes='Important client'
    )
    database.session.add(event)
    database.session.commit()
    return event


# ==================== Data Fixtures ====================

@pytest.fixture
def sample_vendor_data():
    """
    Sample vendor data for testing.

    Returns:
        Dictionary with vendor data
    """
    return {
        'name': 'Sample Vendor',
        'category': 'specialty',
        'contact_name': 'Jane Smith',
        'email': 'jane@sample.com',
        'phone': '555-987-6543',
        'status': 'active'
    }


@pytest.fixture
def sample_recipe_data():
    """
    Sample recipe data for testing.

    Returns:
        Dictionary with recipe data
    """
    return {
        'name': 'Sample Recipe',
        'description': 'A sample recipe for testing',
        'category': 'dessert',
        'serving_size': 8,
        'prep_time': 20,
        'cook_time': 45,
        'instructions': 'Follow the steps carefully',
        'is_active': True
    }


@pytest.fixture
def sample_catering_data():
    """
    Sample catering event data for testing.

    Returns:
        Dictionary with catering event data
    """
    return {
        'event_name': 'Sample Wedding',
        'client_name': 'Happy Couple',
        'client_contact': 'couple@wedding.com',
        'event_date': '2025-06-15T14:00:00',
        'guest_count': 150,
        'total_quote': 7500.00,
        'status': 'pending',
        'notes': 'Outdoor venue'
    }


# ==================== Authentication Fixtures ====================

@pytest.fixture
def auth_headers():
    """
    Sample authentication headers for testing.

    Returns:
        Dictionary with auth headers
    """
    return {
        'Authorization': 'Bearer test-token-12345',
        'Content-Type': 'application/json'
    }


# ==================== API Response Helpers ====================

def assert_success_response(response, status_code=200):
    """
    Assert that response is a success response.

    Args:
        response: Flask response object
        status_code: Expected status code
    """
    assert response.status_code == status_code
    data = response.get_json()
    assert data is not None
    assert 'success' in data
    assert data['success'] is True


def assert_error_response(response, status_code=400):
    """
    Assert that response is an error response.

    Args:
        response: Flask response object
        status_code: Expected status code
    """
    assert response.status_code == status_code
    data = response.get_json()
    assert data is not None
    assert 'success' in data or 'error' in data


# Make helpers available to all tests
pytest.assert_success_response = assert_success_response
pytest.assert_error_response = assert_error_response
