"""
Data Source Factory for creating appropriate data sources from configuration.

This module provides a factory for creating data sources based on
configuration, including preset resolution and error handling.
"""
try:
    from typing import Dict, Any, Optional, Union
except ImportError:
    # CircuitPython doesn't have typing
    pass

from ..utils.error_handler import ErrorHandler

# Import all data source types
from .base import DataSource, StaticDataSource
from .theme_park import ThemeParkDataSource
from .stock import StockDataSource
from .weather import WeatherDataSource
from .url import UrlDataSource
from .function import FunctionDataSource
from .text import TextDataSource

# Initialize logger
logger = ErrorHandler("error_log")


class DataSourceFactory:
    """
    Factory for creating data sources from configuration.
    
    This class handles the creation of appropriate data source instances
    based on configuration dictionaries, including preset resolution and
    type detection.
    """
    
    # Map of data source types to classes
    DATA_SOURCE_CLASSES = {
        'theme_park': ThemeParkDataSource,
        'stock': StockDataSource,
        'weather': WeatherDataSource,
        'url': UrlDataSource,
        'function': FunctionDataSource,
        'text': TextDataSource,
        'static': StaticDataSource,
    }
    
    # Global presets that map to specific configurations
    GLOBAL_PRESETS = {
        # Theme park presets
        'disney_world': {
            'type': 'theme_park',
            'preset': 'disney_world'
        },
        'magic_kingdom': {
            'type': 'theme_park',
            'preset': 'magic_kingdom'
        },
        'disneyland': {
            'type': 'theme_park',
            'preset': 'disneyland'
        },
        'universal_orlando': {
            'type': 'theme_park',
            'preset': 'universal_orlando'
        },
        
        # Stock presets
        'tech_stocks': {
            'type': 'stock',
            'preset': 'tech'
        },
        'faang_stocks': {
            'type': 'stock',
            'preset': 'faang'
        },
        
        # Weather presets
        'weather_nyc': {
            'type': 'weather',
            'preset': 'new_york'
        },
        'weather_la': {
            'type': 'weather',
            'preset': 'los_angeles'
        },
        'weather_orlando': {
            'type': 'weather',
            'preset': 'orlando'
        },
        
        # Common patterns
        'clock': {
            'type': 'function',
            'function': 'time',
            'format': '%H:%M:%S'
        },
        'date': {
            'type': 'function',
            'function': 'time',
            'format': '%Y-%m-%d'
        },
    }
    
    @classmethod
    def create(cls, config, http_client=None):
        """
        Create a data source from configuration.
        
        Args:
            config: Configuration for the data source
                - String: Preset name or static text
                - Dict: Full configuration with 'type' field
                - Callable: Function to use as data source
            http_client: Optional HTTP client for data sources that need it
            
        Returns:
            DataSource instance
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Handle different config types
        if isinstance(config, str):
            # Check if it's a preset
            if config in cls.GLOBAL_PRESETS:
                config = cls.GLOBAL_PRESETS[config].copy()
            else:
                # Treat as static text
                return TextDataSource(config)
                
        elif callable(config):
            # Function data source
            return FunctionDataSource(config)
            
        elif not isinstance(config, dict):
            # Invalid type
            raise ValueError(f"Invalid data source configuration type: {type(config)}")
            
        # Extract type from config
        source_type = config.get('type')
        
        # Auto-detect type if not specified
        if not source_type:
            source_type = cls._detect_type(config)
            
        if not source_type:
            raise ValueError("Unable to determine data source type from configuration")
            
        # Get the appropriate class
        source_class = cls.DATA_SOURCE_CLASSES.get(source_type)
        
        if not source_class:
            raise ValueError(f"Unknown data source type: {source_type}")
            
        # Create instance with appropriate parameters
        try:
            instance = cls._create_instance(source_class, config, http_client)
            
            # Set HTTP client if needed and not set in constructor
            if http_client and hasattr(instance, 'set_http_client'):
                instance.set_http_client(http_client)
                
            return instance
            
        except Exception as e:
            logger.error(e, f"Error creating data source of type {source_type}")
            raise
            
    @classmethod
    def _detect_type(cls, config):
        """Auto-detect data source type from configuration."""
        # Check for type indicators
        if 'url' in config:
            return 'url'
        elif 'function' in config:
            return 'function'
        elif 'text' in config:
            return 'text'
        elif 'data' in config:
            return 'static'
        elif 'park_id' in config or 'park_preset' in config:
            return 'theme_park'
        elif 'symbols' in config or 'symbol' in config:
            return 'stock'
        elif 'location' in config or 'weather_preset' in config:
            return 'weather'
        else:
            return None
            
    @classmethod
    def _create_instance(cls, source_class, config, http_client):
        """Create an instance of the specified data source class."""
        # Remove type from config to avoid passing it to constructor
        config = config.copy()
        config.pop('type', None)
        
        # Handle specific data source types
        if source_class == ThemeParkDataSource:
            return cls._create_theme_park(config, http_client)
        elif source_class == StockDataSource:
            return cls._create_stock(config, http_client)
        elif source_class == WeatherDataSource:
            return cls._create_weather(config, http_client)
        elif source_class == UrlDataSource:
            return cls._create_url(config, http_client)
        elif source_class == FunctionDataSource:
            return cls._create_function(config)
        elif source_class == TextDataSource:
            return cls._create_text(config)
        elif source_class == StaticDataSource:
            return cls._create_static(config)
        else:
            # Generic creation
            return source_class(**config)
            
    @classmethod
    def _create_theme_park(cls, config, http_client):
        """Create a theme park data source."""
        kwargs = {
            'park_id': config.get('park_id'),
            'preset': config.get('preset') or config.get('park_preset'),
            'cache_ttl': config.get('cache_ttl', 300),
            'rate_limit': config.get('rate_limit', 1.0)
        }
        
        # Remove None values
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        
        instance = ThemeParkDataSource(**kwargs)
        if http_client:
            instance.set_http_client(http_client)
        return instance
        
    @classmethod
    def _create_stock(cls, config, http_client):
        """Create a stock data source."""
        kwargs = {
            'symbols': config.get('symbols') or config.get('symbol'),
            'preset': config.get('preset') or config.get('stock_preset'),
            'provider': config.get('provider', 'alpha_vantage'),
            'api_key': config.get('api_key'),
            'cache_ttl': config.get('cache_ttl', 300),
            'rate_limit': config.get('rate_limit')
        }
        
        # Remove None values
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        
        instance = StockDataSource(**kwargs)
        if http_client:
            instance.set_http_client(http_client)
        return instance
        
    @classmethod
    def _create_weather(cls, config, http_client):
        """Create a weather data source."""
        kwargs = {
            'location': config.get('location'),
            'preset': config.get('preset') or config.get('weather_preset'),
            'units': config.get('units', 'imperial'),
            'api_key': config.get('api_key'),
            'provider': config.get('provider', 'openweathermap'),
            'cache_ttl': config.get('cache_ttl', 600),
            'rate_limit': config.get('rate_limit', 1.0)
        }
        
        # Remove None values
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        
        instance = WeatherDataSource(**kwargs)
        if http_client:
            instance.set_http_client(http_client)
        return instance
        
    @classmethod
    def _create_url(cls, config, http_client):
        """Create a URL data source."""
        kwargs = {
            'url': config.get('url'),
            'parser': config.get('parser', 'auto'),
            'parser_config': config.get('parser_config'),
            'headers': config.get('headers'),
            'cache_ttl': config.get('cache_ttl', 300),
            'rate_limit': config.get('rate_limit', 1.0)
        }
        
        # Remove None values
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        
        instance = UrlDataSource(**kwargs)
        if http_client:
            instance.set_http_client(http_client)
        return instance
        
    @classmethod
    def _create_function(cls, config):
        """Create a function data source."""
        # Handle function specification
        func = config.get('function')
        
        if isinstance(func, str):
            # Built-in function name
            if func == 'time':
                from .function import time_function
                return time_function(
                    format_string=config.get('format', '%H:%M:%S'),
                    timezone=config.get('timezone')
                )
            elif func == 'counter':
                from .function import counter_function
                return counter_function(
                    start=config.get('start', 0),
                    step=config.get('step', 1),
                    prefix=config.get('prefix', 'Count: '),
                    suffix=config.get('suffix', '')
                )
            elif func == 'random':
                from .function import random_choice_function
                choices = config.get('choices', ['Option 1', 'Option 2', 'Option 3'])
                return random_choice_function(
                    choices=choices,
                    prefix=config.get('prefix', ''),
                    suffix=config.get('suffix', '')
                )
            else:
                raise ValueError(f"Unknown built-in function: {func}")
                
        elif callable(func):
            # Custom function
            kwargs = {
                'function': func,
                'formatter': config.get('formatter'),
                'cache_ttl': config.get('cache_ttl', 300),
                'rate_limit': config.get('rate_limit', 0)
            }
            
            # Remove None values
            kwargs = {k: v for k, v in kwargs.items() if v is not None}
            
            return FunctionDataSource(**kwargs)
        else:
            raise ValueError("Function data source requires 'function' field")
            
    @classmethod
    def _create_text(cls, config):
        """Create a text data source."""
        kwargs = {
            'text': config.get('text', ''),
            'style': config.get('style'),
            'cache_ttl': config.get('cache_ttl', 0)  # No caching for static text
        }
        
        # Remove None values
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        
        return TextDataSource(**kwargs)
        
    @classmethod
    def _create_static(cls, config):
        """Create a static data source."""
        kwargs = {
            'name': config.get('name', 'Static'),
            'data': config.get('data'),
            'cache_ttl': config.get('cache_ttl', 0)  # No caching for static data
        }
        
        # Remove None values
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        
        return StaticDataSource(**kwargs)
        
    @classmethod
    def list_presets(cls):
        """
        Get a list of all available presets.
        
        Returns:
            List of preset names
        """
        return list(cls.GLOBAL_PRESETS.keys())
        
    @classmethod
    def get_preset_info(cls, preset_name):
        """
        Get information about a specific preset.
        
        Args:
            preset_name: Name of the preset
            
        Returns:
            Preset configuration or None if not found
        """
        return cls.GLOBAL_PRESETS.get(preset_name)


# Convenience function
def create_data_source(config, http_client=None):
    """
    Create a data source from configuration.
    
    This is a convenience function that uses the DataSourceFactory.
    
    Args:
        config: Data source configuration
        http_client: Optional HTTP client
        
    Returns:
        DataSource instance
    """
    return DataSourceFactory.create(config, http_client)