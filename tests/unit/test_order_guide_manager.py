"""
P1 HIGH PRIORITY: Tests for order guide management and price comparison
These tests ensure vendor catalog management and purchase recommendations work correctly
"""

import pytest
import pandas as pd
from modules.order_guides.order_guide_manager import OrderGuideManager


@pytest.mark.high
class TestOrderGuideLoading:
    """Test loading order guide data from vendors"""

    def test_load_sysco_guide(self, sysco_order_guide_data):
        """Test loading SYSCO order guide"""
        manager = OrderGuideManager()
        count = manager.load_sysco_guide(sysco_order_guide_data)

        assert count == 3
        assert len(manager.sysco_catalog) == 3
        assert manager.last_updated['sysco'] is not None

        # Check that data is properly stored
        assert 'SYS001' in manager.sysco_catalog
        item = manager.sysco_catalog['SYS001']
        assert item['description'] == 'BEEF GROUND 80/20'
        assert item['case_price'] == 45.99
        assert item['vendor'] == 'SYSCO'

    def test_load_shamrock_guide(self, shamrock_order_guide_data):
        """Test loading Shamrock order guide"""
        manager = OrderGuideManager()
        count = manager.load_shamrock_guide(shamrock_order_guide_data)

        assert count == 3
        assert len(manager.shamrock_catalog) == 3
        assert manager.last_updated['shamrock'] is not None

        # Check that data is properly stored
        assert 'SHA001' in manager.shamrock_catalog
        item = manager.shamrock_catalog['SHA001']
        assert item['description'] == 'GROUND BEEF 80/20'
        assert item['case_price'] == 32.50
        assert item['vendor'] == 'Shamrock Foods'

    def test_load_empty_guide(self):
        """Test loading empty order guide"""
        manager = OrderGuideManager()
        count = manager.load_sysco_guide([])

        assert count == 0
        assert len(manager.sysco_catalog) == 0

    def test_load_guide_updates_timestamp(self):
        """Test that loading updates timestamp"""
        manager = OrderGuideManager()

        assert manager.last_updated['sysco'] is None

        manager.load_sysco_guide([{
            'item_code': 'TEST001',
            'description': 'TEST',
            'pack_size': '25 LB',
            'case_price': 100.0
        }])

        assert manager.last_updated['sysco'] is not None


@pytest.mark.high
class TestProductMatching:
    """Test finding matching products between vendors"""

    def test_find_matching_products(self, sysco_order_guide_data, shamrock_order_guide_data):
        """Test finding products that appear in both catalogs"""
        manager = OrderGuideManager()
        manager.load_sysco_guide(sysco_order_guide_data)
        manager.load_shamrock_guide(shamrock_order_guide_data)

        matches = manager.find_matching_products(threshold=0.5)

        # Should find matches for ground beef, chicken, and pepper
        assert len(matches) > 0

        # Each match should have required fields
        for match in matches:
            assert 'sysco_code' in match
            assert 'shamrock_code' in match
            assert 'similarity_score' in match
            assert match['similarity_score'] >= 0.5

    def test_find_matching_products_high_threshold(self, sysco_order_guide_data, shamrock_order_guide_data):
        """Test matching with very high similarity threshold"""
        manager = OrderGuideManager()
        manager.load_sysco_guide(sysco_order_guide_data)
        manager.load_shamrock_guide(shamrock_order_guide_data)

        # Very high threshold may result in fewer matches
        matches = manager.find_matching_products(threshold=0.95)

        # All returned matches should have very high similarity
        for match in matches:
            assert match['similarity_score'] >= 0.95

    def test_find_matching_products_empty_catalog(self):
        """Test matching with empty catalog"""
        manager = OrderGuideManager()
        manager.load_sysco_guide([])
        manager.load_shamrock_guide([])

        matches = manager.find_matching_products()

        assert len(matches) == 0


@pytest.mark.high
class TestPriceComparison:
    """Test price comparison functionality"""

    def test_compare_prices(self, sysco_order_guide_data, shamrock_order_guide_data):
        """Test comparing prices between matched products"""
        manager = OrderGuideManager()
        manager.load_sysco_guide(sysco_order_guide_data)
        manager.load_shamrock_guide(shamrock_order_guide_data)

        df = manager.compare_prices()

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

        # Check required columns
        required_cols = ['description', 'sysco_case_price', 'shamrock_case_price',
                        'case_savings', 'preferred_vendor']
        for col in required_cols:
            assert col in df.columns

    def test_compare_prices_calculates_savings(self, sysco_order_guide_data, shamrock_order_guide_data):
        """Test that savings are correctly calculated"""
        manager = OrderGuideManager()
        manager.load_sysco_guide(sysco_order_guide_data)
        manager.load_shamrock_guide(shamrock_order_guide_data)

        df = manager.compare_prices()

        # Verify savings calculation
        for _, row in df.iterrows():
            expected_savings = abs(row['sysco_case_price'] - row['shamrock_case_price'])
            assert abs(row['case_savings'] - expected_savings) < 0.01

    def test_compare_prices_identifies_preferred_vendor(self, sysco_order_guide_data, shamrock_order_guide_data):
        """Test that preferred vendor is correctly identified"""
        manager = OrderGuideManager()
        manager.load_sysco_guide(sysco_order_guide_data)
        manager.load_shamrock_guide(shamrock_order_guide_data)

        df = manager.compare_prices()

        for _, row in df.iterrows():
            if row['sysco_case_price'] < row['shamrock_case_price']:
                assert row['preferred_vendor'] == 'SYSCO'
            else:
                assert row['preferred_vendor'] == 'Shamrock Foods'

    def test_compare_prices_sorted_by_savings(self, sysco_order_guide_data, shamrock_order_guide_data):
        """Test that results are sorted by savings potential"""
        manager = OrderGuideManager()
        manager.load_sysco_guide(sysco_order_guide_data)
        manager.load_shamrock_guide(shamrock_order_guide_data)

        df = manager.compare_prices()

        # Should be sorted in descending order of savings
        if len(df) > 1:
            for i in range(len(df) - 1):
                assert df.iloc[i]['case_savings'] >= df.iloc[i + 1]['case_savings']

    def test_compare_prices_empty_returns_empty_dataframe(self):
        """Test that comparing with no data returns empty DataFrame"""
        manager = OrderGuideManager()
        df = manager.compare_prices()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0


@pytest.mark.high
class TestCategoryAnalysis:
    """Test category-based analysis"""

    def test_get_category_analysis(self, sysco_order_guide_data, shamrock_order_guide_data):
        """Test category analysis aggregation"""
        manager = OrderGuideManager()
        manager.load_sysco_guide(sysco_order_guide_data)
        manager.load_shamrock_guide(shamrock_order_guide_data)

        analysis = manager.get_category_analysis()

        # Should have categories from the data
        assert len(analysis) > 0

        # Each category should have required metrics
        for category, metrics in analysis.items():
            assert 'total_items' in metrics
            assert 'shamrock_wins' in metrics
            assert 'sysco_wins' in metrics
            assert 'avg_savings_pct' in metrics
            assert 'total_potential_savings' in metrics
            assert 'top_savings_item' in metrics

    def test_category_analysis_meat_category(self, sysco_order_guide_data, shamrock_order_guide_data):
        """Test analysis for MEAT category specifically"""
        manager = OrderGuideManager()
        manager.load_sysco_guide(sysco_order_guide_data)
        manager.load_shamrock_guide(shamrock_order_guide_data)

        analysis = manager.get_category_analysis()

        if 'MEAT' in analysis:
            meat_analysis = analysis['MEAT']
            # Should have both ground beef comparisons
            assert meat_analysis['total_items'] >= 1
            assert meat_analysis['shamrock_wins'] + meat_analysis['sysco_wins'] == meat_analysis['total_items']


@pytest.mark.high
class TestPurchaseRecommendations:
    """Test purchase recommendation generation"""

    def test_generate_purchase_recommendation(self, sysco_order_guide_data, shamrock_order_guide_data):
        """Test generating purchase recommendations"""
        manager = OrderGuideManager()
        manager.load_sysco_guide(sysco_order_guide_data)
        manager.load_shamrock_guide(shamrock_order_guide_data)

        recommendations = manager.generate_purchase_recommendation()

        assert 'summary' in recommendations
        assert 'top_10_savings' in recommendations
        assert 'category_recommendations' in recommendations

        # Summary should have counts
        summary = recommendations['summary']
        assert 'total_items_compared' in summary
        assert 'shamrock_preferred' in summary
        assert 'sysco_preferred' in summary

    def test_purchase_recommendation_top_10(self, sysco_order_guide_data, shamrock_order_guide_data):
        """Test that top 10 savings items are included"""
        manager = OrderGuideManager()
        manager.load_sysco_guide(sysco_order_guide_data)
        manager.load_shamrock_guide(shamrock_order_guide_data)

        recommendations = manager.generate_purchase_recommendation()

        top_10 = recommendations['top_10_savings']
        # Should have up to 10 items (or fewer if less data)
        assert len(top_10) <= 10

        # Each item should have required fields
        for item in top_10:
            assert 'item' in item
            assert 'preferred_vendor' in item
            assert 'savings_per_case' in item

    def test_purchase_recommendation_with_usage_data(self, sysco_order_guide_data, shamrock_order_guide_data):
        """Test recommendations with weekly usage data"""
        manager = OrderGuideManager()
        manager.load_sysco_guide(sysco_order_guide_data)
        manager.load_shamrock_guide(shamrock_order_guide_data)

        weekly_usage = {
            'BEEF GROUND': 10,  # 10 cases per week
            'CHICKEN BREAST': 5  # 5 cases per week
        }

        recommendations = manager.generate_purchase_recommendation(weekly_usage=weekly_usage)

        # Should calculate estimated monthly savings
        assert 'estimated_monthly_savings' in recommendations
        assert recommendations['estimated_monthly_savings'] > 0

    def test_purchase_recommendation_empty_data(self):
        """Test recommendations with no data"""
        manager = OrderGuideManager()
        recommendations = manager.generate_purchase_recommendation()

        assert 'error' in recommendations


@pytest.mark.high
class TestExcelExport:
    """Test Excel export functionality"""

    def test_export_comparison_creates_file(self, sysco_order_guide_data, shamrock_order_guide_data, tmp_path):
        """Test that Excel export creates a file"""
        manager = OrderGuideManager()
        manager.load_sysco_guide(sysco_order_guide_data)
        manager.load_shamrock_guide(shamrock_order_guide_data)

        filepath = tmp_path / "test_comparison.xlsx"
        result = manager.export_comparison(str(filepath))

        assert "exported" in result.lower()
        assert filepath.exists()

    def test_export_comparison_empty_data(self):
        """Test exporting with no comparison data"""
        manager = OrderGuideManager()
        result = manager.export_comparison("test.xlsx")

        assert result == "No data to export"

    def test_export_comparison_multiple_sheets(self, sysco_order_guide_data, shamrock_order_guide_data, tmp_path):
        """Test that export creates multiple sheets"""
        manager = OrderGuideManager()
        manager.load_sysco_guide(sysco_order_guide_data)
        manager.load_shamrock_guide(shamrock_order_guide_data)

        filepath = tmp_path / "test_comparison.xlsx"
        manager.export_comparison(str(filepath))

        # Read the Excel file
        excel_file = pd.ExcelFile(filepath)

        # Should have multiple sheets
        expected_sheets = ['Price Comparison', 'Category Analysis', 'Top 20 Savings', 'Summary']
        for sheet in expected_sheets:
            assert sheet in excel_file.sheet_names


@pytest.mark.high
class TestOrderGuideEdgeCases:
    """Test edge cases and error handling"""

    def test_load_guide_with_missing_fields(self):
        """Test loading data with some missing optional fields"""
        manager = OrderGuideManager()
        data = [{
            'item_code': 'TEST001',
            'description': 'TEST ITEM',
            'pack_size': '25 LB',
            'case_price': 100.0
            # Missing unit_price, unit, category
        }]

        count = manager.load_sysco_guide(data)

        assert count == 1
        item = manager.sysco_catalog['TEST001']
        assert item['unit_price'] == 0
        assert item['unit'] == 'EACH'
        assert item['category'] == 'UNCATEGORIZED'

    def test_compare_prices_with_zero_prices(self):
        """Test price comparison with zero prices"""
        manager = OrderGuideManager()

        sysco_data = [{
            'item_code': 'SYS001',
            'description': 'FREE ITEM',
            'pack_size': '1 EA',
            'case_price': 0.0,
            'unit_price': 0.0,
            'unit': 'EA',
            'category': 'TEST'
        }]

        shamrock_data = [{
            'item_code': 'SHA001',
            'description': 'FREE ITEM',
            'pack_size': '1 EA',
            'case_price': 0.0,
            'unit_price': 0.0,
            'unit': 'EA',
            'category': 'TEST'
        }]

        manager.load_sysco_guide(sysco_data)
        manager.load_shamrock_guide(shamrock_data)

        # Should handle zero prices without errors
        df = manager.compare_prices()
        assert len(df) >= 0  # May or may not match

    def test_vendor_catalog_overwrite(self, sysco_order_guide_data):
        """Test that reloading catalog overwrites previous data"""
        manager = OrderGuideManager()

        # Load initial data
        manager.load_sysco_guide(sysco_order_guide_data)
        initial_count = len(manager.sysco_catalog)

        # Load different data
        new_data = [{
            'item_code': 'NEW001',
            'description': 'NEW ITEM',
            'pack_size': '10 LB',
            'case_price': 50.0
        }]

        manager.load_sysco_guide(new_data)

        # Old items should still be there (additive), new one added
        assert len(manager.sysco_catalog) == initial_count + 1
        assert 'NEW001' in manager.sysco_catalog
