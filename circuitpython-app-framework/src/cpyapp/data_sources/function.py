"""
Function Data Source for dynamic content generation.

This module provides a data source that executes functions to generate
display content dynamically.
"""
import asyncio
try:
    from typing import Callable, Any, Optional, List, Dict
except ImportError:
    # CircuitPython doesn't have typing
    pass

from .base import DataSource
from ..utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")


class FunctionDataSource(DataSource):
    """
    Data source that executes functions to generate content.
    
    This class allows you to use any function (sync or async) as a data source,
    making it easy to create dynamic content from code.
    """
    
    def __init__(self, function, formatter=None, **kwargs):
        """
        Initialize function data source.
        
        Args:
            function: The function to call for data
                - Can be sync or async
                - Should return data (string, list, dict, etc.)
            formatter: Optional formatter function to process the result
                - Called as formatter(result) -> formatted_data
            **kwargs: Additional arguments passed to DataSource
        """
        self.function = function
        self.formatter = formatter
        
        # Detect if function is async
        self.is_async = asyncio.iscoroutinefunction(function)
        
        super().__init__("Function", **kwargs)
        
    async def _fetch_data(self):
        """Execute the function to get data."""
        try:
            if self.is_async:
                # Async function
                result = await self.function()
            else:
                # Sync function
                result = self.function()
                
            # Apply formatter if provided
            if self.formatter:
                result = self.formatter(result)
                
            return result
            
        except Exception as e:
            logger.error(e, "Error executing data source function")
            raise
            
    def format_for_display(self, data):
        """Format function result for display."""
        messages = []
        
        if data is None:
            return [{
                'type': 'scroll',
                'text': 'No data from function',
                'delay': 2
            }]
            
        # Handle different return types
        if isinstance(data, str):
            # Simple string
            return [{
                'type': 'scroll',
                'text': data,
                'delay': 2
            }]
            
        elif isinstance(data, (int, float)):
            # Numeric value
            return [{
                'type': 'scroll',
                'text': str(data),
                'delay': 2
            }]
            
        elif isinstance(data, list):
            # List of items
            for item in data:
                if isinstance(item, dict) and 'type' in item:
                    # Pre-formatted message
                    messages.append(item)
                elif isinstance(item, str):
                    messages.append({
                        'type': 'scroll',
                        'text': item,
                        'delay': 2
                    })
                else:
                    messages.append({
                        'type': 'scroll',
                        'text': str(item),
                        'delay': 2
                    })
                    
        elif isinstance(data, dict):
            # Dictionary result
            if 'messages' in data:
                # Pre-formatted messages
                return data['messages']
            elif 'text' in data:
                # Single text message
                return [{
                    'type': 'scroll',
                    'text': data['text'],
                    'delay': data.get('delay', 2)
                }]
            else:
                # Format as key-value pairs
                for key, value in data.items():
                    if not key.startswith('_'):
                        messages.append({
                            'type': 'scroll',
                            'text': f"{key}: {value}",
                            'delay': 1.5
                        })
                        
        else:
            # Unknown type - convert to string
            return [{
                'type': 'scroll',
                'text': str(data),
                'delay': 2
            }]
            
        return messages if messages else [{
            'type': 'scroll',
            'text': 'Unable to format function result',
            'delay': 2
        }]


# Convenience functions for common patterns

def time_function(format_string="%H:%M:%S", timezone=None):
    """
    Create a function data source that displays current time.
    
    Args:
        format_string: strftime format string
        timezone: Optional timezone (not supported in CircuitPython)
        
    Returns:
        FunctionDataSource configured for time display
    """
    def get_time():
        try:
            import time
            if hasattr(time, 'strftime'):
                # Standard Python
                return time.strftime(format_string)
            else:
                # CircuitPython - manual formatting
                t = time.localtime()
                # Basic implementation of common formats
                if format_string == "%H:%M:%S":
                    return f"{t.tm_hour:02d}:{t.tm_min:02d}:{t.tm_sec:02d}"
                elif format_string == "%H:%M":
                    return f"{t.tm_hour:02d}:{t.tm_min:02d}"
                elif format_string == "%Y-%m-%d":
                    return f"{t.tm_year}-{t.tm_mon:02d}-{t.tm_mday:02d}"
                else:
                    # Fallback
                    return f"{t.tm_hour:02d}:{t.tm_min:02d}:{t.tm_sec:02d}"
        except Exception as e:
            logger.error(e, "Error getting time")
            return "Time Error"
            
    return FunctionDataSource(get_time, cache_ttl=1)


def counter_function(start=0, step=1, prefix="Count: ", suffix=""):
    """
    Create a function data source that displays an incrementing counter.
    
    Args:
        start: Starting value
        step: Increment step
        prefix: Text before the counter
        suffix: Text after the counter
        
    Returns:
        FunctionDataSource configured for counter display
    """
    counter = {'value': start}
    
    def get_count():
        result = f"{prefix}{counter['value']}{suffix}"
        counter['value'] += step
        return result
        
    return FunctionDataSource(get_count, cache_ttl=0)  # No caching


def random_choice_function(choices, prefix="", suffix=""):
    """
    Create a function data source that displays random choices.
    
    Args:
        choices: List of strings to choose from
        prefix: Text before the choice
        suffix: Text after the choice
        
    Returns:
        FunctionDataSource configured for random choice display
    """
    import random
    
    def get_choice():
        choice = random.choice(choices)
        return f"{prefix}{choice}{suffix}"
        
    return FunctionDataSource(get_choice, cache_ttl=0)  # No caching


def sensor_function(sensor_getter, formatter=None):
    """
    Create a function data source for sensor readings.
    
    Args:
        sensor_getter: Function that returns sensor value(s)
        formatter: Optional function to format the sensor data
        
    Returns:
        FunctionDataSource configured for sensor display
    """
    if formatter is None:
        # Default formatter
        def formatter(value):
            if isinstance(value, (int, float)):
                return f"Sensor: {value}"
            elif isinstance(value, dict):
                parts = []
                for k, v in value.items():
                    parts.append(f"{k}: {v}")
                return " | ".join(parts)
            else:
                return str(value)
                
    return FunctionDataSource(sensor_getter, formatter=formatter)