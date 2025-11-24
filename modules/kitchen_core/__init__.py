"""
Kitchen Core Module
====================
Complete recipe costing system for The Lariat.

Features:
- Recipe and RecipeIngredient models
- Canonical ingredient library with vendor linking
- Unit conversions (oz, lb, cup, each, can, gallon, etc.)
- Yield and waste factors
- Cost per recipe and cost per portion
- Cost snapshots for historical tracking
- MenuItem support (components vs final items)
- Export formats (CSV, costing sheets)
"""

from .models import (
    Ingredient,
    VendorProduct,
    Recipe,
    RecipeIngredient,
    MenuItem,
    CostSnapshot,
    IngredientMatch
)
from .unit_converter import UnitConverter
from .cost_calculator import CostCalculator
from .recipe_parser import RecipeParser
from .costing_engine import CostingEngine
from .export import CostingExporter

__all__ = [
    # Models
    'Ingredient',
    'VendorProduct',
    'Recipe',
    'RecipeIngredient',
    'MenuItem',
    'CostSnapshot',
    'IngredientMatch',
    # Services
    'UnitConverter',
    'CostCalculator',
    'RecipeParser',
    'CostingEngine',
    'CostingExporter'
]
