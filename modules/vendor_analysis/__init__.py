"""
Vendor Analysis Module
Handles vendor price comparison, invoice OCR, and savings identification
"""

from .comparator import VendorComparator
from .hybrid_matcher import HybridVendorMatcher, MatchResult, match_vendors_from_excel

try:
    from .invoice_processor import InvoiceProcessor
    __all__ = ['VendorComparator', 'HybridVendorMatcher', 'MatchResult',
               'match_vendors_from_excel', 'InvoiceProcessor']
except ImportError:
    # InvoiceProcessor not yet implemented
    __all__ = ['VendorComparator', 'HybridVendorMatcher', 'MatchResult',
               'match_vendors_from_excel']
