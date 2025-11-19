"""
Configuration management for The Lariat Bible application.

This module provides environment-specific configuration classes for development,
staging, and production environments. Configurations are loaded from environment
variables with sensible defaults.
"""

import os
from datetime import timedelta


class Config:
    """Base configuration class with common settings."""

    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    APP_NAME = 'The Lariat Bible'

    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///lariat_bible.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Upload settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'csv'}

    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'logs/lariat_bible.log'

    # Cache settings
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300

    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = 'memory://'

    # Email settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@lariat-bible.com'

    # Feature flags
    ENABLE_WEBSOCKETS = False
    ENABLE_OCR = False
    ENABLE_PDF_EXPORT = True

    @staticmethod
    def init_app(app):
        """Initialize application with this configuration."""
        pass


class DevelopmentConfig(Config):
    """Development environment configuration."""

    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True  # Log SQL queries in development
    LOG_LEVEL = 'DEBUG'
    SESSION_COOKIE_SECURE = False

    # Development-specific feature flags
    ENABLE_WEBSOCKETS = True
    ENABLE_OCR = True

    @staticmethod
    def init_app(app):
        """Initialize development-specific settings."""
        print(f'🚀 Starting {Config.APP_NAME} in DEVELOPMENT mode')


class TestingConfig(Config):
    """Testing environment configuration."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False

    @staticmethod
    def init_app(app):
        """Initialize testing-specific settings."""
        print(f'🧪 Starting {Config.APP_NAME} in TESTING mode')


class StagingConfig(Config):
    """Staging environment configuration."""

    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

    # Use Redis for caching in staging
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

    # Use Redis for rate limiting in staging
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/1'

    @staticmethod
    def init_app(app):
        """Initialize staging-specific settings."""
        import logging
        from logging.handlers import RotatingFileHandler

        # Ensure log directory exists
        os.makedirs('logs', exist_ok=True)

        # Set up file logging
        file_handler = RotatingFileHandler(
            Config.LOG_FILE,
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info(f'🚀 Starting {Config.APP_NAME} in STAGING mode')


class ProductionConfig(Config):
    """Production environment configuration."""

    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

    # Require secret key in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError('SECRET_KEY environment variable must be set in production')

    # Use Redis for caching in production
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    if not CACHE_REDIS_URL:
        raise ValueError('REDIS_URL environment variable must be set in production')

    # Use Redis for rate limiting in production
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL')

    # Enable all features in production
    ENABLE_WEBSOCKETS = True
    ENABLE_OCR = True
    ENABLE_PDF_EXPORT = True

    @staticmethod
    def init_app(app):
        """Initialize production-specific settings."""
        import logging
        from logging.handlers import RotatingFileHandler, SMTPHandler

        # Ensure log directory exists
        os.makedirs('logs', exist_ok=True)

        # Set up file logging
        file_handler = RotatingFileHandler(
            Config.LOG_FILE,
            maxBytes=10240000,  # 10MB
            backupCount=20
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        # Set up email logging for errors
        if Config.MAIL_SERVER:
            auth = None
            if Config.MAIL_USERNAME and Config.MAIL_PASSWORD:
                auth = (Config.MAIL_USERNAME, Config.MAIL_PASSWORD)

            mail_handler = SMTPHandler(
                mailhost=(Config.MAIL_SERVER, Config.MAIL_PORT),
                fromaddr=Config.MAIL_DEFAULT_SENDER,
                toaddrs=[os.environ.get('ADMIN_EMAIL', 'admin@lariat-bible.com')],
                subject=f'{Config.APP_NAME} Application Error',
                credentials=auth,
                secure=() if Config.MAIL_USE_TLS else None
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info(f'🚀 Starting {Config.APP_NAME} in PRODUCTION mode')


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """
    Get configuration class based on environment.

    Args:
        config_name: Name of configuration ('development', 'testing', 'staging', 'production')
                    If None, uses FLASK_ENV environment variable or defaults to 'development'

    Returns:
        Configuration class instance
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    return config.get(config_name, DevelopmentConfig)
