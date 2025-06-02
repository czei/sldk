#!/usr/bin/env python3
"""Visual debugging test to see actual rendered output and implement baseline alignment."""

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


def create_baseline_alignment_test():
    """Create a test showing proper baseline alignment between different fonts."""
    device = MatrixPortalS3(width=64, height=32)
    device.initialize()
    
    pygame.init()
    screen = pygame.display.set_mode((device.matrix.surface_width, device.matrix.surface_height))
    pygame.display.set_caption("Baseline Alignment Test")
    
    # Load fonts
    try:
        tom_thumb = bitmap_font.load_font("PyLEDSimulator/fonts/tom-thumb.bdf")
    except:
        tom_thumb = None
        
    viii_font = terminalio_FONT
    
    print("Font metrics:")
    print(f"viii: height={viii_font.height}, ascent={viii_font.ascent}, descent={viii_font.descent}")
    if tom_thumb:
        print(f"tom-thumb: height={tom_thumb.height}, ascent={tom_thumb.ascent}, descent={tom_thumb.descent}")
    
    # Test 1: Current positioning (top-aligned)
    print("\n=== Test 1: Current positioning ===")
    main_group = displayio.Group()
    device.display.root_group = main_group
    
    # Same Y position for both fonts
    y_pos = 10
    
    label1 = Label(viii_font, text="viii", color=0xFF0000, scale=1)
    label1.x = 5
    label1.y = y_pos
    main_group.append(label1)
    
    if tom_thumb:
        label2 = Label(tom_thumb, text="tom", color=0x00FF00, scale=1) 
        label2.x = 25
        label2.y = y_pos
        main_group.append(label2)
    
    device.display.refresh()
    device.matrix.render()
    
    if hasattr(device.matrix, 'surface'):
        screen.blit(device.matrix.surface, (0, 0))
        pygame.display.flip()
        pygame.image.save(device.matrix.surface, "baseline_test_current.png")
        print("Saved: baseline_test_current.png")
        
        # Analyze the rendering
        analyze_rendered_text(device.matrix.surface, "Current positioning")
    
    pygame.time.wait(1000)
    
    # Test 2: Baseline-aligned positioning
    print("\n=== Test 2: Baseline-aligned positioning ===")
    main_group = displayio.Group()
    device.display.root_group = main_group
    
    # Calculate baseline positions
    # For baseline alignment, position each font so their baselines are at the same level
    baseline_y = 20  # Desired baseline position
    
    # viii font: baseline is at ascent pixels from top
    viii_y = baseline_y - viii_font.ascent
    label1 = Label(viii_font, text="viii", color=0xFF0000, scale=1)
    label1.x = 5
    label1.y = viii_y
    main_group.append(label1)
    
    if tom_thumb:
        # tom-thumb font: baseline is at ascent pixels from top
        tom_y = baseline_y - tom_thumb.ascent
        label2 = Label(tom_thumb, text="tom", color=0x00FF00, scale=1)
        label2.x = 25
        label2.y = tom_y
        main_group.append(label2)
    
    print(f"Baseline at y={baseline_y}")
    print(f"viii positioned at y={viii_y} (baseline={viii_y + viii_font.ascent})")
    if tom_thumb:
        print(f"tom positioned at y={tom_y} (baseline={tom_y + tom_thumb.ascent})")
    
    device.display.refresh()
    device.matrix.render()
    
    if hasattr(device.matrix, 'surface'):
        screen.blit(device.matrix.surface, (0, 0))
        pygame.display.flip()
        pygame.image.save(device.matrix.surface, "baseline_test_aligned.png")
        print("Saved: baseline_test_aligned.png")
        
        # Analyze the rendering
        analyze_rendered_text(device.matrix.surface, "Baseline-aligned positioning")
    
    pygame.time.wait(2000)
    pygame.quit()


def analyze_rendered_text(surface, test_name):
    """Analyze what was actually rendered."""
    pixel_array = pygame.surfarray.array3d(surface)
    
    # Find all non-black pixels
    non_black = np.any(pixel_array > 10, axis=2)
    
    if np.any(non_black):
        rows = np.any(non_black, axis=0)
        cols = np.any(non_black, axis=1)
        
        y_min, y_max = np.where(rows)[0][[0, -1]]
        x_min, x_max = np.where(cols)[0][[0, -1]]
        
        print(f"{test_name}: Characters rendered from ({x_min}, {y_min}) to ({x_max}, {y_max})")
        print(f"  Total height: {y_max - y_min + 1} pixels")
        
        # Check for different colors (different fonts)
        red_pixels = pixel_array[:, :, 0] > 200
        green_pixels = pixel_array[:, :, 1] > 200
        
        if np.any(red_pixels):
            red_rows = np.any(red_pixels, axis=0)
            if np.any(red_rows):
                red_y_min, red_y_max = np.where(red_rows)[0][[0, -1]]
                print(f"  Red text (viii): y={red_y_min} to {red_y_max}")
        
        if np.any(green_pixels):
            green_rows = np.any(green_pixels, axis=0)
            if np.any(green_rows):
                green_y_min, green_y_max = np.where(green_rows)[0][[0, -1]]
                print(f"  Green text (tom): y={green_y_min} to {green_y_max}")
                
                # Check baseline alignment
                if np.any(red_pixels):
                    baseline_diff = abs(red_y_max - green_y_max)
                    print(f"  Baseline difference: {baseline_diff} pixels")
    else:
        print(f"{test_name}: No text rendered!")


def test_scale_2_issue():
    """Test the scale 2 rendering issue specifically."""
    print("\n" + "="*50)
    print("TESTING SCALE 2 ISSUE")
    print("="*50)
    
    device = MatrixPortalS3(width=64, height=32)
    device.initialize()
    
    pygame.init()
    screen = pygame.display.set_mode((device.matrix.surface_width, device.matrix.surface_height))
    
    # Test actual scale=2 behavior (should use Arial font)
    main_group = displayio.Group()
    device.display.root_group = main_group
    
    # This should automatically switch to Arial_16 font
    label = Label(terminalio_FONT, text="Test", color=0xFFFFFF, scale=2)
    label.x = 5
    label.y = 5
    main_group.append(label)
    
    print(f"Scale 2 font: {label.font.name if hasattr(label.font, 'name') else 'Unknown'}")
    print(f"Scale 2 metrics: height={label.font.height}, ascent={label.font.ascent}, descent={label.font.descent}")
    print(f"Label size: {label.width} x {label.height}")
    
    device.display.refresh()
    device.matrix.render()
    
    if hasattr(device.matrix, 'surface'):
        pygame.image.save(device.matrix.surface, "scale2_auto_font.png")
        analyze_rendered_text(device.matrix.surface, "Scale 2 (auto Arial font)")
    
    pygame.time.wait(1000)
    pygame.quit()


if __name__ == "__main__":
    create_baseline_alignment_test()
    test_scale_2_issue()