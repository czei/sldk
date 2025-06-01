#!/usr/bin/env python3
"""Precise baseline alignment test to debug the remaining alignment issue."""

import sys
import os
import pygame
import numpy as np

# Add PyLEDSimulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'PyLEDSimulator'))

from pyledsimulator.devices.matrixportal_s3 import MatrixPortalS3
from pyledsimulator import displayio
from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.terminalio import FONT as terminalio_FONT
from pyledsimulator.adafruit_bitmap_font import bitmap_font


def analyze_glyph_details():
    """Analyze individual glyph metrics to understand positioning."""
    
    # Load fonts
    viii_font = terminalio_FONT
    try:
        tom_thumb = bitmap_font.load_font("PyLEDSimulator/fonts/tom-thumb.bdf")
    except:
        tom_thumb = None
        
    print("=== FONT ANALYSIS ===")
    print(f"viii font: height={viii_font.height}, ascent={viii_font.ascent}, descent={viii_font.descent}")
    if tom_thumb:
        print(f"tom-thumb: height={tom_thumb.height}, ascent={tom_thumb.ascent}, descent={tom_thumb.descent}")
    
    # Analyze individual glyphs
    for font, name in [(viii_font, "viii"), (tom_thumb, "tom-thumb")]:
        if font is None:
            continue
            
        print(f"\n{name} glyph details:")
        for char in "ABCgj":
            glyph = font.get_glyph(char)
            if glyph:
                print(f"  '{char}': height={glyph['height']}, y_offset={glyph.get('y_offset', 0)}, "
                      f"dx={glyph['dx']}, bitmap={glyph['bitmap'].width}x{glyph['bitmap'].height}")


def test_precise_baseline():
    """Test precise baseline positioning with detailed analysis."""
    device = MatrixPortalS3(width=64, height=32)
    device.initialize()
    
    pygame.init()
    screen = pygame.display.set_mode((device.matrix.surface_width, device.matrix.surface_height))
    pygame.display.set_caption("Precise Baseline Test")
    
    # Load fonts
    viii_font = terminalio_FONT
    try:
        tom_thumb = bitmap_font.load_font("PyLEDSimulator/fonts/tom-thumb.bdf")
    except:
        tom_thumb = None
    
    if not tom_thumb:
        print("Could not load tom-thumb font")
        return
    
    # Test with a character that has descenders to verify baseline
    test_char = "g"  # Has descender
    
    print(f"\n=== TESTING BASELINE WITH '{test_char}' ===")
    
    main_group = displayio.Group()
    device.display.root_group = main_group
    
    # Position both at the same baseline
    baseline_y = 20
    
    # Calculate label positions for baseline alignment
    # The Label's y position should position the baseline at baseline_y
    viii_label_y = baseline_y
    tom_label_y = baseline_y
    
    print(f"Target baseline: {baseline_y}")
    print(f"viii label positioned at y={viii_label_y}")
    print(f"tom label positioned at y={tom_label_y}")
    
    # Create labels
    label1 = Label(viii_font, text=test_char, color=0xFF0000, scale=1)
    label1.x = 5
    label1.y = viii_label_y
    main_group.append(label1)
    
    label2 = Label(tom_thumb, text=test_char, color=0x00FF00, scale=1)
    label2.x = 25
    label2.y = tom_label_y
    main_group.append(label2)
    
    device.display.refresh()
    device.matrix.render()
    
    if hasattr(device.matrix, 'surface'):
        pygame.image.save(device.matrix.surface, "baseline_test_precise.png")
        print("Saved: baseline_test_precise.png")
        
        # Detailed analysis
        analyze_baseline_precise(device.matrix.surface, baseline_y)
    
    pygame.time.wait(2000)
    pygame.quit()


def analyze_baseline_precise(surface, expected_baseline):
    """Analyze the precise baseline positioning."""
    pixel_array = pygame.surfarray.array3d(surface)
    
    # Find red and green pixels separately
    red_pixels = pixel_array[:, :, 0] > 200
    green_pixels = pixel_array[:, :, 1] > 200
    
    print("\n=== PRECISE BASELINE ANALYSIS ===")
    
    for pixels, color in [(red_pixels, "Red (viii)"), (green_pixels, "Green (tom)")]:
        if np.any(pixels):
            rows = np.any(pixels, axis=0)
            if np.any(rows):
                y_positions = np.where(rows)[0]
                y_min, y_max = y_positions[[0, -1]]
                
                # Find the actual baseline (bottom of non-descender characters)
                # For 'g', find where the main body ends (before descender)
                cols = np.any(pixels, axis=1)
                if np.any(cols):
                    x_positions = np.where(cols)[0]
                    
                    # Sample middle columns to find baseline
                    mid_x = x_positions[len(x_positions)//2]
                    column_pixels = pixels[mid_x, :]
                    if np.any(column_pixels):
                        pixel_y_positions = np.where(column_pixels)[0]
                        
                        # For 'g', try to find the gap between main body and descender
                        gaps = []
                        for i in range(len(pixel_y_positions)-1):
                            if pixel_y_positions[i+1] - pixel_y_positions[i] > 1:
                                gaps.append(pixel_y_positions[i])
                        
                        estimated_baseline = gaps[0] if gaps else y_max
                        
                        print(f"{color}:")
                        print(f"  Rendered: y={y_min} to {y_max}")
                        print(f"  Estimated baseline: {estimated_baseline}")
                        print(f"  Expected baseline: {expected_baseline}")
                        print(f"  Baseline error: {estimated_baseline - expected_baseline}")


if __name__ == "__main__":
    analyze_glyph_details()
    test_precise_baseline()