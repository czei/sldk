#!/usr/bin/env python3
"""Test the positioning fix."""

import sys
import os

# Add PyLEDSimulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.terminalio import FONT as terminalio_FONT


def test_positioning_fix():
    """Test the corrected positioning calculations."""
    
    font = terminalio_FONT
    
    print("=== POSITIONING FIX TEST ===")
    print(f"Font metrics: height={font.height}, ascent={font.ascent}, descent={font.descent}")
    
    # Create a label and see what happens now
    label = Label(font, text="Ag")
    print(f"\\nLabel for 'Ag':")
    print(f"  Label size: {label.width} x {label.height}")
    
    # Manually calculate what the positioning should be with the new formula
    padding_top = 0
    baseline_y = padding_top + font.ascent  # baseline_y = 9
    
    print(f"\\nNew positioning calculations:")
    print(f"  Baseline at y={baseline_y}")
    
    for char in "Ag":
        glyph = font.get_glyph(char)
        if glyph:
            # New formula: draw_y = baseline_y - glyph['height'] - glyph_y_offset
            draw_y = baseline_y - glyph['height'] - glyph['y_offset']
            print(f"  '{char}': height={glyph['height']}, y_offset={glyph['y_offset']}")
            print(f"    draw_y = {baseline_y} - {glyph['height']} - ({glyph['y_offset']}) = {draw_y}")
            print(f"    Character spans y={draw_y} to {draw_y + glyph['height']}")
            
            # Check if it fits in the bitmap (height = 11)
            if draw_y >= 0 and draw_y + glyph['height'] <= 11:
                print(f"    ✓ Fits within bitmap (0 to 11)")
            else:
                print(f"    ✗ Does not fit within bitmap (0 to 11)")


if __name__ == "__main__":
    test_positioning_fix()