#!/usr/bin/env python
"""
The Lariat Bible - Main Application
Restaurant Management System Web Interface
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import configuration
from config import get_config


def create_app(config_name=None):
    """
    Application factory pattern for creating Flask app instances.

    Args:
        config_name: Name of configuration to use ('development', 'testing', 'staging', 'production')
                    If None, uses FLASK_ENV environment variable

    Returns:
        Configured Flask application instance
    """
    # Initialize Flask app
    app = Flask(__name__)

    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Initialize configuration-specific settings
    config_class.init_app(app)

    # Enable CORS
    CORS(app)

    # Setup logging
    setup_logging(app)

    # Initialize database
    from models import init_db
    init_db(app)

    # Register routes
    register_routes(app)

    # Log startup
    app.logger.info(f'{app.config["APP_NAME"]} initialized successfully')

    return app


def setup_logging(app):
    """
    Configure application logging.

    Args:
        app: Flask application instance
    """
    if not app.debug and not app.testing:
        # Ensure log directory exists
        os.makedirs('logs', exist_ok=True)

        # Configure file logging
        from logging.handlers import RotatingFileHandler

        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=10240000,  # 10MB
            backupCount=10
        )

        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))

        log_level = getattr(logging, app.config['LOG_LEVEL'].upper(), logging.INFO)
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(log_level)


def register_routes(app):
    """
    Register all application blueprints and global error handlers.

    Args:
        app: Flask application instance
    """
    # Register all blueprints
    from api import register_blueprints
    register_blueprints(app)

    # Register global error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors globally."""
        app.logger.warning(f'404 error: {error}')
        return jsonify({
            'error': 'Resource not found',
            'status': 404
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors globally."""
        app.logger.error(f'500 error: {error}', exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'status': 500
        }), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle unexpected exceptions globally."""
        app.logger.error(f'Unhandled exception: {error}', exc_info=True)
        return jsonify({
            'error': 'An unexpected error occurred',
            'status': 500
        }), 500


# Create application instance
app = create_app()


if __name__ == '__main__':
    """Run the application when executed directly."""
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 5000))

    print(f"\n🤠 {app.config['APP_NAME']} - Starting server...")
    print(f"📍 Access at: http://{host}:{port}")
    print(f"📊 API Health: http://{host}:{port}/api/health")
    print(f"🔧 Environment: {os.getenv('FLASK_ENV', 'development')}")
    print("\nPress Ctrl+C to stop the server\n")

    app.run(host=host, port=port)
