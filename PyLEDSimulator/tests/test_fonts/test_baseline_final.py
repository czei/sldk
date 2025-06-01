#!/usr/bin/env python3
"""Final baseline alignment test using proper positioning calculation."""

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


def calculate_baseline_position(font, desired_baseline_y):
    """Calculate the label.y position to place the font's baseline at desired_baseline_y.
    
    Args:
        font: The font object
        desired_baseline_y: Where we want the baseline to appear
        
    Returns:
        The y position to set on the label
    """
    # From the debug output, we know that within each label's bitmap:
    # - The baseline is at (padding_top + font.ascent) pixels from the bitmap's top
    # - So to align baselines, we need: label.y + (padding_top + font.ascent) = desired_baseline_y
    # Therefore: label.y = desired_baseline_y - (padding_top + font.ascent)
    padding_top = 0  # Assuming no padding for this test
    baseline_offset_in_bitmap = padding_top + font.ascent
    return desired_baseline_y - baseline_offset_in_bitmap


def test_calculated_baseline_alignment():
    """Test baseline alignment using calculated positions."""
    device = MatrixPortalS3(width=64, height=32)
    device.initialize()
    
    pygame.init()
    screen = pygame.display.set_mode((device.matrix.surface_width, device.matrix.surface_height))
    pygame.display.set_caption("Calculated Baseline Alignment Test")
    
    # Load fonts
    viii_font = terminalio_FONT
    try:
        tom_thumb = bitmap_font.load_font("PyLEDSimulator/fonts/tom-thumb.bdf")
    except:
        tom_thumb = None
        print("Could not load tom-thumb font")
        return
    
    print("=== CALCULATED BASELINE ALIGNMENT ===")
    print(f"viii: height={viii_font.height}, ascent={viii_font.ascent}, descent={viii_font.descent}")
    print(f"tom-thumb: height={tom_thumb.height}, ascent={tom_thumb.ascent}, descent={tom_thumb.descent}")
    
    # Target baseline position
    desired_baseline = 15
    
    # Calculate the correct label positions
    viii_y = calculate_baseline_position(viii_font, desired_baseline)
    tom_y = calculate_baseline_position(tom_thumb, desired_baseline)
    
    print(f"\\nTarget baseline at y={desired_baseline}")
    print(f"viii label position: y={viii_y} (baseline will be at {viii_y + viii_font.ascent})")
    print(f"tom label position: y={tom_y} (baseline will be at {tom_y + tom_thumb.ascent})")
    
    # Create the display
    main_group = displayio.Group()
    device.display.root_group = main_group
    
    # Create labels with calculated positions
    label1 = Label(viii_font, text="Ag", color=0xFF0000, scale=1)
    label1.x = 5
    label1.y = viii_y
    main_group.append(label1)
    
    label2 = Label(tom_thumb, text="Ag", color=0x00FF00, scale=1)
    label2.x = 25
    label2.y = tom_y
    main_group.append(label2)
    
    device.display.refresh()
    device.matrix.render()
    
    if hasattr(device.matrix, 'surface'):
        pygame.image.save(device.matrix.surface, "baseline_test_calculated.png")
        print("Saved: baseline_test_calculated.png")
        
        # Analyze the result
        analyze_baseline_alignment(device.matrix.surface, desired_baseline)
    
    pygame.time.wait(2000)
    pygame.quit()


def analyze_baseline_alignment(surface, expected_baseline):
    """Analyze whether the fonts are properly baseline-aligned."""
    pixel_array = pygame.surfarray.array3d(surface)
    
    # Find red and green pixels
    red_pixels = pixel_array[:, :, 0] > 200
    green_pixels = pixel_array[:, :, 1] > 200
    
    print("\\n=== BASELINE ALIGNMENT ANALYSIS ===")
    
    red_baseline = None
    green_baseline = None
    
    for pixels, color, var_name in [(red_pixels, "Red (viii)", "red_baseline"), 
                                    (green_pixels, "Green (tom)", "green_baseline")]:
        if np.any(pixels):
            # Find the bottom of the main character body (baseline)
            # Look for the lowest pixels that aren't descenders
            rows = np.any(pixels, axis=0)
            if np.any(rows):
                y_positions = np.where(rows)[0]
                y_min, y_max = y_positions[[0, -1]]
                
                # For baseline estimation, assume it's near the bottom but not the very bottom
                # (to account for potential descenders)
                estimated_baseline = y_max - 1 if y_max > y_min else y_max
                
                print(f"{color}: rendered y={y_min} to {y_max}, estimated baseline={estimated_baseline}")
                
                if var_name == "red_baseline":
                    red_baseline = estimated_baseline
                elif var_name == "green_baseline":
                    green_baseline = estimated_baseline
    
    if red_baseline is not None and green_baseline is not None:
        baseline_diff = abs(red_baseline - green_baseline)
        print(f"\\nBaseline alignment:")
        print(f"  Red baseline: {red_baseline}")
        print(f"  Green baseline: {green_baseline}")
        print(f"  Difference: {baseline_diff} pixels")
        print(f"  Success: {baseline_diff <= 1}")  # Allow 1 pixel tolerance
    else:
        print("Could not detect both baselines")


if __name__ == "__main__":
    test_calculated_baseline_alignment()