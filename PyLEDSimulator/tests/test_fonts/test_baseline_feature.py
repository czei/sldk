#!/usr/bin/env python3
"""Test the new baseline_aligned feature in the Label class."""

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


def test_baseline_aligned_feature():
    """Test the baseline_aligned feature for proper font alignment."""
    device = MatrixPortalS3(width=64, height=32)
    device.initialize()
    
    pygame.init()
    screen = pygame.display.set_mode((device.matrix.surface_width, device.matrix.surface_height))
    pygame.display.set_caption("Baseline Aligned Feature Test")
    
    # Load fonts
    viii_font = terminalio_FONT
    try:
        tom_thumb = bitmap_font.load_font("PyLEDSimulator/fonts/tom-thumb.bdf")
    except:
        tom_thumb = None
        print("Could not load tom-thumb font")
        return
    
    print("=== BASELINE ALIGNED FEATURE TEST ===")
    print(f"viii: height={viii_font.height}, ascent={viii_font.ascent}, descent={viii_font.descent}")
    print(f"tom-thumb: height={tom_thumb.height}, ascent={tom_thumb.ascent}, descent={tom_thumb.descent}")
    
    # Test 1: Standard positioning (baseline_aligned=False)
    print("\\n=== Test 1: Standard positioning ===")
    main_group = displayio.Group()
    device.display.root_group = main_group
    
    label1 = Label(viii_font, text="Ag", color=0xFF0000, scale=1, baseline_aligned=False)
    label1.x = 5
    label1.y = 10
    main_group.append(label1)
    
    if tom_thumb:
        label2 = Label(tom_thumb, text="Ag", color=0x00FF00, scale=1, baseline_aligned=False)
        label2.x = 25
        label2.y = 10
        main_group.append(label2)
    
    device.display.refresh()
    device.matrix.render()
    
    if hasattr(device.matrix, 'surface'):
        pygame.image.save(device.matrix.surface, "baseline_standard.png")
        print("Saved: baseline_standard.png")
        analyze_baseline_alignment(device.matrix.surface, "Standard positioning")
    
    pygame.time.wait(1000)
    
    # Test 2: Baseline aligned positioning
    print("\\n=== Test 2: Baseline aligned positioning ===")
    main_group = displayio.Group()
    device.display.root_group = main_group
    
    # Both labels at same y position with baseline_aligned=True
    label1 = Label(viii_font, text="Ag", color=0xFF0000, scale=1, baseline_aligned=True)
    label1.x = 5
    label1.y = 10  # This is now the baseline position
    main_group.append(label1)
    
    if tom_thumb:
        label2 = Label(tom_thumb, text="Ag", color=0x00FF00, scale=1, baseline_aligned=True)
        label2.x = 25
        label2.y = 10  # Same baseline position
        main_group.append(label2)
    
    device.display.refresh()
    device.matrix.render()
    
    if hasattr(device.matrix, 'surface'):
        pygame.image.save(device.matrix.surface, "baseline_aligned.png")
        print("Saved: baseline_aligned.png")
        analyze_baseline_alignment(device.matrix.surface, "Baseline aligned positioning")
    
    pygame.time.wait(2000)
    pygame.quit()


def analyze_baseline_alignment(surface, test_name):
    """Analyze whether the fonts are properly baseline-aligned."""
    pixel_array = pygame.surfarray.array3d(surface)
    
    # Find red and green pixels
    red_pixels = pixel_array[:, :, 0] > 200
    green_pixels = pixel_array[:, :, 1] > 200
    
    print(f"\\n{test_name} analysis:")
    
    red_baseline = None
    green_baseline = None
    
    for pixels, color, var_name in [(red_pixels, "Red (viii)", "red_baseline"), 
                                    (green_pixels, "Green (tom)", "green_baseline")]:
        if np.any(pixels):
            rows = np.any(pixels, axis=0)
            if np.any(rows):
                y_positions = np.where(rows)[0]
                y_min, y_max = y_positions[[0, -1]]
                
                # Estimate baseline as bottom of main character area
                estimated_baseline = y_max
                
                print(f"  {color}: y={y_min} to {y_max}, baseline≈{estimated_baseline}")
                
                if var_name == "red_baseline":
                    red_baseline = estimated_baseline
                elif var_name == "green_baseline":
                    green_baseline = estimated_baseline
    
    if red_baseline is not None and green_baseline is not None:
        baseline_diff = abs(red_baseline - green_baseline)
        print(f"  Baseline difference: {baseline_diff} pixels")
        print(f"  Aligned: {baseline_diff <= 2}")  # Allow 2 pixel tolerance
    else:
        print("  Could not detect both baselines")


if __name__ == "__main__":
    test_baseline_aligned_feature()