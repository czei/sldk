#!/usr/bin/env python3
"""Debug the font positioning issue."""

import sys
import os

# Add PyLEDSimulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.terminalio import FONT as terminalio_FONT


def debug_positioning():
    """Debug the positioning calculations."""
    
    font = terminalio_FONT
    
    print("=== POSITIONING DEBUG ===")
    print(f"Font metrics: height={font.height}, ascent={font.ascent}, descent={font.descent}")
    
    # Test a simple character
    char = 'A'
    glyph = font.get_glyph(char)
    if glyph:
        print(f"\\nCharacter '{char}':")
        print(f"  BBX: width={glyph['width']}, height={glyph['height']}")
        print(f"  Offsets: x={glyph['x_offset']}, y={glyph['y_offset']}")
        print(f"  DWIDTH: {glyph['dx']}")
    
    # Test a character with descender
    char = 'g'
    glyph = font.get_glyph(char)
    if glyph:
        print(f"\\nCharacter '{char}':")
        print(f"  BBX: width={glyph['width']}, height={glyph['height']}")
        print(f"  Offsets: x={glyph['x_offset']}, y={glyph['y_offset']}")
        print(f"  DWIDTH: {glyph['dx']}")
    
    # Create a label and see what happens
    label = Label(font, text="Ag")
    print(f"\\nLabel for 'Ag':")
    print(f"  Label size: {label.width} x {label.height}")
    print(f"  Padding: top={label.padding_top}, bottom={label.padding_bottom}")
    
    # Calculate what the positioning should be
    padding_top = 0
    baseline_y = padding_top + font.ascent
    print(f"\\nPositioning calculations:")
    print(f"  Baseline at y={baseline_y}")
    
    for char in "Ag":
        glyph = font.get_glyph(char)
        if glyph:
            draw_y = baseline_y - glyph['y_offset']
            print(f"  '{char}': glyph y_offset={glyph['y_offset']}, draw_y={draw_y}")
            print(f"    Character spans y={draw_y} to {draw_y + glyph['height']}")


if __name__ == "__main__":
    debug_positioning()