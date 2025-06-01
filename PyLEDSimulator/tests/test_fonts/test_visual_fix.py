#!/usr/bin/env python3
"""Visual test of the positioning fix."""

import sys
import os
import pygame

# Add PyLEDSimulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from pyledsimulator.devices.matrixportal_s3 import MatrixPortalS3
from pyledsimulator import displayio
from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.terminalio import FONT as terminalio_FONT


def test_visual_fix():
    """Visual test to see if characters are now visible."""
    device = MatrixPortalS3(width=64, height=32)
    device.initialize()
    
    pygame.init()
    screen = pygame.display.set_mode((device.matrix.surface_width, device.matrix.surface_height))
    pygame.display.set_caption("Positioning Fix Test")
    
    font = terminalio_FONT
    
    print("=== VISUAL POSITIONING FIX TEST ===")
    print("Testing if characters are now visible...")
    
    main_group = displayio.Group()
    device.display.root_group = main_group
    
    # Test simple text that was showing only top 2 pixels before
    label = Label(font, text="Hello World", color=0x00FF00)
    label.x = 2
    label.y = 5
    main_group.append(label)
    
    print(f"Created label: '{label.text}'")
    print(f"Label size: {label.width}x{label.height}")
    print(f"Position: ({label.x}, {label.y})")
    
    device.display.refresh()
    device.matrix.render()
    
    if hasattr(device.matrix, 'surface'):
        pygame.image.save(device.matrix.surface, "positioning_fixed.png")
        print("Saved: positioning_fixed.png")
        print("\\nCheck the image - characters should now be fully visible!")
        
        # Quick analysis of the surface
        pixel_array = pygame.surfarray.array3d(device.matrix.surface)
        non_black_pixels = (pixel_array > 10).any(axis=2)
        
        if non_black_pixels.any():
            print("✓ Non-black pixels found - text is rendering!")
        else:
            print("✗ No visible pixels found - still an issue")
    
    pygame.time.wait(3000)
    pygame.quit()


if __name__ == "__main__":
    test_visual_fix()