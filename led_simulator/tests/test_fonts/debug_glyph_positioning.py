#!/usr/bin/env python3
"""Debug glyph positioning to understand why baseline alignment isn't working."""

import sys
import os

# Add PyLEDSimulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'PyLEDSimulator'))

from pyledsimulator.terminalio import FONT as terminalio_FONT
from pyledsimulator.adafruit_bitmap_font import bitmap_font


def debug_font_and_glyph_metrics():
    """Debug font metrics and glyph positioning."""
    
    # Load fonts
    viii_font = terminalio_FONT
    try:
        tom_thumb = bitmap_font.load_font("PyLEDSimulator/fonts/tom-thumb.bdf")
    except:
        tom_thumb = None
        print("Could not load tom-thumb font")
        return
    
    print("=== FONT METRICS DEBUG ===")
    
    for font, name in [(viii_font, "viii"), (tom_thumb, "tom-thumb")]:
        print(f"\\n{name} font:")
        print(f"  height: {font.height}")
        print(f"  ascent: {font.ascent}")
        print(f"  descent: {font.descent}")
        print(f"  ascent + descent: {font.ascent + font.descent}")
        print(f"  height vs ascent+descent: {font.height} vs {font.ascent + font.descent}")
        
        # Test specific characters
        for char in "Ag":
            glyph = font.get_glyph(char)
            if glyph:
                print(f"  '{char}': height={glyph['height']}, y_offset={glyph.get('y_offset', 0)}, width={glyph['bitmap'].width}x{glyph['bitmap'].height}")
                
                # Calculate where this glyph would be positioned
                # Using the current Label logic: y_offset = padding_top + font.ascent
                padding_top = 0
                base_y_offset = padding_top + font.ascent
                glyph_y_offset = glyph.get('y_offset', 0)
                draw_y = base_y_offset + glyph_y_offset
                
                print(f"    Positioning: base_y_offset={base_y_offset}, glyph_y_offset={glyph_y_offset}, draw_y={draw_y}")
                print(f"    Glyph pixels would span: y={draw_y} to {draw_y + glyph['bitmap'].height - 1}")
                
                # Calculate baseline position
                # The baseline is at y = base_y_offset (where glyph_y_offset=0 characters sit)
                baseline_y = base_y_offset
                print(f"    Baseline would be at: y={baseline_y}")


def simulate_label_creation():
    """Simulate the label creation process to understand bitmap sizing."""
    
    viii_font = terminalio_FONT
    try:
        tom_thumb = bitmap_font.load_font("PyLEDSimulator/fonts/tom-thumb.bdf")
    except:
        return
    
    print("\\n=== LABEL CREATION SIMULATION ===")
    
    text = "Ag"
    
    for font, name in [(viii_font, "viii"), (tom_thumb, "tom-thumb")]:
        print(f"\\n{name} label for '{text}':")
        
        # Simulate the _update_text logic
        lines = text.split('\\n')
        max_width = 0
        total_height = 0
        
        for i, line in enumerate(lines):
            line_width = 0
            line_height = 0
            
            for char in line:
                glyph = font.get_glyph(char)
                if glyph:
                    line_width += glyph['dx']
                    line_height = max(line_height, glyph['height'])
                    
            max_width = max(max_width, line_width)
            if i == 0:
                total_height = font.height
            else:
                total_height += int(font.height * 1.25)  # line_spacing = 1.25
        
        # Calculate bitmap dimensions
        padding_top = padding_bottom = padding_left = padding_right = 0
        bitmap_width = max_width + padding_left + padding_right
        bitmap_height = total_height + padding_top + padding_bottom + font.ascent
        
        print(f"  Text dimensions: {max_width} x {total_height}")
        print(f"  Bitmap dimensions: {bitmap_width} x {bitmap_height}")
        print(f"  Added space for ascent: {font.ascent}")
        
        # Simulate glyph positioning
        y_offset = padding_top + font.ascent
        print(f"  Base y_offset (baseline): {y_offset}")
        
        for char in text:
            glyph = font.get_glyph(char)
            if glyph:
                glyph_y_offset = glyph.get('y_offset', 0)
                draw_y = y_offset + glyph_y_offset
                print(f"    '{char}': glyph_y_offset={glyph_y_offset}, draw_y={draw_y}, spans {draw_y} to {draw_y + glyph['bitmap'].height - 1}")


if __name__ == "__main__":
    debug_font_and_glyph_metrics()
    simulate_label_creation()