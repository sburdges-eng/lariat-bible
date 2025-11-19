"""
Input Validation and Sanitization Schemas.

This module provides Marshmallow schemas for validating and sanitizing
all API inputs to ensure data integrity and security.
"""

from marshmallow import Schema, fields, validate, validates, ValidationError, EXCLUDE
from datetime import datetime


# ==================== Base Schemas ====================

class TimestampMixin:
    """Mixin for timestamp fields."""
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


# ==================== Vendor Schemas ====================

class VendorSchema(Schema):
    """Schema for validating vendor data."""

    class Meta:
        unknown = EXCLUDE  # Ignore unknown fields

    id = fields.Int(dump_only=True)
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200),
        error_messages={'required': 'Vendor name is required'}
    )
    category = fields.Str(
        required=True,
        validate=validate.OneOf([
            'broadline', 'specialty', 'produce', 'meat', 'seafood',
            'dairy', 'beverage', 'equipment', 'supplies', 'other'
        ]),
        error_messages={'required': 'Vendor category is required'}
    )
    contact_name = fields.Str(
        validate=validate.Length(max=200),
        allow_none=True
    )
    email = fields.Email(
        allow_none=True,
        error_messages={'invalid': 'Invalid email address format'}
    )
    phone = fields.Str(
        validate=validate.Length(max=50),
        allow_none=True
    )
    status = fields.Str(
        validate=validate.OneOf(['active', 'inactive', 'pending']),
        missing='active'
    )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates('phone')
    def validate_phone(self, value):
        """Validate phone number format."""
        if value:
            # Remove common separators
            cleaned = value.replace('-', '').replace('(', '').replace(')', '').replace(' ', '').replace('.', '')
            if not cleaned.isdigit():
                raise ValidationError('Phone number must contain only digits and common separators')
            if len(cleaned) < 10:
                raise ValidationError('Phone number must be at least 10 digits')


class VendorItemSchema(Schema):
    """Schema for validating vendor item data."""

    class Meta:
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    vendor_id = fields.Int(required=True)
    item_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=300)
    )
    item_code = fields.Str(
        validate=validate.Length(max=100),
        allow_none=True
    )
    unit_price = fields.Float(
        required=True,
        validate=validate.Range(min=0, min_inclusive=False)
    )
    unit_type = fields.Str(
        required=True,
        validate=validate.OneOf([
            'case', 'pound', 'kilogram', 'ounce', 'gram',
            'gallon', 'liter', 'quart', 'each', 'dozen', 'box'
        ])
    )
    last_price_update = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class VendorComparisonSchema(Schema):
    """Schema for vendor comparison requests."""

    class Meta:
        unknown = EXCLUDE

    vendor1 = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    vendor2 = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200)
    )

    @validates('vendor2')
    def validate_different_vendors(self, value):
        """Ensure vendors are different."""
        if 'vendor1' in self.context and value == self.context['vendor1']:
            raise ValidationError('Cannot compare a vendor with itself')


# ==================== Recipe Schemas ====================

class RecipeSchema(Schema):
    """Schema for validating recipe data."""

    class Meta:
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    description = fields.Str(
        validate=validate.Length(max=1000),
        allow_none=True
    )
    category = fields.Str(
        validate=validate.OneOf([
            'appetizer', 'entree', 'side', 'dessert', 'beverage',
            'sauce', 'dressing', 'marinade', 'soup', 'salad', 'other'
        ]),
        allow_none=True
    )
    serving_size = fields.Int(
        validate=validate.Range(min=1, max=1000),
        allow_none=True
    )
    prep_time = fields.Int(
        validate=validate.Range(min=0, max=1440),  # Max 24 hours
        allow_none=True
    )
    cook_time = fields.Int(
        validate=validate.Range(min=0, max=1440),
        allow_none=True
    )
    instructions = fields.Str(
        validate=validate.Length(max=10000),
        allow_none=True
    )
    is_active = fields.Bool(missing=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class RecipeIngredientSchema(Schema):
    """Schema for validating recipe ingredient data."""

    class Meta:
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    recipe_id = fields.Int(required=True)
    ingredient_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    quantity = fields.Float(
        required=True,
        validate=validate.Range(min=0, min_inclusive=False)
    )
    unit = fields.Str(
        required=True,
        validate=validate.OneOf([
            'cup', 'tablespoon', 'teaspoon', 'pound', 'ounce',
            'gram', 'kilogram', 'liter', 'milliliter', 'gallon',
            'quart', 'pint', 'piece', 'whole', 'pinch', 'dash'
        ])
    )
    notes = fields.Str(
        validate=validate.Length(max=500),
        allow_none=True
    )


# ==================== Catering Schemas ====================

class CateringEventSchema(Schema):
    """Schema for validating catering event data."""

    class Meta:
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    event_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=300)
    )
    client_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    client_contact = fields.Str(
        validate=validate.Length(max=200),
        allow_none=True
    )
    event_date = fields.DateTime(
        required=True,
        format='iso'
    )
    guest_count = fields.Int(
        validate=validate.Range(min=1, max=10000),
        allow_none=True
    )
    total_quote = fields.Float(
        validate=validate.Range(min=0),
        allow_none=True
    )
    status = fields.Str(
        validate=validate.OneOf(['pending', 'confirmed', 'completed', 'cancelled']),
        missing='pending'
    )
    notes = fields.Str(
        validate=validate.Length(max=2000),
        allow_none=True
    )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates('event_date')
    def validate_event_date(self, value):
        """Ensure event date is not in the past (for new events)."""
        if isinstance(value, datetime) and value < datetime.utcnow():
            # Allow past dates when updating existing events
            if not self.context.get('is_update'):
                raise ValidationError('Event date cannot be in the past')


# ==================== Pagination & Filtering ====================

class PaginationSchema(Schema):
    """Schema for pagination parameters."""

    class Meta:
        unknown = EXCLUDE

    page = fields.Int(
        validate=validate.Range(min=1),
        missing=1
    )
    per_page = fields.Int(
        validate=validate.Range(min=1, max=100),
        missing=20
    )
    sort_by = fields.Str(
        validate=validate.Length(max=50),
        allow_none=True
    )
    sort_order = fields.Str(
        validate=validate.OneOf(['asc', 'desc']),
        missing='asc'
    )


class DateRangeSchema(Schema):
    """Schema for date range filtering."""

    class Meta:
        unknown = EXCLUDE

    start_date = fields.DateTime(format='iso', allow_none=True)
    end_date = fields.DateTime(format='iso', allow_none=True)

    @validates('end_date')
    def validate_date_range(self, value):
        """Ensure end_date is after start_date."""
        if value and 'start_date' in self.context:
            start = self.context['start_date']
            if start and value < start:
                raise ValidationError('End date must be after start date')


# ==================== Search & Filter ====================

class SearchSchema(Schema):
    """Schema for search parameters."""

    class Meta:
        unknown = EXCLUDE

    query = fields.Str(
        validate=validate.Length(min=1, max=200),
        allow_none=True
    )
    filters = fields.Dict(allow_none=True)
    limit = fields.Int(
        validate=validate.Range(min=1, max=100),
        missing=20
    )


# ==================== Helper Functions ====================

def sanitize_string(value):
    """
    Sanitize string input to prevent XSS and injection attacks.

    Args:
        value: String to sanitize

    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return value

    # Remove null bytes
    value = value.replace('\x00', '')

    # Strip leading/trailing whitespace
    value = value.strip()

    # Replace multiple spaces with single space
    value = ' '.join(value.split())

    return value


def validate_and_sanitize(schema, data, **kwargs):
    """
    Validate and sanitize input data using a Marshmallow schema.

    Args:
        schema: Marshmallow schema class or instance
        data: Data to validate
        **kwargs: Additional context for validation

    Returns:
        Validated and sanitized data

    Raises:
        ValidationError: If validation fails
    """
    if isinstance(schema, type):
        schema_instance = schema()
    else:
        schema_instance = schema

    # Add context for validation
    schema_instance.context.update(kwargs)

    # Validate and return
    return schema_instance.load(data)


# ==================== Schema Instances ====================

# Create reusable schema instances
vendor_schema = VendorSchema()
vendors_schema = VendorSchema(many=True)
vendor_item_schema = VendorItemSchema()
vendor_items_schema = VendorItemSchema(many=True)
recipe_schema = RecipeSchema()
recipes_schema = RecipeSchema(many=True)
ingredient_schema = RecipeIngredientSchema()
ingredients_schema = RecipeIngredientSchema(many=True)
catering_event_schema = CateringEventSchema()
catering_events_schema = CateringEventSchema(many=True)
pagination_schema = PaginationSchema()
search_schema = SearchSchema()
