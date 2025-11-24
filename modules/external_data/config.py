"""
External Data Sources Configuration
====================================
Centralized configuration for all external API integrations.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class APIConfig:
    """Configuration for external API connections"""

    # USDA FoodData Central - FREE (requires API key signup)
    # Get your free key at: https://fdc.nal.usda.gov/api-key-signup.html
    USDA_FOODDATA_API_KEY: str = os.getenv('USDA_FOODDATA_API_KEY', '')
    USDA_FOODDATA_BASE_URL: str = 'https://api.nal.usda.gov/fdc/v1'

    # Open Food Facts - FREE (no API key required)
    OPEN_FOOD_FACTS_BASE_URL: str = 'https://world.openfoodfacts.org/api/v2'
    OPEN_FOOD_FACTS_USER_AGENT: str = 'LariatBible/1.0 (restaurant management system)'

    # Spoonacular - FREE tier (150 requests/day)
    # Get your free key at: https://spoonacular.com/food-api/console
    SPOONACULAR_API_KEY: str = os.getenv('SPOONACULAR_API_KEY', '')
    SPOONACULAR_BASE_URL: str = 'https://api.spoonacular.com'

    # Edamam - FREE tier (1000 calls/month)
    # Get your free key at: https://developer.edamam.com/edamam-recipe-api
    EDAMAM_APP_ID: str = os.getenv('EDAMAM_APP_ID', '')
    EDAMAM_APP_KEY: str = os.getenv('EDAMAM_APP_KEY', '')
    EDAMAM_BASE_URL: str = 'https://api.edamam.com/api'

    # USDA Market News - FREE (no API key required)
    USDA_MARKET_NEWS_BASE_URL: str = 'https://marsapi.ams.usda.gov/services/v1.2'

    # LocalHarvest - FREE (web scraping)
    LOCAL_HARVEST_BASE_URL: str = 'https://www.localharvest.org'

    # Colorado Proud - FREE (web scraping)
    COLORADO_PROUD_BASE_URL: str = 'https://www.coloradoproud.org'

    # UPC Database - FREE tier
    UPC_DATABASE_BASE_URL: str = 'https://api.upcdatabase.org'
    UPC_DATABASE_API_KEY: str = os.getenv('UPC_DATABASE_API_KEY', '')

    # Barcode Lookup - FREE tier (limited)
    BARCODE_LOOKUP_BASE_URL: str = 'https://api.barcodelookup.com/v3'
    BARCODE_LOOKUP_API_KEY: str = os.getenv('BARCODE_LOOKUP_API_KEY', '')

    # Open Product Data - FREE (no API key required)
    OPEN_PRODUCT_DATA_BASE_URL: str = 'https://product-open-data.com/api'

    # Index Mundi - FREE (web scraping for commodity prices)
    INDEX_MUNDI_BASE_URL: str = 'https://www.indexmundi.com'

    # Request settings
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0

    # Cache settings (in seconds)
    CACHE_TTL_SHORT: int = 300       # 5 minutes
    CACHE_TTL_MEDIUM: int = 3600     # 1 hour
    CACHE_TTL_LONG: int = 86400      # 24 hours
    CACHE_TTL_WEEK: int = 604800     # 7 days


# Default configuration instance
config = APIConfig()


def get_config() -> APIConfig:
    """Get the current API configuration"""
    return config


def validate_api_keys() -> dict:
    """Validate which API keys are configured"""
    return {
        'usda_fooddata': bool(config.USDA_FOODDATA_API_KEY),
        'open_food_facts': True,  # No key required
        'spoonacular': bool(config.SPOONACULAR_API_KEY),
        'edamam': bool(config.EDAMAM_APP_ID and config.EDAMAM_APP_KEY),
        'usda_market_news': True,  # No key required
        'local_harvest': True,  # Web scraping
        'colorado_proud': True,  # Web scraping
        'upc_database': bool(config.UPC_DATABASE_API_KEY),
        'barcode_lookup': bool(config.BARCODE_LOOKUP_API_KEY),
        'open_product_data': True,  # No key required
        'index_mundi': True,  # Web scraping
    }
