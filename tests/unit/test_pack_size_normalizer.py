"""
P0 CRITICAL: Tests for pack size parsing and price normalization
These tests protect against financial calculation errors in vendor comparisons
"""

import pytest
from modules.email_parser.email_parser import PackSizeNormalizer


@pytest.mark.critical
class TestPackSizeParsing:
    """Test pack size string parsing accuracy"""

    @pytest.mark.parametrize("pack_str,expected_pounds", [
        ("6/10#", 60.0),         # 6 containers × 10 lbs each
        ("3/6LB", 18.0),         # SYSCO format: 3 × 6 lbs
        ("25 LB", 25.0),         # Simple pounds
        ("10 LB", 10.0),         # Simple pounds
        ("1/25LB", 25.0),        # 1 container × 25 lbs
        ("6/1LB", 6.0),          # 6 containers × 1 lb each
        ("6/1#", 6.0),           # Same as above with # symbol
    ])
    def test_parse_pounds_common_formats(self, pack_str, expected_pounds):
        """Test parsing of common pound-based pack sizes"""
        normalizer = PackSizeNormalizer()
        result = normalizer.parse_pack_size(pack_str)
        assert result['total_pounds'] == expected_pounds, \
            f"Failed to parse {pack_str}: got {result['total_pounds']}, expected {expected_pounds}"
        assert result['unit'] == 'LB'

    @pytest.mark.parametrize("pack_str,expected_ounces", [
        ("6/#10", 654.0),        # 6 × #10 cans (109 oz each)
        ("12/#10", 1308.0),      # 12 × #10 cans
        ("6/#5", 336.0),         # 6 × #5 cans (56 oz each)
        ("24/#303", 384.0),      # 24 × #303 cans (16 oz each)
    ])
    def test_parse_can_sizes(self, pack_str, expected_ounces):
        """Test parsing of standard can sizes"""
        normalizer = PackSizeNormalizer()
        result = normalizer.parse_pack_size(pack_str)
        assert result['total_ounces'] == expected_ounces, \
            f"Failed to parse {pack_str}: got {result['total_ounces']}, expected {expected_ounces}"
        assert result['unit'] == 'OZ'

    @pytest.mark.parametrize("pack_str,expected_total_oz", [
        ("4/1 GAL", 512.0),      # 4 gallons × 128 oz each
        ("1/1 GAL", 128.0),      # 1 gallon
        ("6/1 GAL", 768.0),      # 6 gallons
    ])
    def test_parse_gallon_sizes(self, pack_str, expected_total_oz):
        """Test parsing of gallon-based pack sizes"""
        normalizer = PackSizeNormalizer()
        result = normalizer.parse_pack_size(pack_str)
        assert result['total_ounces'] == expected_total_oz
        assert result['unit'] == 'GAL'

    def test_parse_case_each_formats(self):
        """Test parsing of case/each formats"""
        normalizer = PackSizeNormalizer()

        # Test case format
        result = normalizer.parse_pack_size("12/CASE")
        assert result['count'] == 12
        assert result['unit'] == 'CASE'

        # Test each format
        result = normalizer.parse_pack_size("24/EACH")
        assert result['count'] == 24
        assert result['unit'] == 'EACH'

    def test_parse_unparseable_format(self):
        """Test handling of unknown formats"""
        normalizer = PackSizeNormalizer()
        result = normalizer.parse_pack_size("UNKNOWN FORMAT")
        assert result['unit'] == 'UNKNOWN'
        assert result['total_pounds'] is None
        assert 'original' in result

    @pytest.mark.parametrize("pack_str", [
        "",
        "   ",
        "0/0#",
    ])
    def test_parse_edge_cases(self, pack_str):
        """Test edge cases and malformed inputs"""
        normalizer = PackSizeNormalizer()
        # Should not raise exceptions
        result = normalizer.parse_pack_size(pack_str)
        assert result is not None


@pytest.mark.critical
class TestPriceNormalization:
    """Test price per pound calculations - CRITICAL for vendor comparison accuracy"""

    def test_normalize_sysco_pepper_real_example(self):
        """Test real SYSCO black pepper example: 6/1# @ $298.95 = $49.825/lb"""
        normalizer = PackSizeNormalizer()
        price_per_lb = normalizer.normalize_to_price_per_pound("6/1#", 298.95)

        expected = 298.95 / 6.0  # $49.825 per lb
        assert abs(price_per_lb - expected) < 0.01, \
            f"SYSCO pepper calculation wrong: got {price_per_lb}, expected {expected}"

    def test_normalize_shamrock_pepper_real_example(self):
        """Test real Shamrock black pepper example: 25 LB @ $79.71 = $3.19/lb"""
        normalizer = PackSizeNormalizer()
        price_per_lb = normalizer.normalize_to_price_per_pound("25 LB", 79.71)

        expected = 79.71 / 25.0  # $3.19 per lb
        assert abs(price_per_lb - expected) < 0.01, \
            f"Shamrock pepper calculation wrong: got {price_per_lb}, expected {expected}"

    def test_normalize_garlic_powder_example(self):
        """Test garlic powder: 3/6LB @ $213.19 = $11.84/lb"""
        normalizer = PackSizeNormalizer()
        price_per_lb = normalizer.normalize_to_price_per_pound("3/6LB", 213.19)

        expected = 213.19 / 18.0  # $11.84 per lb
        assert abs(price_per_lb - expected) < 0.01

    def test_normalize_can_format(self):
        """Test normalization of can-based pricing"""
        normalizer = PackSizeNormalizer()
        # 6/#10 cans @ $50 = total 654 oz = 40.875 lbs
        price_per_lb = normalizer.normalize_to_price_per_pound("6/#10", 50.0)

        total_oz = 6 * 109  # 654 oz
        total_lbs = total_oz / 16  # 40.875 lbs
        expected = 50.0 / total_lbs
        assert abs(price_per_lb - expected) < 0.01

    def test_normalize_returns_none_for_unknown_units(self):
        """Test that unparseable formats return None"""
        normalizer = PackSizeNormalizer()
        result = normalizer.normalize_to_price_per_pound("12/CASE", 50.0)
        assert result is None, "Should return None for case/each formats without weight"

    def test_normalize_liquid_measure_returns_none(self):
        """Test that pure liquid measures return None (can't convert gallons to pounds)"""
        normalizer = PackSizeNormalizer()
        result = normalizer.normalize_to_price_per_pound("4/1 GAL", 40.0)
        # Gallons can convert to ounces but total_pounds is None
        assert result is None

    @pytest.mark.parametrize("pack_str,case_price,expected_per_lb", [
        ("6/10#", 300.0, 5.0),      # 60 lbs total
        ("25 LB", 100.0, 4.0),      # 25 lbs
        ("3/6LB", 90.0, 5.0),       # 18 lbs total
        ("1/25LB", 50.0, 2.0),      # 25 lbs
    ])
    def test_normalize_parametrized(self, pack_str, case_price, expected_per_lb):
        """Parametrized tests for various pack sizes and prices"""
        normalizer = PackSizeNormalizer()
        price_per_lb = normalizer.normalize_to_price_per_pound(pack_str, case_price)
        assert abs(price_per_lb - expected_per_lb) < 0.01


@pytest.mark.critical
class TestFinancialImpact:
    """Tests that verify financial calculation accuracy for business decisions"""

    def test_pepper_savings_calculation(self):
        """
        CRITICAL: Verify the $52k annual savings calculation is based on correct parsing
        Black pepper is a key example in the vendor comparison
        """
        normalizer = PackSizeNormalizer()

        # SYSCO: 6/1# @ $298.95
        sysco_per_lb = normalizer.normalize_to_price_per_pound("6/1#", 298.95)

        # Shamrock: 25 LB @ $79.71
        shamrock_per_lb = normalizer.normalize_to_price_per_pound("25 LB", 79.71)

        # Calculate savings per pound
        savings_per_lb = sysco_per_lb - shamrock_per_lb

        # Expected: $49.825 - $3.19 = $46.635 savings per lb
        expected_savings = 46.635
        assert abs(savings_per_lb - expected_savings) < 0.02, \
            f"Pepper savings calculation wrong! This affects the $52k annual savings estimate"

        # Verify percentage
        savings_percent = (savings_per_lb / sysco_per_lb) * 100
        assert savings_percent > 90, "Shamrock should be >90% cheaper for this item"

    def test_zero_division_protection(self):
        """Ensure zero division doesn't occur with edge cases"""
        normalizer = PackSizeNormalizer()

        # Should handle zero price gracefully
        result = normalizer.normalize_to_price_per_pound("25 LB", 0.0)
        assert result == 0.0

    def test_consistency_between_formats(self):
        """
        Verify that different pack string formats for same total weight
        produce same price per pound
        """
        normalizer = PackSizeNormalizer()

        # All of these represent 6 pounds total
        formats = ["6/1LB", "6/1#", "6 LB"]
        results = [normalizer.normalize_to_price_per_pound(fmt, 60.0) for fmt in formats]

        # All should give $10/lb
        for result in results:
            if result is not None:
                assert abs(result - 10.0) < 0.01, \
                    "Different formats for same weight should give same price/lb"
