"""
Validation Schema Tests.

Tests for Marshmallow validation schemas.
"""

import pytest
from marshmallow import ValidationError
from datetime import datetime
from validators import (
    VendorSchema, VendorItemSchema, RecipeSchema,
    RecipeIngredientSchema, CateringEventSchema,
    PaginationSchema, sanitize_string, validate_and_sanitize
)


@pytest.mark.unit
class TestVendorSchema:
    """Test VendorSchema validation."""

    def test_valid_vendor_data(self):
        """Test validation of valid vendor data."""
        data = {
            'name': 'Test Vendor',
            'category': 'broadline',
            'contact_name': 'John Doe',
            'email': 'john@test.com',
            'phone': '555-123-4567',
            'status': 'active'
        }

        schema = VendorSchema()
        result = schema.load(data)

        assert result['name'] == 'Test Vendor'
        assert result['category'] == 'broadline'

    def test_missing_required_fields(self):
        """Test validation fails with missing required fields."""
        data = {'contact_name': 'John Doe'}  # Missing name and category

        schema = VendorSchema()

        with pytest.raises(ValidationError) as exc:
            schema.load(data)

        assert 'name' in exc.value.messages
        assert 'category' in exc.value.messages

    def test_invalid_email(self):
        """Test validation fails with invalid email."""
        data = {
            'name': 'Test',
            'category': 'broadline',
            'email': 'invalid-email'
        }

        schema = VendorSchema()

        with pytest.raises(ValidationError) as exc:
            schema.load(data)

        assert 'email' in exc.value.messages

    def test_invalid_category(self):
        """Test validation fails with invalid category."""
        data = {
            'name': 'Test',
            'category': 'invalid-category'
        }

        schema = VendorSchema()

        with pytest.raises(ValidationError) as exc:
            schema.load(data)

        assert 'category' in exc.value.messages

    def test_invalid_phone(self):
        """Test validation fails with invalid phone."""
        data = {
            'name': 'Test',
            'category': 'broadline',
            'phone': 'abc'  # Not a valid phone
        }

        schema = VendorSchema()

        with pytest.raises(ValidationError) as exc:
            schema.load(data)

        assert 'phone' in exc.value.messages


@pytest.mark.unit
class TestRecipeSchema:
    """Test RecipeSchema validation."""

    def test_valid_recipe_data(self):
        """Test validation of valid recipe data."""
        data = {
            'name': 'Test Recipe',
            'description': 'A test recipe',
            'category': 'entree',
            'serving_size': 4,
            'prep_time': 15,
            'cook_time': 30
        }

        schema = RecipeSchema()
        result = schema.load(data)

        assert result['name'] == 'Test Recipe'
        assert result['serving_size'] == 4

    def test_invalid_serving_size(self):
        """Test validation fails with invalid serving size."""
        data = {
            'name': 'Test',
            'serving_size': 0  # Must be at least 1
        }

        schema = RecipeSchema()

        with pytest.raises(ValidationError) as exc:
            schema.load(data)

        assert 'serving_size' in exc.value.messages

    def test_invalid_times(self):
        """Test validation fails with invalid time values."""
        data = {
            'name': 'Test',
            'prep_time': -5  # Negative not allowed
        }

        schema = RecipeSchema()

        with pytest.raises(ValidationError) as exc:
            schema.load(data)

        assert 'prep_time' in exc.value.messages


@pytest.mark.unit
class TestCateringEventSchema:
    """Test CateringEventSchema validation."""

    def test_valid_event_data(self):
        """Test validation of valid event data."""
        data = {
            'event_name': 'Test Event',
            'client_name': 'Test Client',
            'event_date': '2025-12-31T18:00:00',
            'guest_count': 50,
            'total_quote': 1500.00,
            'status': 'pending'
        }

        schema = CateringEventSchema()
        result = schema.load(data)

        assert result['event_name'] == 'Test Event'
        assert result['guest_count'] == 50

    def test_invalid_guest_count(self):
        """Test validation fails with invalid guest count."""
        data = {
            'event_name': 'Test',
            'client_name': 'Test',
            'event_date': '2025-12-31T18:00:00',
            'guest_count': 0  # Must be at least 1
        }

        schema = CateringEventSchema()

        with pytest.raises(ValidationError) as exc:
            schema.load(data)

        assert 'guest_count' in exc.value.messages

    def test_invalid_status(self):
        """Test validation fails with invalid status."""
        data = {
            'event_name': 'Test',
            'client_name': 'Test',
            'event_date': '2025-12-31T18:00:00',
            'status': 'invalid-status'
        }

        schema = CateringEventSchema()

        with pytest.raises(ValidationError) as exc:
            schema.load(data)

        assert 'status' in exc.value.messages


@pytest.mark.unit
class TestPaginationSchema:
    """Test PaginationSchema validation."""

    def test_valid_pagination(self):
        """Test validation of valid pagination data."""
        data = {
            'page': 2,
            'per_page': 50,
            'sort_by': 'name',
            'sort_order': 'desc'
        }

        schema = PaginationSchema()
        result = schema.load(data)

        assert result['page'] == 2
        assert result['per_page'] == 50

    def test_default_values(self):
        """Test default pagination values."""
        data = {}

        schema = PaginationSchema()
        result = schema.load(data)

        assert result['page'] == 1
        assert result['per_page'] == 20
        assert result['sort_order'] == 'asc'

    def test_invalid_page(self):
        """Test validation fails with invalid page number."""
        data = {'page': 0}  # Must be at least 1

        schema = PaginationSchema()

        with pytest.raises(ValidationError) as exc:
            schema.load(data)

        assert 'page' in exc.value.messages

    def test_per_page_limit(self):
        """Test per_page has maximum limit."""
        data = {'per_page': 1000}  # Over the 100 limit

        schema = PaginationSchema()

        with pytest.raises(ValidationError) as exc:
            schema.load(data)

        assert 'per_page' in exc.value.messages


@pytest.mark.unit
@pytest.mark.security
class TestSanitization:
    """Test data sanitization functions."""

    def test_sanitize_string_removes_xss(self):
        """Test sanitize_string removes XSS attempts."""
        malicious = '<script>alert("xss")</script>Hello'
        cleaned = sanitize_string(malicious)

        assert '<script>' not in cleaned
        assert 'Hello' in cleaned

    def test_sanitize_string_removes_null_bytes(self):
        """Test sanitize_string removes null bytes."""
        data = 'Hello\x00World'
        cleaned = sanitize_string(data)

        assert '\x00' not in cleaned
        assert 'HelloWorld' in cleaned

    def test_sanitize_string_normalizes_whitespace(self):
        """Test sanitize_string normalizes whitespace."""
        data = 'Hello    World   Test'
        cleaned = sanitize_string(data)

        assert cleaned == 'Hello World Test'

    def test_sanitize_dict(self):
        """Test sanitizing dictionary values."""
        from validators import sanitize_dict

        data = {
            'name': '  Test  Name  ',
            'description': '<script>alert("xss")</script>Description'
        }

        cleaned = sanitize_dict(data)

        assert cleaned['name'] == 'Test Name'
        assert '<script>' not in cleaned['description']


@pytest.mark.unit
class TestValidationHelpers:
    """Test validation helper functions."""

    def test_validate_and_sanitize(self):
        """Test combined validation and sanitization."""
        data = {
            'name': '  Test Vendor  ',
            'category': 'broadline'
        }

        result = validate_and_sanitize(VendorSchema, data)

        assert result['name'] == 'Test Vendor'
        assert result['category'] == 'broadline'

    def test_validate_and_sanitize_fails(self):
        """Test validation failure."""
        data = {'invalid': 'data'}

        with pytest.raises(ValidationError):
            validate_and_sanitize(VendorSchema, data)
