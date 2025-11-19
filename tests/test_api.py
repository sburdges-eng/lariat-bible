"""
API Endpoint Tests.

Tests for all API endpoints.
"""

import pytest
import json
from datetime import datetime


@pytest.mark.api
class TestHealthAPI:
    """Test health check API endpoints."""

    def test_health_check(self, client):
        """Test basic health check."""
        response = client.get('/api/health')
        assert response.status_code == 200

        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'application' in data
        assert 'environment' in data
        assert 'version' in data

    def test_detailed_health(self, client):
        """Test detailed health check."""
        response = client.get('/api/health/detailed')
        assert response.status_code == 200

        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'modules' in data
        assert 'system' in data
        assert 'application' in data

    def test_ping(self, client):
        """Test ping endpoint."""
        response = client.get('/api/ping')
        assert response.status_code == 200

        data = response.get_json()
        assert data['message'] == 'pong'
        assert 'timestamp' in data

    def test_version(self, client):
        """Test version endpoint."""
        response = client.get('/api/version')
        assert response.status_code == 200

        data = response.get_json()
        assert 'version' in data
        assert 'application' in data


@pytest.mark.api
class TestMainAPI:
    """Test main API endpoints."""

    def test_dashboard_endpoint(self, client):
        """Test dashboard returns proper data."""
        response = client.get(
            '/',
            headers={'Accept': 'application/json'}
        )
        assert response.status_code == 200

        data = response.get_json()
        assert 'message' in data
        assert 'status' in data
        assert 'modules' in data
        assert 'metrics' in data

    def test_modules_list(self, client):
        """Test modules list endpoint."""
        response = client.get('/api/modules')
        assert response.status_code == 200

        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Check first module has required fields
        module = data[0]
        assert 'name' in module
        assert 'endpoint' in module
        assert 'status' in module
        assert 'description' in module


@pytest.mark.api
class TestVendorAPI:
    """Test vendor API endpoints."""

    def test_vendor_list(self, client):
        """Test vendor list endpoint."""
        response = client.get('/api/vendor/list')
        assert response.status_code == 200

        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_vendor_comparison_defaults(self, client):
        """Test vendor comparison with default values."""
        response = client.get(
            '/api/vendor/comparison',
            query_string={'vendor1': 'Shamrock Foods', 'vendor2': 'SYSCO'}
        )
        # May return 503 if module not available, which is fine
        assert response.status_code in [200, 503]

    def test_vendor_comparison_validation(self, client):
        """Test vendor comparison input validation."""
        # Test with same vendor (should fail validation)
        response = client.get(
            '/api/vendor/comparison',
            query_string={'vendor1': 'Test', 'vendor2': 'Test'}
        )
        # Should return validation error
        assert response.status_code in [400, 503]

    def test_vendor_analytics(self, client):
        """Test vendor analytics endpoint."""
        response = client.get('/api/vendor/analytics')
        assert response.status_code == 200

        data = response.get_json()
        assert 'message' in data or 'features' in data


@pytest.mark.api
class TestAPIResponseFormat:
    """Test API response formats."""

    def test_success_response_format(self, client):
        """Test success responses have consistent format."""
        response = client.get('/api/health')
        assert response.status_code == 200
        assert response.content_type == 'application/json'

    def test_error_response_format(self, client):
        """Test error responses have consistent format."""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404

        data = response.get_json()
        assert 'error' in data
        assert 'status' in data

    def test_json_content_type(self, client):
        """Test all API responses return JSON."""
        endpoints = [
            '/api/health',
            '/api/modules',
            '/api/vendor/list'
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert 'application/json' in response.content_type


@pytest.mark.api
class TestAPIValidation:
    """Test API input validation."""

    def test_invalid_json(self, client):
        """Test handling of invalid JSON."""
        response = client.post(
            '/api/vendor/list',
            data='invalid json',
            content_type='application/json'
        )
        # Should handle gracefully
        assert response.status_code in [400, 405]

    def test_missing_required_field(self, client):
        """Test handling of missing required fields."""
        response = client.get('/api/vendor/comparison')
        # Should return error for missing vendors
        assert response.status_code in [400, 503]


@pytest.mark.api
@pytest.mark.slow
class TestAPIPerformance:
    """Test API performance."""

    def test_health_check_performance(self, client):
        """Test health check responds quickly."""
        import time

        start = time.time()
        response = client.get('/api/health')
        duration = time.time() - start

        assert response.status_code == 200
        assert duration < 1.0  # Should respond in under 1 second

    def test_multiple_requests(self, client):
        """Test handling multiple rapid requests."""
        for _ in range(10):
            response = client.get('/api/health')
            assert response.status_code == 200
