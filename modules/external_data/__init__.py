"""
External Data Sources Module
============================
Integrates free third-party APIs and data sources for The Lariat Bible.

Available Data Sources:
- USDA FoodData Central (nutritional data, ingredients)
- Open Food Facts (product database, barcodes)
- Spoonacular API (recipes, ingredients, costs)
- Edamam API (nutritional analysis, food database)
- USDA Market News (commodity prices)
- LocalHarvest/Colorado Proud (local suppliers)
- UPC/Barcode databases (product lookup)
- Index Mundi (commodity price trends)
"""

from .usda_fooddata import USDAFoodDataClient
from .open_food_facts import OpenFoodFactsClient
from .spoonacular import SpoonacularClient
from .edamam import EdamamClient
from .usda_market_news import USDAMarketNewsClient
from .local_suppliers import LocalSuppliersClient
from .barcode_lookup import BarcodeLookupClient
from .commodity_prices import CommodityPricesClient
from .aggregator import ExternalDataAggregator

__all__ = [
    'USDAFoodDataClient',
    'OpenFoodFactsClient',
    'SpoonacularClient',
    'EdamamClient',
    'USDAMarketNewsClient',
    'LocalSuppliersClient',
    'BarcodeLookupClient',
    'CommodityPricesClient',
    'ExternalDataAggregator'
]
