"""LED Simulator - LED matrix display simulator for CircuitPython development."""

__version__ = "0.1.0"
__author__ = "LED Simulator Contributors"

# Import main components for easy access
from .core import LEDMatrix, PixelBuffer, DisplayManager
from . import displayio

__all__ = ['LEDMatrix', 'PixelBuffer', 'DisplayManager', 'displayio']