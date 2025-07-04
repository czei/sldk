"""
Base preset class for display presets.

This module provides the abstract interface for all display presets,
with common functionality for loading and merging configurations.
"""
import json
try:
    from typing import Dict, Any, Optional, Union
except ImportError:
    # CircuitPython doesn't have typing
    pass

from ..utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")


class BasePreset:
    """
    Abstract base class for all display presets.
    
    A preset combines a data source, style, and board configuration
    into an easy-to-use package for common use cases.
    """
    
    def __init__(self, name, category="general"):
        """
        Initialize the base preset.
        
        Args:
            name: The name of this preset
            category: The category this preset belongs to
        """
        self.name = name
        self.category = category
        self._config = self._get_default_config()
        
    def _get_default_config(self):
        """
        Get the default configuration for this preset.
        
        Returns:
            Dict with default configuration
        """
        return {
            'data_source': None,
            'style': 'default',
            'board': 'auto',
            'metadata': {
                'name': self.name,
                'category': self.category,
                'description': '',
                'author': '',
                'version': '1.0.0',
                'tags': []
            }
        }
        
    def get_config(self):
        """
        Get the complete preset configuration.
        
        Returns:
            Dict with preset configuration
        """
        return self._config.copy()
        
    def merge_with_user_config(self, user_config):
        """
        Merge preset configuration with user overrides.
        
        Args:
            user_config: User configuration to merge
            
        Returns:
            Merged configuration dictionary
        """
        if not user_config:
            return self.get_config()
            
        merged = self.get_config()
        
        # Handle different types of user config
        if isinstance(user_config, dict):
            # Deep merge configuration
            merged = self._deep_merge(merged, user_config)
        elif isinstance(user_config, str):
            # String might be a different style name
            merged['style'] = user_config
            
        return merged
        
    def _deep_merge(self, base, override):
        """
        Deep merge two dictionaries.
        
        Args:
            base: Base dictionary
            override: Override dictionary
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result
        
    def validate(self):
        """
        Validate the preset configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        config = self.get_config()
        
        # Check required fields
        if not config.get('data_source'):
            return False, "Data source is required"
            
        if not config.get('style'):
            return False, "Style is required"
            
        if not config.get('board'):
            return False, "Board configuration is required"
            
        return True, None
        
    def get_requirements(self):
        """
        Get any special requirements for this preset.
        
        Returns:
            Dict with requirements (e.g., API keys needed)
        """
        return {}
        
    def get_description(self):
        """
        Get a human-readable description of this preset.
        
        Returns:
            String description
        """
        metadata = self._config.get('metadata', {})
        return metadata.get('description', f"{self.name} preset")
        
    def get_example_usage(self):
        """
        Get example code for using this preset.
        
        Returns:
            String with example code
        """
        return f'''
# Basic usage
from cpyapp.apps import SimpleScrollApp
app = SimpleScrollApp.from_preset("{self.name}")
app.run()

# With customization
app = SimpleScrollApp.from_preset("{self.name}", style="rainbow")
app.run()
'''

    def to_dict(self):
        """
        Convert preset to dictionary format.
        
        Returns:
            Dict representation of the preset
        """
        return {
            'name': self.name,
            'category': self.category,
            'config': self.get_config(),
            'requirements': self.get_requirements(),
            'description': self.get_description()
        }


class ConfigurablePreset(BasePreset):
    """
    A preset that can be configured with parameters.
    
    This class extends BasePreset to support parameterized presets
    that can be customized at runtime.
    """
    
    def __init__(self, name, category="general", parameters=None):
        """
        Initialize configurable preset.
        
        Args:
            name: Preset name
            category: Preset category
            parameters: Dict of parameter definitions
        """
        super().__init__(name, category)
        self.parameters = parameters or {}
        self._parameter_values = {}
        
    def set_parameter(self, param_name, value):
        """
        Set a parameter value.
        
        Args:
            param_name: Name of the parameter
            value: Value to set
        """
        if param_name in self.parameters:
            self._parameter_values[param_name] = value
        else:
            logger.info(f"Unknown parameter: {param_name}")
            
    def get_parameter(self, param_name, default=None):
        """
        Get a parameter value.
        
        Args:
            param_name: Name of the parameter
            default: Default value if not set
            
        Returns:
            Parameter value or default
        """
        return self._parameter_values.get(param_name, default)
        
    def apply_parameters(self, config):
        """
        Apply parameter values to configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Updated configuration
        """
        # Override this in subclasses to apply parameters
        return config
        
    def get_config(self):
        """
        Get configuration with parameters applied.
        
        Returns:
            Configuration dictionary
        """
        config = super().get_config()
        return self.apply_parameters(config)