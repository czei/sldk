"""
Style factory for creating and managing display styles.

This module provides a factory pattern for creating styles from
various sources including names, configurations, and custom definitions.

Copyright 2024 3DUPFitters LLC
"""
from .base import BaseStyle
from .templates import get_core_style, list_core_styles
from .themes import get_theme_style, list_theme_styles
from .animations import get_animation_style, list_animation_styles
from .layouts import get_layout_style, list_layout_styles
from ..utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")


class StyleFactory:
    """Factory for creating and managing display styles."""
    
    # Style categories in priority order
    STYLE_CATEGORIES = [
        ('core', get_core_style, list_core_styles),
        ('theme', get_theme_style, list_theme_styles),
        ('animation', get_animation_style, list_animation_styles),
        ('layout', get_layout_style, list_layout_styles),
    ]
    
    @classmethod
    def create_style(cls, style_spec):
        """
        Create a style from various specifications.
        
        Args:
            style_spec: Can be:
                - String: Style name to lookup
                - Dict: Style properties
                - BaseStyle: Existing style instance
                - List: Multiple styles to merge
                - None: Default style
                
        Returns:
            A BaseStyle instance
        """
        # Handle None - return default
        if style_spec is None:
            return cls.get_style('default')
            
        # Handle existing style instance
        if isinstance(style_spec, BaseStyle):
            return style_spec
            
        # Handle string style name
        if isinstance(style_spec, str):
            return cls.get_style(style_spec)
            
        # Handle dictionary of properties
        if isinstance(style_spec, dict):
            return cls.create_custom_style(style_spec)
            
        # Handle list of styles to merge
        if isinstance(style_spec, list):
            return cls.merge_styles(style_spec)
            
        # Unknown type - return default
        logger.warning(f"Unknown style specification type: {type(style_spec)}")
        return cls.get_style('default')
        
    @classmethod
    def get_style(cls, name):
        """
        Get a style by name from any category.
        
        Args:
            name: The style name
            
        Returns:
            A style instance or default if not found
        """
        # Try each category in order
        for category_name, getter, _ in cls.STYLE_CATEGORIES:
            style = getter(name)
            if style:
                logger.debug(f"Found style '{name}' in {category_name} category")
                return style
                
        # Not found - log warning and return default
        logger.warning(f"Style '{name}' not found, using default")
        return get_core_style('default')
        
    @classmethod
    def create_custom_style(cls, properties, base_style='default'):
        """
        Create a custom style from properties.
        
        Args:
            properties: Dictionary of style properties
            base_style: Base style to extend (default: 'default')
            
        Returns:
            A new style instance
        """
        # Get base style
        style = cls.get_style(base_style)
        
        # Create a copy to avoid modifying the original
        custom_style = style.clone()
        custom_style.name = properties.get('name', 'custom')
        
        # Apply custom properties
        custom_style.update_properties(properties)
        
        return custom_style
        
    @classmethod
    def merge_styles(cls, style_list):
        """
        Merge multiple styles into one.
        
        Args:
            style_list: List of style specs to merge
            
        Returns:
            A new merged style instance
        """
        if not style_list:
            return cls.get_style('default')
            
        # Start with the first style
        merged = cls.create_style(style_list[0]).clone()
        merged.name = 'merged'
        
        # Merge in remaining styles
        for style_spec in style_list[1:]:
            style = cls.create_style(style_spec)
            merged.merge(style)
            
        return merged
        
    @classmethod
    def create_composite_style(cls, *components, **properties):
        """
        Create a composite style from multiple components.
        
        Args:
            *components: Style names or specs to combine
            **properties: Additional properties to apply
            
        Returns:
            A new composite style instance
            
        Example:
            style = StyleFactory.create_composite_style(
                'rainbow',      # Base colors
                'fast',         # Speed
                'two_line',     # Layout
                brightness=0.8  # Custom property
            )
        """
        # Merge all component styles
        composite = cls.merge_styles(list(components))
        composite.name = 'composite'
        
        # Apply additional properties
        if properties:
            composite.update_properties(properties)
            
        return composite
        
    @classmethod
    def list_all_styles(cls):
        """
        List all available style names.
        
        Returns:
            Dictionary with categories and their styles
        """
        all_styles = {}
        
        for category_name, _, lister in cls.STYLE_CATEGORIES:
            all_styles[category_name] = lister()
            
        return all_styles
        
    @classmethod
    def get_style_info(cls, name):
        """
        Get information about a style.
        
        Args:
            name: The style name
            
        Returns:
            Dictionary with style information or None
        """
        style = cls.get_style(name)
        if style and style.name != 'default':  # Found the actual style
            return {
                'name': style.name,
                'category': cls._find_category(name),
                'properties': style.to_dict(),
                'class': style.__class__.__name__,
            }
        return None
        
    @classmethod
    def _find_category(cls, name):
        """Find which category a style belongs to."""
        for category_name, getter, _ in cls.STYLE_CATEGORIES:
            if getter(name):
                return category_name
        return 'unknown'


# Convenience functions
def create_style(style_spec):
    """
    Create a style from a specification.
    
    This is a convenience wrapper around StyleFactory.create_style()
    
    Args:
        style_spec: Style specification (see StyleFactory.create_style)
        
    Returns:
        A BaseStyle instance
    """
    return StyleFactory.create_style(style_spec)


def get_style(name):
    """
    Get a style by name.
    
    This is a convenience wrapper around StyleFactory.get_style()
    
    Args:
        name: The style name
        
    Returns:
        A BaseStyle instance
    """
    return StyleFactory.get_style(name)


def list_styles():
    """
    List all available styles.
    
    Returns:
        Dictionary with categories and their styles
    """
    return StyleFactory.list_all_styles()


def merge_styles(*styles):
    """
    Merge multiple styles together.
    
    Args:
        *styles: Style specs to merge
        
    Returns:
        A merged style instance
    """
    return StyleFactory.merge_styles(list(styles))


def create_composite(*components, **properties):
    """
    Create a composite style.
    
    Args:
        *components: Style components to combine
        **properties: Additional properties
        
    Returns:
        A composite style instance
    """
    return StyleFactory.create_composite_style(*components, **properties)