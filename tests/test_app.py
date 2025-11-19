"""
Application Tests.

Tests for core Flask application functionality.
"""

import pytest
from app import create_app
from config import DevelopmentConfig, ProductionConfig, TestingConfig


class TestAppCreation:
    """Test application creation and configuration."""

    def test_app_creation(self):
        """Test that app can be created."""
        app = create_app('testing')
        assert app is not None
        assert app.config['TESTING'] is True

    def test_app_config_testing(self):
        """Test testing configuration is loaded correctly."""
        app = create_app('testing')
        assert app.config['TESTING'] is True
        assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'
        assert app.config['WTF_CSRF_ENABLED'] is False

    def test_app_config_development(self):
        """Test development configuration."""
        app = create_app('development')
        assert app.config['DEBUG'] is True
        assert app.config['TESTING'] is False

    def test_app_has_correct_name(self):
        """Test app has correct name from config."""
        app = create_app('testing')
        assert app.config['APP_NAME'] == 'The Lariat Bible'


class TestRoutes:
    """Test that routes are registered correctly."""

    def test_main_route_exists(self, client):
        """Test main route is accessible."""
        response = client.get('/')
        assert response.status_code == 200

    def test_health_route_exists(self, client):
        """Test health check route is accessible."""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'

    def test_modules_route_exists(self, client):
        """Test modules list route is accessible."""
        response = client.get('/api/modules')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

    def test_vendor_routes_exist(self, client):
        """Test vendor routes are accessible."""
        # Test vendor list
        response = client.get('/api/vendor/list')
        assert response.status_code == 200

        # Test vendor analytics
        response = client.get('/api/vendor/analytics')
        assert response.status_code == 200


class TestErrorHandling:
    """Test error handling."""

    def test_404_error(self, client):
        """Test 404 error handler."""
        response = client.get('/nonexistent-route')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data

    def test_404_has_proper_format(self, client):
        """Test 404 error has proper JSON format."""
        response = client.get('/api/does-not-exist')
        assert response.status_code == 404
        data = response.get_json()
        assert data['status'] == 404
        assert 'error' in data


class TestCORS:
    """Test CORS configuration."""

    def test_cors_headers_present(self, client):
        """Test CORS headers are present in responses."""
        response = client.get('/api/health')
        assert 'Access-Control-Allow-Origin' in response.headers


class TestLogging:
    """Test logging configuration."""

    def test_app_has_logger(self, app):
        """Test app has a logger configured."""
        assert app.logger is not None

    def test_logging_level_configured(self, app):
        """Test logging level is configured."""
        assert app.config['LOG_LEVEL'] in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
