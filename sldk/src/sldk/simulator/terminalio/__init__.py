"""CircuitPython terminalio module - provides default terminal font."""

import os
from ..adafruit_bitmap_font import bitmap_font

# Load default font matching CircuitPython's terminalio.FONT
# Changed from tom-thumb.bdf to Arial-12.bdf for better readability
_font_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
    'fonts', 
    'viii.bdf'
)

# Check if we're running from installed package or development
if not os.path.exists(_font_path):
    # Try to find it relative to the package installation
    import pkg_resources
    try:
        _font_path = pkg_resources.resource_filename('pyledsimulator', 'fonts/viii.bdf')
    except:
        # Fall back to a simple search
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '..', '..', 'fonts', 'viii.bdf'),
            os.path.join(os.path.dirname(__file__), '..', '..', '..', 'fonts', 'viii.bdf'),
            'fonts/viii.bdf',
            'PyLEDSimulator/fonts/viii.bdf'
        ]
        for path in possible_paths:
            if os.path.exists(path):
                _font_path = path
                break

# Load the default font
FONT = bitmap_font.load_font(_font_path)

# Import font scaling functionality
from .font_scaler import get_font_for_scale

__all__ = ['FONT', 'get_font_for_scale']