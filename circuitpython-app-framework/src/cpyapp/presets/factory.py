"""
Preset factory for creating and managing display presets.

This module provides centralized access to all presets and handles
preset creation, validation, and configuration.
"""
try:
    from typing import Dict, List, Optional, Union, Any
except ImportError:
    # CircuitPython doesn't have typing
    pass

from .base import BasePreset
from .theme_parks import THEME_PARK_PRESETS, get_theme_park_preset
from .displays import DISPLAY_PRESETS, get_display_preset
from .time import TIME_PRESETS, get_time_preset
from .entertainment import ENTERTAINMENT_PRESETS, get_entertainment_preset
from ..utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")


class PresetFactory:
    """
    Factory for creating and managing display presets.
    
    This class provides a centralized way to access all available presets,
    create preset instances, and manage preset configurations.
    """
    
    # Registry of all preset categories and their getters
    PRESET_CATEGORIES = {
        'theme_parks': {
            'presets': THEME_PARK_PRESETS,
            'getter': get_theme_park_preset,
            'description': 'Theme park wait times and attractions'
        },
        'displays': {
            'presets': DISPLAY_PRESETS,
            'getter': get_display_preset,
            'description': 'Financial, weather, and information displays'
        },
        'time': {
            'presets': TIME_PRESETS,
            'getter': get_time_preset,
            'description': 'Clocks, timers, and time-based displays'
        },
        'entertainment': {
            'presets': ENTERTAINMENT_PRESETS,
            'getter': get_entertainment_preset,
            'description': 'Movies, concerts, TV, and gaming'
        }
    }
    
    @classmethod
    def create_preset(cls, name, **kwargs):
        """
        Create a preset instance by name.
        
        Args:
            name: Preset name
            **kwargs: Additional parameters for the preset
            
        Returns:
            Preset instance or None if not found
        """
        # Search all categories for the preset
        for category_info in cls.PRESET_CATEGORIES.values():
            if name in category_info['presets']:
                preset = category_info['getter'](name)
                if preset:
                    # Apply any provided parameters
                    for key, value in kwargs.items():
                        if hasattr(preset, 'set_parameter'):
                            preset.set_parameter(key, value)
                    return preset
                    
        logger.info(f"Preset '{name}' not found")
        return None
        
    @classmethod
    def get_preset_config(cls, name, user_config=None):
        """
        Get preset configuration, optionally merged with user config.
        
        Args:
            name: Preset name
            user_config: Optional user configuration to merge
            
        Returns:
            Merged configuration dictionary or None
        """
        preset = cls.create_preset(name)
        if not preset:
            return None
            
        # Merge with user config if provided
        if user_config:
            return preset.merge_with_user_config(user_config)
            
        return preset.get_config()
        
    @classmethod
    def list_presets(cls, category=None):
        """
        List available presets.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            List of preset information dictionaries
        """
        presets = []
        
        if category:
            # List presets from specific category
            if category in cls.PRESET_CATEGORIES:
                category_info = cls.PRESET_CATEGORIES[category]
                for preset_name in category_info['presets']:
                    preset = category_info['getter'](preset_name)
                    if preset:
                        presets.append({
                            'name': preset_name,
                            'category': category,
                            'description': preset.get_description(),
                            'requirements': preset.get_requirements()
                        })
        else:
            # List all presets from all categories
            for cat_name, category_info in cls.PRESET_CATEGORIES.items():
                for preset_name in category_info['presets']:
                    preset = category_info['getter'](preset_name)
                    if preset:
                        presets.append({
                            'name': preset_name,
                            'category': cat_name,
                            'description': preset.get_description(),
                            'requirements': preset.get_requirements()
                        })
                        
        return sorted(presets, key=lambda x: (x['category'], x['name']))
        
    @classmethod
    def list_categories(cls):
        """
        List available preset categories.
        
        Returns:
            List of category information
        """
        categories = []
        for name, info in cls.PRESET_CATEGORIES.items():
            categories.append({
                'name': name,
                'description': info['description'],
                'preset_count': len(info['presets'])
            })
        return categories
        
    @classmethod
    def validate_preset(cls, name, config=None):
        """
        Validate a preset configuration.
        
        Args:
            name: Preset name
            config: Optional configuration to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        preset = cls.create_preset(name)
        if not preset:
            return False, f"Preset '{name}' not found"
            
        # Apply config if provided
        if config:
            preset._config = preset.merge_with_user_config(config)
            
        return preset.validate()
        
    @classmethod
    def get_preset_example(cls, name):
        """
        Get example usage for a preset.
        
        Args:
            name: Preset name
            
        Returns:
            Example code string or None
        """
        preset = cls.create_preset(name)
        if preset:
            return preset.get_example_usage()
        return None
        
    @classmethod
    def search_presets(cls, query):
        """
        Search for presets by name or tag.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching presets
        """
        query_lower = query.lower()
        matches = []
        
        for preset_info in cls.list_presets():
            # Check name
            if query_lower in preset_info['name'].lower():
                matches.append(preset_info)
                continue
                
            # Check description
            if query_lower in preset_info['description'].lower():
                matches.append(preset_info)
                continue
                
            # Check category
            if query_lower in preset_info['category'].lower():
                matches.append(preset_info)
                
        return matches


# Convenience functions
def create_preset(name, **kwargs):
    """
    Create a preset instance.
    
    Args:
        name: Preset name
        **kwargs: Preset parameters
        
    Returns:
        Preset instance
    """
    return PresetFactory.create_preset(name, **kwargs)


def list_presets(category=None):
    """
    List available presets.
    
    Args:
        category: Optional category filter
        
    Returns:
        List of preset information
    """
    return PresetFactory.list_presets(category)


def get_preset_config(name, user_config=None):
    """
    Get preset configuration.
    
    Args:
        name: Preset name
        user_config: Optional user configuration
        
    Returns:
        Configuration dictionary
    """
    return PresetFactory.get_preset_config(name, user_config)


def validate_preset(name, config=None):
    """
    Validate a preset.
    
    Args:
        name: Preset name
        config: Optional configuration
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    return PresetFactory.validate_preset(name, config)


def list_categories():
    """
    List available preset categories.
    
    Returns:
        List of category information
    """
    return PresetFactory.list_categories()


# Add from_preset method to SimpleScrollApp
def add_from_preset_to_app():
    """Add from_preset class method to SimpleScrollApp."""
    try:
        from ..apps.simple import SimpleScrollApp
        
        @classmethod
        def from_preset(cls, preset_name, **kwargs):
            """
            Create a SimpleScrollApp from a preset.
            
            Args:
                preset_name: Name of the preset
                **kwargs: Override parameters
                
            Returns:
                SimpleScrollApp instance
            """
            # Get preset configuration
            config = get_preset_config(preset_name, kwargs)
            if not config:
                raise ValueError(f"Unknown preset: {preset_name}")
                
            # Extract main components
            data_source = config.get('data_source')
            style = config.get('style', 'default')
            board = config.get('board', 'auto')
            
            # Create app instance
            return cls(data_source=data_source, style=style, board=board)
            
        # Add method to class
        SimpleScrollApp.from_preset = from_preset
        
    except ImportError:
        logger.info("Could not add from_preset to SimpleScrollApp")