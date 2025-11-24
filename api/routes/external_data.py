"""
External Data Routes
=====================
Access external data sources (nutrition, prices, suppliers).
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
import sys
import os

router = APIRouter()

# Import external data module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from modules.external_data import ExternalDataAggregator
    aggregator = ExternalDataAggregator()
except ImportError:
    aggregator = None


class NutritionRequest(BaseModel):
    ingredients: List[str]
    title: str = "Recipe"


@router.get("/status")
async def get_external_data_status():
    """Get status of all external data sources"""
    if not aggregator:
        return {"error": "External data module not available", "available": False}

    return aggregator.get_status()


@router.get("/search")
async def search_all_sources(
    q: str,
    sources: Optional[str] = None,
    limit: int = 5
):
    """Search across all external data sources"""
    if not aggregator:
        raise HTTPException(status_code=503, detail="External data not available")

    sources_list = sources.split(',') if sources else None
    return aggregator.search_all(q, sources=sources_list, limit_per_source=limit)


@router.get("/ingredients/search")
async def search_ingredients(q: str):
    """Search for ingredient information"""
    if not aggregator:
        raise HTTPException(status_code=503, detail="External data not available")

    return aggregator.search_ingredients(q)


@router.get("/ingredients/nutrition")
async def get_ingredient_nutrition(
    ingredient: str,
    amount: float = 100,
    unit: str = "g"
):
    """Get nutritional information for an ingredient"""
    if not aggregator:
        raise HTTPException(status_code=503, detail="External data not available")

    return aggregator.get_nutrition(ingredient, amount, unit)


@router.get("/ingredients/substitutes")
async def get_ingredient_substitutes(ingredient: str):
    """Get substitutes for an ingredient"""
    if not aggregator:
        raise HTTPException(status_code=503, detail="External data not available")

    return aggregator.get_ingredient_substitutes(ingredient)


@router.get("/products/search")
async def search_products(q: str):
    """Search for product information"""
    if not aggregator:
        raise HTTPException(status_code=503, detail="External data not available")

    return aggregator.search_products(q)


@router.get("/products/barcode/{barcode}")
async def lookup_barcode(barcode: str):
    """Look up product by barcode"""
    if not aggregator:
        raise HTTPException(status_code=503, detail="External data not available")

    return aggregator.lookup_barcode(barcode)


@router.get("/recipes/search")
async def search_recipes(
    q: str,
    cuisine: Optional[str] = None,
    diet: Optional[str] = None
):
    """Search for recipes from external sources"""
    if not aggregator:
        raise HTTPException(status_code=503, detail="External data not available")

    return aggregator.search_recipes(q, cuisine=cuisine, diet=diet)


@router.post("/recipes/analyze")
async def analyze_recipe_nutrition(data: NutritionRequest):
    """Analyze nutrition for a recipe"""
    if not aggregator:
        raise HTTPException(status_code=503, detail="External data not available")

    return aggregator.analyze_recipe_nutrition(data.ingredients, data.title)


@router.get("/prices/commodities")
async def get_commodity_prices(commodities: Optional[str] = None):
    """Get commodity price trends"""
    if not aggregator:
        raise HTTPException(status_code=503, detail="External data not available")

    commodities_list = commodities.split(',') if commodities else None
    return aggregator.get_commodity_prices(commodities_list)


@router.get("/prices/market")
async def get_market_prices(category: str = "all"):
    """Get USDA market prices"""
    if not aggregator:
        raise HTTPException(status_code=503, detail="External data not available")

    return aggregator.get_market_prices(category)


@router.get("/prices/summary")
async def get_price_summary():
    """Get comprehensive restaurant input cost summary"""
    if not aggregator:
        raise HTTPException(status_code=503, detail="External data not available")

    return aggregator.get_restaurant_input_summary()


@router.get("/suppliers/local")
async def find_local_suppliers(
    category: Optional[str] = None,
    city: str = "Fort Collins",
    state: str = "CO",
    radius: int = 25
):
    """Find local food suppliers"""
    if not aggregator:
        raise HTTPException(status_code=503, detail="External data not available")

    return aggregator.find_local_suppliers(
        category=category,
        city=city,
        state=state,
        radius=radius
    )
