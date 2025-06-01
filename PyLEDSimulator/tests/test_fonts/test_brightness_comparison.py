#!/usr/bin/env python3
"""Test brightness with different settings to find the issue."""

import sys
import os
import pygame

# Add PyLEDSimulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from pyledsimulator.devices.matrixportal_s3 import MatrixPortalS3
from pyledsimulator import displayio
from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.terminalio import FONT as terminalio_FONT


def test_brightness_comparison():
    """Test different brightness settings to compare appearance."""
    
    print("=== BRIGHTNESS COMPARISON TEST ===")
    
    # Test with multiple brightness levels
    brightness_levels = [1.0, 0.8, 0.6, 0.4, 0.2]
    
    for brightness in brightness_levels:
        print(f"\\nTesting brightness: {brightness} ({int(brightness*100)}%)")
        
        device = MatrixPortalS3(width=64, height=32)
        device.initialize()
        
        pygame.init()
        screen = pygame.display.set_mode((device.matrix.surface_width, device.matrix.surface_height))
        
        # Set brightness
        device.display.brightness = brightness
        
        # Create bright test content
        main_group = displayio.Group()
        device.display.root_group = main_group
        
        # Create multiple labels with different colors
        label1 = Label(terminalio_FONT, text="RED", color=0xFF0000, x=2, y=5)
        label2 = Label(terminalio_FONT, text="GREEN", color=0x00FF00, x=2, y=15)
        label3 = Label(terminalio_FONT, text="WHITE", color=0xFFFFFF, x=2, y=25)
        
        main_group.append(label1)
        main_group.append(label2) 
        main_group.append(label3)
        
        device.display.refresh()
        device.matrix.render()
        
        # Save image
        filename = f"brightness_{int(brightness*100)}_percent.png"
        pygame.image.save(device.matrix.surface, filename)
        
        # Analyze brightness
        pixel_array = pygame.surfarray.array3d(device.matrix.surface)
        max_red = pixel_array[:, :, 0].max()
        max_green = pixel_array[:, :, 1].max()
        max_blue = pixel_array[:, :, 2].max()
        
        print(f"  Saved: {filename}")
        print(f"  Max colors: R={max_red}, G={max_green}, B={max_blue}")
        print(f"  Expected ~{int(255 * brightness)} for full colors")
        
        pygame.quit()
    
    print(f"\\n=== SUMMARY ===")
    print(f"Generated brightness comparison images:")
    for brightness in brightness_levels:
        print(f"  - brightness_{int(brightness*100)}_percent.png")
    print(f"\\nCompare these images to see if 100% brightness looks dim.")
    print(f"If 100% still looks dim, the issue might be:")
    print(f"1. Display/monitor brightness settings")
    print(f"2. LED highlight effects making non-highlight areas look dim")
    print(f"3. Background contrast making bright areas appear dimmer")


if __name__ == "__main__":
    test_brightness_comparison()