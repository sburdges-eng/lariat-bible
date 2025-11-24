"""
USDA Market News API Integration
=================================
FREE API - NO API KEY REQUIRED.

Website: https://www.ams.usda.gov/market-news

Features:
- Wholesale food prices (beef, pork, poultry, dairy, produce)
- Regional market reports
- Historical price data
- Daily/weekly market updates
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from .base_client import BaseClient, cached


class USDAMarketNewsClient(BaseClient):
    """
    Client for USDA Agricultural Marketing Service (AMS) Market News API

    Completely FREE, no API key required.
    Real wholesale commodity prices.
    """

    COMMODITIES = {
        'beef': 'LM_CT',
        'pork': 'LM_PK',
        'poultry': 'PY',
        'dairy': 'DY',
        'fruits': 'FVWTRK',
        'vegetables': 'FVWTRK',
        'specialty': 'FVWTRK',
        'grain': 'GR',
        'cotton': 'CT',
        'livestock': 'LS'
    }

    REGIONS = {
        'national': 'National',
        'midwest': 'Midwest',
        'southwest': 'Southwest',
        'southeast': 'Southeast',
        'northeast': 'Northeast',
        'northwest': 'Northwest',
        'colorado': 'CO'
    }

    def __init__(self):
        super().__init__()
        self.base_url = self.config.USDA_MARKET_NEWS_BASE_URL

    def health_check(self) -> Dict[str, Any]:
        """Check if USDA Market News API is accessible"""
        # Try to get available reports
        result = self._get(f"{self.base_url}/reports")

        if result and not result.get('error'):
            return {
                'available': True,
                'source': 'USDA Market News',
                'message': 'API is accessible (no key required)'
            }

        return {
            'available': False,
            'source': 'USDA Market News',
            'message': result.get('message', 'API unavailable') if result else 'Connection failed'
        }

    @cached(ttl=3600)
    def search(self, query: str, **kwargs) -> List[Dict]:
        """Search for commodity reports"""
        return self.search_reports(query)

    @cached(ttl=3600)
    def get_available_reports(self) -> List[Dict]:
        """
        Get list of all available market reports

        Returns:
            List of available reports with metadata
        """
        result = self._get(f"{self.base_url}/reports")

        if result and isinstance(result, list):
            return [
                {
                    'slug_id': report.get('slug_id'),
                    'slug_name': report.get('slug_name'),
                    'report_title': report.get('report_title'),
                    'market_type': report.get('market_type'),
                    'published_date': report.get('published_date'),
                    'source': 'USDA Market News'
                }
                for report in result
            ]

        return []

    @cached(ttl=1800)  # 30 minute cache for prices
    def get_report(
        self,
        slug_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get specific market report data

        Args:
            slug_id: Report slug ID (e.g., 'LM_CT100')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Report data with prices
        """
        params = {}

        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date

        result = self._get(f"{self.base_url}/reports/{slug_id}", params=params)

        if result and not result.get('error'):
            return {
                'slug_id': slug_id,
                'results': result.get('results', []),
                'count': len(result.get('results', [])),
                'source': 'USDA Market News'
            }

        return None

    @cached(ttl=1800)
    def get_beef_prices(
        self,
        report_type: str = 'daily',
        days_back: int = 7
    ) -> List[Dict]:
        """
        Get beef/cattle market prices

        Args:
            report_type: 'daily' or 'weekly'
            days_back: Number of days of history

        Returns:
            List of beef price reports
        """
        # Common beef reports
        reports = {
            'daily': 'LM_CT100',   # National Daily Cattle Report
            'weekly': 'LM_CT106',  # Weekly Boxed Beef Cutout
            'carcass': 'LM_CT102', # National Daily Boxed Beef Cutout
        }

        slug_id = reports.get(report_type, reports['daily'])
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        return self._get_commodity_prices(
            slug_id,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

    @cached(ttl=1800)
    def get_pork_prices(self, days_back: int = 7) -> List[Dict]:
        """
        Get pork market prices

        Args:
            days_back: Number of days of history

        Returns:
            List of pork price reports
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        return self._get_commodity_prices(
            'LM_PK602',  # National Daily Pork Report
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

    @cached(ttl=1800)
    def get_poultry_prices(self, days_back: int = 7) -> List[Dict]:
        """
        Get poultry market prices

        Args:
            days_back: Number of days of history

        Returns:
            List of poultry price reports
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        return self._get_commodity_prices(
            'PY_WB001',  # Weekly Poultry Report
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

    @cached(ttl=1800)
    def get_dairy_prices(self, days_back: int = 7) -> List[Dict]:
        """
        Get dairy market prices

        Args:
            days_back: Number of days of history

        Returns:
            List of dairy price reports
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        return self._get_commodity_prices(
            'DY_CL101',  # Weekly National Dairy Products Report
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

    @cached(ttl=1800)
    def get_produce_prices(
        self,
        produce_type: str = 'vegetables',
        region: str = 'national'
    ) -> List[Dict]:
        """
        Get fresh produce market prices

        Args:
            produce_type: 'fruits', 'vegetables', 'specialty'
            region: Region code

        Returns:
            List of produce price reports
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        # Terminal market reports
        slug_id = 'FVWTRK'  # Fruit and Vegetable Terminal Market Report

        return self._get_commodity_prices(
            slug_id,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

    @cached(ttl=3600)
    def search_reports(self, keyword: str) -> List[Dict]:
        """
        Search for reports by keyword

        Args:
            keyword: Search term

        Returns:
            List of matching reports
        """
        all_reports = self.get_available_reports()

        if not all_reports:
            return []

        keyword_lower = keyword.lower()
        matching = [
            report for report in all_reports
            if keyword_lower in report.get('slug_name', '').lower()
            or keyword_lower in report.get('report_title', '').lower()
            or keyword_lower in report.get('market_type', '').lower()
        ]

        return matching

    def _get_commodity_prices(
        self,
        slug_id: str,
        start_date: str,
        end_date: str
    ) -> List[Dict]:
        """Helper to get commodity prices for a date range"""
        report = self.get_report(slug_id, start_date, end_date)

        if report and report.get('results'):
            return [
                {
                    'report_date': item.get('report_date'),
                    'commodity': item.get('commodity'),
                    'grade': item.get('grade'),
                    'price_low': item.get('price_low'),
                    'price_high': item.get('price_high'),
                    'price_avg': item.get('weighted_avg') or (
                        (float(item.get('price_low', 0)) + float(item.get('price_high', 0))) / 2
                        if item.get('price_low') and item.get('price_high') else None
                    ),
                    'unit': item.get('unit'),
                    'region': item.get('region'),
                    'source': 'USDA Market News'
                }
                for item in report.get('results', [])
            ]

        return []

    def get_price_trends(
        self,
        commodity: str,
        days: int = 30
    ) -> Optional[Dict]:
        """
        Get price trends for a commodity

        Args:
            commodity: Commodity type ('beef', 'pork', 'poultry', 'dairy')
            days: Number of days to analyze

        Returns:
            Price trend analysis
        """
        price_methods = {
            'beef': self.get_beef_prices,
            'pork': self.get_pork_prices,
            'poultry': self.get_poultry_prices,
            'dairy': self.get_dairy_prices
        }

        method = price_methods.get(commodity.lower())
        if not method:
            return None

        prices = method(days_back=days)

        if not prices:
            return None

        # Calculate trend statistics
        avg_prices = [p.get('price_avg') for p in prices if p.get('price_avg')]

        if not avg_prices:
            return None

        return {
            'commodity': commodity,
            'period_days': days,
            'data_points': len(avg_prices),
            'min_price': min(avg_prices),
            'max_price': max(avg_prices),
            'avg_price': sum(avg_prices) / len(avg_prices),
            'latest_price': avg_prices[-1] if avg_prices else None,
            'price_change': avg_prices[-1] - avg_prices[0] if len(avg_prices) > 1 else 0,
            'price_change_pct': (
                ((avg_prices[-1] - avg_prices[0]) / avg_prices[0] * 100)
                if len(avg_prices) > 1 and avg_prices[0] != 0 else 0
            ),
            'source': 'USDA Market News'
        }
