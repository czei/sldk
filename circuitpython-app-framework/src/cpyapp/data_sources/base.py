"""
Base DataSource class for all data sources.

This module provides the abstract interface for all data sources
and common functionality like error handling, caching, and rate limiting.
"""
import asyncio
import json
import time
try:
    from typing import Dict, Any, Optional, List, Union
except ImportError:
    # CircuitPython doesn't have typing
    pass

from ..utils.error_handler import ErrorHandler
from ..utils.timer import Timer

# Initialize logger
logger = ErrorHandler("error_log")


class DataSource:
    """
    Abstract base class for all data sources.
    
    This class provides the interface and common functionality that all
    data sources must implement, including caching, rate limiting, and
    error handling.
    """
    
    def __init__(self, name, cache_ttl=300, rate_limit=1.0):
        """
        Initialize the data source.
        
        Args:
            name: Name of the data source
            cache_ttl: Cache time-to-live in seconds (default: 5 minutes)
            rate_limit: Minimum seconds between requests (default: 1 second)
        """
        self.name = name
        self.cache_ttl = cache_ttl
        self.rate_limit = rate_limit
        
        # Caching
        self._cache = None
        self._cache_time = 0
        
        # Rate limiting
        self._last_request_time = 0
        
        # Error tracking
        self._error_count = 0
        self._last_error = None
        
    async def get_data(self, force_refresh=False):
        """
        Get data from the source with caching and rate limiting.
        
        Args:
            force_refresh: Force refresh even if cache is valid
            
        Returns:
            The data from the source, or cached data if still valid
        """
        # Check cache
        if not force_refresh and self._is_cache_valid():
            logger.debug(f"{self.name}: Using cached data")
            return self._cache
            
        # Rate limiting
        await self._rate_limit_check()
        
        try:
            # Fetch fresh data
            logger.info(f"{self.name}: Fetching fresh data")
            data = await self._fetch_data()
            
            # Update cache
            self._cache = data
            self._cache_time = time.monotonic()
            
            # Reset error count on success
            self._error_count = 0
            
            return data
            
        except Exception as e:
            self._error_count += 1
            self._last_error = e
            logger.error(e, f"{self.name}: Error fetching data (attempt {self._error_count})")
            
            # Return cached data if available
            if self._cache is not None:
                logger.info(f"{self.name}: Returning stale cache after error")
                return self._cache
                
            # Re-raise if no cache
            raise
            
    async def _fetch_data(self):
        """
        Fetch data from the source. Must be implemented by subclasses.
        
        Returns:
            The fetched data
        """
        raise NotImplementedError("Subclasses must implement _fetch_data")
        
    def parse_data(self, raw_data):
        """
        Parse raw data into a standard format. Can be overridden by subclasses.
        
        Args:
            raw_data: The raw data to parse
            
        Returns:
            Parsed data in a standard format
        """
        return raw_data
        
    def format_for_display(self, data):
        """
        Format parsed data for display. Must be implemented by subclasses.
        
        Args:
            data: The parsed data
            
        Returns:
            List of message dictionaries for display
        """
        raise NotImplementedError("Subclasses must implement format_for_display")
        
    def _is_cache_valid(self):
        """Check if cached data is still valid."""
        if self._cache is None:
            return False
            
        age = time.monotonic() - self._cache_time
        return age < self.cache_ttl
        
    async def _rate_limit_check(self):
        """Enforce rate limiting between requests."""
        elapsed = time.monotonic() - self._last_request_time
        if elapsed < self.rate_limit:
            wait_time = self.rate_limit - elapsed
            logger.debug(f"{self.name}: Rate limiting, waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
            
        self._last_request_time = time.monotonic()
        
    def get_error_status(self):
        """
        Get current error status.
        
        Returns:
            Dictionary with error information
        """
        return {
            'error_count': self._error_count,
            'last_error': str(self._last_error) if self._last_error else None,
            'has_cache': self._cache is not None,
            'cache_age': time.monotonic() - self._cache_time if self._cache else None
        }
        
    def clear_cache(self):
        """Clear cached data."""
        self._cache = None
        self._cache_time = 0
        logger.info(f"{self.name}: Cache cleared")


class HttpDataSource(DataSource):
    """
    Base class for HTTP-based data sources.
    
    This class extends DataSource with HTTP-specific functionality
    like URL handling, headers, and response parsing.
    """
    
    def __init__(self, name, url=None, http_client=None, **kwargs):
        """
        Initialize HTTP data source.
        
        Args:
            name: Name of the data source
            url: Base URL for the data source
            http_client: HTTP client instance to use
            **kwargs: Additional arguments passed to DataSource
        """
        super().__init__(name, **kwargs)
        self.url = url
        self.http_client = http_client
        self.headers = {}
        
    def set_http_client(self, http_client):
        """Set the HTTP client instance."""
        self.http_client = http_client
        
    def set_headers(self, headers):
        """Set custom headers for HTTP requests."""
        self.headers = headers
        
    async def _fetch_data(self):
        """Fetch data via HTTP."""
        if not self.http_client:
            raise RuntimeError(f"{self.name}: No HTTP client configured")
            
        if not self.url:
            raise RuntimeError(f"{self.name}: No URL configured")
            
        try:
            response = await self.http_client.get(self.url, headers=self.headers)
            
            if not response:
                raise RuntimeError(f"{self.name}: Empty response from {self.url}")
                
            # Try to parse as JSON
            try:
                data = json.loads(response.text if hasattr(response, 'text') else response)
                return self.parse_data(data)
            except ValueError:
                # Not JSON, return raw text
                return self.parse_data(response.text if hasattr(response, 'text') else response)
                
        except Exception as e:
            logger.error(e, f"{self.name}: HTTP request failed")
            raise


class StaticDataSource(DataSource):
    """
    Data source for static data.
    
    This is useful for testing or displaying fixed messages.
    """
    
    def __init__(self, name, data, **kwargs):
        """
        Initialize static data source.
        
        Args:
            name: Name of the data source
            data: The static data to return
            **kwargs: Additional arguments passed to DataSource
        """
        super().__init__(name, **kwargs)
        self.static_data = data
        
    async def _fetch_data(self):
        """Return the static data."""
        return self.static_data
        
    def format_for_display(self, data):
        """Format static data for display."""
        if isinstance(data, str):
            return [{
                'type': 'scroll',
                'text': data,
                'delay': 2
            }]
        elif isinstance(data, list):
            messages = []
            for item in data:
                if isinstance(item, str):
                    messages.append({
                        'type': 'scroll',
                        'text': item,
                        'delay': 2
                    })
                elif isinstance(item, dict) and 'text' in item:
                    messages.append({
                        'type': 'scroll',
                        'text': item['text'],
                        'delay': item.get('delay', 2)
                    })
            return messages
        else:
            return [{
                'type': 'scroll',
                'text': str(data),
                'delay': 2
            }]