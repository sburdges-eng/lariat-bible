"""
Kitchen Core Models
====================
Data models for recipe costing system.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum


class RecipeType(Enum):
    """Type of recipe"""
    COMPONENT = "component"      # Sub-recipe (bacon jam, dressing, sauce)
    MENU_ITEM = "menu_item"      # Final sellable item
    BATCH = "batch"              # Large batch prep
    MISE_EN_PLACE = "mise"       # Prep item


class MatchConfidence(Enum):
    """Confidence level of ingredient-to-vendor matching"""
    HIGH = "high"          # 90%+ confidence, auto-link
    MEDIUM = "medium"      # 70-90%, suggest for review
    LOW = "low"            # Below 70%, manual review required
    MANUAL = "manual"      # Manually linked by user
    UNMATCHED = "unmatched"


class Unit(Enum):
    """Standard units for ingredients"""
    # Weight
    OZ = "oz"
    LB = "lb"
    G = "g"
    KG = "kg"

    # Volume
    TSP = "tsp"
    TBSP = "tbsp"
    FL_OZ = "fl_oz"
    CUP = "cup"
    PINT = "pint"
    QUART = "quart"
    GALLON = "gallon"
    ML = "ml"
    LITER = "liter"

    # Count
    EACH = "each"
    DOZEN = "dozen"

    # Packaging
    CAN = "can"
    JAR = "jar"
    BAG = "bag"
    CASE = "case"
    BOX = "box"

    # Special
    BUNCH = "bunch"
    HEAD = "head"
    CLOVE = "clove"
    SLICE = "slice"
    PORTION = "portion"


@dataclass
class VendorProduct:
    """
    Product from a vendor (SYSCO, Shamrock, etc.)
    """
    id: str
    vendor: str                          # 'SYSCO', 'Shamrock', etc.
    item_code: str                        # Vendor's item/product code
    description: str                      # Product description
    pack_size: str                        # e.g., "6/5 LB", "1/CASE"
    unit: str                             # Unit of measure
    price: Decimal                        # Current price
    price_per_unit: Optional[Decimal] = None  # Calculated price per base unit
    category: Optional[str] = None
    brand: Optional[str] = None
    upc: Optional[str] = None
    last_updated: datetime = field(default_factory=datetime.now)
    is_active: bool = True

    def __post_init__(self):
        if isinstance(self.price, (int, float)):
            self.price = Decimal(str(self.price))
        if self.price_per_unit and isinstance(self.price_per_unit, (int, float)):
            self.price_per_unit = Decimal(str(self.price_per_unit))


@dataclass
class IngredientMatch:
    """
    Match between canonical ingredient and vendor product
    """
    ingredient_id: str
    vendor_product_id: str
    vendor: str
    confidence: MatchConfidence
    match_score: float                   # 0.0 to 1.0
    is_preferred: bool = False           # Is this the cheapest/preferred option?
    notes: Optional[str] = None
    matched_at: datetime = field(default_factory=datetime.now)
    matched_by: Optional[str] = None     # 'auto' or user name


@dataclass
class Ingredient:
    """
    Canonical ingredient in the ingredient library.
    Links to vendor products for pricing.
    """
    id: str
    name: str                            # Canonical name
    category: str                        # e.g., 'Protein', 'Produce', 'Dairy'
    default_unit: Unit                   # Standard unit for this ingredient

    # Vendor matches
    vendor_matches: List[IngredientMatch] = field(default_factory=list)

    # Cost info (from preferred vendor)
    current_cost_per_unit: Optional[Decimal] = None
    preferred_vendor: Optional[str] = None
    preferred_product_id: Optional[str] = None

    # Waste/yield factors
    waste_factor: float = 0.0            # 0.1 = 10% waste
    yield_factor: float = 1.0            # After cooking/prep

    # Metadata
    aliases: List[str] = field(default_factory=list)  # Alternative names
    notes: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.current_cost_per_unit and isinstance(self.current_cost_per_unit, (int, float)):
            self.current_cost_per_unit = Decimal(str(self.current_cost_per_unit))

    def get_cost(self) -> Decimal:
        """Get cost accounting for waste factor"""
        if not self.current_cost_per_unit:
            return Decimal('0')
        return self.current_cost_per_unit / Decimal(str(1 - self.waste_factor))

    def get_cheapest_match(self) -> Optional[IngredientMatch]:
        """Get the cheapest vendor match"""
        preferred = [m for m in self.vendor_matches if m.is_preferred]
        return preferred[0] if preferred else None


@dataclass
class RecipeIngredient:
    """
    Ingredient usage within a recipe
    """
    id: str
    recipe_id: str
    ingredient_id: str
    ingredient: Optional[Ingredient] = None  # Linked ingredient object

    # Quantity
    quantity: Decimal
    unit: Unit

    # Prep notes
    prep_notes: Optional[str] = None     # e.g., "diced", "julienned"

    # Calculated costs (filled in by cost calculator)
    unit_cost: Optional[Decimal] = None
    extended_cost: Optional[Decimal] = None  # quantity * unit_cost

    # For sub-recipes
    is_sub_recipe: bool = False
    sub_recipe_id: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.quantity, (int, float)):
            self.quantity = Decimal(str(self.quantity))
        if self.unit_cost and isinstance(self.unit_cost, (int, float)):
            self.unit_cost = Decimal(str(self.unit_cost))
        if self.extended_cost and isinstance(self.extended_cost, (int, float)):
            self.extended_cost = Decimal(str(self.extended_cost))


@dataclass
class Recipe:
    """
    Recipe with ingredients and costing
    """
    id: str
    name: str
    recipe_type: RecipeType
    category: Optional[str] = None       # e.g., 'Appetizers', 'Entrees', 'Sauces'

    # Ingredients
    ingredients: List[RecipeIngredient] = field(default_factory=list)

    # Yield
    yield_quantity: Decimal = Decimal('1')
    yield_unit: str = "portion"          # What the yield is measured in
    portions: int = 1                    # Number of portions this makes

    # Instructions
    instructions: Optional[str] = None
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None

    # Costing
    total_cost: Optional[Decimal] = None
    cost_per_portion: Optional[Decimal] = None
    target_food_cost_pct: Decimal = Decimal('0.28')  # 28% default
    suggested_price: Optional[Decimal] = None

    # Metadata
    source: Optional[str] = None         # 'Lariat Recipe Book', 'CSV', etc.
    notes: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_costed_at: Optional[datetime] = None

    def __post_init__(self):
        if isinstance(self.yield_quantity, (int, float)):
            self.yield_quantity = Decimal(str(self.yield_quantity))
        if isinstance(self.target_food_cost_pct, (int, float)):
            self.target_food_cost_pct = Decimal(str(self.target_food_cost_pct))

    def calculate_costs(self):
        """Calculate total and per-portion costs"""
        total = Decimal('0')
        for ing in self.ingredients:
            if ing.extended_cost:
                total += ing.extended_cost

        self.total_cost = total
        self.cost_per_portion = total / Decimal(str(self.portions)) if self.portions > 0 else Decimal('0')

        # Calculate suggested price based on target food cost %
        if self.cost_per_portion and self.target_food_cost_pct > 0:
            self.suggested_price = self.cost_per_portion / self.target_food_cost_pct

        self.last_costed_at = datetime.now()


@dataclass
class MenuItem:
    """
    Menu item that may use one or more recipes
    """
    id: str
    name: str
    description: Optional[str] = None
    category: str = "Entrees"            # Menu category

    # Linked recipes
    recipe_id: Optional[str] = None      # Main recipe
    recipe: Optional[Recipe] = None
    component_recipes: List[str] = field(default_factory=list)  # Additional component recipe IDs

    # Pricing
    menu_price: Optional[Decimal] = None
    total_food_cost: Optional[Decimal] = None
    food_cost_pct: Optional[Decimal] = None
    gross_profit: Optional[Decimal] = None

    # Sales data
    monthly_sales: int = 0
    popularity_score: float = 0.0

    # Metadata
    is_active: bool = True
    is_seasonal: bool = False
    available_start: Optional[datetime] = None
    available_end: Optional[datetime] = None

    def __post_init__(self):
        if self.menu_price and isinstance(self.menu_price, (int, float)):
            self.menu_price = Decimal(str(self.menu_price))

    def calculate_metrics(self):
        """Calculate food cost % and profit"""
        if self.menu_price and self.total_food_cost:
            self.food_cost_pct = self.total_food_cost / self.menu_price
            self.gross_profit = self.menu_price - self.total_food_cost


@dataclass
class CostSnapshot:
    """
    Historical snapshot of recipe/ingredient costs
    """
    id: str
    snapshot_date: datetime
    snapshot_type: str                   # 'recipe' or 'ingredient'

    # Reference
    recipe_id: Optional[str] = None
    ingredient_id: Optional[str] = None

    # Cost data
    cost: Decimal = Decimal('0')
    cost_per_portion: Optional[Decimal] = None

    # Vendor prices at snapshot time
    vendor_prices: Dict[str, Decimal] = field(default_factory=dict)

    # Variance from previous
    previous_cost: Optional[Decimal] = None
    variance: Optional[Decimal] = None
    variance_pct: Optional[Decimal] = None

    # Details
    ingredient_costs: Dict[str, Decimal] = field(default_factory=dict)
    notes: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.cost, (int, float)):
            self.cost = Decimal(str(self.cost))

    def calculate_variance(self, previous: Optional['CostSnapshot'] = None):
        """Calculate variance from previous snapshot"""
        if previous:
            self.previous_cost = previous.cost
            self.variance = self.cost - previous.cost
            if previous.cost > 0:
                self.variance_pct = self.variance / previous.cost


@dataclass
class CostingResult:
    """
    Result of costing a recipe
    """
    recipe_id: str
    recipe_name: str
    costed_at: datetime

    # Costs
    total_cost: Decimal
    cost_per_portion: Decimal
    portions: int

    # Pricing
    target_food_cost_pct: Decimal
    suggested_price: Decimal

    # Ingredient breakdown
    ingredient_costs: List[Dict[str, Any]] = field(default_factory=list)

    # Warnings
    warnings: List[str] = field(default_factory=list)
    uncosted_ingredients: List[str] = field(default_factory=list)

    # Snapshot
    snapshot: Optional[CostSnapshot] = None


# Type aliases for convenience
IngredientList = List[Ingredient]
RecipeList = List[Recipe]
VendorProductList = List[VendorProduct]
