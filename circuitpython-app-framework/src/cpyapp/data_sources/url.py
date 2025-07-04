"""
Generic URL Data Source for fetching data from any HTTP endpoint.

This module provides a flexible data source that can fetch and parse
data from any URL with configurable parsers.
"""
import json
try:
    from typing import Dict, Any, Optional, List, Callable
except ImportError:
    # CircuitPython doesn't have typing
    pass

from .base import HttpDataSource
from ..utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")


class UrlDataSource(HttpDataSource):
    """
    Generic data source for fetching data from any URL.
    
    This class provides a flexible way to fetch data from any HTTP endpoint
    and parse it using configurable parsers.
    """
    
    def __init__(self, url, parser='auto', parser_config=None, headers=None, **kwargs):
        """
        Initialize URL data source.
        
        Args:
            url: The URL to fetch data from
            parser: Parser type or callable
                - 'auto': Auto-detect JSON or text
                - 'json': Parse as JSON
                - 'text': Keep as plain text
                - 'json_path': Extract using JSON path (requires parser_config['path'])
                - callable: Custom parser function(response_text, config) -> data
            parser_config: Configuration for the parser
            headers: Optional HTTP headers
            **kwargs: Additional arguments passed to HttpDataSource
        """
        self.parser = parser
        self.parser_config = parser_config or {}
        
        super().__init__("URL", url=url, **kwargs)
        
        if headers:
            self.set_headers(headers)
            
    def parse_data(self, raw_data):
        """Parse the raw response data based on parser configuration."""
        if self.parser == 'auto':
            # Auto-detect format
            if isinstance(raw_data, dict) or isinstance(raw_data, list):
                # Already parsed (JSON)
                return raw_data
            elif isinstance(raw_data, str):
                # Try JSON first
                try:
                    return json.loads(raw_data)
                except ValueError:
                    # Not JSON, keep as text
                    return raw_data
            else:
                return raw_data
                
        elif self.parser == 'json':
            # Force JSON parsing
            if isinstance(raw_data, str):
                try:
                    return json.loads(raw_data)
                except ValueError as e:
                    logger.error(e, "Failed to parse response as JSON")
                    return None
            else:
                return raw_data
                
        elif self.parser == 'text':
            # Keep as text
            return str(raw_data)
            
        elif self.parser == 'json_path':
            # Extract using JSON path
            if 'path' not in self.parser_config:
                logger.error(None, "json_path parser requires 'path' in parser_config")
                return raw_data
                
            # Parse JSON if needed
            if isinstance(raw_data, str):
                try:
                    data = json.loads(raw_data)
                except ValueError:
                    logger.error(None, "json_path parser requires valid JSON")
                    return None
            else:
                data = raw_data
                
            # Apply JSON path
            return self._apply_json_path(data, self.parser_config['path'])
            
        elif callable(self.parser):
            # Custom parser function
            try:
                return self.parser(raw_data, self.parser_config)
            except Exception as e:
                logger.error(e, "Error in custom parser")
                return None
                
        else:
            logger.warning(f"Unknown parser type: {self.parser}")
            return raw_data
            
    def _apply_json_path(self, data, path):
        """Apply a JSON path to extract data."""
        parts = path.split('.')
        result = data
        
        for part in parts:
            if '[' in part and ']' in part:
                # Handle array index notation
                field, index_str = part.split('[')
                index = int(index_str.rstrip(']'))
                
                # Navigate to field first if present
                if field and isinstance(result, dict):
                    result = result.get(field)
                    
                # Then apply index
                if isinstance(result, list) and 0 <= index < len(result):
                    result = result[index]
                else:
                    return None
                    
            elif isinstance(result, dict) and part in result:
                result = result[part]
            elif isinstance(result, list):
                # Handle array operations
                if part == '*':
                    # Return all items
                    return result
                elif part.isdigit():
                    # Numeric index
                    index = int(part)
                    if 0 <= index < len(result):
                        result = result[index]
                    else:
                        return None
                else:
                    # Extract field from all items
                    return [item.get(part) for item in result if isinstance(item, dict)]
            else:
                return None
                
        return result
        
    def format_for_display(self, data):
        """Format data for display based on its type."""
        messages = []
        
        if data is None:
            return [{
                'type': 'scroll',
                'text': 'No data available',
                'delay': 2
            }]
            
        # Check for format configuration
        if 'format' in self.parser_config:
            return self._format_with_template(data)
            
        # Auto-format based on data type
        if isinstance(data, str):
            # Simple text
            return [{
                'type': 'scroll',
                'text': data,
                'delay': 2
            }]
            
        elif isinstance(data, list):
            # List of items
            for item in data:
                if isinstance(item, str):
                    messages.append({
                        'type': 'scroll',
                        'text': item,
                        'delay': 2
                    })
                elif isinstance(item, dict):
                    # Format dict item
                    text = self._format_dict_item(item)
                    if text:
                        messages.append({
                            'type': 'scroll',
                            'text': text,
                            'delay': 2
                        })
                else:
                    messages.append({
                        'type': 'scroll',
                        'text': str(item),
                        'delay': 2
                    })
                    
        elif isinstance(data, dict):
            # Single dict - check for common patterns
            if 'messages' in data and isinstance(data['messages'], list):
                # Pre-formatted messages
                return data['messages']
            elif 'items' in data and isinstance(data['items'], list):
                # Items list
                for item in data['items']:
                    text = self._format_dict_item(item)
                    if text:
                        messages.append({
                            'type': 'scroll',
                            'text': text,
                            'delay': 2
                        })
            else:
                # Format the dict itself
                text = self._format_dict_item(data)
                if text:
                    messages.append({
                        'type': 'scroll',
                        'text': text,
                        'delay': 2
                    })
                    
        else:
            # Fallback to string representation
            messages.append({
                'type': 'scroll',
                'text': str(data),
                'delay': 2
            })
            
        return messages if messages else [{
            'type': 'scroll',
            'text': 'Unable to format data',
            'delay': 2
        }]
        
    def _format_dict_item(self, item):
        """Format a dictionary item for display."""
        if not isinstance(item, dict):
            return str(item)
            
        # Check for common fields
        if 'text' in item:
            return item['text']
        elif 'message' in item:
            return item['message']
        elif 'title' in item:
            if 'value' in item:
                return f"{item['title']}: {item['value']}"
            else:
                return item['title']
        elif 'name' in item:
            if 'value' in item:
                return f"{item['name']}: {item['value']}"
            elif 'status' in item:
                return f"{item['name']} - {item['status']}"
            else:
                return item['name']
        else:
            # Create a summary of the first few fields
            parts = []
            for key, value in list(item.items())[:3]:
                if not key.startswith('_') and isinstance(value, (str, int, float)):
                    parts.append(f"{key}: {value}")
            return " | ".join(parts) if parts else str(item)
            
    def _format_with_template(self, data):
        """Format data using a template string."""
        template = self.parser_config.get('format', '{data}')
        messages = []
        
        if isinstance(data, list):
            # Apply template to each item
            for item in data:
                try:
                    if isinstance(item, dict):
                        text = template.format(**item, data=item)
                    else:
                        text = template.format(data=item, item=item)
                    messages.append({
                        'type': 'scroll',
                        'text': text,
                        'delay': 2
                    })
                except Exception as e:
                    logger.error(e, "Error formatting with template")
                    messages.append({
                        'type': 'scroll',
                        'text': str(item),
                        'delay': 2
                    })
        else:
            # Apply template to single item
            try:
                if isinstance(data, dict):
                    text = template.format(**data, data=data)
                else:
                    text = template.format(data=data)
                messages.append({
                    'type': 'scroll',
                    'text': text,
                    'delay': 2
                })
            except Exception as e:
                logger.error(e, "Error formatting with template")
                messages.append({
                    'type': 'scroll',
                    'text': str(data),
                    'delay': 2
                })
                
        return messages