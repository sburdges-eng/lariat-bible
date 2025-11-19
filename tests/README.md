# Testing Suite

Comprehensive test suite for The Lariat Bible restaurant management system.

## Overview

This directory contains automated tests using pytest and pytest-flask. Tests are organized by component and functionality, with extensive coverage of all major features.

## Test Organization

```
tests/
├── conftest.py           # Shared fixtures and configuration
├── test_app.py           # Application core tests
├── test_api.py           # API endpoint tests
├── test_models.py        # Database model tests
├── test_validators.py    # Input validation tests
└── README.md            # This file
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run with Coverage Report

```bash
pytest --cov=. --cov-report=html
```

View the HTML coverage report:
```bash
open htmlcov/index.html
```

### Run Specific Test Categories

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only API tests
pytest -m api

# Run only database tests
pytest -m database

# Skip slow tests
pytest -m "not slow"
```

### Run Specific Test Files

```bash
# Run app tests
pytest tests/test_app.py

# Run API tests
pytest tests/test_api.py

# Run model tests
pytest tests/test_models.py

# Run validator tests
pytest tests/test_validators.py
```

### Run Specific Tests

```bash
# Run a specific test class
pytest tests/test_app.py::TestAppCreation

# Run a specific test function
pytest tests/test_api.py::TestHealthAPI::test_health_check
```

### Verbose Output

```bash
# Show detailed output
pytest -v

# Show even more detail
pytest -vv

# Show print statements
pytest -s
```

## Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.integration` - Integration tests for multiple components
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.database` - Database-related tests
- `@pytest.mark.slow` - Tests that take longer to run
- `@pytest.mark.security` - Security-related tests

## Fixtures

### Application Fixtures

- `app` - Flask application instance (session scope)
- `client` - Flask test client for making requests
- `runner` - Flask CLI test runner
- `database` - Clean database for each test

### Model Fixtures

- `vendor` - Sample vendor instance
- `vendor_item` - Sample vendor item instance
- `recipe` - Sample recipe instance
- `recipe_ingredient` - Sample recipe ingredient instance
- `catering_event` - Sample catering event instance

### Data Fixtures

- `sample_vendor_data` - Dictionary with sample vendor data
- `sample_recipe_data` - Dictionary with sample recipe data
- `sample_catering_data` - Dictionary with sample catering event data
- `auth_headers` - Sample authentication headers

## Test Coverage

Current test coverage includes:

### Application Core
- Configuration management
- Blueprint registration
- Error handling
- CORS configuration
- Logging setup

### API Endpoints
- Health checks
- Dashboard data
- Module listing
- Vendor comparison
- Response format consistency
- Input validation

### Database Models
- Vendor CRUD operations
- Recipe management
- Catering events
- Relationships and cascades
- Timestamps and defaults

### Validation
- Input sanitization
- XSS prevention
- Field validation
- Required fields
- Data type validation
- Range validation

## Writing New Tests

### Test File Template

```python
"""
Module Tests.

Description of what this module tests.
"""

import pytest


@pytest.mark.unit  # Add appropriate marker
class TestMyFeature:
    """Test my feature."""

    def test_something(self, client):
        """Test that something works."""
        # Arrange
        data = {'key': 'value'}

        # Act
        response = client.post('/api/endpoint', json=data)

        # Assert
        assert response.status_code == 200
        assert response.get_json()['key'] == 'value'
```

### Best Practices

1. **Use Descriptive Names**: Test names should clearly describe what they test
2. **Follow AAA Pattern**: Arrange, Act, Assert
3. **One Assert Per Test**: Focus each test on a single behavior
4. **Use Fixtures**: Leverage fixtures for setup and teardown
5. **Test Edge Cases**: Include tests for error conditions
6. **Keep Tests Fast**: Minimize database and network operations
7. **Mark Slow Tests**: Use `@pytest.mark.slow` for long-running tests

### Example Test

```python
def test_create_vendor_validates_email(self, client):
    """Test creating vendor with invalid email returns error."""
    # Arrange
    invalid_data = {
        'name': 'Test Vendor',
        'category': 'broadline',
        'email': 'not-an-email'  # Invalid
    }

    # Act
    response = client.post('/api/vendors', json=invalid_data)

    # Assert
    assert response.status_code == 400
    data = response.get_json()
    assert 'email' in data['errors']
```

## Continuous Integration

Tests are automatically run in CI/CD pipeline on:
- Every push to main branch
- Every pull request
- Scheduled daily runs

See `.github/workflows/tests.yml` for CI configuration.

## Troubleshooting

### Tests Fail Locally But Pass in CI

- Check environment variables in `.env`
- Ensure database is clean: `pytest --create-db`
- Update dependencies: `pip install -r requirements.txt`

### Database Tests Fail

- Make sure SQLite or test database is accessible
- Check file permissions on database file
- Verify migrations are up to date

### Import Errors

- Ensure you're in the project root directory
- Check that `PYTHONPATH` includes project root
- Verify all dependencies are installed

### Slow Test Performance

- Run only fast tests: `pytest -m "not slow"`
- Use parallel execution: `pytest -n auto` (requires pytest-xdist)
- Profile tests: `pytest --durations=10`

## Code Coverage Goals

- **Overall**: > 80%
- **Critical paths**: > 95%
- **API endpoints**: > 90%
- **Database models**: > 85%

Generate coverage report:
```bash
pytest --cov=. --cov-report=term-missing
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-Flask Documentation](https://pytest-flask.readthedocs.io/)
- [Testing Flask Applications](https://flask.palletsprojects.com/en/latest/testing/)
- [Python Testing Best Practices](https://realpython.com/python-testing/)
