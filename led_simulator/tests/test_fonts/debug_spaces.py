#!/usr/bin/env python3
"""Debug space character handling."""

import sys
import os

# Add PyLEDSimulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.terminalio import FONT as terminalio_FONT


def debug_spaces():
    """Debug how space characters are being handled."""
    
    font = terminalio_FONT
    
    print("=== SPACE CHARACTER DEBUG ===")
    
    # Test space character specifically
    space_char = ' '
    space_glyph = font.get_glyph(space_char)
    
    print(f"Space character (ASCII 32):")
    if space_glyph:
        print(f"  Found glyph:")
        print(f"    BBX: width={space_glyph['width']}, height={space_glyph['height']}")
        print(f"    Offsets: x={space_glyph['x_offset']}, y={space_glyph['y_offset']}")
        print(f"    DWIDTH: {space_glyph['dx']}")
        print(f"    Bitmap size: {space_glyph['bitmap'].width if space_glyph['bitmap'] else 'None'}x{space_glyph['bitmap'].height if space_glyph['bitmap'] else 'None'}")
    else:
        print(f"  No glyph found for space character!")
    
    # Test text with spaces
    test_text = "Hello World"
    print(f"\\nTest text: '{test_text}'")
    
    label = Label(font, text=test_text)
    print(f"Label width: {label.width}")
    
    # Calculate expected width manually
    expected_width = 0
    char_count = 0
    for char in test_text:
        glyph = font.get_glyph(char)
        if glyph:
            expected_width += glyph['dx']
            char_count += 1
            print(f"  '{char}': dx={glyph['dx']}, running total={expected_width}")
        else:
            print(f"  '{char}': NO GLYPH FOUND!")
    
    print(f"\\nExpected total width: {expected_width}")
    print(f"Actual label width: {label.width}")
    print(f"Characters processed: {char_count}")
    
    if expected_width == label.width:
        print("✓ Width calculation matches - spaces are being processed")
    else:
        print("✗ Width mismatch - possible issue with space handling")


if __name__ == "__main__":
    debug_spaces()