"""
API Blueprints Package for The Lariat Bible.

This package contains all API route blueprints organized by functionality.
"""

from flask import Blueprint


def register_blueprints(app):
    """
    Register all API blueprints with the Flask application.

    Args:
        app: Flask application instance

    Returns:
        None
    """
    from api.main import main_bp
    from api.vendor import vendor_bp
    from api.health import health_bp

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(vendor_bp, url_prefix='/api/vendor')
    app.register_blueprint(health_bp, url_prefix='/api')

    app.logger.info('All blueprints registered successfully')
