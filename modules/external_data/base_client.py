"""
Base Client for External Data Sources
======================================
Provides common functionality for all API integrations.
"""

import requests
import time
import json
import hashlib
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
from functools import wraps
from .config import get_config


class SimpleCache:
    """Simple in-memory cache with TTL support"""

    def __init__(self):
        self._cache: Dict[str, tuple] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key in self._cache:
            value, expiry = self._cache[key]
            if datetime.now() < expiry:
                return value
            del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL in seconds"""
        expiry = datetime.now() + timedelta(seconds=ttl)
        self._cache[key] = (value, expiry)

    def clear(self):
        """Clear all cached values"""
        self._cache.clear()

    def make_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()


# Global cache instance
_cache = SimpleCache()


def cached(ttl: int = 3600):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__module__}.{func.__name__}:{_cache.make_key(*args[1:], **kwargs)}"
            result = _cache.get(cache_key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            if result is not None:
                _cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator


class BaseClient(ABC):
    """Base class for all external data source clients"""

    def __init__(self):
        self.config = get_config()
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self):
        """Setup session with default headers"""
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })

    def _make_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[int] = None
    ) -> Optional[Dict]:
        """Make HTTP request with retry logic"""
        timeout = timeout or self.config.REQUEST_TIMEOUT

        for attempt in range(self.config.MAX_RETRIES):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    headers=headers,
                    timeout=timeout
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # Rate limited - wait and retry
                    wait_time = self.config.RETRY_DELAY * (attempt + 1) * 2
                    time.sleep(wait_time)
                    continue
                elif response.status_code >= 400:
                    return {
                        'error': True,
                        'status_code': response.status_code,
                        'message': response.text
                    }

            except requests.exceptions.Timeout:
                if attempt < self.config.MAX_RETRIES - 1:
                    time.sleep(self.config.RETRY_DELAY)
                    continue
                return {'error': True, 'message': 'Request timed out'}

            except requests.exceptions.RequestException as e:
                if attempt < self.config.MAX_RETRIES - 1:
                    time.sleep(self.config.RETRY_DELAY)
                    continue
                return {'error': True, 'message': str(e)}

        return {'error': True, 'message': 'Max retries exceeded'}

    def _get(self, url: str, params: Optional[Dict] = None, **kwargs) -> Optional[Dict]:
        """Make GET request"""
        return self._make_request('GET', url, params=params, **kwargs)

    def _post(self, url: str, data: Optional[Dict] = None, **kwargs) -> Optional[Dict]:
        """Make POST request"""
        return self._make_request('POST', url, data=data, **kwargs)

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Check if the API is accessible"""
        pass

    @abstractmethod
    def search(self, query: str, **kwargs) -> List[Dict]:
        """Search for items in the data source"""
        pass

    def get_source_name(self) -> str:
        """Get the name of this data source"""
        return self.__class__.__name__.replace('Client', '')

    def is_available(self) -> bool:
        """Check if this data source is available"""
        try:
            result = self.health_check()
            return result.get('available', False)
        except Exception:
            return False
