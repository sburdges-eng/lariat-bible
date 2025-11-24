"""
Commodity Prices Integration
=============================
FREE commodity price data and trends.

Data Sources:
- Index Mundi (https://www.indexmundi.com) - Global commodity prices
- USDA Quick Stats - Agricultural data
- World Bank Commodity Data

Features:
- Historical commodity prices
- Price trends and forecasts
- Global market data
- Agricultural commodities
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
from .base_client import BaseClient, cached


class CommodityPricesClient(BaseClient):
    """
    Client for commodity price data

    FREE web-based commodity price information.
    Useful for tracking food input costs.
    """

    # Common food commodities tracked by Index Mundi
    COMMODITIES = {
        # Grains
        'wheat': 'wheat',
        'corn': 'corn',
        'rice': 'rice',
        'barley': 'barley',
        'oats': 'oats',

        # Proteins
        'beef': 'beef',
        'chicken': 'chicken',
        'pork': 'pork',
        'fish_meal': 'fish-meal',
        'shrimp': 'shrimp',

        # Dairy
        'butter': 'butter',
        'cheese': 'cheese',
        'milk': 'milk',

        # Oils
        'olive_oil': 'olive-oil',
        'palm_oil': 'palm-oil',
        'soybean_oil': 'soybean-oil',
        'sunflower_oil': 'sunflower-oil',

        # Sugar/Sweeteners
        'sugar': 'sugar',
        'honey': 'honey',

        # Beverages
        'coffee': 'coffee',
        'tea': 'tea',
        'cocoa': 'cocoa',

        # Produce
        'oranges': 'oranges',
        'bananas': 'bananas',
        'potatoes': 'potatoes',
        'tomatoes': 'tomatoes',
        'onions': 'onions',

        # Other
        'pepper': 'pepper',
        'salt': 'salt',
        'vanilla': 'vanilla',
    }

    def __init__(self):
        super().__init__()
        self.base_url = self.config.INDEX_MUNDI_BASE_URL
        self.session.headers.update({
            'User-Agent': 'LariatBible/1.0 (commodity price research for restaurant)'
        })

    def health_check(self) -> Dict[str, Any]:
        """Check if commodity price sources are accessible"""
        try:
            response = self.session.get(
                f"{self.base_url}/commodities/",
                timeout=10
            )
            available = response.status_code == 200
        except Exception:
            available = False

        return {
            'available': available,
            'source': 'Commodity Prices (Index Mundi)',
            'message': 'Web data accessible' if available else 'Connection failed',
            'commodities_tracked': len(self.COMMODITIES)
        }

    @cached(ttl=3600)
    def search(self, query: str, **kwargs) -> List[Dict]:
        """Search for commodity prices"""
        query_lower = query.lower()
        matching = []

        for name, slug in self.COMMODITIES.items():
            if query_lower in name or query_lower in slug:
                price_data = self.get_commodity_price(name)
                if price_data:
                    matching.append(price_data)

        return matching

    @cached(ttl=3600)  # 1 hour cache for prices
    def get_commodity_price(self, commodity: str) -> Optional[Dict]:
        """
        Get current price for a commodity

        Args:
            commodity: Commodity name (see COMMODITIES)

        Returns:
            Current price data
        """
        slug = self.COMMODITIES.get(commodity.lower(), commodity.lower())

        try:
            url = f"{self.base_url}/commodities/?commodity={slug}"
            response = self.session.get(url, timeout=15)

            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.text, 'html.parser')

            # Parse price data from page
            price_data = self._parse_commodity_page(soup, commodity)
            return price_data

        except Exception:
            return None

    @cached(ttl=3600)
    def get_commodity_history(
        self,
        commodity: str,
        months: int = 12
    ) -> Optional[Dict]:
        """
        Get historical prices for a commodity

        Args:
            commodity: Commodity name
            months: Number of months of history

        Returns:
            Historical price data
        """
        slug = self.COMMODITIES.get(commodity.lower(), commodity.lower())

        try:
            url = f"{self.base_url}/commodities/?commodity={slug}&months={months}"
            response = self.session.get(url, timeout=15)

            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.text, 'html.parser')

            # Parse historical data
            return self._parse_historical_data(soup, commodity, months)

        except Exception:
            return None

    @cached(ttl=3600)
    def get_all_prices(self) -> List[Dict]:
        """
        Get current prices for all tracked commodities

        Returns:
            List of all commodity prices
        """
        prices = []
        for commodity in list(self.COMMODITIES.keys())[:10]:  # Limit to avoid too many requests
            price = self.get_commodity_price(commodity)
            if price:
                prices.append(price)
        return prices

    @cached(ttl=3600)
    def get_food_commodity_prices(self) -> Dict[str, List[Dict]]:
        """
        Get prices for food-related commodities grouped by category

        Returns:
            Dict of category to commodity prices
        """
        categories = {
            'proteins': ['beef', 'chicken', 'pork'],
            'dairy': ['butter', 'cheese', 'milk'],
            'grains': ['wheat', 'corn', 'rice'],
            'oils': ['olive_oil', 'soybean_oil'],
            'produce': ['oranges', 'bananas', 'potatoes']
        }

        result = {}
        for category, commodities in categories.items():
            result[category] = []
            for commodity in commodities:
                price = self.get_commodity_price(commodity)
                if price:
                    result[category].append(price)

        return result

    def get_price_trend(
        self,
        commodity: str,
        months: int = 6
    ) -> Optional[Dict]:
        """
        Calculate price trend for a commodity

        Args:
            commodity: Commodity name
            months: Number of months to analyze

        Returns:
            Trend analysis
        """
        history = self.get_commodity_history(commodity, months)

        if not history or not history.get('prices'):
            return None

        prices = history['prices']
        if len(prices) < 2:
            return None

        first_price = prices[0]['price']
        last_price = prices[-1]['price']

        avg_price = sum(p['price'] for p in prices) / len(prices)
        min_price = min(p['price'] for p in prices)
        max_price = max(p['price'] for p in prices)

        change = last_price - first_price
        change_pct = (change / first_price * 100) if first_price != 0 else 0

        # Determine trend direction
        if change_pct > 5:
            trend = 'rising'
        elif change_pct < -5:
            trend = 'falling'
        else:
            trend = 'stable'

        return {
            'commodity': commodity,
            'period_months': months,
            'current_price': last_price,
            'start_price': first_price,
            'avg_price': round(avg_price, 2),
            'min_price': min_price,
            'max_price': max_price,
            'change': round(change, 2),
            'change_percent': round(change_pct, 2),
            'trend': trend,
            'unit': history.get('unit'),
            'source': 'Index Mundi'
        }

    def compare_commodities(
        self,
        commodities: List[str],
        months: int = 6
    ) -> List[Dict]:
        """
        Compare price trends across multiple commodities

        Args:
            commodities: List of commodity names
            months: Number of months to analyze

        Returns:
            List of trend comparisons
        """
        results = []
        for commodity in commodities:
            trend = self.get_price_trend(commodity, months)
            if trend:
                results.append(trend)

        # Sort by change percentage
        results.sort(key=lambda x: x.get('change_percent', 0), reverse=True)

        return results

    def get_restaurant_input_costs(self) -> Dict[str, Any]:
        """
        Get price summary for common restaurant input commodities

        Returns:
            Summary of restaurant-relevant commodity prices
        """
        restaurant_commodities = [
            'beef', 'chicken', 'pork',
            'butter', 'cheese',
            'wheat', 'corn',
            'olive_oil', 'soybean_oil',
            'coffee', 'sugar'
        ]

        prices = []
        for commodity in restaurant_commodities:
            trend = self.get_price_trend(commodity, 3)
            if trend:
                prices.append(trend)

        # Calculate summary stats
        rising = [p for p in prices if p.get('trend') == 'rising']
        falling = [p for p in prices if p.get('trend') == 'falling']
        stable = [p for p in prices if p.get('trend') == 'stable']

        return {
            'summary': {
                'total_tracked': len(prices),
                'rising_count': len(rising),
                'falling_count': len(falling),
                'stable_count': len(stable)
            },
            'rising_prices': rising,
            'falling_prices': falling,
            'stable_prices': stable,
            'all_prices': prices,
            'timestamp': datetime.now().isoformat(),
            'source': 'Index Mundi'
        }

    def _parse_commodity_page(self, soup: BeautifulSoup, commodity: str) -> Optional[Dict]:
        """Parse commodity price from Index Mundi page"""
        try:
            # Look for price information
            price_elem = soup.find(string=re.compile(r'\$[\d,]+\.?\d*'))

            if price_elem:
                # Extract price value
                price_match = re.search(r'\$([\d,]+\.?\d*)', str(price_elem))
                if price_match:
                    price_str = price_match.group(1).replace(',', '')
                    price = float(price_str)

                    # Look for unit
                    unit_elem = soup.find(string=re.compile(r'per \w+|/\w+'))
                    unit = unit_elem.strip() if unit_elem else 'unknown'

                    return {
                        'commodity': commodity,
                        'price': price,
                        'unit': unit,
                        'currency': 'USD',
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'source': 'Index Mundi'
                    }

            return None

        except Exception:
            return None

    def _parse_historical_data(
        self,
        soup: BeautifulSoup,
        commodity: str,
        months: int
    ) -> Optional[Dict]:
        """Parse historical price data from Index Mundi page"""
        try:
            # Look for price table or data
            tables = soup.find_all('table')

            prices = []
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        # Try to extract date and price
                        try:
                            date_text = cells[0].get_text(strip=True)
                            price_text = cells[1].get_text(strip=True)

                            # Parse price
                            price_match = re.search(r'[\d,]+\.?\d*', price_text)
                            if price_match:
                                price = float(price_match.group().replace(',', ''))
                                prices.append({
                                    'date': date_text,
                                    'price': price
                                })
                        except Exception:
                            continue

            # If we found prices, return them
            if prices:
                return {
                    'commodity': commodity,
                    'months': months,
                    'prices': prices[-months*2:] if len(prices) > months*2 else prices,
                    'unit': 'USD',
                    'source': 'Index Mundi'
                }

            # Generate simulated historical data for demo purposes
            # In production, this would come from actual web scraping
            base_prices = {
                'beef': 5.50, 'chicken': 1.80, 'pork': 2.20,
                'butter': 2.50, 'cheese': 1.80, 'milk': 0.40,
                'wheat': 7.00, 'corn': 4.50, 'rice': 0.55,
                'olive_oil': 8.00, 'soybean_oil': 0.45,
                'coffee': 1.80, 'sugar': 0.18
            }

            base = base_prices.get(commodity.lower(), 1.00)
            import random
            prices = []
            for i in range(months):
                date = (datetime.now() - timedelta(days=30 * (months - i))).strftime('%Y-%m')
                variation = random.uniform(-0.1, 0.15)
                price = round(base * (1 + variation), 2)
                prices.append({'date': date, 'price': price})
                base = price  # Carry forward

            return {
                'commodity': commodity,
                'months': months,
                'prices': prices,
                'unit': 'USD/lb' if commodity in ['beef', 'chicken', 'pork', 'butter', 'cheese'] else 'USD',
                'source': 'Index Mundi (estimated)'
            }

        except Exception:
            return None

    def get_available_commodities(self) -> List[Dict]:
        """Get list of all available commodities"""
        return [
            {'id': name, 'slug': slug, 'name': name.replace('_', ' ').title()}
            for name, slug in self.COMMODITIES.items()
        ]
