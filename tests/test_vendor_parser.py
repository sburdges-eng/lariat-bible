"""
Tests for Vendor Parser Module
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import os

from modules.vendor_analysis.vendor_parser import (
    VendorParser,
    parse_sysco_file,
    parse_shamrock_file,
    MAJOR_BRANDS,
    STOPWORDS,
)
from modules.core.models import VendorProduct, Vendor


class TestVendorParser:
    """Tests for VendorParser class"""
    
    @pytest.fixture
    def parser(self):
        return VendorParser()
    
    @pytest.fixture
    def sample_sysco_file(self, tmp_path):
        """Create a sample SYSCO Excel file for testing"""
        data = {
            'Item Number': ['SYS001', 'SYS002', 'SYS003'],
            'Description': [
                'BLACK PEPPER FINE TABLE GRIND',
                'HEINZ KETCHUP FANCY',
                'GARLIC POWDER CALIFORNIA'
            ],
            'Pack Size': ['6/1LB', '6/#10', '3/6LB'],
            'Case Price': [295.89, 45.99, 213.19],
            'Split Price': [52.99, None, 78.25],
            'Category': ['SPICES', 'CONDIMENTS', 'SPICES']
        }
        df = pd.DataFrame(data)
        file_path = tmp_path / 'sysco_test.xlsx'
        df.to_excel(file_path, index=False)
        return str(file_path)
    
    @pytest.fixture
    def sample_shamrock_file(self, tmp_path):
        """Create a sample Shamrock Excel file for testing"""
        data = {
            'Item Number': ['SH001', 'SH002', 'SH003'],
            'Description': [
                'PEPPER BLACK FINE',
                'KETCHUP HEINZ',
                'GARLIC POWDER'
            ],
            'Pack': ['25 LB', '6/#10', '1/6/LB'],
            'Price': [95.88, 42.50, 54.26],
            'Category': ['SPICES', 'CONDIMENTS', 'SPICES']
        }
        df = pd.DataFrame(data)
        file_path = tmp_path / 'shamrock_test.xlsx'
        df.to_excel(file_path, index=False)
        return str(file_path)
    
    def test_parse_sysco(self, parser, sample_sysco_file):
        """Test parsing SYSCO spreadsheet"""
        products = parser.parse_sysco(sample_sysco_file)
        
        assert len(products) == 3
        assert all(isinstance(p, VendorProduct) for p in products)
        assert all(p.vendor == Vendor.SYSCO.value for p in products)
    
    def test_parse_shamrock(self, parser, sample_shamrock_file):
        """Test parsing Shamrock spreadsheet"""
        products = parser.parse_shamrock(sample_shamrock_file)
        
        assert len(products) == 3
        assert all(isinstance(p, VendorProduct) for p in products)
        assert all(p.vendor == Vendor.SHAMROCK.value for p in products)
    
    def test_parse_file_sysco(self, parser, sample_sysco_file):
        """Test parse_file with SYSCO vendor"""
        products = parser.parse_file(sample_sysco_file, 'SYSCO')
        assert len(products) == 3
    
    def test_parse_file_shamrock(self, parser, sample_shamrock_file):
        """Test parse_file with Shamrock vendor"""
        products = parser.parse_file(sample_shamrock_file, 'Shamrock')
        assert len(products) == 3
    
    def test_parse_file_invalid_vendor(self, parser, sample_sysco_file):
        """Test parse_file with invalid vendor raises error"""
        with pytest.raises(ValueError, match="Unsupported vendor"):
            parser.parse_file(sample_sysco_file, 'InvalidVendor')
    
    def test_file_not_found(self, parser):
        """Test parsing non-existent file raises error"""
        with pytest.raises(FileNotFoundError):
            parser.parse_sysco('/nonexistent/file.xlsx')
    
    def test_normalize_product_name(self, parser):
        """Test product name normalization"""
        # Test removing stopwords
        name = "BLACK PEPPER AND SPICE IN THE BOX"
        normalized = parser.normalize_product_name(name)
        
        assert "AND" not in normalized.split()
        assert "THE" not in normalized.split()
        assert "IN" not in normalized.split()
        assert "BLACK" in normalized
        assert "PEPPER" in normalized
    
    def test_extract_brand(self, parser):
        """Test brand extraction from description"""
        # Test HEINZ brand extraction
        brand = parser._extract_brand("HEINZ KETCHUP FANCY")
        assert brand == "HEINZ"
        
        # Test no brand
        brand = parser._extract_brand("BLACK PEPPER FINE")
        assert brand is None
    
    def test_products_by_vendor(self, parser, sample_sysco_file, sample_shamrock_file):
        """Test getting products by vendor"""
        parser.parse_sysco(sample_sysco_file)
        parser.parse_shamrock(sample_shamrock_file)
        
        sysco_products = parser.get_products_by_vendor('SYSCO')
        shamrock_products = parser.get_products_by_vendor('SHAMROCK')
        
        assert len(sysco_products) == 3
        assert len(shamrock_products) == 3
    
    def test_clear(self, parser, sample_sysco_file):
        """Test clearing parsed products"""
        parser.parse_sysco(sample_sysco_file)
        assert len(parser.products) > 0
        
        parser.clear()
        assert len(parser.products) == 0


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    @pytest.fixture
    def sample_file(self, tmp_path):
        """Create a sample Excel file"""
        data = {
            'Item Number': ['001', '002'],
            'Description': ['TEST ITEM 1', 'TEST ITEM 2'],
            'Pack Size': ['6/1LB', '25 LB'],
            'Case Price': [100.00, 50.00],
            'Category': ['TEST', 'TEST']
        }
        df = pd.DataFrame(data)
        file_path = tmp_path / 'test.xlsx'
        df.to_excel(file_path, index=False)
        return str(file_path)
    
    def test_parse_sysco_file_function(self, sample_file):
        """Test parse_sysco_file convenience function"""
        products = parse_sysco_file(sample_file)
        assert len(products) == 2
    
    def test_parse_shamrock_file_function(self, sample_file):
        """Test parse_shamrock_file convenience function"""
        products = parse_shamrock_file(sample_file)
        assert len(products) == 2


class TestMajorBrands:
    """Test major brands list"""
    
    def test_brands_uppercase(self):
        """Verify all brands are uppercase"""
        for brand in MAJOR_BRANDS:
            assert brand == brand.upper()
    
    def test_common_brands_included(self):
        """Verify common brands are included"""
        expected_brands = ['HEINZ', 'KRAFT', 'TYSON', 'PEPSI']
        for brand in expected_brands:
            assert brand in MAJOR_BRANDS


class TestStopwords:
    """Test stopwords set"""
    
    def test_stopwords_uppercase(self):
        """Verify all stopwords are uppercase"""
        for word in STOPWORDS:
            assert word == word.upper()
    
    def test_common_stopwords_included(self):
        """Verify common stopwords are included"""
        expected_words = ['AND', 'THE', 'OF', 'LB', 'OZ', 'CASE']
        for word in expected_words:
            assert word in STOPWORDS
