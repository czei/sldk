#!/usr/bin/env python3
"""Detailed debugging of label rendering."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.adafruit_display_text import Label
from pyledsimulator.terminalio import FONT


def debug_font():
    """Debug font glyph data."""
    print("=== Font Debug ===")
    
    # Test a simple character
    glyph = FONT.get_glyph('A')
    print(f"Glyph 'A': {glyph}")
    
    if glyph:
        bitmap = glyph['bitmap']
        print(f"Glyph bitmap: {bitmap.width}x{bitmap.height}")
        print(f"Font height: {FONT.height}")
        print(f"Font ascent: {FONT.ascent}")
        print(f"Font descent: {FONT.descent}")
        
        # Print bitmap content
        print("Bitmap content:")
        for y in range(bitmap.height):
            row = ""
            for x in range(bitmap.width):
                pixel = bitmap[x, y]
                row += "#" if pixel > 0 else "."
            print(f"  {row}")
            

def debug_label_creation():
    """Debug label creation step by step."""
    print("\n=== Label Creation Debug ===")
    
    # Create a simple label
    label = Label(
        font=FONT,
        text="A",
        color=0xFF0000,
        x=0,
        y=0
    )
    
    print(f"Label text: '{label.text}'")
    print(f"Label color: 0x{label.color:04X}")
    print(f"Label position: ({label.x}, {label.y})")
    print(f"Label bitmap: {label._bitmap}")
    print(f"Label palette: {label._palette}")
    print(f"Label tilegrid: {label._tilegrid}")
    
    if label._bitmap:
        print(f"Bitmap size: {label._bitmap.width}x{label._bitmap.height}")
        print(f"Bitmap value_count: {label._bitmap.value_count}")
        
        # Check bitmap content
        has_content = False
        for y in range(label._bitmap.height):
            for x in range(label._bitmap.width):
                value = label._bitmap[x, y]
                if value > 0:
                    print(f"  Bitmap pixel ({x},{y}) = {value}")
                    has_content = True
                    
        if not has_content:
            print("  Bitmap is empty!")
            
    if label._palette:
        print(f"Palette color count: {len(label._palette)}")
        for i in range(len(label._palette)):
            color = label._palette[i]
            rgb = label._palette.get_rgb888(i)
            print(f"  Palette[{i}] = 0x{color:04X} = RGB{rgb}")
            

def debug_manual_rendering():
    """Debug manual text rendering."""
    print("\n=== Manual Rendering Debug ===")
    
    # Try to manually render text like Label does
    from pyledsimulator.displayio import Bitmap, Palette
    
    # Get glyph for 'A'
    glyph = FONT.get_glyph('A')
    if not glyph:
        print("No glyph found for 'A'")
        return
        
    glyph_bitmap = glyph['bitmap']
    print(f"Glyph 'A' size: {glyph_bitmap.width}x{glyph_bitmap.height}")
    
    # Create label-style bitmap
    bitmap_width = glyph['width'] + 2  # Add padding
    bitmap_height = FONT.height
    bitmap = Bitmap(bitmap_width, bitmap_height, 2)
    
    print(f"Target bitmap size: {bitmap_width}x{bitmap_height}")
    
    # Copy glyph manually
    x_offset = 1  # Padding
    y_offset = FONT.ascent + glyph.get('y_offset', 0)
    
    print(f"Drawing at offset: ({x_offset}, {y_offset})")
    
    pixels_set = 0
    for gy in range(glyph_bitmap.height):
        for gx in range(glyph_bitmap.width):
            glyph_pixel = glyph_bitmap[gx, gy]
            if glyph_pixel > 0:
                bx = x_offset + gx
                by = y_offset + gy
                print(f"  Glyph pixel ({gx},{gy})={glyph_pixel} -> bitmap ({bx},{by})")
                if 0 <= bx < bitmap_width and 0 <= by < bitmap_height:
                    bitmap[bx, by] = 1
                    pixels_set += 1
                else:
                    print(f"    Out of bounds!")
                    
    print(f"Pixels set in bitmap: {pixels_set}")
    
    # Check final bitmap
    print("Final bitmap content:")
    for y in range(bitmap_height):
        row = ""
        for x in range(bitmap_width):
            pixel = bitmap[x, y]
            row += "#" if pixel > 0 else "."
        print(f"  {row}")


def main():
    """Run all debugging."""
    debug_font()
    debug_label_creation()
    debug_manual_rendering()


if __name__ == "__main__":
    main()