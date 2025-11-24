"""
External Data Aggregator
=========================
Unified interface for all external data sources.

Aggregates data from:
- USDA FoodData Central (nutrition)
- Open Food Facts (products, barcodes)
- Spoonacular (recipes, ingredients)
- Edamam (recipes, nutrition analysis)
- USDA Market News (commodity prices)
- LocalHarvest/Colorado Proud (local suppliers)
- Barcode databases (UPC lookup)
- Index Mundi (commodity trends)
"""

from typing import Any, Dict, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from .config import validate_api_keys, get_config
from .usda_fooddata import USDAFoodDataClient
from .open_food_facts import OpenFoodFactsClient
from .spoonacular import SpoonacularClient
from .edamam import EdamamClient
from .usda_market_news import USDAMarketNewsClient
from .local_suppliers import LocalSuppliersClient
from .barcode_lookup import BarcodeLookupClient
from .commodity_prices import CommodityPricesClient


class ExternalDataAggregator:
    """
    Unified interface for all external data sources.

    Provides:
    - Parallel searches across all sources
    - Data normalization
    - Source health monitoring
    - Automatic fallback between sources
    """

    def __init__(self):
        """Initialize all data source clients"""
        self.usda_fooddata = USDAFoodDataClient()
        self.open_food_facts = OpenFoodFactsClient()
        self.spoonacular = SpoonacularClient()
        self.edamam = EdamamClient()
        self.usda_market_news = USDAMarketNewsClient()
        self.local_suppliers = LocalSuppliersClient()
        self.barcode_lookup = BarcodeLookupClient()
        self.commodity_prices = CommodityPricesClient()

        # All clients for iteration
        self._clients = {
            'usda_fooddata': self.usda_fooddata,
            'open_food_facts': self.open_food_facts,
            'spoonacular': self.spoonacular,
            'edamam': self.edamam,
            'usda_market_news': self.usda_market_news,
            'local_suppliers': self.local_suppliers,
            'barcode_lookup': self.barcode_lookup,
            'commodity_prices': self.commodity_prices
        }

    def get_status(self) -> Dict[str, Any]:
        """
        Get status of all data sources

        Returns:
            Status report for all sources
        """
        api_keys = validate_api_keys()
        status = {
            'timestamp': datetime.now().isoformat(),
            'api_keys_configured': api_keys,
            'sources': {}
        }

        # Check each source
        for name, client in self._clients.items():
            try:
                health = client.health_check()
                status['sources'][name] = health
            except Exception as e:
                status['sources'][name] = {
                    'available': False,
                    'error': str(e)
                }

        # Summary
        available = sum(1 for s in status['sources'].values() if s.get('available'))
        status['summary'] = {
            'total_sources': len(self._clients),
            'available_sources': available,
            'unavailable_sources': len(self._clients) - available
        }

        return status

    def search_all(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        limit_per_source: int = 5
    ) -> Dict[str, List[Dict]]:
        """
        Search across all data sources in parallel

        Args:
            query: Search term
            sources: Specific sources to search (default: all)
            limit_per_source: Maximum results per source

        Returns:
            Dict of source name to results
        """
        results = {}
        sources_to_search = sources or list(self._clients.keys())

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {}
            for source_name in sources_to_search:
                if source_name in self._clients:
                    client = self._clients[source_name]
                    futures[executor.submit(
                        self._safe_search,
                        client,
                        query,
                        limit_per_source
                    )] = source_name

            for future in as_completed(futures):
                source_name = futures[future]
                try:
                    results[source_name] = future.result()
                except Exception as e:
                    results[source_name] = {'error': str(e)}

        return results

    def search_ingredients(self, query: str) -> Dict[str, Any]:
        """
        Search for ingredient information

        Searches USDA, Open Food Facts, and Spoonacular for ingredient data.

        Args:
            query: Ingredient name

        Returns:
            Aggregated ingredient data
        """
        results = self.search_all(
            query,
            sources=['usda_fooddata', 'open_food_facts', 'spoonacular'],
            limit_per_source=5
        )

        # Merge and deduplicate results
        all_ingredients = []
        for source, data in results.items():
            if isinstance(data, list):
                all_ingredients.extend(data)

        return {
            'query': query,
            'results': all_ingredients,
            'by_source': results,
            'total_results': len(all_ingredients)
        }

    def search_products(self, query: str) -> Dict[str, Any]:
        """
        Search for product information

        Searches Open Food Facts and barcode databases.

        Args:
            query: Product name or barcode

        Returns:
            Aggregated product data
        """
        # Check if query looks like a barcode
        if query.isdigit() and len(query) >= 8:
            product = self.barcode_lookup.lookup(query)
            return {
                'query': query,
                'type': 'barcode',
                'product': product,
                'found': product is not None
            }

        # Search by name
        results = self.search_all(
            query,
            sources=['open_food_facts', 'barcode_lookup'],
            limit_per_source=10
        )

        all_products = []
        for source, data in results.items():
            if isinstance(data, list):
                all_products.extend(data)

        return {
            'query': query,
            'type': 'search',
            'results': all_products,
            'by_source': results,
            'total_results': len(all_products)
        }

    def search_recipes(
        self,
        query: str,
        cuisine: Optional[str] = None,
        diet: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for recipes

        Searches Spoonacular and Edamam for recipes.

        Args:
            query: Recipe search term
            cuisine: Cuisine type filter
            diet: Diet type filter

        Returns:
            Aggregated recipe results
        """
        results = {}

        # Search Spoonacular
        try:
            spoon_results = self.spoonacular.search_recipes(
                query, cuisine=cuisine, diet=diet, number=10
            )
            results['spoonacular'] = spoon_results
        except Exception as e:
            results['spoonacular'] = {'error': str(e)}

        # Search Edamam
        try:
            edamam_results = self.edamam.search_recipes(
                query,
                cuisine_type=[cuisine] if cuisine else None,
                diet=[diet] if diet else None,
                num_results=10
            )
            results['edamam'] = edamam_results
        except Exception as e:
            results['edamam'] = {'error': str(e)}

        # Merge results
        all_recipes = []
        for source, data in results.items():
            if isinstance(data, list):
                all_recipes.extend(data)

        return {
            'query': query,
            'filters': {'cuisine': cuisine, 'diet': diet},
            'results': all_recipes,
            'by_source': results,
            'total_results': len(all_recipes)
        }

    def get_nutrition(
        self,
        ingredient: str,
        amount: float = 100,
        unit: str = 'g'
    ) -> Dict[str, Any]:
        """
        Get nutritional information for an ingredient

        Args:
            ingredient: Ingredient name
            amount: Amount of ingredient
            unit: Unit of measurement

        Returns:
            Nutritional data from available sources
        """
        results = {}

        # Try USDA FoodData Central
        try:
            usda_results = self.usda_fooddata.search_ingredients(ingredient)
            if usda_results:
                # Get detailed nutrition for first result
                fdc_id = usda_results[0].get('fdc_id')
                if fdc_id:
                    nutrition = self.usda_fooddata.get_nutrition_facts(fdc_id)
                    results['usda'] = nutrition
        except Exception as e:
            results['usda'] = {'error': str(e)}

        # Try Spoonacular
        try:
            spoon_results = self.spoonacular.search_ingredients(ingredient, number=1)
            if spoon_results:
                ing_id = spoon_results[0].get('id')
                if ing_id:
                    info = self.spoonacular.get_ingredient_info(ing_id, amount, unit)
                    results['spoonacular'] = info
        except Exception as e:
            results['spoonacular'] = {'error': str(e)}

        return {
            'ingredient': ingredient,
            'amount': amount,
            'unit': unit,
            'nutrition': results
        }

    def get_commodity_prices(
        self,
        commodities: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get current commodity prices

        Args:
            commodities: Specific commodities to check (default: common food items)

        Returns:
            Commodity price data
        """
        if not commodities:
            commodities = ['beef', 'chicken', 'pork', 'butter', 'wheat', 'corn']

        results = {
            'timestamp': datetime.now().isoformat(),
            'commodities': {}
        }

        for commodity in commodities:
            try:
                trend = self.commodity_prices.get_price_trend(commodity, months=3)
                results['commodities'][commodity] = trend
            except Exception as e:
                results['commodities'][commodity] = {'error': str(e)}

        return results

    def get_market_prices(self, category: str = 'all') -> Dict[str, Any]:
        """
        Get USDA market prices

        Args:
            category: Price category ('beef', 'pork', 'poultry', 'dairy', 'produce', 'all')

        Returns:
            Market price data
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'prices': {}
        }

        try:
            if category == 'all' or category == 'beef':
                results['prices']['beef'] = self.usda_market_news.get_beef_prices()
            if category == 'all' or category == 'pork':
                results['prices']['pork'] = self.usda_market_news.get_pork_prices()
            if category == 'all' or category == 'poultry':
                results['prices']['poultry'] = self.usda_market_news.get_poultry_prices()
            if category == 'all' or category == 'dairy':
                results['prices']['dairy'] = self.usda_market_news.get_dairy_prices()
        except Exception as e:
            results['error'] = str(e)

        return results

    def find_local_suppliers(
        self,
        category: Optional[str] = None,
        city: str = "Fort Collins",
        state: str = "CO",
        radius: int = 25
    ) -> Dict[str, Any]:
        """
        Find local food suppliers

        Args:
            category: Product category (produce, meat, dairy, etc.)
            city: City to search near
            state: State
            radius: Search radius in miles

        Returns:
            Local supplier data
        """
        results = {
            'location': f"{city}, {state}",
            'radius': radius,
            'suppliers': []
        }

        try:
            if category:
                suppliers = self.local_suppliers.search(category, location=f"{city}, {state}")
            else:
                suppliers = self.local_suppliers.get_farms_near_location(city, state, radius)

            results['suppliers'] = suppliers
            results['count'] = len(suppliers)

            # Also get farmers markets
            markets = self.local_suppliers.get_farmers_markets(city, state)
            results['farmers_markets'] = markets

        except Exception as e:
            results['error'] = str(e)

        return results

    def lookup_barcode(self, barcode: str) -> Dict[str, Any]:
        """
        Look up product by barcode

        Args:
            barcode: Product barcode (UPC/EAN)

        Returns:
            Product information
        """
        # Validate barcode first
        validation = self.barcode_lookup.validate_barcode(barcode)

        if not validation.get('valid'):
            return {
                'barcode': barcode,
                'valid': False,
                'error': validation.get('error')
            }

        # Look up product
        product = self.barcode_lookup.lookup(barcode)

        return {
            'barcode': barcode,
            'valid': True,
            'barcode_type': validation.get('type'),
            'found': product is not None,
            'product': product
        }

    def get_ingredient_substitutes(self, ingredient: str) -> Dict[str, Any]:
        """
        Get substitutes for an ingredient

        Args:
            ingredient: Ingredient name

        Returns:
            List of possible substitutes
        """
        result = {
            'ingredient': ingredient,
            'substitutes': []
        }

        try:
            subs = self.spoonacular.get_ingredient_substitutes(ingredient)
            if subs:
                result['substitutes'] = subs.get('substitutes', [])
                result['message'] = subs.get('message')
        except Exception as e:
            result['error'] = str(e)

        return result

    def analyze_recipe_nutrition(
        self,
        ingredients: List[str],
        title: str = "Recipe"
    ) -> Dict[str, Any]:
        """
        Analyze nutrition for a recipe

        Args:
            ingredients: List of ingredient strings (e.g., ['1 cup flour', '2 eggs'])
            title: Recipe title

        Returns:
            Nutritional analysis
        """
        try:
            analysis = self.edamam.analyze_nutrition(ingredients, title)
            return {
                'title': title,
                'ingredients': ingredients,
                'analysis': analysis,
                'success': analysis is not None
            }
        except Exception as e:
            return {
                'title': title,
                'ingredients': ingredients,
                'error': str(e),
                'success': False
            }

    def get_restaurant_input_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of restaurant input costs

        Returns:
            Summary of commodity prices, market data, and trends
        """
        result = {
            'timestamp': datetime.now().isoformat(),
            'commodity_trends': {},
            'market_prices': {},
            'local_suppliers': {},
            'summary': {}
        }

        try:
            # Commodity price trends
            result['commodity_trends'] = self.commodity_prices.get_restaurant_input_costs()
        except Exception as e:
            result['commodity_trends'] = {'error': str(e)}

        try:
            # USDA market prices
            result['market_prices'] = self.get_market_prices('all')
        except Exception as e:
            result['market_prices'] = {'error': str(e)}

        try:
            # Local suppliers count
            suppliers = self.local_suppliers.get_farms_near_location('Fort Collins', 'CO', 25)
            result['local_suppliers'] = {
                'count': len(suppliers),
                'sample': suppliers[:5] if suppliers else []
            }
        except Exception as e:
            result['local_suppliers'] = {'error': str(e)}

        return result

    def _safe_search(
        self,
        client,
        query: str,
        limit: int
    ) -> List[Dict]:
        """Safely execute search on a client"""
        try:
            results = client.search(query)
            return results[:limit] if isinstance(results, list) else []
        except Exception:
            return []
