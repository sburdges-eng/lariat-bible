"""
Tests for Product Matcher Module
"""

import pytest
from modules.vendor_analysis.accurate_matcher import (
    AccurateVendorMatcher,
    ProductMatch,
    SPECIFICATION_KEYWORDS,
)
from modules.core.models import VendorProduct, ProductComparison, MatchConfidence


class TestProductMatch:
    """Tests for ProductMatch dataclass"""
    
    @pytest.fixture
    def sample_match(self):
        return ProductMatch(
            product_name="Black Pepper",
            specification="Fine Grind",
            sysco_code="SYS001",
            sysco_description="BLACK PEPPER FINE TABLE GRIND",
            sysco_pack="6/1LB",
            sysco_case_price=295.89,
            sysco_split_price=52.99,
            shamrock_code="SH001",
            shamrock_description="PEPPER BLACK FINE",
            shamrock_pack="25 LB",
            shamrock_price=95.88,
            notes="Test match"
        )
    
    def test_calculate_savings(self, sample_match):
        """Test savings calculation"""
        savings = sample_match.calculate_savings()
        
        assert "error" not in savings
        assert "product" in savings
        assert "sysco_per_lb" in savings
        assert "shamrock_per_lb" in savings
        assert "savings_per_lb" in savings
        assert "preferred_vendor" in savings
    
    def test_calculate_savings_with_split(self, sample_match):
        """Test savings calculation includes split pricing"""
        savings = sample_match.calculate_savings()
        
        assert "sysco_split_per_lb" in savings
        assert savings["sysco_split_per_lb"] > 0
    
    def test_parse_pounds_shamrock_format(self, sample_match):
        """Test parsing Shamrock format (1/6/LB)"""
        result = sample_match._parse_pounds("1/6/LB")
        assert result == 6.0
    
    def test_parse_pounds_sysco_format(self, sample_match):
        """Test parsing SYSCO format (6/1LB)"""
        result = sample_match._parse_pounds("6/1LB")
        assert result == 6.0
    
    def test_parse_pounds_simple(self, sample_match):
        """Test parsing simple format (25 LB)"""
        result = sample_match._parse_pounds("25 LB")
        assert result == 25.0


class TestAccurateVendorMatcher:
    """Tests for AccurateVendorMatcher class"""
    
    @pytest.fixture
    def matcher(self):
        return AccurateVendorMatcher()
    
    @pytest.fixture
    def sysco_products(self):
        return [
            VendorProduct(
                vendor="SYSCO",
                product_code="SYS001",
                product_name="BLACK PEPPER FINE",
                unit_size="6/1LB",
                unit_price=49.32,
                case_price=295.89,
                brand=None
            ),
            VendorProduct(
                vendor="SYSCO",
                product_code="SYS002",
                product_name="GARLIC POWDER",
                unit_size="3/6LB",
                unit_price=11.84,
                case_price=213.19,
                brand=None
            )
        ]
    
    @pytest.fixture
    def shamrock_products(self):
        return [
            VendorProduct(
                vendor="Shamrock",
                product_code="SH001",
                product_name="PEPPER BLACK FINE",
                unit_size="25 LB",
                unit_price=3.84,
                case_price=95.88,
                brand=None
            ),
            VendorProduct(
                vendor="Shamrock",
                product_code="SH002",
                product_name="GARLIC POWDER CALIFORNIA",
                unit_size="1/6/LB",
                unit_price=9.04,
                case_price=54.26,
                brand=None
            )
        ]
    
    def test_load_pepper_products(self, matcher):
        """Test loading pepper product matches"""
        products = matcher.load_pepper_products()
        
        assert len(products) > 0
        assert all(isinstance(p, ProductMatch) for p in products)
        assert all("Pepper" in p.product_name for p in products)
    
    def test_load_all_spice_matches(self, matcher):
        """Test loading all spice matches"""
        products = matcher.load_all_spice_matches()
        
        assert len(products) > 0
        # Should include peppers and other spices
        product_names = [p.product_name for p in products]
        assert "Black Pepper" in product_names
        assert "Garlic Powder" in product_names
    
    def test_fuzzy_match_products(self, matcher, sysco_products, shamrock_products):
        """Test fuzzy matching between vendors"""
        matched, sysco_only, shamrock_only = matcher.fuzzy_match_products(
            sysco_products,
            shamrock_products,
            min_confidence=0.5
        )
        
        # Should match the pepper and garlic products
        assert len(matched) >= 1
        assert all(isinstance(m, ProductComparison) for m in matched)
    
    def test_fuzzy_match_high_confidence(self, matcher, sysco_products, shamrock_products):
        """Test that higher confidence threshold reduces matches"""
        low_conf_matched, _, _ = matcher.fuzzy_match_products(
            sysco_products, shamrock_products, min_confidence=0.3
        )
        
        high_conf_matched, _, _ = matcher.fuzzy_match_products(
            sysco_products, shamrock_products, min_confidence=0.9
        )
        
        assert len(high_conf_matched) <= len(low_conf_matched)
    
    def test_calculate_match_score(self, matcher, sysco_products, shamrock_products):
        """Test match score calculation"""
        score = matcher._calculate_match_score(
            sysco_products[0],  # BLACK PEPPER FINE
            shamrock_products[0]  # PEPPER BLACK FINE
        )
        
        # Should be a reasonable match
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Similar products should score well
    
    def test_compare_specifications_same(self, matcher):
        """Test specification comparison for matching specs"""
        score = matcher._compare_specifications(
            "BLACK PEPPER FINE GRIND",
            "PEPPER BLACK FINE GROUND"
        )
        
        assert score >= 0.5  # Similar specifications
    
    def test_compare_specifications_different(self, matcher):
        """Test specification comparison for different specs"""
        score = matcher._compare_specifications(
            "BLACK PEPPER FINE",
            "BLACK PEPPER COARSE"
        )
        
        assert score < 1.0  # Different specifications
    
    def test_get_confidence_level_high(self, matcher):
        """Test high confidence level"""
        level = matcher.get_confidence_level(0.9)
        assert level == MatchConfidence.HIGH
    
    def test_get_confidence_level_medium(self, matcher):
        """Test medium confidence level"""
        level = matcher.get_confidence_level(0.75)
        assert level == MatchConfidence.MEDIUM
    
    def test_get_confidence_level_low(self, matcher):
        """Test low confidence level"""
        level = matcher.get_confidence_level(0.5)
        assert level == MatchConfidence.LOW
    
    def test_add_manual_match(self, matcher, sysco_products, shamrock_products):
        """Test adding manual match"""
        initial_count = len(matcher.matched_products)
        
        comparison = matcher.add_manual_match(
            sysco_products[0],
            shamrock_products[0],
            notes="Verified match"
        )
        
        assert comparison.confidence == 1.0
        assert len(matcher.matched_products) == initial_count + 1


class TestSpecificationKeywords:
    """Tests for specification keywords"""
    
    def test_grind_keywords(self):
        """Test grind keywords are defined"""
        assert 'grind' in SPECIFICATION_KEYWORDS
        grind_keywords = SPECIFICATION_KEYWORDS['grind']
        assert 'FINE' in grind_keywords
        assert 'COARSE' in grind_keywords
    
    def test_cut_keywords(self):
        """Test cut keywords are defined"""
        assert 'cut' in SPECIFICATION_KEYWORDS
        cut_keywords = SPECIFICATION_KEYWORDS['cut']
        assert 'DICED' in cut_keywords
        assert 'SLICED' in cut_keywords
    
    def test_form_keywords(self):
        """Test form keywords are defined"""
        assert 'form' in SPECIFICATION_KEYWORDS
        form_keywords = SPECIFICATION_KEYWORDS['form']
        assert 'POWDER' in form_keywords
        assert 'GRANULATED' in form_keywords
