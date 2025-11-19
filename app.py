#!/usr/bin/env python
"""
The Lariat Bible - Main Application
Restaurant Management System Web Interface
"""

from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import os
from dotenv import load_dotenv
from datetime import datetime
from io import BytesIO

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
CORS(app)

# Import modules
try:
    from modules.vendor_analysis import VendorComparator
    vendor_comparator = VendorComparator()
except ImportError:
    vendor_comparator = None

try:
    from modules.core.excel_handler import excel_handler
except ImportError:
    excel_handler = None

# ========================================
# Page Routes
# ========================================

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/vendor-analysis')
def vendor_analysis_page():
    """Vendor analysis page"""
    return render_template('vendor_analysis.html')

@app.route('/price-comparison')
def price_comparison_page():
    """Price comparison page"""
    return render_template('price_comparison.html')

@app.route('/order-guides')
def order_guides_page():
    """Order guides page"""
    return render_template('order_guides.html')

@app.route('/profit-calculator')
def profit_calculator_page():
    """Profit calculator page"""
    return render_template('profit_calculator.html')

@app.route('/recipe-costing')
def recipe_costing_page():
    """Recipe costing page"""
    return render_template('recipe_costing.html')

# ========================================
# API Routes - Vendor Analysis
# ========================================

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

@app.route('/api/vendor-comparison/detailed')
def vendor_comparison_detailed():
    """Get detailed vendor comparison with product breakdown"""
    # Sample data - replace with actual comparison logic
    comparison_data = [
        {
            'product': 'Black Pepper Fine 25lb',
            'vendor_a': 'SYSCO',
            'price_a': 3.25,
            'vendor_b': 'Shamrock Foods',
            'price_b': 2.18,
            'difference': 1.07,
            'savings_percent': 32.9,
            'recommended': 'Shamrock Foods'
        },
        # Add more products here
    ]

    return jsonify({
        'comparison': comparison_data,
        'summary': {
            'total_items': len(comparison_data),
            'total_savings': sum(item['difference'] for item in comparison_data),
            'avg_savings_percent': sum(item['savings_percent'] for item in comparison_data) / len(comparison_data) if comparison_data else 0
        }
    })

# ========================================
# API Routes - Excel Export/Import
# ========================================

@app.route('/api/export/price-comparison', methods=['POST'])
def export_price_comparison():
    """Export price comparison to Excel"""
    if not excel_handler:
        return jsonify({'error': 'Excel handler not available'}), 503

    # Sample data - replace with actual data
    comparison_data = [
        {
            'product': 'Black Pepper Fine 25lb',
            'vendor_a': 'SYSCO',
            'price_a': 3.25,
            'vendor_b': 'Shamrock Foods',
            'price_b': 2.18,
            'difference': 1.07,
            'savings_percent': 32.9,
            'recommended': 'Shamrock Foods'
        },
    ]

    excel_file = excel_handler.export_price_comparison(comparison_data)

    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'price_comparison_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )

@app.route('/api/export/order-guide', methods=['POST'])
def export_order_guide():
    """Export order guide to Excel"""
    if not excel_handler:
        return jsonify({'error': 'Excel handler not available'}), 503

    data = request.json or {}
    vendor_name = data.get('vendor', 'Vendor')

    # Sample order guide data
    items = [
        {
            'item_code': '12345',
            'description': 'Black Pepper Fine',
            'pack_size': '25 LB',
            'case_price': 54.99,
            'unit_price': 2.20,
            'unit': 'LB',
            'category': 'Spices',
            'last_updated': datetime.now().strftime('%Y-%m-%d')
        },
    ]

    excel_file = excel_handler.export_order_guide(items, vendor_name)

    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'order_guide_{vendor_name.lower().replace(" ", "_")}_{datetime.now().strftime("%Y%m%d")}.xlsx'
    )

@app.route('/api/export/savings-opportunities', methods=['POST'])
def export_savings_opportunities():
    """Export top savings opportunities to Excel"""
    if not excel_handler:
        return jsonify({'error': 'Excel handler not available'}), 503

    # Sample opportunities data
    opportunities = [
        {
            'product': 'Black Pepper Fine',
            'current_vendor': 'SYSCO',
            'current_price': 3.25,
            'best_vendor': 'Shamrock Foods',
            'best_price': 2.18,
            'savings': 1.07,
            'savings_percent': 32.9,
            'monthly_usage': 10
        },
    ]

    excel_file = excel_handler.export_savings_opportunities(opportunities)

    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'savings_opportunities_{datetime.now().strftime("%Y%m%d")}.xlsx'
    )

@app.route('/api/export/recipe-costs', methods=['POST'])
def export_recipe_costs():
    """Export recipe cost analysis to Excel"""
    if not excel_handler:
        return jsonify({'error': 'Excel handler not available'}), 503

    # Sample recipe data
    recipes = [
        {
            'name': 'BBQ Sandwich',
            'category': 'Entree',
            'servings': 1,
            'ingredient_cost': 4.50,
            'ingredients': [
                {'name': 'Brisket', 'quantity': 8, 'unit': 'oz', 'price_per_unit': 0.50, 'total_cost': 4.00},
                {'name': 'BBQ Sauce', 'quantity': 2, 'unit': 'oz', 'price_per_unit': 0.15, 'total_cost': 0.30},
                {'name': 'Bun', 'quantity': 1, 'unit': 'each', 'price_per_unit': 0.20, 'total_cost': 0.20},
            ]
        },
    ]

    excel_file = excel_handler.export_recipe_costs(recipes)

    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'recipe_costs_{datetime.now().strftime("%Y%m%d")}.xlsx'
    )

@app.route('/api/template/<template_type>')
def download_template(template_type):
    """Download import template"""
    if not excel_handler:
        return jsonify({'error': 'Excel handler not available'}), 503

    valid_types = ['price_list', 'order_guide', 'recipe']
    if template_type not in valid_types:
        return jsonify({'error': 'Invalid template type'}), 400

    excel_file = excel_handler.create_import_template(template_type)

    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'{template_type}_template.xlsx'
    )

@app.route('/api/import/price-list', methods=['POST'])
def import_price_list():
    """Import price list from Excel"""
    if not excel_handler:
        return jsonify({'error': 'Excel handler not available'}), 503

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        df = excel_handler.import_price_list(file)

        return jsonify({
            'success': True,
            'message': f'Imported {len(df)} items',
            'columns': list(df.columns),
            'preview': df.head(5).to_dict('records')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/import/order-guide', methods=['POST'])
def import_order_guide():
    """Import order guide from Excel"""
    if not excel_handler:
        return jsonify({'error': 'Excel handler not available'}), 503

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        data = excel_handler.import_order_guide(file)

        return jsonify({
            'success': True,
            'message': f'Imported {data["total_items"]} items',
            'data': data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ========================================
# API Routes - System
# ========================================

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'restaurant': os.getenv('RESTAURANT_NAME', 'The Lariat')
    })

@app.route('/api/modules')
def list_modules():
    """List all available modules and their status"""
    modules = [
        {
            'name': 'Vendor Analysis',
            'endpoint': '/vendor-analysis',
            'status': 'active' if vendor_comparator else 'development',
            'description': 'Compare vendor prices and identify savings'
        },
        {
            'name': 'Price Comparison',
            'endpoint': '/price-comparison',
            'status': 'active',
            'description': 'Import and compare vendor prices with Excel support'
        },
        {
            'name': 'Order Guides',
            'endpoint': '/order-guides',
            'status': 'active',
            'description': 'Manage vendor order guides with import/export'
        },
        {
            'name': 'Profit Calculator',
            'endpoint': '/profit-calculator',
            'status': 'active',
            'description': 'Calculate profit margins and analyze scenarios'
        },
        {
            'name': 'Recipe Costing',
            'endpoint': '/recipe-costing',
            'status': 'active',
            'description': 'Cost recipes and analyze ingredient pricing'
        },
    ]

    return jsonify(modules)

if __name__ == '__main__':
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"\n🤠 The Lariat Bible - Starting server...")
    print(f"📍 Access at: http://{host}:{port}")
    print(f"📊 API Health: http://{host}:{port}/api/health")
    print(f"🔧 Debug mode: {debug}")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(host=host, port=port, debug=debug)
