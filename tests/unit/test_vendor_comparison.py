"""
P0 CRITICAL: Tests for vendor comparison and savings calculations
These tests protect the $52k annual savings business case
"""

import pytest
from modules.vendor_analysis.accurate_matcher import ProductMatch, AccurateVendorMatcher
from modules.vendor_analysis.comparator import VendorComparator


@pytest.mark.critical
class TestProductMatchSavings:
    """Test ProductMatch savings calculations"""

    def test_calculate_savings_basic(self, sample_product_match):
        """Test basic savings calculation for matched products"""
        result = sample_product_match.calculate_savings()

        assert 'product' in result
        assert 'sysco_per_lb' in result
        assert 'shamrock_per_lb' in result
        assert 'savings_per_lb' in result
        assert 'savings_percent' in result
        assert 'preferred_vendor' in result

    def test_calculate_savings_pepper_example(self):
        """Test real black pepper savings calculation"""
        pepper_match = ProductMatch(
            product_name="Black Pepper",
            specification="Coarse Grind",
            sysco_code="SYSCO_COARSE",
            sysco_description="BLACK PEPPER COARSE",
            sysco_pack="6/1LB",
            sysco_case_price=298.95,
            sysco_split_price=None,
            shamrock_code="SHAM_COARSE",
            shamrock_description="PEPPER BLACK COARSE GRIND",
            shamrock_pack="25 LB",
            shamrock_price=79.71
        )

        result = pepper_match.calculate_savings()

        # SYSCO: $298.95 / 6 lbs = $49.825/lb
        # Shamrock: $79.71 / 25 lbs = $3.19/lb
        # Savings: $46.635/lb
        assert abs(result['sysco_per_lb'] - 49.825) < 0.01
        assert abs(result['shamrock_per_lb'] - 3.19) < 0.02
        assert abs(result['savings_per_lb'] - 46.635) < 0.02
        assert result['preferred_vendor'] == 'Shamrock'
        assert result['savings_percent'] > 90

    def test_calculate_savings_garlic_powder(self):
        """Test garlic powder savings calculation"""
        garlic_match = ProductMatch(
            product_name="Garlic Powder",
            specification="Powder",
            sysco_code="SYSCO_GARLIC",
            sysco_description="GARLIC POWDER",
            sysco_pack="3/6LB",
            sysco_case_price=213.19,
            sysco_split_price=78.25,
            shamrock_code="SHAM_GARLIC",
            shamrock_description="GARLIC POWDER CALIFORNIA",
            shamrock_pack="1/6/LB",  # Shamrock format: 1 × 6 lbs
            shamrock_price=54.26
        )

        result = garlic_match.calculate_savings()

        # SYSCO: $213.19 / 18 lbs = $11.84/lb
        # Shamrock: $54.26 / 6 lbs = $9.04/lb
        assert abs(result['sysco_per_lb'] - 11.84) < 0.02
        assert abs(result['shamrock_per_lb'] - 9.04) < 0.02
        assert result['preferred_vendor'] == 'Shamrock'
        assert result['savings_per_lb'] > 0

    def test_calculate_savings_with_split_pricing(self):
        """Test savings calculation including SYSCO split pricing"""
        product = ProductMatch(
            product_name="Garlic Powder",
            specification="Powder",
            sysco_code="SYSCO_GARLIC",
            sysco_description="GARLIC POWDER",
            sysco_pack="3/6LB",
            sysco_case_price=213.19,
            sysco_split_price=78.25,  # Price per container
            shamrock_code="SHAM_GARLIC",
            shamrock_description="GARLIC POWDER",
            shamrock_pack="1/6/LB",
            shamrock_price=54.26
        )

        result = product.calculate_savings()

        # Should include split pricing comparison
        assert 'sysco_split_per_lb' in result
        assert 'split_vs_shamrock' in result

        # Split: $78.25 per 6-lb container = $13.04/lb
        expected_split_per_lb = 78.25 / 6.0
        assert abs(result['sysco_split_per_lb'] - expected_split_per_lb) < 0.02

    def test_preferred_vendor_sysco_when_cheaper(self):
        """Test that SYSCO is preferred when it has better pricing"""
        product = ProductMatch(
            product_name="Test Product",
            specification="Standard",
            sysco_code="SYS001",
            sysco_description="TEST ITEM",
            sysco_pack="25 LB",
            sysco_case_price=50.0,  # $2/lb
            sysco_split_price=None,
            shamrock_code="SHA001",
            shamrock_description="TEST ITEM",
            shamrock_pack="25 LB",
            shamrock_price=75.0  # $3/lb - more expensive
        )

        result = product.calculate_savings()
        assert result['preferred_vendor'] == 'SYSCO'
        assert result['savings_per_lb'] < 0  # Negative savings = SYSCO cheaper

    def test_parse_pounds_shamrock_format(self):
        """Test parsing of Shamrock-specific pack format (1/6/LB)"""
        product = ProductMatch(
            product_name="Test",
            specification="Test",
            sysco_code="SYS001",
            sysco_description="TEST",
            sysco_pack="25 LB",
            sysco_case_price=100.0,
            sysco_split_price=None,
            shamrock_code="SHA001",
            shamrock_description="TEST",
            shamrock_pack="1/6/LB",  # 1 container × 6 lbs
            shamrock_price=30.0
        )

        result = product.calculate_savings()

        # Should parse 1/6/LB as 6 lbs total
        # $30 / 6 lbs = $5/lb
        assert abs(result['shamrock_per_lb'] - 5.0) < 0.01

    def test_parse_pounds_unparseable(self):
        """Test handling of unparseable pack sizes"""
        product = ProductMatch(
            product_name="Test",
            specification="Test",
            sysco_code="SYS001",
            sysco_description="TEST",
            sysco_pack="UNKNOWN FORMAT",
            sysco_case_price=100.0,
            sysco_split_price=None,
            shamrock_code="SHA001",
            shamrock_description="TEST",
            shamrock_pack="UNKNOWN",
            shamrock_price=50.0
        )

        result = product.calculate_savings()
        assert 'error' in result


@pytest.mark.critical
class TestVendorComparator:
    """Test VendorComparator class for overall savings analysis"""

    def test_compare_vendors_shamrock_vs_sysco(self):
        """Test comparison between Shamrock and SYSCO"""
        comparator = VendorComparator()
        savings = comparator.compare_vendors('Shamrock Foods', 'SYSCO')

        # Should calculate monthly savings based on 29.5% discount
        # Estimated monthly food cost: $8000
        # Expected savings: $8000 × 0.295 = $2360
        assert savings > 0
        assert len(comparator.comparison_results) > 0

        # Check the comparison result structure
        result = comparator.comparison_results[0]
        assert result['primary_vendor'] == 'Shamrock Foods'
        assert result['comparison_vendor'] == 'SYSCO'
        assert result['percentage_difference'] == 29.5
        assert result['annual_savings'] == savings * 12

    def test_compare_vendors_reverse_order_returns_zero(self):
        """Test that reverse comparison returns 0 (not implemented)"""
        comparator = VendorComparator()
        savings = comparator.compare_vendors('SYSCO', 'Shamrock Foods')
        assert savings == 0.0

    def test_analyze_category_with_items(self):
        """Test category analysis with item list"""
        comparator = VendorComparator()
        items = [
            {
                'name': 'Black Pepper',
                'shamrock_price': 79.71,
                'sysco_price': 298.95
            },
            {
                'name': 'Garlic Powder',
                'shamrock_price': 54.26,
                'sysco_price': 213.19
            }
        ]

        result = comparator.analyze_category('Spices', items)

        assert result['category'] == 'Spices'
        assert result['shamrock_total'] == 79.71 + 54.26
        assert result['sysco_total'] == 298.95 + 213.19
        assert result['savings'] == result['sysco_total'] - result['shamrock_total']
        assert result['percentage_saved'] > 0
        assert result['recommendation'] == 'Use Shamrock Foods'

    def test_identify_top_savings_sorted_correctly(self):
        """Test that top savings are sorted by savings amount"""
        comparator = VendorComparator()
        products = [
            {
                'name': 'Item A',
                'shamrock_price': 10.0,
                'sysco_price': 50.0  # $40 savings
            },
            {
                'name': 'Item B',
                'shamrock_price': 5.0,
                'sysco_price': 10.0  # $5 savings
            },
            {
                'name': 'Item C',
                'shamrock_price': 20.0,
                'sysco_price': 50.0  # $30 savings
            }
        ]

        top_items = comparator.identify_top_savings(products, top_n=2)

        # Should return top 2, sorted by savings
        assert len(top_items) == 2
        assert top_items[0]['name'] == 'Item A'  # $40 savings
        assert top_items[1]['name'] == 'Item C'  # $30 savings
        assert top_items[0]['savings'] == 40.0

    def test_calculate_margin_impact(self):
        """Test margin impact calculation from savings"""
        comparator = VendorComparator()
        monthly_savings = 4333.0

        impact = comparator.calculate_margin_impact(monthly_savings)

        assert 'catering' in impact
        assert 'restaurant' in impact

        # Catering gets 60% of savings
        assert impact['catering']['monthly_impact'] == monthly_savings * 0.6

        # Restaurant gets 40% of savings
        assert impact['restaurant']['monthly_impact'] == monthly_savings * 0.4

        # Margins should increase
        assert impact['catering']['margin_increase'] > 0
        assert impact['restaurant']['margin_increase'] > 0

        # New margins should be higher than current
        assert impact['catering']['new_margin'] > impact['catering']['current_margin']
        assert impact['restaurant']['new_margin'] > impact['restaurant']['current_margin']

    def test_generate_report_structure(self):
        """Test that report generation produces correct structure"""
        comparator = VendorComparator()
        report = comparator.generate_report()

        # Should contain key sections
        assert "THE LARIAT - VENDOR ANALYSIS REPORT" in report
        assert "EXECUTIVE SUMMARY" in report
        assert "KEY FINDINGS" in report
        assert "RECOMMENDATIONS" in report
        assert "$52,000" in report  # Annual savings


@pytest.mark.critical
class TestAccurateVendorMatcher:
    """Test AccurateVendorMatcher for product matching"""

    def test_load_pepper_products(self):
        """Test loading pepper product variations"""
        matcher = AccurateVendorMatcher()
        pepper_matches = matcher.load_pepper_products()

        assert len(pepper_matches) > 0

        # Should have different specifications
        specifications = [m.specification for m in pepper_matches]
        assert "Fine/Table Grind" in specifications or \
               "Restaurant/Medium Grind" in specifications or \
               "Coarse Grind" in specifications

    def test_load_all_spice_matches(self):
        """Test loading all spice matches"""
        matcher = AccurateVendorMatcher()
        all_matches = matcher.load_all_spice_matches()

        assert len(all_matches) > 0

        # Should include various spices
        product_names = [m.product_name for m in all_matches]
        assert "Black Pepper" in product_names or "Garlic Powder" in product_names

    def test_generate_comparison_report_returns_dataframe(self):
        """Test that comparison report generates a DataFrame"""
        matcher = AccurateVendorMatcher()
        df = matcher.generate_comparison_report()

        # Should return a DataFrame
        assert df is not None
        assert len(df) > 0

        # Should have required columns
        expected_columns = ['product', 'sysco_per_lb', 'shamrock_per_lb',
                          'savings_per_lb', 'savings_percent', 'preferred_vendor']
        for col in expected_columns:
            assert col in df.columns

    def test_different_specifications_not_confused(self):
        """
        CRITICAL: Verify that different specifications aren't treated as same product
        Fine pepper ≠ Coarse pepper (different uses)
        """
        matcher = AccurateVendorMatcher()
        pepper_matches = matcher.load_pepper_products()

        # Get all specifications
        specs = [m.specification for m in pepper_matches]

        # Should have multiple different specifications
        unique_specs = set(specs)
        assert len(unique_specs) > 1, \
            "Different pepper grinds should be tracked separately"

        # Each should have its own pricing
        for match in pepper_matches:
            result = match.calculate_savings()
            if 'error' not in result:
                assert 'specification' in match.specification or \
                       match.specification != "", \
                       "Each product should have a specification"
