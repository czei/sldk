#!/usr/bin/env python3
"""Visual test of space character fix."""

import sys
import os
import pygame

# Add PyLEDSimulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from pyledsimulator.devices.matrixportal_s3 import MatrixPortalS3
from pyledsimulator import displayio
from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.terminalio import FONT as terminalio_FONT


def test_spaces_visual():
    """Visual test to see if spaces are creating proper gaps."""
    device = MatrixPortalS3(width=64, height=32)
    device.initialize()
    
    pygame.init()
    screen = pygame.display.set_mode((device.matrix.surface_width, device.matrix.surface_height))
    pygame.display.set_caption("Space Character Test")
    
    font = terminalio_FONT
    
    print("=== VISUAL SPACE CHARACTER TEST ===")
    print("Testing if spaces create proper gaps between words...")
    
    main_group = displayio.Group()
    device.display.root_group = main_group
    
    # Test different space scenarios
    test_texts = [
        "Hello World",     # Single space
        "Space Test",      # Another single space  
        "A B C D",         # Multiple single spaces
        "No-Space-Here"    # No spaces (for comparison)
    ]
    
    y_pos = 2
    for i, text in enumerate(test_texts):
        label = Label(font, text=text, color=0x00FF00)
        label.x = 1
        label.y = y_pos
        main_group.append(label)
        
        # Count spaces in text
        space_count = text.count(' ')
        expected_space_width = space_count * 6  # 6 pixels per space
        
        print(f"Line {i+1}: '{text}'")
        print(f"  {space_count} spaces × 6px = {expected_space_width}px space width")
        print(f"  Total label width: {label.width}px")
        
        y_pos += 8
    
    device.display.refresh()
    device.matrix.render()
    
    if hasattr(device.matrix, 'surface'):
        pygame.image.save(device.matrix.surface, "spaces_test.png")
        print("\\nSaved: spaces_test.png")
        print("Check the image - words should now be properly separated!")
    
    pygame.time.wait(3000)
    pygame.quit()


if __name__ == "__main__":
    test_spaces_visual()