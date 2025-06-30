"""SLDK - Scrolling LED Dev Kit

A development framework for creating scrolling LED display applications
that work on both CircuitPython hardware and desktop simulators.
"""

__version__ = "0.1.0"

# Core exports
from .app import SLDKApp
from .content import (
    DisplayContent,
    ScrollingText,
    StaticText,
    RainbowText,
    ContentQueue,
)
from .display import (
    DisplayInterface,
    UnifiedDisplay,
)

# Optional simulator import
try:
    from . import simulator
except ImportError:
    simulator = None

__all__ = [
    "SLDKApp",
    "DisplayInterface",
    "DisplayContent", 
    "ScrollingText",
    "StaticText",
    "RainbowText",
    "ContentQueue",
    "UnifiedDisplay",
    "simulator",
    "__version__",
]