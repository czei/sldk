#!/usr/bin/env python3
"""Debug the relationship between label.y and actual rendering position."""

import sys
import os
import pygame

# Add PyLEDSimulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'PyLEDSimulator'))

from pyledsimulator.devices.matrixportal_s3 import MatrixPortalS3
from pyledsimulator import displayio
from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.terminalio import FONT as terminalio_FONT


def test_position_mapping():
    """Test how label.y maps to actual pixel positions."""
    device = MatrixPortalS3(width=64, height=32)
    device.initialize()
    
    pygame.init()
    screen = pygame.display.set_mode((device.matrix.surface_width, device.matrix.surface_height))
    
    viii_font = terminalio_FONT
    
    print("=== POSITION MAPPING TEST ===")
    print(f"Font metrics: height={viii_font.height}, ascent={viii_font.ascent}, descent={viii_font.descent}")
    
    # Test simple positioning
    main_group = displayio.Group()
    device.display.root_group = main_group
    
    # Create a simple label at y=5
    label = Label(viii_font, text="A", color=0xFF0000, scale=1)
    label.x = 5
    label.y = 5
    main_group.append(label)
    
    print(f"Label created: x={label.x}, y={label.y}")
    print(f"Label dimensions: {label.width} x {label.height}")
    print(f"Label bounding box: {label.bounding_box}")
    
    device.display.refresh()
    device.matrix.render()
    
    if hasattr(device.matrix, 'surface'):
        pygame.image.save(device.matrix.surface, "position_debug.png")
        print("Saved: position_debug.png")
        
        # Find where the pixels actually rendered
        pixel_array = pygame.surfarray.array3d(device.matrix.surface)
        red_pixels = pixel_array[:, :, 0] > 200
        
        if red_pixels.any():
            rows = red_pixels.any(axis=0)
            cols = red_pixels.any(axis=1)
            
            if rows.any() and cols.any():
                y_min, y_max = rows.nonzero()[0][[0, -1]]
                x_min, x_max = cols.nonzero()[0][[0, -1]]
                
                print(f"Actual rendered position: ({x_min}, {y_min}) to ({x_max}, {y_max})")
                print(f"Expected label.y={label.y}, actual top pixel at y={y_min}")
                print(f"Offset from label.y: {y_min - label.y}")
    
    pygame.time.wait(1000)
    pygame.quit()


if __name__ == "__main__":
    test_position_mapping()