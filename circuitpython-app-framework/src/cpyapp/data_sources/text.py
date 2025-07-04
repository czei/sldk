"""
Text Data Source for static text content.

This module provides a simple data source for displaying static text
or pre-formatted messages.
"""
try:
    from typing import Union, List, Dict, Any
except ImportError:
    # CircuitPython doesn't have typing
    pass

from .base import StaticDataSource
from ..utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")


class TextDataSource(StaticDataSource):
    """
    Data source for static text content.
    
    This class provides a simple way to display static text messages
    with optional formatting and styling.
    """
    
    def __init__(self, text, style=None, **kwargs):
        """
        Initialize text data source.
        
        Args:
            text: The text content
                - String: Single message
                - List of strings: Multiple messages
                - List of dicts: Pre-formatted messages with properties
            style: Optional style configuration
                - 'scroll': Normal scrolling (default)
                - 'static': Static display
                - 'blink': Blinking text
                - Dict: Custom style properties
            **kwargs: Additional arguments passed to StaticDataSource
        """
        self.style = style or 'scroll'
        
        # Process text into standard format
        if isinstance(text, str):
            data = [text]
        elif isinstance(text, list):
            data = text
        else:
            data = [str(text)]
            
        super().__init__("Text", data=data, **kwargs)
        
    def format_for_display(self, data):
        """Format text data for display with styling."""
        messages = []
        
        if not data:
            return [{
                'type': 'scroll',
                'text': '',
                'delay': 2
            }]
            
        # Apply style to each message
        for item in data:
            if isinstance(item, str):
                # Simple string - apply style
                message = self._create_message(item)
                messages.append(message)
            elif isinstance(item, dict):
                # Pre-formatted message - merge with style
                message = item.copy()
                if 'type' not in message:
                    message['type'] = 'scroll'
                if 'delay' not in message:
                    message['delay'] = 2
                messages.append(message)
            else:
                # Convert to string and apply style
                message = self._create_message(str(item))
                messages.append(message)
                
        return messages
        
    def _create_message(self, text):
        """Create a message dict with the configured style."""
        if isinstance(self.style, dict):
            # Custom style dict
            message = {
                'type': self.style.get('type', 'scroll'),
                'text': text,
                'delay': self.style.get('delay', 2)
            }
            
            # Add optional properties
            if 'color' in self.style:
                message['color'] = self.style['color']
            if 'speed' in self.style:
                message['speed'] = self.style['speed']
            if 'font' in self.style:
                message['font'] = self.style['font']
                
            return message
            
        elif self.style == 'static':
            return {
                'type': 'static',
                'text': text,
                'delay': 5
            }
        elif self.style == 'blink':
            return {
                'type': 'blink',
                'text': text,
                'delay': 3
            }
        else:
            # Default scroll style
            return {
                'type': 'scroll',
                'text': text,
                'delay': 2
            }


def create_message_list(*messages, delay=2, style='scroll'):
    """
    Convenience function to create a text data source with multiple messages.
    
    Args:
        *messages: Variable number of text messages
        delay: Delay between messages
        style: Display style for all messages
        
    Returns:
        TextDataSource configured with the messages
        
    Example:
        source = create_message_list(
            "Welcome!",
            "Temperature: 72°F",
            "Have a great day!",
            delay=3
        )
    """
    formatted_messages = []
    
    for msg in messages:
        formatted_messages.append({
            'type': style,
            'text': msg,
            'delay': delay
        })
        
    return TextDataSource(formatted_messages)


def create_formatted_text(template, data, style='scroll'):
    """
    Create a text data source with formatted text.
    
    Args:
        template: Format string template
        data: Dictionary of values to format into template
        style: Display style
        
    Returns:
        TextDataSource with formatted text
        
    Example:
        source = create_formatted_text(
            "Hello {name}! The time is {time}.",
            {'name': 'World', 'time': '12:00'}
        )
    """
    try:
        text = template.format(**data)
    except Exception as e:
        logger.error(e, "Error formatting text")
        text = template
        
    return TextDataSource(text, style=style)


def create_scrolling_banner(messages, separator=" • ", style=None):
    """
    Create a scrolling banner from multiple messages.
    
    Args:
        messages: List of messages to join
        separator: Separator between messages
        style: Optional style configuration
        
    Returns:
        TextDataSource with joined messages
        
    Example:
        source = create_scrolling_banner([
            "Breaking News",
            "Weather: Sunny 72°F",
            "Traffic: Clear"
        ])
    """
    banner_text = separator.join(messages)
    return TextDataSource(banner_text, style=style)


def create_alternating_messages(messages, delay=3):
    """
    Create a data source that alternates between messages.
    
    Args:
        messages: List of messages to alternate
        delay: Time to show each message
        
    Returns:
        TextDataSource configured for alternating display
        
    Example:
        source = create_alternating_messages([
            "Welcome to the Matrix",
            "Current Time: 12:00",
            "Temperature: 72°F"
        ], delay=5)
    """
    formatted = []
    for msg in messages:
        formatted.append({
            'type': 'scroll',
            'text': msg,
            'delay': delay
        })
        
    return TextDataSource(formatted)