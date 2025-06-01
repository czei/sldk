#!/usr/bin/env python3
"""Test proper kerning implementation using DWIDTH from BDF files."""

import sys
import os

# Add PyLEDSimulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.terminalio import FONT as terminalio_FONT
from pyledsimulator.adafruit_bitmap_font import bitmap_font


def test_kerning_implementation():
    """Test that kerning is now using DWIDTH from BDF files."""
    
    print("=== KERNING IMPLEMENTATION TEST ===")
    
    # Test with terminalio font (viii)
    font = terminalio_FONT
    
    # Check some sample characters and their DWIDTH values
    test_chars = "igloo"
    
    print(f"Font: {font.name if hasattr(font, 'name') else 'Unknown'}")
    print(f"Font metrics: height={font.height}, ascent={font.ascent}, descent={font.descent}")
    
    print(f"\\nCharacter DWIDTH analysis for '{test_chars}':")
    total_width = 0
    for char in test_chars:
        glyph = font.get_glyph(char)
        if glyph:
            print(f"  '{char}': bitmap={glyph['width']}x{glyph['height']}, dx={glyph['dx']}, x_offset={glyph['x_offset']}, y_offset={glyph['y_offset']}")
            total_width += glyph['dx']
        else:
            print(f"  '{char}': no glyph found")
    
    print(f"\\nCalculated total width using DWIDTH: {total_width}")
    
    # Create a label and check its width
    label = Label(font, text=test_chars, color=0x00FF00)
    print(f"Label actual width: {label.width}")
    print(f"Label dimensions: {label.width} x {label.height}")
    
    # Test with tom-thumb font for comparison
    try:
        tom_thumb = bitmap_font.load_font("../fonts/tom-thumb.bdf")
        print(f"\\n--- Tom-thumb font ---")
        print(f"Font metrics: height={tom_thumb.height}, ascent={tom_thumb.ascent}, descent={tom_thumb.descent}")
        
        total_width_tom = 0
        for char in test_chars:
            glyph = tom_thumb.get_glyph(char)
            if glyph:
                print(f"  '{char}': bitmap={glyph['width']}x{glyph['height']}, dx={glyph['dx']}, x_offset={glyph['x_offset']}, y_offset={glyph['y_offset']}")
                total_width_tom += glyph['dx']
            else:
                print(f"  '{char}': no glyph found")
        
        print(f"\\nCalculated total width using DWIDTH: {total_width_tom}")
        
        label_tom = Label(tom_thumb, text=test_chars, color=0x00FF00)
        print(f"Label actual width: {label_tom.width}")
        
    except Exception as e:
        print(f"\\nCould not load tom-thumb font: {e}")


if __name__ == "__main__":
    test_kerning_implementation()