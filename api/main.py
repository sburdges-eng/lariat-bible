"""
Main Dashboard Blueprint.

Handles the main dashboard routes and module status endpoints.
"""

from flask import Blueprint, jsonify, current_app, render_template, request
import os

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """
    Main dashboard endpoint.

    Returns HTML page for web interface or JSON for API requests.
    """
    current_app.logger.info('Dashboard accessed')

    # Check if request is for JSON (API call) or HTML (browser)
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        # Return JSON for API requests
        return get_dashboard_data()
    else:
        # Render HTML template for browser requests
        return render_template('index.html')


def get_dashboard_data():
    """
    Get dashboard data for API requests.

    Returns:
        JSON response with application status and metrics
    """
    # Check module availability
    vendor_status = 'pending'
    try:
        from modules.vendor_analysis import VendorComparator
        vendor_status = 'ready'
    except ImportError:
        pass

    return jsonify({
        'message': f'Welcome to {current_app.config["APP_NAME"]}',
        'status': 'operational',
        'environment': os.getenv('FLASK_ENV', 'development'),
        'version': '1.0.0',
        'modules': {
            'vendor_analysis': vendor_status,
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


@main_bp.route('/api/modules')
def list_modules():
    """
    List all available modules and their status.

    Returns:
        JSON list of modules with their metadata
    """
    # Check if vendor module is available
    vendor_status = 'development'
    try:
        from modules.vendor_analysis import VendorComparator
        vendor_status = 'active'
    except ImportError:
        pass

    modules = [
        {
            'name': 'Vendor Analysis',
            'endpoint': '/api/vendor',
            'status': vendor_status,
            'description': 'Compare vendor prices and identify savings opportunities'
        },
        {
            'name': 'Inventory Management',
            'endpoint': '/api/inventory',
            'status': 'development',
            'description': 'Track stock levels and automate ordering processes'
        },
        {
            'name': 'Recipe Management',
            'endpoint': '/api/recipes',
            'status': 'development',
            'description': 'Standardize recipes and calculate accurate food costs'
        },
        {
            'name': 'Catering Operations',
            'endpoint': '/api/catering',
            'status': 'development',
            'description': 'Manage catering quotes, events, and revenue tracking'
        },
        {
            'name': 'Maintenance Tracking',
            'endpoint': '/api/maintenance',
            'status': 'development',
            'description': 'Schedule and track equipment maintenance to prevent downtime'
        },
        {
            'name': 'Reporting Dashboard',
            'endpoint': '/api/reports',
            'status': 'development',
            'description': 'Business intelligence, analytics, and performance metrics'
        }
    ]

    return jsonify(modules)


@main_bp.errorhandler(404)
def not_found(error):
    """
    Handle 404 errors for this blueprint.

    Args:
        error: The error object

    Returns:
        JSON error response with 404 status
    """
    current_app.logger.warning(f'404 error in main blueprint: {error}')
    return jsonify({
        'error': 'Resource not found',
        'status': 404
    }), 404
