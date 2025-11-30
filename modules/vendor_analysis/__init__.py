"""
Vendor Analysis Module
Handles vendor price comparison, invoice OCR, and savings identification

Components:
- VendorComparator: Core price comparison logic
- InvoiceProcessor: Parse and process vendor invoices
- AccurateVendorMatcher: Match products between vendors with specification awareness
- CorrectedVendorComparison: Pack size parsing and unit conversion
- Models: Data structures for vendors, products, and price history
"""

from .comparator import VendorComparator
from .invoice_processor import InvoiceProcessor, Invoice, InvoiceLineItem
from .accurate_matcher import AccurateVendorMatcher, ProductMatch
from .corrected_comparison import CorrectedVendorComparison
from .models import (
    Vendor,
    VendorTier,
    Product,
    ProductCategory,
    VendorProduct,
    PriceHistory,
    PriceComparison,
    VendorDatabase
)

__all__ = [
    # Core comparison
    'VendorComparator',
    
    # Invoice processing
    'InvoiceProcessor',
    'Invoice',
    'InvoiceLineItem',
    
    # Product matching
    'AccurateVendorMatcher',
    'ProductMatch',
    
    # Price calculations
    'CorrectedVendorComparison',
    
    # Data models
    'Vendor',
    'VendorTier',
    'Product',
    'ProductCategory',
    'VendorProduct',
    'PriceHistory',
    'PriceComparison',
    'VendorDatabase',
]
