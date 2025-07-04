"""CircuitPython App Framework - Build LED matrix applications with just 2 lines of code!

The CircuitPython App Framework makes it incredibly easy to create scrolling text displays,
data dashboards, and interactive LED applications. Start simple, grow powerful.

Quick Start:
    from cpyapp import SimpleScrollApp
    
    app = SimpleScrollApp("Hello World!")
    app.run()

Main Classes:
    SimpleScrollApp: High-level API for quick apps (recommended for beginners)
    BaseApplication: Low-level API for full control (advanced users)

Common Imports:
    from cpyapp import SimpleScrollApp
    from cpyapp.presets import ClockPreset, WeatherPreset, StockTickerPreset
    from cpyapp.data import URLDataSource, FileDataSource
    from cpyapp.styles import STYLE_PRESETS
    from cpyapp.boards import BoardConfig, BOARD_PRESETS
"""

# Version info
__version__ = "2.0.0"
__author__ = "3DUPFitters LLC"
__license__ = "MIT"

# Core application components
from .core.application import BaseApplication

# Simple high-level interface (most users start here)
from .simple import SimpleScrollApp

# Data sources for dynamic content
from .data import (
    DataSource,
    URLDataSource, 
    FileDataSource,
    FunctionDataSource,
    StaticDataSource
)

# Style system
from .styles import STYLE_PRESETS, StyleEngine

# Board configurations
from .boards import BoardConfig, BOARD_PRESETS, detect_board

# Presets for ready-made apps
from .presets import (
    ClockPreset,
    WeatherPreset,
    StockTickerPreset,
    NewsTickerPreset,
    CountdownPreset,
    SystemMonitorPreset,
    MultiPreset
)

# Display components
from .display import DisplayMessage, ScrollingText

# Network components
from .network import NetworkManager, HTTPClient

# Utilities
from .utils import (
    ErrorHandler,
    ConfigManager,
    StateManager
)

# Plugin system
from .plugins import Plugin, PluginManager

# Constants
from . import constants

# Main exports
__all__ = [
    # High-level API (start here!)
    "SimpleScrollApp",
    
    # Core framework
    "BaseApplication",
    
    # Data sources
    "DataSource",
    "URLDataSource",
    "FileDataSource", 
    "FunctionDataSource",
    "StaticDataSource",
    
    # Presets
    "ClockPreset",
    "WeatherPreset",
    "StockTickerPreset",
    "NewsTickerPreset",
    "CountdownPreset",
    "SystemMonitorPreset",
    "MultiPreset",
    
    # Configuration
    "STYLE_PRESETS",
    "BOARD_PRESETS",
    "BoardConfig",
    "detect_board",
    
    # Components
    "DisplayMessage",
    "ScrollingText",
    "NetworkManager",
    "HTTPClient",
    
    # Utilities
    "ErrorHandler",
    "ConfigManager",
    "StateManager",
    
    # Extensibility
    "Plugin",
    "PluginManager",
    
    # Info
    "__version__",
    "constants"
]

# Convenience function for quick start
def create_app(text="Hello World!", **kwargs):
    """Quick function to create and return a simple app.
    
    Examples:
        # Simplest usage
        app = create_app()
        app.run()
        
        # With options
        app = create_app("My Text", styles={"text_color": (255, 0, 0)})
        app.run()
    """
    return SimpleScrollApp(text, **kwargs)