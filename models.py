"""
Database Models for The Lariat Bible.

This module contains all SQLAlchemy models for the restaurant management system.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship

# Initialize SQLAlchemy
db = SQLAlchemy()


class Vendor(db.Model):
    """
    Vendor model for food and supply vendors.

    Attributes:
        id: Primary key
        name: Vendor company name
        category: Type of vendor (broadline, specialty, produce, etc.)
        contact_name: Primary contact person
        email: Contact email
        phone: Contact phone number
        status: active, inactive, or pending
        created_at: Timestamp of record creation
        updated_at: Timestamp of last update
    """

    __tablename__ = 'vendors'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    category = Column(String(100), nullable=False)
    contact_name = Column(String(200))
    email = Column(String(200))
    phone = Column(String(50))
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    items = relationship('VendorItem', back_populates='vendor', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Vendor {self.name}>'

    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'contact_name': self.contact_name,
            'email': self.email,
            'phone': self.phone,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class VendorItem(db.Model):
    """
    Items/products available from vendors.

    Attributes:
        id: Primary key
        vendor_id: Foreign key to Vendor
        item_name: Product/item name
        item_code: Vendor's product code
        unit_price: Price per unit
        unit_type: Unit of measurement (case, pound, each, etc.)
        last_price_update: When price was last updated
    """

    __tablename__ = 'vendor_items'

    id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey('vendors.id'), nullable=False)
    item_name = Column(String(300), nullable=False)
    item_code = Column(String(100))
    unit_price = Column(Float, nullable=False)
    unit_type = Column(String(50), nullable=False)
    last_price_update = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    vendor = relationship('Vendor', back_populates='items')

    def __repr__(self):
        return f'<VendorItem {self.item_name} - ${self.unit_price}>'

    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'vendor_id': self.vendor_id,
            'item_name': self.item_name,
            'item_code': self.item_code,
            'unit_price': self.unit_price,
            'unit_type': self.unit_type,
            'last_price_update': self.last_price_update.isoformat() if self.last_price_update else None
        }


class Recipe(db.Model):
    """
    Standardized recipes with ingredients and instructions.

    Attributes:
        id: Primary key
        name: Recipe name
        description: Recipe description
        category: Type of dish (entree, side, appetizer, etc.)
        serving_size: Number of servings
        prep_time: Preparation time in minutes
        cook_time: Cooking time in minutes
        instructions: Cooking instructions
        is_active: Whether recipe is currently in use
    """

    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    serving_size = Column(Integer)
    prep_time = Column(Integer)  # minutes
    cook_time = Column(Integer)  # minutes
    instructions = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    ingredients = relationship('RecipeIngredient', back_populates='recipe', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Recipe {self.name}>'

    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'serving_size': self.serving_size,
            'prep_time': self.prep_time,
            'cook_time': self.cook_time,
            'instructions': self.instructions,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class RecipeIngredient(db.Model):
    """
    Ingredients required for recipes.

    Attributes:
        id: Primary key
        recipe_id: Foreign key to Recipe
        ingredient_name: Name of ingredient
        quantity: Amount needed
        unit: Unit of measurement
        notes: Special preparation notes
    """

    __tablename__ = 'recipe_ingredients'

    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=False)
    ingredient_name = Column(String(200), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    notes = Column(Text)

    # Relationships
    recipe = relationship('Recipe', back_populates='ingredients')

    def __repr__(self):
        return f'<RecipeIngredient {self.quantity} {self.unit} {self.ingredient_name}>'

    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'recipe_id': self.recipe_id,
            'ingredient_name': self.ingredient_name,
            'quantity': self.quantity,
            'unit': self.unit,
            'notes': self.notes
        }


class CateringEvent(db.Model):
    """
    Catering events and quotes.

    Attributes:
        id: Primary key
        event_name: Name/description of event
        client_name: Client name
        client_contact: Client contact info
        event_date: Date of event
        guest_count: Number of guests
        total_quote: Total quoted price
        status: pending, confirmed, completed, cancelled
        notes: Additional notes
    """

    __tablename__ = 'catering_events'

    id = Column(Integer, primary_key=True)
    event_name = Column(String(300), nullable=False)
    client_name = Column(String(200), nullable=False)
    client_contact = Column(String(200))
    event_date = Column(DateTime, nullable=False)
    guest_count = Column(Integer)
    total_quote = Column(Float)
    status = Column(String(50), default='pending')
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<CateringEvent {self.event_name} - {self.event_date}>'

    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'event_name': self.event_name,
            'client_name': self.client_name,
            'client_contact': self.client_contact,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'guest_count': self.guest_count,
            'total_quote': self.total_quote,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


def init_db(app):
    """
    Initialize the database with the Flask app.

    Args:
        app: Flask application instance
    """
    db.init_app(app)

    with app.app_context():
        # Create all tables
        db.create_all()
        app.logger.info('Database tables created successfully')


def get_db():
    """
    Get the database instance.

    Returns:
        SQLAlchemy database instance
    """
    return db
