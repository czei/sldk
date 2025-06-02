#!/usr/bin/env python3
"""Comprehensive test of BDF parsing and baseline alignment."""

import sys
import os
import pygame

# Add PyLEDSimulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from pyledsimulator.devices.matrixportal_s3 import MatrixPortalS3
from pyledsimulator import displayio
from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.terminalio import FONT as terminalio_FONT
from pyledsimulator.adafruit_bitmap_font import bitmap_font


def test_bdf_parsing():
    """Test that BDF parsing extracts all required metrics."""
    
    print("=== BDF PARSING TEST ===")
    
    # Test terminalio font (viii)
    font = terminalio_FONT
    
    print(f"Font: {font.name}")
    print(f"Global metrics:")
    print(f"  Size: {font.size}")
    print(f"  Height: {font.height}")
    print(f"  Ascent: {font.ascent}")
    print(f"  Descent: {font.descent}")
    print(f"  Font bounding box: {font.font_bounding_box}")
    print(f"  Font ascent (from properties): {font.font_ascent}")
    print(f"  Font descent (from properties): {font.font_descent}")
    print(f"  Baseline to top: {font.baseline_to_top}")
    
    # Test character metrics with descenders
    test_chars = ['A', 'g', 'j', 'p', 'q', 'y']
    print(f"\\nCharacter BBX metrics:")
    for char in test_chars:
        glyph = font.get_glyph(char)
        if glyph:
            print(f"  '{char}': BBX({glyph['width']}, {glyph['height']}, {glyph['x_offset']}, {glyph['y_offset']}), DWIDTH={glyph['dx']}")
        else:
            print(f"  '{char}': no glyph found")
    
    # Test tom-thumb font for comparison
    try:
        tom_thumb = bitmap_font.load_font("../fonts/tom-thumb.bdf")
        print(f"\\n--- Tom-thumb font ---")
        print(f"Global metrics:")
        print(f"  Height: {tom_thumb.height}")
        print(f"  Ascent: {tom_thumb.ascent}")
        print(f"  Descent: {tom_thumb.descent}")
        print(f"  Font bounding box: {tom_thumb.font_bounding_box}")
        print(f"  Font ascent: {tom_thumb.font_ascent}")
        print(f"  Font descent: {tom_thumb.font_descent}")
        
        print(f"\\nCharacter BBX metrics:")
        for char in test_chars:
            glyph = tom_thumb.get_glyph(char)
            if glyph:
                print(f"  '{char}': BBX({glyph['width']}, {glyph['height']}, {glyph['x_offset']}, {glyph['y_offset']}), DWIDTH={glyph['dx']}")
    except Exception as e:
        print(f"\\nCould not load tom-thumb font: {e}")


def test_baseline_alignment():
    """Test proper baseline alignment with descenders."""
    
    print(f"\\n=== BASELINE ALIGNMENT TEST ===")
    
    device = MatrixPortalS3(width=64, height=32)
    device.initialize()
    
    pygame.init()
    screen = pygame.display.set_mode((device.matrix.surface_width, device.matrix.surface_height))
    pygame.display.set_caption("Baseline Alignment Test")
    
    font = terminalio_FONT
    
    print(f"Testing text with descenders...")
    
    main_group = displayio.Group()
    device.display.root_group = main_group
    
    # Test text with multiple character types
    test_texts = [
        "Typography",  # Mix of ascenders and descenders
        "gypjq",       # All descenders
        "HELLO",       # All capitals (no descenders)
        "hippy joy"    # Mix with descenders
    ]
    
    y_pos = 5
    for i, text in enumerate(test_texts):
        label = Label(font, text=text, color=0x00FF00 if i % 2 == 0 else 0x0000FF)
        label.x = 2
        label.y = y_pos
        main_group.append(label)
        
        print(f"  '{text}' at y={y_pos}, label size: {label.width}x{label.height}")
        y_pos += 8  # Space between lines
    
    device.display.refresh()
    device.matrix.render()
    
    if hasattr(device.matrix, 'surface'):
        pygame.image.save(device.matrix.surface, "baseline_comprehensive.png")
        print(f"\\nSaved: baseline_comprehensive.png")
        print("Check image to verify:")
        print("  - All characters on each line align at the same baseline")
        print("  - Descenders (g, j, p, q, y) extend below the baseline")
        print("  - Ascenders align properly with other characters")
    
    pygame.time.wait(3000)
    pygame.quit()


def test_character_positioning():
    """Test individual character positioning with BBX offsets."""
    
    print(f"\\n=== CHARACTER POSITIONING TEST ===")
    
    font = terminalio_FONT
    
    # Analyze how specific characters should be positioned
    test_char = 'g'  # Character with descender
    glyph = font.get_glyph(test_char)
    
    if glyph:
        print(f"Character '{test_char}' analysis:")
        print(f"  BBX: width={glyph['width']}, height={glyph['height']}")
        print(f"  Offsets: x={glyph['x_offset']}, y={glyph['y_offset']}")
        print(f"  DWIDTH: {glyph['dx']}")
        print(f"  Font ascent: {font.ascent}")
        print(f"  Font descent: {font.descent}")
        
        # Calculate expected positioning
        baseline_y = 10  # Example baseline position
        expected_draw_y = baseline_y - glyph['y_offset']
        
        print(f"\\nIf baseline is at y={baseline_y}:")
        print(f"  Character top would be at y={expected_draw_y}")
        print(f"  Character bottom would be at y={expected_draw_y + glyph['height']}")
        print(f"  Descender extends {-glyph['y_offset']} pixels below baseline")


if __name__ == "__main__":
    test_bdf_parsing()
    test_character_positioning()
    test_baseline_alignment()