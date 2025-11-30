"""
Core Data Models for The Lariat Bible
Defines dataclasses for vendor products, matching, and BEO data
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum


class Vendor(str, Enum):
    """Supported vendor types"""
    SYSCO = "SYSCO"
    SHAMROCK = "Shamrock"


class MatchConfidence(str, Enum):
    """Confidence levels for product matching"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class VendorProduct:
    """
    Represents a product from a vendor's catalog/invoice

    Attributes:
        vendor: Vendor name ("SYSCO" or "Shamrock")
        product_code: Vendor's internal product code
        product_name: Product name/description
        brand: Optional brand name
        unit_size: Size description (e.g., "6/1LB", "25 LB")
        unit_price: Price per unit
        case_price: Price per case
        case_quantity: Number of units per case
        category: Optional product category
    """
    vendor: str
    product_code: str
    product_name: str
    unit_size: str
    unit_price: float
    case_price: float
    case_quantity: int = 1
    brand: Optional[str] = None
    category: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'vendor': self.vendor,
            'product_code': self.product_code,
            'product_name': self.product_name,
            'brand': self.brand,
            'unit_size': self.unit_size,
            'unit_price': self.unit_price,
            'case_price': self.case_price,
            'case_quantity': self.case_quantity,
            'category': self.category
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'VendorProduct':
        """Create from dictionary"""
        return cls(
            vendor=data.get('vendor', ''),
            product_code=data.get('product_code', ''),
            product_name=data.get('product_name', ''),
            brand=data.get('brand'),
            unit_size=data.get('unit_size', ''),
            unit_price=float(data.get('unit_price', 0)),
            case_price=float(data.get('case_price', 0)),
            case_quantity=int(data.get('case_quantity', 1)),
            category=data.get('category')
        )


@dataclass
class ProductComparison:
    """
    Represents a comparison between two vendor products

    Attributes:
        sysco_product: Product from SYSCO
        shamrock_product: Product from Shamrock
        confidence: Match confidence score (0.0 to 1.0)
        price_difference: Price difference (positive = Shamrock cheaper)
        recommendation: Recommended vendor
    """
    sysco_product: VendorProduct
    shamrock_product: VendorProduct
    confidence: float
    price_difference: float
    recommendation: str

    @property
    def savings_percent(self) -> float:
        """Calculate savings percentage"""
        if self.sysco_product.unit_price > 0:
            return (self.price_difference / self.sysco_product.unit_price) * 100
        return 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'sysco_product': self.sysco_product.to_dict(),
            'shamrock_product': self.shamrock_product.to_dict(),
            'confidence': self.confidence,
            'price_difference': self.price_difference,
            'savings_percent': self.savings_percent,
            'recommendation': self.recommendation
        }


@dataclass
class MenuItem:
    """
    Represents a menu item for catering events

    Attributes:
        name: Menu item name
        quantity: Number of servings
        unit_price: Price per serving
        ingredients: List of ingredient quantities
    """
    name: str
    quantity: int = 1
    unit_price: float = 0.0
    ingredients: List['IngredientQuantity'] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'ingredients': [i.to_dict() for i in self.ingredients]
        }


@dataclass
class IngredientQuantity:
    """
    Represents an ingredient with quantity

    Attributes:
        ingredient_name: Name of the ingredient
        quantity: Amount needed
        unit: Unit of measurement
        vendor_product: Optional linked vendor product
    """
    ingredient_name: str
    quantity: float
    unit: str
    vendor_product: Optional[VendorProduct] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'ingredient_name': self.ingredient_name,
            'quantity': self.quantity,
            'unit': self.unit,
            'vendor_product': self.vendor_product.to_dict() if self.vendor_product else None
        }


@dataclass
class BanquetEvent:
    """
    Represents a banquet/catering event from BEO

    Attributes:
        event_id: Unique event identifier
        client_name: Client/customer name
        event_date: Date and time of event
        guest_count: Expected number of guests
        menu_items: List of menu items
        ingredients_needed: Calculated ingredient quantities
        notes: Additional notes
    """
    event_id: str
    client_name: str
    event_date: datetime
    guest_count: int
    menu_items: List[MenuItem] = field(default_factory=list)
    ingredients_needed: List[IngredientQuantity] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'event_id': self.event_id,
            'client_name': self.client_name,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'guest_count': self.guest_count,
            'menu_items': [m.to_dict() for m in self.menu_items],
            'ingredients_needed': [i.to_dict() for i in self.ingredients_needed],
            'notes': self.notes
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'BanquetEvent':
        """Create from dictionary"""
        event_date = data.get('event_date')
        if isinstance(event_date, str):
            event_date = datetime.fromisoformat(event_date)

        return cls(
            event_id=data.get('event_id', ''),
            client_name=data.get('client_name', ''),
            event_date=event_date or datetime.now(),
            guest_count=int(data.get('guest_count', 0)),
            notes=data.get('notes', '')
        )


@dataclass
class SavingsSummary:
    """
    Summary of vendor comparison savings

    Attributes:
        total_sysco_cost: Total cost if buying all from SYSCO
        total_shamrock_cost: Total cost if buying all from Shamrock
        total_savings: Total savings from optimal purchasing
        monthly_savings: Estimated monthly savings
        annual_savings: Estimated annual savings
        products_cheaper_sysco: Count of products cheaper at SYSCO
        products_cheaper_shamrock: Count of products cheaper at Shamrock
        products_equal: Count of products with equal pricing
    """
    total_sysco_cost: float = 0.0
    total_shamrock_cost: float = 0.0
    total_savings: float = 0.0
    monthly_savings: float = 0.0
    annual_savings: float = 0.0
    products_cheaper_sysco: int = 0
    products_cheaper_shamrock: int = 0
    products_equal: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'total_sysco_cost': self.total_sysco_cost,
            'total_shamrock_cost': self.total_shamrock_cost,
            'total_savings': self.total_savings,
            'monthly_savings': self.monthly_savings,
            'annual_savings': self.annual_savings,
            'products_cheaper_sysco': self.products_cheaper_sysco,
            'products_cheaper_shamrock': self.products_cheaper_shamrock,
            'products_equal': self.products_equal
        }
