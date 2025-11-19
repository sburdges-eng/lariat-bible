"""
Vendor Analysis Module
Handles vendor price comparison, invoice OCR, and savings identification

Key Components:
- HybridVendorMatcher: Fuzzy matching with domain validation (RECOMMENDED)
- AccurateVendorMatcher: Manual product specification matching
- CorrectedVendorComparison: Pack size parsing and unit price calculations
- VendorComparator: High-level vendor comparison and reporting
- InvoiceProcessor: Invoice OCR and data extraction
"""

from .comparator import VendorComparator
from .invoice_processor import InvoiceProcessor
from .hybrid_matcher import HybridVendorMatcher, FuzzyMatch
from .accurate_matcher import AccurateVendorMatcher, ProductMatch
from .corrected_comparison import CorrectedVendorComparison

__all__ = [
    'VendorComparator',
    'InvoiceProcessor',
    'HybridVendorMatcher',
    'FuzzyMatch',
    'AccurateVendorMatcher',
    'ProductMatch',
    'CorrectedVendorComparison'
]
