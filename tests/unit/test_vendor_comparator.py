"""
Unit tests for VendorComparator
Tests core business logic for vendor price comparison and savings analysis
"""

import pytest
from datetime import datetime
from modules.vendor_analysis.comparator import VendorComparator


class TestVendorComparatorInitialization:
    """Tests for VendorComparator initialization"""

    def test_initialization(self, vendor_comparator):
        """Test that VendorComparator initializes correctly"""
        assert vendor_comparator is not None
        assert 'Shamrock Foods' in vendor_comparator.vendors
        assert 'SYSCO' in vendor_comparator.vendors
        assert vendor_comparator.comparison_results == []

    def test_vendor_discount_rates(self, vendor_comparator):
        """Test that vendor discount rates are set correctly"""
        assert vendor_comparator.vendors['Shamrock Foods']['discount'] == 0.295
        assert vendor_comparator.vendors['SYSCO']['discount'] == 0.0


class TestCompareVendors:
    """Tests for the compare_vendors method"""

    def test_shamrock_vs_sysco_comparison(self, vendor_comparator):
        """Test basic Shamrock vs SYSCO comparison"""
        monthly_savings = vendor_comparator.compare_vendors('Shamrock Foods', 'SYSCO')

        # Expected: $8000 × 0.295 = $2,360
        assert monthly_savings == 2360.0
        assert len(vendor_comparator.comparison_results) == 1

    def test_comparison_result_structure(self, vendor_comparator):
        """Test that comparison result has correct structure"""
        vendor_comparator.compare_vendors('Shamrock Foods', 'SYSCO')
        result = vendor_comparator.comparison_results[0]

        assert 'comparison_date' in result
        assert 'primary_vendor' in result
        assert 'comparison_vendor' in result
        assert 'monthly_savings' in result
        assert 'annual_savings' in result
        assert 'percentage_difference' in result

    def test_comparison_result_values(self, vendor_comparator):
        """Test that comparison result values are correct"""
        vendor_comparator.compare_vendors('Shamrock Foods', 'SYSCO')
        result = vendor_comparator.comparison_results[0]

        assert result['primary_vendor'] == 'Shamrock Foods'
        assert result['comparison_vendor'] == 'SYSCO'
        assert result['monthly_savings'] == 2360.0
        assert result['annual_savings'] == 28320.0  # 2360 × 12
        assert result['percentage_difference'] == 29.5

    def test_multiple_comparisons(self, vendor_comparator):
        """Test that multiple comparisons are stored"""
        vendor_comparator.compare_vendors('Shamrock Foods', 'SYSCO')
        vendor_comparator.compare_vendors('Shamrock Foods', 'SYSCO')

        assert len(vendor_comparator.comparison_results) == 2

    def test_comparison_date_is_set(self, vendor_comparator):
        """Test that comparison date is set and is ISO format"""
        vendor_comparator.compare_vendors('Shamrock Foods', 'SYSCO')
        result = vendor_comparator.comparison_results[0]

        # Should be able to parse the ISO date
        comparison_date = datetime.fromisoformat(result['comparison_date'])
        assert comparison_date is not None

    def test_reverse_comparison_returns_zero(self, vendor_comparator):
        """Test that SYSCO vs Shamrock returns 0 (not implemented)"""
        monthly_savings = vendor_comparator.compare_vendors('SYSCO', 'Shamrock Foods')

        assert monthly_savings == 0.0

    def test_unknown_vendors_return_zero(self, vendor_comparator):
        """Test that unknown vendor combinations return 0"""
        monthly_savings = vendor_comparator.compare_vendors('Unknown Vendor', 'SYSCO')

        assert monthly_savings == 0.0


class TestAnalyzeCategory:
    """Tests for category-level price analysis"""

    def test_category_analysis_shamrock_cheaper(self, vendor_comparator, sample_products_for_comparison):
        """Test category analysis when Shamrock is cheaper"""
        spice_items = [p for p in sample_products_for_comparison if p['category'] == 'Spice']

        result = vendor_comparator.analyze_category('Spice', spice_items)

        assert result['category'] == 'Spice'
        assert result['shamrock_total'] < result['sysco_total']
        assert result['savings'] > 0
        assert result['percentage_saved'] > 0
        assert result['recommendation'] == 'Use Shamrock Foods'

    def test_category_analysis_calculations(self, vendor_comparator):
        """Test category analysis calculation accuracy"""
        items = [
            {'shamrock_price': 50.00, 'sysco_price': 100.00},
            {'shamrock_price': 30.00, 'sysco_price': 60.00},
            {'shamrock_price': 20.00, 'sysco_price': 40.00}
        ]

        result = vendor_comparator.analyze_category('Test Category', items)

        assert result['shamrock_total'] == 100.00  # 50 + 30 + 20
        assert result['sysco_total'] == 200.00     # 100 + 60 + 40
        assert result['savings'] == 100.00
        assert result['percentage_saved'] == 50.0

    def test_category_analysis_empty_items(self, vendor_comparator):
        """Test category analysis with no items"""
        result = vendor_comparator.analyze_category('Empty Category', [])

        assert result['shamrock_total'] == 0
        assert result['sysco_total'] == 0
        assert result['savings'] == 0
        assert result['percentage_saved'] == 0

    def test_category_analysis_sysco_cheaper(self, vendor_comparator):
        """Test category analysis when SYSCO is cheaper"""
        items = [
            {'shamrock_price': 100.00, 'sysco_price': 50.00}
        ]

        result = vendor_comparator.analyze_category('Test', items)

        assert result['savings'] < 0
        assert result['recommendation'] == 'Review individually'

    def test_category_analysis_missing_prices(self, vendor_comparator):
        """Test category analysis with missing prices (uses 0 default)"""
        items = [
            {'shamrock_price': 50.00},  # Missing sysco_price
            {'sysco_price': 100.00}      # Missing shamrock_price
        ]

        result = vendor_comparator.analyze_category('Test', items)

        assert result['shamrock_total'] == 50.00
        assert result['sysco_total'] == 100.00

    def test_category_zero_sysco_total(self, vendor_comparator):
        """Test percentage calculation when SYSCO total is 0"""
        items = [
            {'shamrock_price': 50.00, 'sysco_price': 0.00}
        ]

        result = vendor_comparator.analyze_category('Test', items)

        # Should handle division by zero
        assert result['percentage_saved'] == 0


class TestIdentifyTopSavings:
    """Tests for identifying products with highest savings potential"""

    def test_identify_top_savings(self, vendor_comparator, sample_products_for_comparison):
        """Test identifying top savings opportunities"""
        top_items = vendor_comparator.identify_top_savings(sample_products_for_comparison, top_n=2)

        assert len(top_items) == 2
        # Should be sorted by savings amount (descending)
        assert top_items[0]['savings'] >= top_items[1]['savings']

    def test_savings_calculation(self, vendor_comparator):
        """Test that savings are calculated correctly"""
        products = [
            {'name': 'Item A', 'shamrock_price': 50.00, 'sysco_price': 100.00},
            {'name': 'Item B', 'shamrock_price': 30.00, 'sysco_price': 50.00}
        ]

        top_items = vendor_comparator.identify_top_savings(products)

        # Item A: 100 - 50 = 50 savings
        assert top_items[0]['savings'] == 50.00
        # Item B: 50 - 30 = 20 savings
        assert top_items[1]['savings'] == 20.00

    def test_savings_percent_calculation(self, vendor_comparator):
        """Test that savings percentage is calculated"""
        products = [
            {'name': 'Item A', 'shamrock_price': 50.00, 'sysco_price': 100.00}
        ]

        top_items = vendor_comparator.identify_top_savings(products)

        # Savings: 50, Percent: (50 / 100) × 100 = 50%
        assert top_items[0]['savings_percent'] == 50.0

    def test_sorting_by_savings_amount(self, vendor_comparator):
        """Test that items are sorted by savings amount"""
        products = [
            {'name': 'Small Savings', 'shamrock_price': 90.00, 'sysco_price': 100.00},  # $10 savings
            {'name': 'Large Savings', 'shamrock_price': 50.00, 'sysco_price': 150.00},  # $100 savings
            {'name': 'Medium Savings', 'shamrock_price': 70.00, 'sysco_price': 100.00}  # $30 savings
        ]

        top_items = vendor_comparator.identify_top_savings(products)

        assert top_items[0]['name'] == 'Large Savings'
        assert top_items[1]['name'] == 'Medium Savings'
        assert top_items[2]['name'] == 'Small Savings'

    def test_top_n_limit(self, vendor_comparator):
        """Test that top_n parameter limits results"""
        products = [
            {'name': f'Item {i}', 'shamrock_price': i * 10, 'sysco_price': i * 20}
            for i in range(1, 11)  # 10 products
        ]

        top_5 = vendor_comparator.identify_top_savings(products, top_n=5)

        assert len(top_5) == 5

    def test_negative_savings(self, vendor_comparator):
        """Test handling of negative savings (SYSCO cheaper)"""
        products = [
            {'name': 'SYSCO Cheaper', 'shamrock_price': 100.00, 'sysco_price': 50.00}
        ]

        top_items = vendor_comparator.identify_top_savings(products)

        assert top_items[0]['savings'] == -50.00

    def test_zero_savings(self, vendor_comparator):
        """Test products with equal pricing"""
        products = [
            {'name': 'Equal Price', 'shamrock_price': 100.00, 'sysco_price': 100.00}
        ]

        top_items = vendor_comparator.identify_top_savings(products)

        assert top_items[0]['savings'] == 0.0
        assert top_items[0]['savings_percent'] == 0.0

    def test_missing_price_data(self, vendor_comparator):
        """Test handling of products with missing price data"""
        products = [
            {'name': 'Complete', 'shamrock_price': 50.00, 'sysco_price': 100.00},
            {'name': 'Missing Shamrock'},  # No prices
            {'name': 'Missing SYSCO', 'shamrock_price': 50.00}
        ]

        # Should handle gracefully, missing items get 0 savings
        top_items = vendor_comparator.identify_top_savings(products)

        assert len(top_items) == 3


class TestGenerateReport:
    """Tests for report generation"""

    def test_generate_report_returns_string(self, vendor_comparator):
        """Test that generate_report returns a string"""
        report = vendor_comparator.generate_report()

        assert isinstance(report, str)
        assert len(report) > 0

    def test_report_contains_key_sections(self, vendor_comparator):
        """Test that report contains expected sections"""
        report = vendor_comparator.generate_report()

        assert "THE LARIAT - VENDOR ANALYSIS REPORT" in report
        assert "EXECUTIVE SUMMARY" in report
        assert "KEY FINDINGS" in report
        assert "RECOMMENDATIONS" in report

    def test_report_contains_vendor_names(self, vendor_comparator):
        """Test that report mentions vendors"""
        report = vendor_comparator.generate_report()

        assert "Shamrock Foods" in report
        assert "SYSCO" in report

    def test_report_contains_savings_figures(self, vendor_comparator):
        """Test that report includes savings amounts"""
        report = vendor_comparator.generate_report()

        assert "29.5%" in report  # Savings percentage
        assert "$4,333" in report or "$52,000" in report  # Savings amounts

    def test_report_has_timestamp(self, vendor_comparator):
        """Test that report includes generation timestamp"""
        report = vendor_comparator.generate_report()

        assert "Generated:" in report

    def test_report_save_to_file(self, vendor_comparator, tmp_path):
        """Test saving report to file"""
        output_file = tmp_path / "test_report.txt"

        report = vendor_comparator.generate_report(output_path=str(output_file))

        # File should be created
        assert output_file.exists()
        # Content should match returned string
        assert output_file.read_text() == report


class TestCalculateMarginImpact:
    """Tests for margin impact calculations"""

    def test_margin_impact_basic(self, vendor_comparator):
        """Test basic margin impact calculation"""
        impact = vendor_comparator.calculate_margin_impact(monthly_savings=1000.00)

        assert 'catering' in impact
        assert 'restaurant' in impact
        assert 'total_monthly_impact' in impact

    def test_margin_impact_values(self, vendor_comparator):
        """Test margin impact calculation values"""
        impact = vendor_comparator.calculate_margin_impact(monthly_savings=1000.00)

        # 60% to catering, 40% to restaurant
        assert impact['catering']['monthly_impact'] == 600.00
        assert impact['restaurant']['monthly_impact'] == 400.00
        assert impact['total_monthly_impact'] == 1000.00

    def test_catering_margin_increase(self, vendor_comparator):
        """Test catering margin increase calculation"""
        impact = vendor_comparator.calculate_margin_impact(monthly_savings=2800.00)

        # Catering savings: 2800 × 0.6 = 1680
        # Margin increase: 1680 / 28000 = 0.06
        # New margin: 0.45 + 0.06 = 0.51
        assert impact['catering']['current_margin'] == 0.45
        assert abs(impact['catering']['margin_increase'] - 0.06) < 0.01
        assert abs(impact['catering']['new_margin'] - 0.51) < 0.01

    def test_restaurant_margin_increase(self, vendor_comparator):
        """Test restaurant margin increase calculation"""
        impact = vendor_comparator.calculate_margin_impact(monthly_savings=2500.00)

        # Restaurant savings: 2500 × 0.4 = 1000
        # Margin increase: 1000 / 20000 = 0.05
        # New margin: 0.04 + 0.05 = 0.09
        assert impact['restaurant']['current_margin'] == 0.04
        assert abs(impact['restaurant']['margin_increase'] - 0.05) < 0.01
        assert abs(impact['restaurant']['new_margin'] - 0.09) < 0.01

    def test_zero_savings_impact(self, vendor_comparator):
        """Test margin impact with zero savings"""
        impact = vendor_comparator.calculate_margin_impact(monthly_savings=0.0)

        assert impact['catering']['margin_increase'] == 0.0
        assert impact['restaurant']['margin_increase'] == 0.0
        assert impact['catering']['new_margin'] == impact['catering']['current_margin']
        assert impact['restaurant']['new_margin'] == impact['restaurant']['current_margin']

    def test_negative_savings_impact(self, vendor_comparator):
        """Test margin impact with negative savings (worse pricing)"""
        impact = vendor_comparator.calculate_margin_impact(monthly_savings=-1000.00)

        # Margins should decrease
        assert impact['catering']['margin_increase'] < 0
        assert impact['restaurant']['margin_increase'] < 0
        assert impact['catering']['new_margin'] < impact['catering']['current_margin']

    def test_large_savings_impact(self, vendor_comparator):
        """Test margin impact with very large savings"""
        # Based on 29.5% savings: $8000 × 0.295 = $2,360
        impact = vendor_comparator.calculate_margin_impact(monthly_savings=2360.00)

        # Should significantly improve margins
        assert impact['catering']['margin_increase'] > 0.05
        assert impact['restaurant']['margin_increase'] > 0.04


class TestRealWorldScenarios:
    """Integration-style tests using realistic scenarios"""

    def test_full_vendor_analysis_workflow(self, vendor_comparator, sample_products_for_comparison):
        """Test a complete vendor analysis workflow"""
        # Step 1: Compare vendors
        monthly_savings = vendor_comparator.compare_vendors('Shamrock Foods', 'SYSCO')
        assert monthly_savings > 0

        # Step 2: Analyze categories
        spices = [p for p in sample_products_for_comparison if p['category'] == 'Spice']
        spice_analysis = vendor_comparator.analyze_category('Spice', spices)
        assert spice_analysis['recommendation'] == 'Use Shamrock Foods'

        # Step 3: Identify top savings
        top_savings = vendor_comparator.identify_top_savings(sample_products_for_comparison, top_n=3)
        assert len(top_savings) == 3

        # Step 4: Calculate margin impact
        impact = vendor_comparator.calculate_margin_impact(monthly_savings)
        assert impact['total_monthly_impact'] == monthly_savings

        # Step 5: Generate report
        report = vendor_comparator.generate_report()
        assert "Shamrock Foods" in report

    def test_actual_savings_scenario(self, vendor_comparator):
        """Test with actual discovered 29.5% savings"""
        monthly_food_cost = 8000
        expected_monthly_savings = monthly_food_cost * 0.295

        monthly_savings = vendor_comparator.compare_vendors('Shamrock Foods', 'SYSCO')

        assert monthly_savings == expected_monthly_savings
        assert monthly_savings == 2360.00

        # Annual projection
        result = vendor_comparator.comparison_results[0]
        assert result['annual_savings'] == 28320.00  # 2360 × 12
