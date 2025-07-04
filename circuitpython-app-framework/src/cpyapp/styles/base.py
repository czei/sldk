"""
Base style class for display styles.

This module provides the abstract interface for all display styles,
with common functionality for color management, animation settings,
and integration with the display system.

Copyright 2024 3DUPFitters LLC
"""
import sys

# Platform detection
IS_CIRCUITPYTHON = hasattr(sys, 'implementation') and sys.implementation.name == 'circuitpython'

# Import ColorUtils from parent directory
from ..utils.colors import ColorUtils
from ..utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")


class BaseStyle:
    """
    Abstract base class for all display styles.
    
    This class provides common functionality for managing display styles
    including colors, animations, fonts, and layout.
    """
    
    def __init__(self, name="default"):
        """
        Initialize the base style.
        
        Args:
            name: The name of this style
        """
        self.name = name
        
        # Default style properties
        self._properties = {
            # Text properties
            'text_color': ColorUtils.colors["White"],
            'background_color': ColorUtils.colors["Black"],
            'font_scale': 1,
            
            # Scrolling properties
            'scroll_speed': 0.05,  # Seconds between scroll steps
            'scroll_delay': 2,     # Delay after scrolling completes
            'scroll_direction': 'left',  # left, right, up, down
            
            # Animation properties
            'transition_effect': None,  # None, fade, slide, reveal
            'transition_speed': 0.1,
            'pulse_enabled': False,
            'pulse_speed': 1.0,
            'color_cycle_enabled': False,
            'color_cycle_speed': 1.0,
            
            # Layout properties
            'text_align': 'left',  # left, center, right
            'vertical_align': 'center',  # top, center, bottom
            'padding_x': 0,
            'padding_y': 0,
            
            # Message properties
            'message_delay': 3,  # Delay between messages
            'static_duration': 3,  # Duration for static messages
            
            # Special effects
            'rainbow_enabled': False,
            'sparkle_enabled': False,
            'breathe_enabled': False,
            'breathe_speed': 2.0,
            
            # Brightness
            'brightness': 0.5,
            'brightness_scale': 0.5,
        }
        
    def get_property(self, key, default=None):
        """
        Get a style property value.
        
        Args:
            key: The property key
            default: Default value if property doesn't exist
            
        Returns:
            The property value
        """
        return self._properties.get(key, default)
        
    def set_property(self, key, value):
        """
        Set a style property value.
        
        Args:
            key: The property key
            value: The property value
        """
        self._properties[key] = value
        
    def update_properties(self, properties):
        """
        Update multiple properties at once.
        
        Args:
            properties: Dictionary of properties to update
        """
        self._properties.update(properties)
        
    def get_color(self, color_key, brightness_scale=None):
        """
        Get a color value with optional brightness scaling.
        
        Args:
            color_key: The color property key
            brightness_scale: Optional brightness scale override
            
        Returns:
            The color value as hex string
        """
        color = self._properties.get(color_key, ColorUtils.colors["White"])
        
        # Handle special color values
        if color == 'rainbow':
            # Return a marker that the display handler will interpret
            return 'rainbow'
            
        # Apply brightness scaling if needed
        if brightness_scale is None:
            brightness_scale = self._properties.get('brightness_scale', 0.5)
            
        if brightness_scale < 1.0:
            color = ColorUtils.scale_color(color, brightness_scale)
            
        return color
        
    def get_text_color(self):
        """Get the text color with brightness applied."""
        return self.get_color('text_color')
        
    def get_background_color(self):
        """Get the background color with brightness applied."""
        return self.get_color('background_color')
        
    def apply_to_display(self, display):
        """
        Apply this style to a display instance.
        
        Args:
            display: The display instance
        """
        # Set brightness
        if hasattr(display, 'set_brightness'):
            display.set_brightness(self._properties.get('brightness', 0.5))
            
        # More style applications can be added here
        
    def apply_to_label(self, label):
        """
        Apply this style to a text label.
        
        Args:
            label: The label instance
        """
        try:
            # Set text color
            color = self.get_text_color()
            if color != 'rainbow':  # Rainbow is handled elsewhere
                label.color = self._convert_color(color)
                
            # Set scale
            if hasattr(label, 'scale'):
                label.scale = self._properties.get('font_scale', 1)
                
        except Exception as e:
            logger.error(e, f"Error applying style to label")
            
    def _convert_color(self, color):
        """
        Convert color to platform-appropriate format.
        
        Args:
            color: Color value as hex string
            
        Returns:
            Platform-appropriate color value
        """
        if IS_CIRCUITPYTHON:
            return int(color, 16) if isinstance(color, str) else int(color)
        else:
            # Handle both string hex and numeric values
            if isinstance(color, str):
                return int(color, 16)
            return int(color)
            
    def get_scroll_config(self):
        """
        Get scrolling configuration.
        
        Returns:
            Dictionary with scroll configuration
        """
        return {
            'speed': self._properties.get('scroll_speed', 0.05),
            'delay': self._properties.get('scroll_delay', 2),
            'direction': self._properties.get('scroll_direction', 'left'),
        }
        
    def get_animation_config(self):
        """
        Get animation configuration.
        
        Returns:
            Dictionary with animation configuration
        """
        return {
            'transition_effect': self._properties.get('transition_effect', None),
            'transition_speed': self._properties.get('transition_speed', 0.1),
            'pulse_enabled': self._properties.get('pulse_enabled', False),
            'pulse_speed': self._properties.get('pulse_speed', 1.0),
            'color_cycle_enabled': self._properties.get('color_cycle_enabled', False),
            'color_cycle_speed': self._properties.get('color_cycle_speed', 1.0),
            'rainbow_enabled': self._properties.get('rainbow_enabled', False),
            'sparkle_enabled': self._properties.get('sparkle_enabled', False),
            'breathe_enabled': self._properties.get('breathe_enabled', False),
            'breathe_speed': self._properties.get('breathe_speed', 2.0),
        }
        
    def get_layout_config(self):
        """
        Get layout configuration.
        
        Returns:
            Dictionary with layout configuration
        """
        return {
            'text_align': self._properties.get('text_align', 'left'),
            'vertical_align': self._properties.get('vertical_align', 'center'),
            'padding_x': self._properties.get('padding_x', 0),
            'padding_y': self._properties.get('padding_y', 0),
        }
        
    def to_dict(self):
        """
        Convert style to dictionary representation.
        
        Returns:
            Dictionary with all style properties
        """
        return self._properties.copy()
        
    def from_dict(self, properties):
        """
        Load style from dictionary representation.
        
        Args:
            properties: Dictionary with style properties
        """
        self._properties = properties.copy()
        
    def clone(self):
        """
        Create a copy of this style.
        
        Returns:
            A new style instance with the same properties
        """
        # Create a generic BaseStyle instance for cloning
        # This avoids issues with subclass constructors
        new_style = BaseStyle(self.name + "_copy")
        new_style.from_dict(self.to_dict())
        return new_style
        
    def merge(self, other_style):
        """
        Merge another style into this one.
        
        Args:
            other_style: Another style instance or dictionary
        """
        if isinstance(other_style, BaseStyle):
            self.update_properties(other_style.to_dict())
        elif isinstance(other_style, dict):
            self.update_properties(other_style)
            
    def __repr__(self):
        """String representation of the style."""
        return f"<{self.__class__.__name__}('{self.name}')>"