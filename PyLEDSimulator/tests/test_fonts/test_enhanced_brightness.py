#!/usr/bin/env python3
"""Test the enhanced LED brightness at 100%."""

import sys
import os
import pygame

# Add PyLEDSimulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from pyledsimulator.devices.matrixportal_s3 import MatrixPortalS3
from pyledsimulator import displayio
from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.terminalio import FONT as terminalio_FONT


def test_enhanced_brightness():
    """Test the enhanced LED brightness at 100% vs other levels."""
    
    print("=== ENHANCED LED BRIGHTNESS TEST ===")
    
    # Test 100% brightness (should be enhanced)
    print("\\nTesting 100% brightness (enhanced):")
    device = MatrixPortalS3(width=64, height=32)
    device.initialize()
    
    pygame.init()
    screen = pygame.display.set_mode((device.matrix.surface_width, device.matrix.surface_height))
    
    device.display.brightness = 1.0
    
    main_group = displayio.Group()
    device.display.root_group = main_group
    
    label = Label(terminalio_FONT, text="ENHANCED", color=0x00FF00, x=2, y=10)
    main_group.append(label)
    
    device.display.refresh()
    device.matrix.render()
    
    pygame.image.save(device.matrix.surface, "enhanced_100_percent.png")
    
    # Analyze colors
    pixel_array = pygame.surfarray.array3d(device.matrix.surface)
    max_green = pixel_array[:, :, 1].max()
    print(f"  Max green at 100%: {max_green}")
    print(f"  Input color: 0x00FF00 (0, 255, 0)")
    print(f"  Enhancement: 255 × 1.15 = {255 * 1.15}, clamped to 255")
    
    pygame.quit()
    
    # Test 90% brightness (should not be enhanced)
    print("\\nTesting 90% brightness (not enhanced):")
    device = MatrixPortalS3(width=64, height=32)
    device.initialize()
    
    pygame.init()
    screen = pygame.display.set_mode((device.matrix.surface_width, device.matrix.surface_height))
    
    device.display.brightness = 0.9
    
    main_group = displayio.Group()
    device.display.root_group = main_group
    
    label = Label(terminalio_FONT, text="NORMAL", color=0x00FF00, x=2, y=10)
    main_group.append(label)
    
    device.display.refresh()
    device.matrix.render()
    
    pygame.image.save(device.matrix.surface, "normal_90_percent.png")
    
    # Analyze colors
    pixel_array = pygame.surfarray.array3d(device.matrix.surface)
    max_green = pixel_array[:, :, 1].max()
    expected_90 = int(255 * 0.9)
    print(f"  Max green at 90%: {max_green}")
    print(f"  Expected: ~{expected_90}")
    
    pygame.quit()
    
    print(f"\\n=== COMPARISON ===")
    print(f"Compare the images:")
    print(f"  enhanced_100_percent.png - Should appear brighter")
    print(f"  normal_90_percent.png - Standard brightness")
    print(f"\\nThe 100% setting should now have enhanced LED brightness!")


if __name__ == "__main__":
    test_enhanced_brightness()