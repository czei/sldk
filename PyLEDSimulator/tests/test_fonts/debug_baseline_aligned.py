#!/usr/bin/env python3
"""Debug the baseline_aligned feature to see what's happening."""

import sys
import os

# Add PyLEDSimulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'PyLEDSimulator'))

from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.terminalio import FONT as terminalio_FONT
from pyledsimulator.adafruit_bitmap_font import bitmap_font


def debug_baseline_aligned_logic():
    """Debug what happens when baseline_aligned is True vs False."""
    
    # Load fonts
    viii_font = terminalio_FONT
    try:
        tom_thumb = bitmap_font.load_font("PyLEDSimulator/fonts/tom-thumb.bdf")
    except:
        print("Could not load tom-thumb font")
        return
    
    print("=== DEBUGGING BASELINE_ALIGNED LOGIC ===")
    
    # Test both modes for each font
    for font, name in [(viii_font, "viii"), (tom_thumb, "tom-thumb")]:
        print(f"\\n{name} font:")
        print(f"  Metrics: height={font.height}, ascent={font.ascent}, descent={font.descent}")
        
        for baseline_aligned in [False, True]:
            print(f"\\n  baseline_aligned={baseline_aligned}:")
            
            # Create label
            label = Label(font, text="Ag", color=0xFF0000, baseline_aligned=baseline_aligned)
            
            # Check internal state
            print(f"    label.baseline_aligned: {label.baseline_aligned}")
            print(f"    label dimensions: {label.width} x {label.height}")
            print(f"    label.bounding_box: {label.bounding_box}")
            
            # Print what should happen in _update_text based on our logic
            # This simulates the y_offset calculation
            padding_top = 0
            if baseline_aligned:
                expected_y_offset = padding_top
                print(f"    Expected y_offset: {expected_y_offset} (baseline at padding_top)")
            else:
                expected_y_offset = padding_top + font.ascent
                print(f"    Expected y_offset: {expected_y_offset} (standard positioning)")
            
            # For character 'A' (no descender)
            glyph = font.get_glyph('A')
            if glyph:
                glyph_y_offset = glyph.get('y_offset', 0)
                if baseline_aligned:
                    expected_draw_y = expected_y_offset + font.ascent + glyph_y_offset
                    print(f"    'A' draw_y: {expected_draw_y} (y_offset + ascent + glyph_y_offset)")
                    print(f"      = {expected_y_offset} + {font.ascent} + {glyph_y_offset}")
                else:
                    expected_draw_y = expected_y_offset + glyph_y_offset
                    print(f"    'A' draw_y: {expected_draw_y} (y_offset + glyph_y_offset)")
                    print(f"      = {expected_y_offset} + {glyph_y_offset}")


if __name__ == "__main__":
    debug_baseline_aligned_logic()