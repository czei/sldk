"""
Data Sources for CircuitPython App Framework.

This module provides built-in data sources for common use cases including
theme parks, stocks, weather, and generic data fetching.
"""

# Base classes
from .base import DataSource, HttpDataSource, StaticDataSource

# Specific data sources
from .theme_park import ThemeParkDataSource
from .stock import StockDataSource
from .weather import WeatherDataSource
from .url import UrlDataSource
from .function import FunctionDataSource
from .text import TextDataSource

# Utilities
from .parsers import (
    parser_registry,
    extract_json_path,
    extract_multiple_paths,
    format_template,
    format_number,
    format_percentage,
    format_currency,
    flatten_dict,
    group_by_field,
    filter_items,
    sort_items
)

# Factory
from .factory import DataSourceFactory, create_data_source

# Convenience functions from text module
from .text import (
    create_message_list,
    create_formatted_text,
    create_scrolling_banner,
    create_alternating_messages
)

# Convenience functions from function module
from .function import (
    time_function,
    counter_function,
    random_choice_function,
    sensor_function
)

__all__ = [
    # Base classes
    'DataSource',
    'HttpDataSource',
    'StaticDataSource',
    
    # Specific data sources
    'ThemeParkDataSource',
    'StockDataSource',
    'WeatherDataSource',
    'UrlDataSource',
    'FunctionDataSource',
    'TextDataSource',
    
    # Factory
    'DataSourceFactory',
    'create_data_source',
    
    # Parser utilities
    'parser_registry',
    'extract_json_path',
    'extract_multiple_paths',
    'format_template',
    'format_number',
    'format_percentage',
    'format_currency',
    
    # Data utilities
    'flatten_dict',
    'group_by_field',
    'filter_items',
    'sort_items',
    
    # Convenience functions
    'create_message_list',
    'create_formatted_text',
    'create_scrolling_banner',
    'create_alternating_messages',
    'time_function',
    'counter_function',
    'random_choice_function',
    'sensor_function',
]