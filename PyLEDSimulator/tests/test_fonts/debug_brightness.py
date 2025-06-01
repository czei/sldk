#!/usr/bin/env python3
"""Debug brightness settings and color output."""

import sys
import os
import pygame

# Add PyLEDSimulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from pyledsimulator.devices.matrixportal_s3 import MatrixPortalS3
from pyledsimulator import displayio
from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.terminalio import FONT as terminalio_FONT


def debug_brightness():
    """Debug brightness settings and color output."""
    
    print("=== BRIGHTNESS DEBUG ===")
    
    device = MatrixPortalS3(width=64, height=32)
    device.initialize()
    
    pygame.init()
    screen = pygame.display.set_mode((device.matrix.surface_width, device.matrix.surface_height))
    pygame.display.set_caption("Brightness Debug")
    
    font = terminalio_FONT
    
    # Check initial brightness values
    print(f"Initial matrix brightness: {device.matrix.brightness}")
    print(f"Initial display brightness: {device.display.brightness}")
    
    # Test with maximum brightness
    device.display.brightness = 1.0
    print(f"Set display brightness to 1.0")
    print(f"Matrix brightness now: {device.matrix.brightness}")
    print(f"Display brightness now: {device.display.brightness}")
    
    # Create a bright white label
    main_group = displayio.Group()
    device.display.root_group = main_group
    
    label = Label(font, text="BRIGHT", color=0xFFFFFF)  # Pure white
    label.x = 5
    label.y = 10
    main_group.append(label)
    
    print(f"\\nCreated white text with color=0xFFFFFF")
    print(f"Expected RGB: (255, 255, 255)")
    
    device.display.refresh()
    device.matrix.render()
    
    if hasattr(device.matrix, 'surface'):
        pygame.image.save(device.matrix.surface, "brightness_test_max.png")
        print("Saved: brightness_test_max.png")
        
        # Analyze actual pixel colors
        pixel_array = pygame.surfarray.array3d(device.matrix.surface)
        non_black_pixels = pixel_array > 10
        
        if non_black_pixels.any():
            # Find max color values in the rendered surface
            max_red = pixel_array[:, :, 0].max()
            max_green = pixel_array[:, :, 1].max()
            max_blue = pixel_array[:, :, 2].max()
            
            print(f"\\nActual rendered colors:")
            print(f"  Max red: {max_red}/255")
            print(f"  Max green: {max_green}/255")
            print(f"  Max blue: {max_blue}/255")
            
            if max_red < 255 or max_green < 255 or max_blue < 255:
                print(f"\\n⚠️  Colors are dimmer than expected!")
                print(f"   Expected: (255, 255, 255)")
                print(f"   Actual max: ({max_red}, {max_green}, {max_blue})")
            else:
                print(f"\\n✓ Colors are at maximum brightness")
        else:
            print("\\n✗ No visible pixels found")
    
    # Test with different brightness levels
    for brightness in [0.5, 0.25]:
        print(f"\\n--- Testing brightness {brightness} ---")
        device.display.brightness = brightness
        device.display.refresh()
        device.matrix.render()
        
        pygame.image.save(device.matrix.surface, f"brightness_test_{int(brightness*100)}.png")
        
        # Analyze colors at this brightness
        pixel_array = pygame.surfarray.array3d(device.matrix.surface)
        max_red = pixel_array[:, :, 0].max()
        max_green = pixel_array[:, :, 1].max()
        max_blue = pixel_array[:, :, 2].max()
        
        expected_value = int(255 * brightness)
        print(f"  Expected max RGB: ~{expected_value}")
        print(f"  Actual max RGB: ({max_red}, {max_green}, {max_blue})")
    
    pygame.time.wait(2000)
    pygame.quit()


if __name__ == "__main__":
    debug_brightness()