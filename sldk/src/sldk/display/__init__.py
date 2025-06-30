"""SLDK Display Module

Core display functionality for LED matrix displays.
"""

from .interface import DisplayInterface
from .content import DisplayContent, ScrollingText, StaticText, ContentQueue
from .unified import UnifiedDisplay

__all__ = [
    "DisplayInterface",
    "DisplayContent", 
    "ScrollingText",
    "StaticText",
    "ContentQueue",
    "UnifiedDisplay",
]

# Optional imports that might not be available
try:
    from .hardware import HardwareDisplay
    __all__.append("HardwareDisplay")
except ImportError:
    HardwareDisplay = None

try:
    from .simulator import SimulatorDisplay
    __all__.append("SimulatorDisplay") 
except ImportError:
    SimulatorDisplay = None