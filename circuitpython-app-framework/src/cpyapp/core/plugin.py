"""
Plugin system for extending application functionality.
"""


class Plugin:
    """Base class for all plugins."""
    
    def __init__(self, name=None):
        """
        Initialize plugin.
        
        Args:
            name: Optional plugin name (defaults to class name)
        """
        self.name = name or self.__class__.__name__
        
    def initialize(self, app):
        """
        Initialize plugin with application reference.
        
        Args:
            app: Application instance
        """
        self.app = app
        

class DisplayPlugin(Plugin):
    """Base class for display content plugins."""
    
    def get_messages(self, data):
        """
        Get display messages from data.
        
        Args:
            data: Application data
            
        Returns:
            List of message dictionaries with format:
            {
                'type': 'scroll'|'static'|'animation',
                'text': 'Message text' (for scroll/static),
                'animation': animation_instance (for animation),
                'delay': seconds (optional),
                'duration': seconds (optional)
            }
        """
        return []
        
    def get_animations(self):
        """
        Get custom animations provided by this plugin.
        
        Returns:
            Dictionary of animation_name: animation_class
        """
        return {}
        
    def get_colors(self):
        """
        Get custom color scheme for this plugin.
        
        Returns:
            Dictionary of color_name: color_value (RGB tuple or hex)
        """
        return {}
        
    def filter_data(self, data):
        """
        Filter or transform data before display.
        
        Args:
            data: Raw application data
            
        Returns:
            Filtered/transformed data
        """
        return data