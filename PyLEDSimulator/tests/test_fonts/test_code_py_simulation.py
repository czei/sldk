#!/usr/bin/env python3
"""Simulate what happens when running code.py with the font fix."""

import sys
import os
import pygame

# Add PyLEDSimulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from pyledsimulator.devices.matrixportal_s3 import MatrixPortalS3
from pyledsimulator import displayio
from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.terminalio import FONT as terminalio_FONT


def simulate_code_py():
    """Simulate the typical usage in code.py."""
    
    print("=== CODE.PY SIMULATION ===")
    print("Simulating typical theme park display usage...")
    
    device = MatrixPortalS3(width=64, height=32)
    device.initialize()
    
    pygame.init()
    screen = pygame.display.set_mode((device.matrix.surface_width, device.matrix.surface_height))
    pygame.display.set_caption("Code.py Simulation")
    
    font = terminalio_FONT
    
    # Create main group like in the theme park app
    main_group = displayio.Group()
    device.display.root_group = main_group
    
    # Test typical theme park text (what user was seeing only top 2 pixels of)
    test_texts = [
        "Pirates: 45 min",
        "Space: 20 min", 
        "igloo time",
        "gypjq test"
    ]
    
    y_pos = 2
    for i, text in enumerate(test_texts):
        label = Label(font, text=text, color=0x00FF00)
        label.x = 1
        label.y = y_pos
        main_group.append(label)
        
        print(f"Line {i+1}: '{text}' at y={y_pos}")
        y_pos += 8
    
    device.display.refresh()
    device.matrix.render()
    
    if hasattr(device.matrix, 'surface'):
        pygame.image.save(device.matrix.surface, "code_py_simulation.png")
        print("\\nSaved: code_py_simulation.png")
        
        # Analyze if text is visible
        pixel_array = pygame.surfarray.array3d(device.matrix.surface)
        non_black_pixels = (pixel_array > 10).any(axis=2)
        
        if non_black_pixels.any():
            rows_with_pixels = non_black_pixels.any(axis=0)
            y_positions = rows_with_pixels.nonzero()[0]
            if len(y_positions) > 0:
                print(f"✓ Text visible from y={y_positions[0]} to y={y_positions[-1]}")
                print("✓ Fix successful - full characters should now be visible!")
            else:
                print("✗ No visible text found")
        else:
            print("✗ No visible pixels found")
    
    pygame.time.wait(2000)
    pygame.quit()


if __name__ == "__main__":
    simulate_code_py()