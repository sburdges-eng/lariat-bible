#!/usr/bin/env python
"""
The Lariat Bible - Main Application
Restaurant Management System Web Interface

Includes integration with FREE external data sources:
- USDA FoodData Central (nutrition)
- Open Food Facts (products, barcodes)
- Spoonacular (recipes, ingredients)
- Edamam (recipes, nutrition)
- USDA Market News (commodity prices)
- LocalHarvest/Colorado Proud (local suppliers)
- Barcode databases (UPC lookup)
- Index Mundi (commodity trends)
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
CORS(app)

# Import modules (when implemented)
try:
    from modules.vendor_analysis import VendorComparator
    vendor_comparator = VendorComparator()
except ImportError:
    vendor_comparator = None

# Import external data aggregator
try:
    from modules.external_data import ExternalDataAggregator
    external_data = ExternalDataAggregator()
except ImportError as e:
    print(f"Warning: External data module not available: {e}")
    external_data = None


# =============================================================================
# CORE ROUTES
# =============================================================================

@app.route('/')
def index():
    """Main dashboard"""
    return jsonify({
        'message': 'Welcome to The Lariat Bible',
        'status': 'operational',
        'modules': {
            'vendor_analysis': 'ready' if vendor_comparator else 'pending',
            'external_data': 'ready' if external_data else 'pending',
            'inventory': 'pending',
            'recipes': 'pending',
            'catering': 'pending',
            'maintenance': 'pending',
            'reporting': 'pending'
        },
        'metrics': {
            'monthly_catering_revenue': 28000,
            'monthly_restaurant_revenue': 20000,
            'potential_annual_savings': 52000
        },
        'external_data_sources': [
            'USDA FoodData Central',
            'Open Food Facts',
            'Spoonacular',
            'Edamam',
            'USDA Market News',
            'LocalHarvest',
            'Colorado Proud',
            'Barcode Lookup',
            'Index Mundi'
        ] if external_data else []
    })


@app.route('/api/vendor-comparison')
def vendor_comparison():
    """Get vendor comparison data"""
    if vendor_comparator:
        savings = vendor_comparator.compare_vendors('Shamrock Foods', 'SYSCO')
        margin_impact = vendor_comparator.calculate_margin_impact(savings)

        return jsonify({
            'monthly_savings': savings,
            'annual_savings': savings * 12,
            'margin_impact': margin_impact,
            'timestamp': datetime.now().isoformat()
        })

    return jsonify({'error': 'Vendor analysis module not available'}), 503


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'restaurant': os.getenv('RESTAURANT_NAME', 'The Lariat'),
        'external_data_available': external_data is not None
    })


@app.route('/api/modules')
def list_modules():
    """List all available modules and their status"""
    modules = [
        {
            'name': 'Vendor Analysis',
            'endpoint': '/api/vendor-analysis',
            'status': 'active' if vendor_comparator else 'development',
            'description': 'Compare vendor prices and identify savings'
        },
        {
            'name': 'External Data Sources',
            'endpoint': '/api/external-data',
            'status': 'active' if external_data else 'development',
            'description': 'Access FREE third-party data sources for ingredients, products, prices'
        },
        {
            'name': 'Inventory Management',
            'endpoint': '/api/inventory',
            'status': 'development',
            'description': 'Track stock levels and automate ordering'
        },
        {
            'name': 'Recipe Management',
            'endpoint': '/api/recipes',
            'status': 'development',
            'description': 'Standardize recipes and calculate costs'
        },
        {
            'name': 'Catering Operations',
            'endpoint': '/api/catering',
            'status': 'development',
            'description': 'Manage catering quotes and events'
        },
        {
            'name': 'Maintenance Tracking',
            'endpoint': '/api/maintenance',
            'status': 'development',
            'description': 'Schedule and track equipment maintenance'
        },
        {
            'name': 'Reporting Dashboard',
            'endpoint': '/api/reports',
            'status': 'development',
            'description': 'Business intelligence and analytics'
        }
    ]

    return jsonify(modules)


# =============================================================================
# EXTERNAL DATA ROUTES
# =============================================================================

@app.route('/api/external-data/status')
def external_data_status():
    """Get status of all external data sources"""
    if not external_data:
        return jsonify({'error': 'External data module not available'}), 503

    return jsonify(external_data.get_status())


@app.route('/api/external-data/search')
def external_data_search():
    """
    Search across all external data sources

    Query params:
        q: Search query (required)
        sources: Comma-separated list of sources (optional)
        limit: Max results per source (default: 5)
    """
    if not external_data:
        return jsonify({'error': 'External data module not available'}), 503

    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400

    sources = request.args.get('sources')
    sources_list = sources.split(',') if sources else None
    limit = int(request.args.get('limit', 5))

    results = external_data.search_all(query, sources=sources_list, limit_per_source=limit)
    return jsonify({
        'query': query,
        'results': results,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/external-data/ingredients/search')
def search_ingredients():
    """
    Search for ingredient information

    Query params:
        q: Ingredient name (required)
    """
    if not external_data:
        return jsonify({'error': 'External data module not available'}), 503

    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400

    return jsonify(external_data.search_ingredients(query))


@app.route('/api/external-data/ingredients/nutrition')
def get_ingredient_nutrition():
    """
    Get nutritional information for an ingredient

    Query params:
        ingredient: Ingredient name (required)
        amount: Amount (default: 100)
        unit: Unit of measurement (default: g)
    """
    if not external_data:
        return jsonify({'error': 'External data module not available'}), 503

    ingredient = request.args.get('ingredient')
    if not ingredient:
        return jsonify({'error': 'Query parameter "ingredient" is required'}), 400

    amount = float(request.args.get('amount', 100))
    unit = request.args.get('unit', 'g')

    return jsonify(external_data.get_nutrition(ingredient, amount, unit))


@app.route('/api/external-data/ingredients/substitutes')
def get_ingredient_substitutes():
    """
    Get substitutes for an ingredient

    Query params:
        ingredient: Ingredient name (required)
    """
    if not external_data:
        return jsonify({'error': 'External data module not available'}), 503

    ingredient = request.args.get('ingredient')
    if not ingredient:
        return jsonify({'error': 'Query parameter "ingredient" is required'}), 400

    return jsonify(external_data.get_ingredient_substitutes(ingredient))


@app.route('/api/external-data/products/search')
def search_products():
    """
    Search for product information

    Query params:
        q: Product name or barcode (required)
    """
    if not external_data:
        return jsonify({'error': 'External data module not available'}), 503

    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400

    return jsonify(external_data.search_products(query))


@app.route('/api/external-data/products/barcode/<barcode>')
def lookup_barcode(barcode):
    """Look up product by barcode"""
    if not external_data:
        return jsonify({'error': 'External data module not available'}), 503

    return jsonify(external_data.lookup_barcode(barcode))


@app.route('/api/external-data/recipes/search')
def search_recipes():
    """
    Search for recipes

    Query params:
        q: Search query (required)
        cuisine: Cuisine type (optional)
        diet: Diet type (optional)
    """
    if not external_data:
        return jsonify({'error': 'External data module not available'}), 503

    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400

    cuisine = request.args.get('cuisine')
    diet = request.args.get('diet')

    return jsonify(external_data.search_recipes(query, cuisine=cuisine, diet=diet))


@app.route('/api/external-data/recipes/analyze', methods=['POST'])
def analyze_recipe():
    """
    Analyze nutrition for a recipe

    JSON body:
        ingredients: List of ingredient strings (required)
        title: Recipe title (optional)
    """
    if not external_data:
        return jsonify({'error': 'External data module not available'}), 503

    data = request.get_json()
    if not data or 'ingredients' not in data:
        return jsonify({'error': 'JSON body with "ingredients" array is required'}), 400

    ingredients = data['ingredients']
    title = data.get('title', 'Recipe')

    return jsonify(external_data.analyze_recipe_nutrition(ingredients, title))


@app.route('/api/external-data/prices/commodities')
def get_commodity_prices():
    """
    Get commodity price trends

    Query params:
        commodities: Comma-separated list (optional, default: common food items)
    """
    if not external_data:
        return jsonify({'error': 'External data module not available'}), 503

    commodities = request.args.get('commodities')
    commodities_list = commodities.split(',') if commodities else None

    return jsonify(external_data.get_commodity_prices(commodities_list))


@app.route('/api/external-data/prices/market')
def get_market_prices():
    """
    Get USDA market prices

    Query params:
        category: Price category (beef, pork, poultry, dairy, all)
    """
    if not external_data:
        return jsonify({'error': 'External data module not available'}), 503

    category = request.args.get('category', 'all')

    return jsonify(external_data.get_market_prices(category))


@app.route('/api/external-data/prices/summary')
def get_price_summary():
    """Get comprehensive restaurant input cost summary"""
    if not external_data:
        return jsonify({'error': 'External data module not available'}), 503

    return jsonify(external_data.get_restaurant_input_summary())


@app.route('/api/external-data/suppliers/local')
def find_local_suppliers():
    """
    Find local food suppliers

    Query params:
        category: Product category (optional)
        city: City name (default: Fort Collins)
        state: State abbreviation (default: CO)
        radius: Search radius in miles (default: 25)
    """
    if not external_data:
        return jsonify({'error': 'External data module not available'}), 503

    category = request.args.get('category')
    city = request.args.get('city', 'Fort Collins')
    state = request.args.get('state', 'CO')
    radius = int(request.args.get('radius', 25))

    return jsonify(external_data.find_local_suppliers(
        category=category,
        city=city,
        state=state,
        radius=radius
    ))


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    print(f"\n The Lariat Bible - Starting server...")
    print(f" Access at: http://{host}:{port}")
    print(f" API Health: http://{host}:{port}/api/health")
    print(f" Debug mode: {debug}")

    if external_data:
        print(f"\n External Data Sources Available:")
        print(f"   - USDA FoodData Central (nutrition, ingredients)")
        print(f"   - Open Food Facts (products, barcodes)")
        print(f"   - Spoonacular (recipes, costs)")
        print(f"   - Edamam (recipe analysis)")
        print(f"   - USDA Market News (commodity prices)")
        print(f"   - LocalHarvest (local suppliers)")
        print(f"   - Index Mundi (price trends)")
        print(f"\n API Endpoints:")
        print(f"   GET /api/external-data/status")
        print(f"   GET /api/external-data/search?q=<query>")
        print(f"   GET /api/external-data/ingredients/search?q=<ingredient>")
        print(f"   GET /api/external-data/products/barcode/<barcode>")
        print(f"   GET /api/external-data/prices/commodities")
        print(f"   GET /api/external-data/suppliers/local")

    print("\nPress Ctrl+C to stop the server\n")

    app.run(host=host, port=port, debug=debug)
