#!/usr/bin/env python
"""
The Lariat Bible - Main Application
Restaurant Management System Web Interface
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
CORS(app)

# Import modules
try:
    from modules.vendor_analysis import (
        VendorComparator,
        VendorParser,
        AccurateVendorMatcher,
        ReportGenerator,
    )
    vendor_comparator = VendorComparator()
    vendor_parser = VendorParser()
    vendor_matcher = AccurateVendorMatcher()
    report_generator = ReportGenerator()
except ImportError:
    vendor_comparator = None
    vendor_parser = None
    vendor_matcher = None
    report_generator = None

try:
    from modules.beo_integration import (
        BEOParser,
        PrepSheetGenerator,
        OrderCalculator,
    )
    from modules.beo_integration.order_calculator import get_sample_recipes
    beo_parser = BEOParser()
    prep_generator = PrepSheetGenerator()
    order_calculator = OrderCalculator()
    # Load sample recipes
    for name, recipe in get_sample_recipes().items():
        order_calculator.add_recipe(recipe)
except ImportError:
    beo_parser = None
    prep_generator = None
    order_calculator = None

# Store for parsed products and events (in-memory for demo)
parsed_products = {'sysco': [], 'shamrock': []}
parsed_events = {}


@app.route('/')
def index():
    """Main dashboard"""
    return jsonify({
        'message': 'Welcome to The Lariat Bible',
        'status': 'operational',
        'modules': {
            'vendor_analysis': 'ready' if vendor_comparator else 'pending',
            'beo_integration': 'ready' if beo_parser else 'pending',
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
        }
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


@app.route('/api/vendor/upload', methods=['POST'])
def vendor_upload():
    """
    Upload vendor spreadsheet for parsing

    POST /api/vendor/upload
    Form data:
        - file: Excel file (.xlsx or .xls)
        - vendor: "sysco" or "shamrock"
    """
    if not vendor_parser:
        return jsonify({'error': 'Vendor parser not available'}), 503

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    vendor = request.form.get('vendor', '').lower()

    if not file.filename:
        return jsonify({'error': 'No file selected'}), 400

    if vendor not in ('sysco', 'shamrock'):
        return jsonify({'error': 'Invalid vendor. Use "sysco" or "shamrock"'}), 400

    # Save to temp file
    filename = secure_filename(file.filename)
    if not filename.endswith(('.xlsx', '.xls')):
        return jsonify({'error': 'Invalid file type. Use .xlsx or .xls'}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        # Parse the file
        products = vendor_parser.parse_file(tmp_path, vendor)

        # Store parsed products
        parsed_products[vendor] = products

        return jsonify({
            'success': True,
            'vendor': vendor,
            'products_parsed': len(products),
            'sample': [p.to_dict() for p in products[:5]]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up temp file
        os.unlink(tmp_path)


@app.route('/api/vendor/comparison')
def get_vendor_comparison():
    """
    Get full vendor comparison data

    GET /api/vendor/comparison
    Query params:
        - min_confidence: Minimum match confidence (0.0-1.0), default 0.6
    """
    if not vendor_matcher or not report_generator:
        return jsonify({'error': 'Vendor comparison not available'}), 503

    sysco_products = parsed_products.get('sysco', [])
    shamrock_products = parsed_products.get('shamrock', [])

    if not sysco_products or not shamrock_products:
        return jsonify({
            'error': 'Upload vendor files first using POST /api/vendor/upload',
            'sysco_products': len(sysco_products),
            'shamrock_products': len(shamrock_products)
        }), 400

    min_confidence = float(request.args.get('min_confidence', 0.6))

    # Perform matching
    matched, sysco_only, shamrock_only = vendor_matcher.fuzzy_match_products(
        sysco_products,
        shamrock_products,
        min_confidence=min_confidence
    )

    # Generate report
    report_generator.set_data(matched, sysco_only, shamrock_only)

    return jsonify(report_generator.generate_json_report())


@app.route('/api/vendor/savings')
def get_vendor_savings():
    """
    Get savings summary

    GET /api/vendor/savings
    """
    if not report_generator:
        return jsonify({'error': 'Report generator not available'}), 503

    summary = report_generator.calculate_summary()

    return jsonify({
        'summary': summary.to_dict(),
        'key_metrics': {
            'monthly_catering_revenue': 28000,
            'monthly_restaurant_revenue': 20000,
            'target_catering_margin': 0.45,
            'potential_annual_savings': 52000
        },
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/beo/parse', methods=['POST'])
def beo_parse():
    """
    Parse uploaded BEO file

    POST /api/beo/parse
    Form data:
        - file: BEO Excel file (.xlsx or .xls)
    """
    if not beo_parser:
        return jsonify({'error': 'BEO parser not available'}), 503

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if not file.filename:
        return jsonify({'error': 'No file selected'}), 400

    # Save to temp file
    filename = secure_filename(file.filename)
    if not filename.endswith(('.xlsx', '.xls')):
        return jsonify({'error': 'Invalid file type. Use .xlsx or .xls'}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        # Parse the file
        events = beo_parser.parse_file(tmp_path)

        # Store parsed events
        for event in events:
            parsed_events[event.event_id] = event

        return jsonify({
            'success': True,
            'events_parsed': len(events),
            'events': [
                {
                    'event_id': e.event_id,
                    'client_name': e.client_name,
                    'event_date': e.event_date.isoformat() if e.event_date else None,
                    'guest_count': e.guest_count,
                    'menu_items': len(e.menu_items)
                }
                for e in events
            ]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up temp file
        os.unlink(tmp_path)


@app.route('/api/beo/prep-sheet/<event_id>')
def get_prep_sheet(event_id):
    """
    Generate prep sheet for an event

    GET /api/beo/prep-sheet/<event_id>
    Query params:
        - format: "text" or "html" (default: "text")
    """
    if not prep_generator or not order_calculator:
        return jsonify({'error': 'Prep sheet generator not available'}), 503

    event = parsed_events.get(event_id)
    if not event:
        return jsonify({'error': f'Event not found: {event_id}'}), 404

    # Calculate ingredients
    ingredients = order_calculator.calculate_for_event(event)

    output_format = request.args.get('format', 'text').lower()

    if output_format == 'html':
        content = prep_generator.generate_html_prep_sheet(event, ingredients)
        return content, 200, {'Content-Type': 'text/html'}
    else:
        content = prep_generator.generate_text_prep_sheet(event, ingredients)
        return content, 200, {'Content-Type': 'text/plain'}


@app.route('/api/beo/events')
def list_beo_events():
    """
    List all parsed BEO events

    GET /api/beo/events
    """
    return jsonify({
        'events': [
            {
                'event_id': e.event_id,
                'client_name': e.client_name,
                'event_date': e.event_date.isoformat() if e.event_date else None,
                'guest_count': e.guest_count
            }
            for e in parsed_events.values()
        ]
    })


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'restaurant': os.getenv('RESTAURANT_NAME', 'The Lariat'),
        'modules': {
            'vendor_analysis': vendor_comparator is not None,
            'beo_integration': beo_parser is not None
        }
    })


@app.route('/api/modules')
def list_modules():
    """List all available modules and their status"""
    modules = [
        {
            'name': 'Vendor Analysis',
            'endpoint': '/api/vendor',
            'status': 'active' if vendor_comparator else 'development',
            'description': 'Compare vendor prices and identify savings',
            'endpoints': [
                'POST /api/vendor/upload',
                'GET /api/vendor/comparison',
                'GET /api/vendor/savings'
            ]
        },
        {
            'name': 'BEO Integration',
            'endpoint': '/api/beo',
            'status': 'active' if beo_parser else 'development',
            'description': 'Parse BEO files and generate prep sheets',
            'endpoints': [
                'POST /api/beo/parse',
                'GET /api/beo/events',
                'GET /api/beo/prep-sheet/<event_id>'
            ]
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


if __name__ == '__main__':
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    print("\n🤠 The Lariat Bible - Starting server...")
    print(f"📍 Access at: http://{host}:{port}")
    print(f"📊 API Health: http://{host}:{port}/api/health")
    print(f"🔧 Debug mode: {debug}")
    print("\nPress Ctrl+C to stop the server\n")

    app.run(host=host, port=port, debug=debug)
