#!/usr/bin/env python3
"""Test the brightness boost at 100% setting."""

import sys
import os
import pygame

# Add PyLEDSimulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from pyledsimulator.devices.matrixportal_s3 import MatrixPortalS3
from pyledsimulator import displayio
from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.terminalio import FONT as terminalio_FONT


def test_brightness_boost():
    """Test the brightness boost at 100% brightness setting."""
    
    print("=== BRIGHTNESS BOOST TEST ===")
    
    device = MatrixPortalS3(width=64, height=32)
    device.initialize()
    
    pygame.init()
    screen = pygame.display.set_mode((device.matrix.surface_width, device.matrix.surface_height))
    pygame.display.set_caption("Brightness Boost Test")
    
    font = terminalio_FONT
    
    # Set brightness to 100%
    device.display.brightness = 1.0
    print(f"Set brightness to 100%")
    print(f"Matrix brightness: {device.matrix.brightness}")
    
    # Create bright test content
    main_group = displayio.Group()
    device.display.root_group = main_group
    
    label = Label(font, text="BOOSTED!", color=0xFFFFFF)
    label.x = 5
    label.y = 10
    main_group.append(label)
    
    device.display.refresh()
    device.matrix.render()
    
    if hasattr(device.matrix, 'surface'):
        pygame.image.save(device.matrix.surface, "brightness_boosted.png")
        print("Saved: brightness_boosted.png")
        
        # Analyze actual pixel colors with boost
        pixel_array = pygame.surfarray.array3d(device.matrix.surface)
        non_black_pixels = pixel_array > 10
        
        if non_black_pixels.any():
            max_red = pixel_array[:, :, 0].max()
            max_green = pixel_array[:, :, 1].max()
            max_blue = pixel_array[:, :, 2].max()
            
            print(f"\\nWith 20% brightness boost:")
            print(f"  Max colors: R={max_red}, G={max_green}, B={max_blue}")
            print(f"  Input color was (255, 255, 255)")
            print(f"  Boost calculation: 255 × 1.2 = {255 * 1.2}, clamped to 255")
            
            if max_red == 255 and max_green == 255 and max_blue == 255:
                print(f"  ✓ Colors are at maximum after boost")
            else:
                print(f"  ⚠️  Colors didn't reach maximum: ({max_red}, {max_green}, {max_blue})")
        else:
            print("\\n✗ No visible pixels found")
    
    # Compare with 99% brightness (no boost)
    print(f"\\n--- Comparing with 99% brightness (no boost) ---")
    device.display.brightness = 0.99
    device.display.refresh()
    device.matrix.render()
    
    pygame.image.save(device.matrix.surface, "brightness_99_percent.png")
    
    pixel_array = pygame.surfarray.array3d(device.matrix.surface)
    max_red = pixel_array[:, :, 0].max()
    max_green = pixel_array[:, :, 1].max()
    max_blue = pixel_array[:, :, 2].max()
    
    expected_99 = int(255 * 0.99)
    print(f"At 99% brightness:")
    print(f"  Max colors: R={max_red}, G={max_green}, B={max_blue}")
    print(f"  Expected: ~{expected_99}")
    
    print(f"\\n=== SUMMARY ===")
    print(f"100% brightness should now appear brighter than 99% due to the boost.")
    print(f"Compare brightness_boosted.png with brightness_99_percent.png")
    
    pygame.time.wait(2000)
    pygame.quit()


if __name__ == "__main__":
    test_brightness_boost()