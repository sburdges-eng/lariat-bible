"""
Vendor Analysis Blueprint.

Handles vendor comparison, price analysis, and savings calculations.
"""

from flask import Blueprint, jsonify, current_app, request
from datetime import datetime

vendor_bp = Blueprint('vendor', __name__)

# Try to import vendor module
try:
    from modules.vendor_analysis import VendorComparator
    vendor_comparator = VendorComparator()
except ImportError:
    vendor_comparator = None


@vendor_bp.route('/comparison')
def vendor_comparison():
    """
    Compare prices between two vendors.

    Query Parameters:
        vendor1 (str): Name of first vendor (default: 'Shamrock Foods')
        vendor2 (str): Name of second vendor (default: 'SYSCO')

    Returns:
        JSON response with savings analysis and margin impact
    """
    if not vendor_comparator:
        current_app.logger.error('Vendor analysis module not available')
        return jsonify({
            'error': 'Vendor analysis module not available',
            'status': 503
        }), 503

    # Get vendor names from query parameters or use defaults
    vendor1 = request.args.get('vendor1', 'Shamrock Foods')
    vendor2 = request.args.get('vendor2', 'SYSCO')

    try:
        # Calculate savings
        savings = vendor_comparator.compare_vendors(vendor1, vendor2)
        margin_impact = vendor_comparator.calculate_margin_impact(savings)

        current_app.logger.info(
            f'Vendor comparison: {vendor1} vs {vendor2} - ${savings:.2f} monthly savings'
        )

        return jsonify({
            'vendors': {
                'vendor1': vendor1,
                'vendor2': vendor2
            },
            'savings': {
                'monthly': round(savings, 2),
                'annual': round(savings * 12, 2)
            },
            'margin_impact': round(margin_impact, 2),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f'Error in vendor comparison: {str(e)}', exc_info=True)
        return jsonify({
            'error': 'Error calculating vendor comparison',
            'message': str(e),
            'status': 500
        }), 500


@vendor_bp.route('/list')
def list_vendors():
    """
    List all available vendors in the system.

    Returns:
        JSON list of vendors with their metadata
    """
    # Placeholder - will be implemented when vendor database is ready
    vendors = [
        {
            'name': 'Shamrock Foods',
            'category': 'broadline',
            'status': 'active',
            'coverage': 'regional'
        },
        {
            'name': 'SYSCO',
            'category': 'broadline',
            'status': 'active',
            'coverage': 'national'
        },
        {
            'name': 'US Foods',
            'category': 'broadline',
            'status': 'pending',
            'coverage': 'national'
        }
    ]

    return jsonify(vendors)


@vendor_bp.route('/analytics')
def vendor_analytics():
    """
    Get comprehensive vendor analytics and performance metrics.

    Returns:
        JSON response with vendor performance data
    """
    # Placeholder for future implementation
    return jsonify({
        'message': 'Vendor analytics endpoint - coming soon',
        'features': [
            'Price trend analysis',
            'Delivery reliability metrics',
            'Quality score tracking',
            'Order frequency analysis'
        ]
    })


@vendor_bp.errorhandler(404)
def not_found(error):
    """
    Handle 404 errors for vendor blueprint.

    Args:
        error: The error object

    Returns:
        JSON error response with 404 status
    """
    return jsonify({
        'error': 'Vendor endpoint not found',
        'status': 404
    }), 404
