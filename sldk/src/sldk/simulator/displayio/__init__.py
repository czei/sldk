"""CircuitPython displayio API compatibility module."""

from .display import Display
from .group import Group
from .bitmap import Bitmap
from .palette import Palette
from .tilegrid import TileGrid
from .ondiskbitmap import OnDiskBitmap
from .fourwire import FourWire

# Constants
CIRCUITPYTHON_TERMINAL = None  # Terminal group (not used in simulator)

__all__ = [
    'Display', 'Group', 'Bitmap', 'Palette', 'TileGrid', 
    'OnDiskBitmap', 'FourWire', 'CIRCUITPYTHON_TERMINAL'
]