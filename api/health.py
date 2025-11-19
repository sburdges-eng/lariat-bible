"""
Health Check Blueprint.

Provides system health monitoring and status endpoints.
"""

from flask import Blueprint, jsonify, current_app
from datetime import datetime
import os
import sys

health_bp = Blueprint('health', __name__)


@health_bp.route('/health')
def health_check():
    """
    Basic health check endpoint.

    Returns:
        JSON response with system health status
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'application': current_app.config['APP_NAME'],
        'environment': os.getenv('FLASK_ENV', 'development'),
        'version': '1.0.0'
    })


@health_bp.route('/health/detailed')
def detailed_health():
    """
    Detailed health check with system information.

    Returns:
        JSON response with comprehensive health metrics
    """
    # Check module availability
    modules_status = {}

    # Check vendor module
    try:
        from modules.vendor_analysis import VendorComparator
        modules_status['vendor_analysis'] = 'healthy'
    except ImportError:
        modules_status['vendor_analysis'] = 'unavailable'

    # System information
    system_info = {
        'python_version': sys.version,
        'platform': sys.platform,
        'working_directory': os.getcwd()
    }

    # Application configuration (safe items only)
    app_config = {
        'debug': current_app.debug,
        'testing': current_app.testing,
        'environment': os.getenv('FLASK_ENV', 'development'),
        'log_level': current_app.config.get('LOG_LEVEL', 'INFO')
    }

    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'application': {
            'name': current_app.config['APP_NAME'],
            'version': '1.0.0',
            'config': app_config
        },
        'modules': modules_status,
        'system': system_info
    })


@health_bp.route('/ping')
def ping():
    """
    Simple ping endpoint for uptime monitoring.

    Returns:
        JSON response with pong message
    """
    return jsonify({
        'message': 'pong',
        'timestamp': datetime.now().isoformat()
    })


@health_bp.route('/version')
def version():
    """
    Get application version information.

    Returns:
        JSON response with version details
    """
    return jsonify({
        'application': current_app.config['APP_NAME'],
        'version': '1.0.0',
        'python_version': sys.version.split()[0],
        'environment': os.getenv('FLASK_ENV', 'development')
    })
