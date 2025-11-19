"""
Unit tests for pack size parsing and price normalization
This is CRITICAL functionality - errors here cascade through all vendor analysis
"""

import pytest
from modules.vendor_analysis.corrected_comparison import CorrectedVendorComparison


class TestInterpretPackSize:
    """Tests for the interpret_pack_size method - the foundation of accurate pricing"""

    def test_shamrock_format_single_container(self, corrected_vendor_comparison):
        """Test Shamrock format: 1/6/LB = 1 container × 6 lbs"""
        result = corrected_vendor_comparison.interpret_pack_size("1/6/LB")

        assert result['original'] == "1/6/LB"
        assert result['containers'] == 1
        assert result['pounds_per_container'] == 6
        assert result['total_pounds'] == 6
        assert result['total_ounces'] == 96  # 6 × 16
        assert result['unit_type'] == 'LB'

    def test_shamrock_format_multiple_containers(self, corrected_vendor_comparison):
        """Test Shamrock format with multiple containers: 2/5/LB"""
        result = corrected_vendor_comparison.interpret_pack_size("2/5/LB")

        assert result['containers'] == 2
        assert result['pounds_per_container'] == 5
        assert result['total_pounds'] == 10  # 2 × 5
        assert result['total_ounces'] == 160  # 10 × 16
        assert result['unit_type'] == 'LB'

    def test_sysco_format_with_lb(self, corrected_vendor_comparison):
        """Test SYSCO format: 3/6LB = 3 containers × 6 lbs each"""
        result = corrected_vendor_comparison.interpret_pack_size("3/6LB")

        assert result['containers'] == 3
        assert result['pounds_per_container'] == 6
        assert result['total_pounds'] == 18  # 3 × 6
        assert result['total_ounces'] == 288  # 18 × 16
        assert result['unit_type'] == 'LB'

    def test_sysco_format_with_pound_symbol(self, corrected_vendor_comparison):
        """Test SYSCO format with # symbol: 6/5# = 6 containers × 5 lbs each"""
        result = corrected_vendor_comparison.interpret_pack_size("6/5#")

        assert result['containers'] == 6
        assert result['pounds_per_container'] == 5
        assert result['total_pounds'] == 30  # 6 × 5
        assert result['total_ounces'] == 480  # 30 × 16
        assert result['unit_type'] == 'LB'

    def test_sysco_format_single_pounds(self, corrected_vendor_comparison):
        """Test SYSCO format: 6/1LB = 6 containers × 1 lb each"""
        result = corrected_vendor_comparison.interpret_pack_size("6/1LB")

        assert result['containers'] == 6
        assert result['pounds_per_container'] == 1
        assert result['total_pounds'] == 6
        assert result['total_ounces'] == 96
        assert result['unit_type'] == 'LB'

    def test_simple_pounds_format(self, corrected_vendor_comparison):
        """Test simple format: 25 LB = 25 pounds total"""
        result = corrected_vendor_comparison.interpret_pack_size("25 LB")

        assert result['containers'] == 1
        assert result['pounds_per_container'] == 25
        assert result['total_pounds'] == 25
        assert result['total_ounces'] == 400  # 25 × 16
        assert result['unit_type'] == 'LB'

    def test_simple_pounds_no_space(self, corrected_vendor_comparison):
        """Test simple format without space: 50LB"""
        result = corrected_vendor_comparison.interpret_pack_size("50LB")

        assert result['total_pounds'] == 50
        assert result['total_ounces'] == 800
        assert result['unit_type'] == 'LB'

    def test_number_10_can_format(self, corrected_vendor_comparison):
        """Test #10 can format: 6/#10 = 6 cans × 109 oz each"""
        result = corrected_vendor_comparison.interpret_pack_size("6/#10")

        assert result['containers'] == 6
        assert result['unit_type'] == 'CAN#10'
        assert result['total_ounces'] == 654  # 6 × 109
        assert result['total_pounds'] == 40.875  # 654 / 16

    def test_gallon_format(self, corrected_vendor_comparison):
        """Test gallon format: 2/1GAL = 2 containers × 1 gallon"""
        result = corrected_vendor_comparison.interpret_pack_size("2/1GAL")

        assert result['containers'] == 2
        assert result['unit_type'] == 'GAL'
        assert result['total_ounces'] == 256  # 2 × 1 × 128

    def test_gallon_format_multiple_gallons(self, corrected_vendor_comparison):
        """Test gallon format with multiple gallons: 4/2GAL"""
        result = corrected_vendor_comparison.interpret_pack_size("4/2GAL")

        assert result['containers'] == 4
        assert result['total_ounces'] == 1024  # 4 × 2 × 128

    def test_case_format(self, corrected_vendor_comparison):
        """Test case format: 12CS"""
        result = corrected_vendor_comparison.interpret_pack_size("12CS")

        assert result['containers'] == 12
        assert result['unit_type'] == 'EACH'

    def test_each_format(self, corrected_vendor_comparison):
        """Test 'each' format: 24EA"""
        result = corrected_vendor_comparison.interpret_pack_size("24EA")

        assert result['containers'] == 24
        assert result['unit_type'] == 'EACH'

    def test_case_insensitivity(self, corrected_vendor_comparison):
        """Test that parsing is case-insensitive"""
        result_upper = corrected_vendor_comparison.interpret_pack_size("3/6LB")
        result_lower = corrected_vendor_comparison.interpret_pack_size("3/6lb")
        result_mixed = corrected_vendor_comparison.interpret_pack_size("3/6Lb")

        assert result_upper['total_pounds'] == result_lower['total_pounds'] == result_mixed['total_pounds']
        assert result_upper['total_pounds'] == 18

    def test_whitespace_handling(self, corrected_vendor_comparison):
        """Test that extra whitespace is handled correctly"""
        result_normal = corrected_vendor_comparison.interpret_pack_size("25 LB")
        result_extra_space = corrected_vendor_comparison.interpret_pack_size("  25  LB  ")

        assert result_normal['total_pounds'] == result_extra_space['total_pounds']
        assert result_normal['total_pounds'] == 25


class TestPackSizeEdgeCases:
    """Tests for edge cases and malformed pack sizes"""

    def test_empty_string(self, corrected_vendor_comparison):
        """Test empty string returns structure with None values"""
        result = corrected_vendor_comparison.interpret_pack_size("")

        assert result['original'] == ""
        assert result['total_pounds'] is None
        assert result['total_ounces'] is None

    def test_invalid_format(self, corrected_vendor_comparison):
        """Test completely invalid format"""
        result = corrected_vendor_comparison.interpret_pack_size("INVALID")

        assert result['total_pounds'] is None
        assert result['total_ounces'] is None

    def test_just_number(self, corrected_vendor_comparison):
        """Test just a number without unit"""
        result = corrected_vendor_comparison.interpret_pack_size("42")

        assert result['total_pounds'] is None
        assert result['total_ounces'] is None

    def test_missing_containers_in_shamrock_format(self, corrected_vendor_comparison):
        """Test malformed Shamrock format: /6/LB (missing containers)"""
        result = corrected_vendor_comparison.interpret_pack_size("/6/LB")

        # Should not match Shamrock pattern, should fall through
        assert result['total_pounds'] is None or result.get('error') is not None

    def test_missing_pounds_in_sysco_format(self, corrected_vendor_comparison):
        """Test malformed SYSCO format: 3/LB (missing pounds)"""
        result = corrected_vendor_comparison.interpret_pack_size("3/LB")

        # Should not match SYSCO pattern cleanly
        assert result['total_pounds'] is None or result.get('error') is not None

    def test_letters_instead_of_numbers(self, corrected_vendor_comparison):
        """Test letters where numbers should be: ABC/DEF"""
        result = corrected_vendor_comparison.interpret_pack_size("ABC/DEF")

        assert result['total_pounds'] is None

    def test_zero_containers(self, corrected_vendor_comparison):
        """Test zero containers: 0/6LB (edge case)"""
        result = corrected_vendor_comparison.interpret_pack_size("0/6LB")

        assert result['containers'] == 0
        assert result['total_pounds'] == 0

    def test_zero_pounds(self, corrected_vendor_comparison):
        """Test zero pounds: 3/0LB (edge case)"""
        result = corrected_vendor_comparison.interpret_pack_size("3/0LB")

        assert result['pounds_per_container'] == 0
        assert result['total_pounds'] == 0


class TestCalculatePricePerUnit:
    """Tests for price per unit calculations"""

    def test_shamrock_price_per_pound(self, corrected_vendor_comparison):
        """Test price per pound calculation for Shamrock format"""
        # 1/6/LB at $54.26 = $9.04 per pound
        price_per_lb = corrected_vendor_comparison.calculate_price_per_unit(
            "1/6/LB", 54.26, 'LB'
        )

        assert price_per_lb is not None
        assert abs(price_per_lb - 9.043333) < 0.01  # Allow for rounding

    def test_sysco_price_per_pound(self, corrected_vendor_comparison):
        """Test price per pound calculation for SYSCO format"""
        # 3/6LB at $213.19 = $11.844 per pound
        price_per_lb = corrected_vendor_comparison.calculate_price_per_unit(
            "3/6LB", 213.19, 'LB'
        )

        assert price_per_lb is not None
        assert abs(price_per_lb - 11.844) < 0.01

    def test_simple_pounds_price_per_pound(self, corrected_vendor_comparison):
        """Test price per pound for simple format"""
        # 25 LB at $95.88 = $3.835 per pound
        price_per_lb = corrected_vendor_comparison.calculate_price_per_unit(
            "25 LB", 95.88, 'LB'
        )

        assert price_per_lb is not None
        assert abs(price_per_lb - 3.8352) < 0.01

    def test_price_per_ounce(self, corrected_vendor_comparison):
        """Test price per ounce calculation"""
        # 1/6/LB = 96 oz at $54.26 = $0.565 per oz
        price_per_oz = corrected_vendor_comparison.calculate_price_per_unit(
            "1/6/LB", 54.26, 'OZ'
        )

        assert price_per_oz is not None
        assert abs(price_per_oz - 0.565) < 0.01

    def test_invalid_pack_size_returns_none(self, corrected_vendor_comparison):
        """Test that invalid pack size returns None"""
        price_per_lb = corrected_vendor_comparison.calculate_price_per_unit(
            "INVALID", 100.00, 'LB'
        )

        assert price_per_lb is None

    def test_zero_price(self, corrected_vendor_comparison):
        """Test calculation with zero price"""
        price_per_lb = corrected_vendor_comparison.calculate_price_per_unit(
            "25 LB", 0.00, 'LB'
        )

        assert price_per_lb == 0.0

    def test_negative_price(self, corrected_vendor_comparison):
        """Test calculation with negative price (edge case)"""
        price_per_lb = corrected_vendor_comparison.calculate_price_per_unit(
            "25 LB", -50.00, 'LB'
        )

        # Should still calculate, even if negative
        assert price_per_lb == -2.0


class TestCompareItems:
    """Tests for vendor item comparison logic"""

    def test_shamrock_cheaper_comparison(self, corrected_vendor_comparison):
        """Test comparison where Shamrock is cheaper"""
        result = corrected_vendor_comparison.compare_items(
            item_name="Garlic Powder",
            sysco_pack="3/6LB",
            sysco_price=213.19,
            shamrock_pack="1/6/LB",
            shamrock_price=54.26
        )

        assert result is not None
        assert result['item'] == "Garlic Powder"
        assert result['preferred_vendor'] == 'Shamrock'
        assert result['sysco_per_lb'] > result['shamrock_per_lb']
        assert result['savings_per_lb'] > 0
        assert result['savings_percent'] > 0

    def test_sysco_cheaper_comparison(self, corrected_vendor_comparison):
        """Test comparison where SYSCO is cheaper (hypothetical)"""
        result = corrected_vendor_comparison.compare_items(
            item_name="Test Item",
            sysco_pack="25 LB",
            sysco_price=50.00,  # $2/lb
            shamrock_pack="25 LB",
            shamrock_price=75.00  # $3/lb
        )

        assert result is not None
        assert result['preferred_vendor'] == 'SYSCO'
        assert result['sysco_per_lb'] < result['shamrock_per_lb']
        assert result['savings_per_lb'] < 0  # Negative because SYSCO is cheaper

    def test_equal_pricing(self, corrected_vendor_comparison):
        """Test comparison where prices are equal"""
        result = corrected_vendor_comparison.compare_items(
            item_name="Equal Price Item",
            sysco_pack="25 LB",
            sysco_price=100.00,
            shamrock_pack="25 LB",
            shamrock_price=100.00
        )

        assert result is not None
        assert result['savings_per_lb'] == 0.0
        assert result['savings_percent'] == 0.0

    def test_with_split_pricing(self, corrected_vendor_comparison):
        """Test comparison including SYSCO split pricing"""
        result = corrected_vendor_comparison.compare_items(
            item_name="Test Item",
            sysco_pack="3/6LB",  # 3 containers of 6 lbs each
            sysco_price=180.00,
            shamrock_pack="25 LB",
            shamrock_price=100.00,
            sysco_split_price=35.00  # Price for 1 container (6 lbs)
        )

        assert result is not None
        assert 'sysco_split_per_lb' in result
        assert result['sysco_split_per_lb'] is not None
        assert 'split_vs_shamrock_savings' in result
        assert 'split_savings_pct' in result

    def test_monthly_savings_estimate(self, corrected_vendor_comparison):
        """Test that monthly savings estimate is calculated"""
        result = corrected_vendor_comparison.compare_items(
            item_name="Test Item",
            sysco_pack="25 LB",
            sysco_price=100.00,  # $4/lb
            shamrock_pack="25 LB",
            shamrock_price=75.00   # $3/lb
        )

        assert result is not None
        # Savings = $1/lb, monthly estimate = $1 × 10 = $10
        assert result['monthly_savings_estimate'] == 10.0

    def test_incompatible_pack_sizes_returns_none(self, corrected_vendor_comparison):
        """Test that invalid pack sizes return None"""
        result = corrected_vendor_comparison.compare_items(
            item_name="Invalid Item",
            sysco_pack="INVALID",
            sysco_price=100.00,
            shamrock_pack="ALSO INVALID",
            shamrock_price=75.00
        )

        assert result is None


class TestRealWorldScenarios:
    """Integration-style tests using real data from the codebase"""

    def test_garlic_powder_real_comparison(self, corrected_vendor_comparison):
        """Test actual Garlic Powder comparison from the codebase"""
        result = corrected_vendor_comparison.compare_items(
            "Garlic Powder",
            "3/6LB", 213.19,
            "1/6/LB", 54.26
        )

        assert result is not None
        assert result['preferred_vendor'] == 'Shamrock'
        # SYSCO: 213.19 / 18 lbs = 11.84/lb
        assert abs(result['sysco_per_lb'] - 11.84) < 0.01
        # Shamrock: 54.26 / 6 lbs = 9.04/lb
        assert abs(result['shamrock_per_lb'] - 9.04) < 0.1
        # Savings should be around $2.80/lb
        assert result['savings_per_lb'] > 2.5
        assert result['savings_percent'] > 20

    def test_black_pepper_real_comparison(self, corrected_vendor_comparison):
        """Test actual Black Pepper comparison"""
        result = corrected_vendor_comparison.compare_items(
            "Black Pepper Ground",
            "6/1LB", 295.89,
            "25 LB", 95.88
        )

        assert result is not None
        assert result['preferred_vendor'] == 'Shamrock'
        # SYSCO: 295.89 / 6 lbs = 49.315/lb
        assert abs(result['sysco_per_lb'] - 49.315) < 0.01
        # Shamrock: 95.88 / 25 lbs = 3.84/lb
        assert abs(result['shamrock_per_lb'] - 3.84) < 0.01
        # MASSIVE savings!
        assert result['savings_per_lb'] > 45
        assert result['savings_percent'] > 90

    def test_all_spice_comparisons(self, corrected_vendor_comparison, sample_spice_comparisons):
        """Test all spice comparisons from real data"""
        results = []

        for item_data in sample_spice_comparisons:
            comparison = corrected_vendor_comparison.compare_items(*item_data)
            if comparison:
                results.append(comparison)

        assert len(results) == 6
        # All should prefer Shamrock
        assert all(r['preferred_vendor'] == 'Shamrock' for r in results)
        # All should have positive savings
        assert all(r['savings_per_lb'] > 0 for r in results)


class TestPriceCalculationAccuracy:
    """Tests to ensure price calculations are mathematically accurate"""

    def test_price_per_pound_precision(self, corrected_vendor_comparison):
        """Test that price calculations maintain proper precision"""
        # Use a price that requires precision
        price_per_lb = corrected_vendor_comparison.calculate_price_per_unit(
            "3/7LB", 123.45, 'LB'
        )

        # 123.45 / 21 = 5.878571...
        assert price_per_lb is not None
        assert abs(price_per_lb - 5.878571428) < 0.000001

    def test_ounce_conversion_accuracy(self, corrected_vendor_comparison):
        """Test that pound to ounce conversion is accurate"""
        result = corrected_vendor_comparison.interpret_pack_size("3/7LB")

        assert result['total_pounds'] == 21
        assert result['total_ounces'] == 336  # 21 × 16

    def test_percentage_calculation(self, corrected_vendor_comparison):
        """Test that savings percentage is calculated correctly"""
        result = corrected_vendor_comparison.compare_items(
            "Test Item",
            "25 LB", 100.00,  # $4/lb
            "25 LB", 80.00    # $3.20/lb
        )

        # Savings = $0.80/lb
        # Percentage = (0.80 / 4.00) × 100 = 20%
        assert abs(result['savings_percent'] - 20.0) < 0.1
