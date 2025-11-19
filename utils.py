"""
Utility Functions and Decorators.

This module provides helper functions, decorators, and utilities
for the application.
"""

from functools import wraps
from flask import request, jsonify, current_app
from marshmallow import ValidationError
import re
import bleach


# ==================== Validation Decorators ====================

def validate_request(schema, location='json'):
    """
    Decorator to validate request data using a Marshmallow schema.

    Args:
        schema: Marshmallow schema class or instance
        location: Where to get data from ('json', 'args', 'form')

    Usage:
        @app.route('/api/vendors', methods=['POST'])
        @validate_request(VendorSchema)
        def create_vendor(validated_data):
            # validated_data contains the validated input
            ...
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Get data from request
            if location == 'json':
                data = request.get_json(silent=True)
                if data is None:
                    return jsonify({
                        'error': 'Invalid JSON or no data provided',
                        'status': 400
                    }), 400
            elif location == 'args':
                data = request.args.to_dict()
            elif location == 'form':
                data = request.form.to_dict()
            else:
                return jsonify({
                    'error': 'Invalid data location specified',
                    'status': 500
                }), 500

            # Validate data
            try:
                if isinstance(schema, type):
                    schema_instance = schema()
                else:
                    schema_instance = schema

                validated_data = schema_instance.load(data)

                # Sanitize string fields
                validated_data = sanitize_dict(validated_data)

                # Pass validated data to the route handler
                return f(validated_data=validated_data, *args, **kwargs)

            except ValidationError as err:
                current_app.logger.warning(f'Validation error: {err.messages}')
                return jsonify({
                    'error': 'Validation failed',
                    'errors': err.messages,
                    'status': 400
                }), 400

        return wrapper
    return decorator


def validate_query_params(schema):
    """
    Decorator to validate URL query parameters.

    Args:
        schema: Marshmallow schema class or instance

    Usage:
        @app.route('/api/vendors')
        @validate_query_params(PaginationSchema)
        def list_vendors(validated_params):
            ...
    """
    return validate_request(schema, location='args')


# ==================== Sanitization Functions ====================

def sanitize_string(value, allowed_tags=None):
    """
    Sanitize a string to prevent XSS attacks.

    Args:
        value: String to sanitize
        allowed_tags: List of allowed HTML tags (default: None - strip all)

    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return value

    # Use bleach to clean HTML
    if allowed_tags is None:
        # Strip all HTML tags by default
        cleaned = bleach.clean(value, tags=[], strip=True)
    else:
        cleaned = bleach.clean(value, tags=allowed_tags, strip=True)

    # Remove null bytes
    cleaned = cleaned.replace('\x00', '')

    # Normalize whitespace
    cleaned = ' '.join(cleaned.split())

    return cleaned


def sanitize_dict(data, allowed_tags=None):
    """
    Recursively sanitize all string values in a dictionary.

    Args:
        data: Dictionary to sanitize
        allowed_tags: List of allowed HTML tags

    Returns:
        Sanitized dictionary
    """
    if isinstance(data, dict):
        return {
            key: sanitize_dict(value, allowed_tags)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [sanitize_dict(item, allowed_tags) for item in data]
    elif isinstance(data, str):
        return sanitize_string(data, allowed_tags)
    else:
        return data


def sanitize_filename(filename):
    """
    Sanitize a filename to prevent directory traversal attacks.

    Args:
        filename: Filename to sanitize

    Returns:
        Safe filename
    """
    # Remove path separators
    filename = filename.replace('/', '').replace('\\', '')

    # Remove null bytes
    filename = filename.replace('\x00', '')

    # Remove leading dots (hidden files)
    filename = filename.lstrip('.')

    # Allow only alphanumeric, dash, underscore, and dot
    filename = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)

    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250] + ('.' + ext if ext else '')

    return filename


# ==================== Response Helpers ====================

def success_response(data, message=None, status=200):
    """
    Create a standardized success response.

    Args:
        data: Response data
        message: Optional success message
        status: HTTP status code

    Returns:
        Flask response tuple
    """
    response = {'success': True}

    if message:
        response['message'] = message

    if data is not None:
        response['data'] = data

    return jsonify(response), status


def error_response(message, errors=None, status=400):
    """
    Create a standardized error response.

    Args:
        message: Error message
        errors: Optional detailed error information
        status: HTTP status code

    Returns:
        Flask response tuple
    """
    response = {
        'success': False,
        'error': message,
        'status': status
    }

    if errors:
        response['errors'] = errors

    return jsonify(response), status


def paginated_response(items, page, per_page, total, schema=None):
    """
    Create a paginated response with metadata.

    Args:
        items: List of items for current page
        page: Current page number
        per_page: Items per page
        total: Total number of items
        schema: Optional Marshmallow schema for serialization

    Returns:
        Flask response
    """
    total_pages = (total + per_page - 1) // per_page  # Ceiling division

    # Serialize items if schema provided
    if schema:
        if isinstance(schema, type):
            schema = schema(many=True)
        items = schema.dump(items)

    response = {
        'success': True,
        'data': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_items': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }

    return jsonify(response)


# ==================== Security Helpers ====================

def is_safe_url(url):
    """
    Check if a URL is safe for redirects.

    Args:
        url: URL to check

    Returns:
        bool: True if safe, False otherwise
    """
    if not url:
        return False

    # Reject URLs with dangerous protocols
    dangerous_protocols = ['javascript:', 'data:', 'vbscript:']
    url_lower = url.lower().strip()

    for protocol in dangerous_protocols:
        if url_lower.startswith(protocol):
            return False

    return True


def validate_email(email):
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not email:
        return False

    # Simple regex for email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone):
    """
    Validate and normalize phone number.

    Args:
        phone: Phone number to validate

    Returns:
        str or None: Normalized phone number if valid, None otherwise
    """
    if not phone:
        return None

    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)

    # Check if it's all digits and has appropriate length
    if cleaned.isdigit() and 10 <= len(cleaned) <= 15:
        return cleaned

    return None


# ==================== Data Formatting ====================

def format_currency(amount):
    """
    Format amount as currency.

    Args:
        amount: Numeric amount

    Returns:
        Formatted currency string
    """
    try:
        return f"${float(amount):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"


def format_percentage(value):
    """
    Format value as percentage.

    Args:
        value: Numeric value (0-1 or 0-100)

    Returns:
        Formatted percentage string
    """
    try:
        num = float(value)
        # Assume 0-1 if less than 1, otherwise 0-100
        if num <= 1:
            num *= 100
        return f"{num:.1f}%"
    except (ValueError, TypeError):
        return "0%"


def truncate_string(text, length=100, suffix='...'):
    """
    Truncate string to specified length.

    Args:
        text: String to truncate
        length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if not text or len(text) <= length:
        return text

    return text[:length - len(suffix)] + suffix


# ==================== File Handling ====================

def allowed_file(filename, allowed_extensions):
    """
    Check if file extension is allowed.

    Args:
        filename: Filename to check
        allowed_extensions: Set of allowed extensions

    Returns:
        bool: True if allowed, False otherwise
    """
    if not filename:
        return False

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def get_file_extension(filename):
    """
    Get file extension from filename.

    Args:
        filename: Filename

    Returns:
        Extension (without dot) or None
    """
    if not filename or '.' not in filename:
        return None

    return filename.rsplit('.', 1)[1].lower()


# ==================== Database Helpers ====================

def get_or_404(model, id):
    """
    Get model instance by ID or return 404.

    Args:
        model: SQLAlchemy model class
        id: Record ID

    Returns:
        Model instance

    Raises:
        404 error if not found
    """
    instance = model.query.get(id)
    if instance is None:
        from flask import abort
        abort(404, description=f"{model.__name__} not found")
    return instance


def commit_or_rollback(db):
    """
    Commit database changes or rollback on error.

    Args:
        db: Database instance

    Returns:
        tuple: (success: bool, error: str or None)
    """
    try:
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Database commit error: {e}', exc_info=True)
        return False, str(e)


# ==================== Logging Helpers ====================

def log_request():
    """Log incoming request details."""
    current_app.logger.info(
        f'{request.method} {request.path} - '
        f'IP: {request.remote_addr} - '
        f'User-Agent: {request.user_agent.string[:100]}'
    )


def log_performance(func):
    """
    Decorator to log function performance.

    Usage:
        @log_performance
        def expensive_operation():
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        import time
        start = time.time()

        result = func(*args, **kwargs)

        duration = time.time() - start
        current_app.logger.info(f'{func.__name__} took {duration:.3f}s')

        return result

    return wrapper
