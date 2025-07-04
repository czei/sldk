"""
Parser utilities for data sources.

This module provides common parsing functions and utilities for
extracting and formatting data from various sources.
"""
import json
try:
    from typing import Any, Dict, List, Union, Callable, Optional
except ImportError:
    # CircuitPython doesn't have typing
    pass

from ..utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")


class ParserRegistry:
    """Registry for custom parsers."""
    
    def __init__(self):
        self.parsers = {}
        
    def register(self, name, parser):
        """
        Register a custom parser.
        
        Args:
            name: Parser name
            parser: Parser function(data, config) -> parsed_data
        """
        self.parsers[name] = parser
        logger.info(f"Registered parser: {name}")
        
    def get(self, name):
        """Get a registered parser by name."""
        return self.parsers.get(name)
        
    def list(self):
        """List all registered parsers."""
        return list(self.parsers.keys())


# Global parser registry
parser_registry = ParserRegistry()


# JSON Path utilities

def extract_json_path(data, path):
    """
    Extract data using a JSON path expression.
    
    Args:
        data: The data to extract from
        path: JSON path string (e.g., "user.profile.name", "items[0].value")
        
    Returns:
        The extracted value or None if path not found
        
    Examples:
        extract_json_path({'user': {'name': 'John'}}, 'user.name') -> 'John'
        extract_json_path({'items': [{'id': 1}, {'id': 2}]}, 'items[1].id') -> 2
        extract_json_path({'items': [1, 2, 3]}, 'items[*]') -> [1, 2, 3]
    """
    if not path:
        return data
        
    parts = path.split('.')
    result = data
    
    for part in parts:
        if result is None:
            return None
            
        # Handle array notation
        if '[' in part and ']' in part:
            field, index_part = part.split('[', 1)
            index_str = index_part.rstrip(']')
            
            # Navigate to field first if present
            if field and isinstance(result, dict):
                result = result.get(field)
                
            # Handle array operations
            if isinstance(result, list):
                if index_str == '*':
                    # Return all items
                    return result
                elif index_str.isdigit():
                    # Specific index
                    index = int(index_str)
                    if 0 <= index < len(result):
                        result = result[index]
                    else:
                        return None
                else:
                    # Complex expression not supported
                    return None
            else:
                return None
                
        # Handle regular field access
        elif isinstance(result, dict):
            result = result.get(part)
        elif isinstance(result, list):
            if part == '*':
                return result
            elif part.isdigit():
                index = int(part)
                if 0 <= index < len(result):
                    result = result[index]
                else:
                    return None
            else:
                # Extract field from all items
                extracted = []
                for item in result:
                    if isinstance(item, dict) and part in item:
                        extracted.append(item[part])
                return extracted if extracted else None
        else:
            return None
            
    return result


def extract_multiple_paths(data, paths):
    """
    Extract multiple values using JSON paths.
    
    Args:
        data: The data to extract from
        paths: Dictionary mapping names to JSON paths
        
    Returns:
        Dictionary with extracted values
        
    Example:
        paths = {
            'username': 'user.profile.name',
            'email': 'user.contact.email',
            'score': 'stats.score'
        }
        extract_multiple_paths(data, paths) -> {'username': 'John', ...}
    """
    results = {}
    
    for name, path in paths.items():
        value = extract_json_path(data, path)
        if value is not None:
            results[name] = value
            
    return results


# Text formatting utilities

def format_template(template, data):
    """
    Format a template string with data.
    
    Args:
        template: Template string with {field} placeholders
        data: Dictionary of values
        
    Returns:
        Formatted string
        
    Example:
        format_template("Hello {name}!", {'name': 'World'}) -> "Hello World!"
    """
    try:
        return template.format(**data)
    except KeyError as e:
        logger.warning(f"Missing template field: {e}")
        return template
    except Exception as e:
        logger.error(e, "Error formatting template")
        return template


def format_number(value, decimals=2, thousands_sep=True):
    """
    Format a number for display.
    
    Args:
        value: Numeric value
        decimals: Number of decimal places
        thousands_sep: Whether to include thousands separator
        
    Returns:
        Formatted string
    """
    try:
        num = float(value)
        
        if decimals == 0:
            result = str(int(num))
        else:
            # Simple decimal formatting for CircuitPython
            factor = 10 ** decimals
            rounded = int(num * factor + 0.5) / factor
            result = f"{rounded:.{decimals}f}"
            
        if thousands_sep and abs(num) >= 1000:
            # Add thousands separator manually
            parts = result.split('.')
            whole = parts[0]
            
            # Add commas
            formatted_whole = ''
            for i, digit in enumerate(reversed(whole)):
                if i > 0 and i % 3 == 0 and digit != '-':
                    formatted_whole = ',' + formatted_whole
                formatted_whole = digit + formatted_whole
                
            result = formatted_whole
            if len(parts) > 1:
                result += '.' + parts[1]
                
        return result
        
    except (ValueError, TypeError):
        return str(value)


def format_percentage(value, decimals=1):
    """
    Format a value as a percentage.
    
    Args:
        value: Numeric value (0.5 = 50%)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    try:
        percentage = float(value) * 100
        return format_number(percentage, decimals, False) + '%'
    except (ValueError, TypeError):
        return str(value)


def format_currency(value, symbol='$', decimals=2):
    """
    Format a value as currency.
    
    Args:
        value: Numeric value
        symbol: Currency symbol
        decimals: Number of decimal places
        
    Returns:
        Formatted currency string
    """
    try:
        formatted = format_number(abs(value), decimals, True)
        if value < 0:
            return f"-{symbol}{formatted}"
        else:
            return f"{symbol}{formatted}"
    except (ValueError, TypeError):
        return f"{symbol}{value}"


# Data transformation utilities

def flatten_dict(data, separator='.', prefix=''):
    """
    Flatten a nested dictionary.
    
    Args:
        data: Dictionary to flatten
        separator: Separator for nested keys
        prefix: Prefix for all keys
        
    Returns:
        Flattened dictionary
        
    Example:
        flatten_dict({'user': {'name': 'John', 'age': 30}})
        -> {'user.name': 'John', 'user.age': 30}
    """
    flattened = {}
    
    for key, value in data.items():
        new_key = f"{prefix}{separator}{key}" if prefix else key
        
        if isinstance(value, dict):
            flattened.update(flatten_dict(value, separator, new_key))
        else:
            flattened[new_key] = value
            
    return flattened


def group_by_field(items, field):
    """
    Group a list of items by a field value.
    
    Args:
        items: List of dictionaries
        field: Field name to group by
        
    Returns:
        Dictionary mapping field values to lists of items
        
    Example:
        items = [
            {'category': 'A', 'value': 1},
            {'category': 'B', 'value': 2},
            {'category': 'A', 'value': 3}
        ]
        group_by_field(items, 'category')
        -> {'A': [...], 'B': [...]}
    """
    groups = {}
    
    for item in items:
        if isinstance(item, dict) and field in item:
            key = item[field]
            if key not in groups:
                groups[key] = []
            groups[key].append(item)
            
    return groups


def filter_items(items, conditions):
    """
    Filter a list of items based on conditions.
    
    Args:
        items: List of items to filter
        conditions: Dictionary of field -> value conditions
        
    Returns:
        Filtered list
        
    Example:
        filter_items(items, {'status': 'active', 'priority': 'high'})
    """
    filtered = []
    
    for item in items:
        if isinstance(item, dict):
            match = True
            for field, value in conditions.items():
                if field not in item or item[field] != value:
                    match = False
                    break
            if match:
                filtered.append(item)
                
    return filtered


def sort_items(items, field, reverse=False):
    """
    Sort a list of items by a field.
    
    Args:
        items: List of dictionaries
        field: Field to sort by
        reverse: Sort in descending order
        
    Returns:
        Sorted list
    """
    def get_sort_key(item):
        if isinstance(item, dict) and field in item:
            return item[field]
        return None
        
    try:
        return sorted(items, key=get_sort_key, reverse=reverse)
    except Exception as e:
        logger.error(e, "Error sorting items")
        return items


# Built-in parsers

def parse_csv_line(line, delimiter=','):
    """
    Parse a CSV line into fields.
    
    Args:
        line: CSV line string
        delimiter: Field delimiter
        
    Returns:
        List of field values
    """
    # Simple CSV parser for CircuitPython
    fields = []
    current_field = ''
    in_quotes = False
    
    for char in line:
        if char == '"':
            in_quotes = not in_quotes
        elif char == delimiter and not in_quotes:
            fields.append(current_field.strip())
            current_field = ''
        else:
            current_field += char
            
    # Add last field
    if current_field:
        fields.append(current_field.strip())
        
    return fields


def parse_key_value_pairs(text, delimiter=':', separator='\n'):
    """
    Parse key-value pairs from text.
    
    Args:
        text: Text containing key-value pairs
        delimiter: Delimiter between key and value
        separator: Separator between pairs
        
    Returns:
        Dictionary of parsed pairs
        
    Example:
        parse_key_value_pairs("name: John\nage: 30")
        -> {'name': 'John', 'age': '30'}
    """
    pairs = {}
    
    for line in text.split(separator):
        line = line.strip()
        if delimiter in line:
            key, value = line.split(delimiter, 1)
            pairs[key.strip()] = value.strip()
            
    return pairs


# Register built-in parsers
parser_registry.register('json_path', lambda data, config: extract_json_path(data, config.get('path', '')))
parser_registry.register('template', lambda data, config: format_template(config.get('template', ''), data))
parser_registry.register('csv', lambda data, config: parse_csv_line(data, config.get('delimiter', ',')))
parser_registry.register('key_value', lambda data, config: parse_key_value_pairs(data, config.get('delimiter', ':'), config.get('separator', '\n')))