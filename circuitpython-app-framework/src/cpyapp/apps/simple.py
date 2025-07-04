"""
Simple Scroll Application - Progressive API for LED matrix displays.

This module provides a simple, beginner-friendly interface for creating
scrolling text applications on LED matrices while maintaining all the
power of the full framework.

Example usage:
    # Minimal - just text
    app = SimpleScrollApp("Hello World!")
    app.run()
    
    # With style
    app = SimpleScrollApp("Hello World!", style="rainbow")
    app.run()
    
    # With data source
    app = SimpleScrollApp(
        data_source="https://api.example.com/data.json",
        style="scroll",
        board="matrixportal_s3"
    )
    app.run()
"""
import asyncio
import json
try:
    from typing import Union, Dict, Any, Callable, Optional, List
except ImportError:
    # CircuitPython doesn't have typing
    pass

from ..core.application import BaseApplication
from ..core.plugin import DisplayPlugin
from ..display.factory import create_display
from ..network.http_client import HttpClient
from ..config.settings import SettingsManager
from ..utils.error_handler import ErrorHandler
from ..data_sources import create_data_source
from ..styles import create_style, get_style
from ..boards import create_board, BoardSettingsManager

# Initialize logger
logger = ErrorHandler("error_log")


class DataSourcePlugin(DisplayPlugin):
    """Internal plugin for handling different data sources."""
    
    def __init__(self, data_source_instance):
        """
        Initialize data source plugin.
        
        Args:
            data_source_instance: A DataSource instance
        """
        super().__init__("DataSource")
        self.data_source = data_source_instance
        self.cached_data = None
        
    async def get_messages(self, app):
        """
        Get messages from the data source.
        
        Args:
            app: The application instance
            
        Returns:
            List of message dictionaries
        """
        try:
            # Fetch data from the data source
            data = await self.data_source.get_data()
            
            # Store for potential reuse
            self.cached_data = data
            
            # Format for display
            messages = self.data_source.format_for_display(data)
            
            return messages
            
        except Exception as e:
            logger.error(e, "Error getting messages from data source")
            return [{
                'type': 'scroll',
                'text': 'Data source error',
                'delay': 2
            }]


class SimpleScrollApp(BaseApplication):
    """
    Simple scrolling text application with progressive API.
    
    This class provides an easy-to-use interface for creating LED matrix
    applications that scroll text from various data sources.
    """
    
    # Legacy style mapping for backward compatibility
    # New code should use the styles module directly
    LEGACY_STYLES = {
        'default': 'default',
        'rainbow': 'rainbow',
        'fast': 'fast',
        'slow': 'slow',
        'alert': 'alert',
        'success': 'success',
        'info': 'info',
    }
    
    
    def __init__(self, data_source=None, style="default", board="auto"):
        """
        Initialize a simple scroll application.
        
        Args:
            data_source: Text string, function, URL, or dict with parser config
                - String: Static text to display
                - Function: Called to get display text
                - URL (http/https): Fetched periodically
                - Dict: {'url': '...', 'parser': '...', 'config': {...}}
            style: Style name (string) or custom style dict
            board: Board type (string) or board config dict
                - "auto": Auto-detect board
                - "matrixportal_s3": MatrixPortal S3
                - "matrixportal_m4": MatrixPortal M4
                - Dict: Custom board configuration
        """
        # Default data source if none provided
        if data_source is None:
            data_source = "Hello World!"
            
        # Create style instance using the new system
        self.style = self._create_style_instance(style)
        self.style_config = self.style.to_dict()
        
        # Parse board configuration
        self.board_config = self._parse_board(board)
        
        # Create components
        self._create_components()
        
        # Create data source using factory
        self.data_source_instance = create_data_source(data_source, self.http_client)
        
        # Initialize base application
        super().__init__(self.display, self.http_client, self.settings_manager)
        
        # Register data source plugin
        self.data_plugin = DataSourcePlugin(self.data_source_instance)
        self.register_plugin(self.data_plugin)
        
        # Store parsed data
        self._current_data = None
        
    @property
    def board(self):
        """Get the board instance."""
        return self.board_instance
        
    def _create_style_instance(self, style_spec):
        """Create a style instance using the new style system."""
        # Handle legacy style names
        if isinstance(style_spec, str) and style_spec in self.LEGACY_STYLES:
            style_spec = self.LEGACY_STYLES[style_spec]
            
        # Use the style factory to create the style
        return create_style(style_spec)
        
    def _parse_style(self, style):
        """Parse style into configuration (legacy method for compatibility)."""
        style_instance = self._create_style_instance(style)
        return style_instance.to_dict()
            
    def _parse_board(self, board):
        """Parse board configuration."""
        if board is None:
            board = 'auto'
            
        # Create board instance
        if isinstance(board, str):
            # Use board factory to create board from spec
            self.board_instance = create_board(board)
        elif isinstance(board, dict):
            # Create custom board from config
            self.board_instance = create_board(board)
        else:
            # Assume it's already a board instance
            self.board_instance = board
            
        return {
            'type': self.board_instance.name,
            'instance': self.board_instance
        }
            
    def _create_components(self):
        """Create required components."""
        # Board settings manager
        self.board_settings_manager = BoardSettingsManager()
        board_settings = self.board_settings_manager.get_board_settings(self.board_instance.name)
        
        # Settings manager with style configuration
        self.settings_manager = SettingsManager("settings.json")
        
        # Apply board-specific settings first
        board_display_settings = board_settings.get('display', {})
        for key, value in board_display_settings.items():
            self.settings_manager.set(f"display.{key}", value)
        
        # Apply style settings from the style instance (can override board defaults)
        for key, value in self.style_config.items():
            self.settings_manager.set(key, value)
            
        # Apply style-specific display settings
        if hasattr(self.style, 'apply_to_settings'):
            self.style.apply_to_settings(self.settings_manager)
            
        # Create display with board instance
        display_config = {
            'settings_manager': self.settings_manager,
            'board': self.board_config
        }
        self.display = create_display(display_config, self.board_instance)
        
        # Set up network if board supports it
        self.network = None
        if hasattr(self.board_instance, 'setup_network'):
            try:
                self.network = self.board_instance.setup_network()
                logger.info(f"Network initialized for board {self.board_instance.name}")
            except Exception as e:
                logger.warning(f"Network setup failed: {e}")
        
        # Create HTTP client
        self.http_client = HttpClient()
        
    async def update_data(self):
        """Update data from the data source."""
        # The data source plugin handles fetching and formatting
        # This method is kept for compatibility but simplified
        return self._current_data
            
    def create_display_content(self, data):
        """
        Create display content from data.
        The DataSourcePlugin handles this.
        """
        # Plugin handles message creation
        return []
        
    def run(self):
        """
        Run the application synchronously.
        This hides the async complexity from beginners.
        """
        try:
            # Use asyncio.run for simplicity
            asyncio.run(super().run())
        except KeyboardInterrupt:
            logger.info("Application stopped by user")
        except Exception as e:
            logger.error(e, "Error running application")
            raise
            
    async def run_async(self):
        """
        Run the application asynchronously.
        For advanced users who need async control.
        """
        await super().run()


# Convenience functions for common use cases
def scroll_text(text, style="default"):
    """
    Simple function to scroll text on the display.
    
    Args:
        text: Text to scroll
        style: Style name or dict
        
    Example:
        scroll_text("Hello World!")
        scroll_text("Alert!", style="alert")
    """
    app = SimpleScrollApp(text, style)
    app.run()


def scroll_url(url, parser="auto", style="default", **kwargs):
    """
    Scroll text from a URL.
    
    Args:
        url: URL to fetch data from
        parser: Parser type or function
        style: Style name or dict
        **kwargs: Additional parser configuration
        
    Example:
        scroll_url("https://api.example.com/message")
        scroll_url("https://api.example.com/data.json", parser="json_path", path="message.text")
    """
    config = {
        'type': 'url',
        'url': url,
        'parser': parser,
        'parser_config': kwargs
    }
    app = SimpleScrollApp(config, style)
    app.run()


def scroll_function(func, style="default", update_interval=300):
    """
    Scroll text from a function that returns text.
    
    Args:
        func: Function that returns text to display
        style: Style name or dict
        update_interval: How often to call the function (seconds)
        
    Example:
        def get_time():
            import time
            return time.strftime("%H:%M:%S")
            
        scroll_function(get_time, update_interval=1)
    """
    config = {
        'type': 'function',
        'function': func,
        'cache_ttl': 0 if update_interval < 60 else update_interval
    }
    app = SimpleScrollApp(config, style)
    app.settings_manager.set('update_interval', update_interval)
    app.run()