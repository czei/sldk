#!/usr/bin/env python3
"""Visual test of the kerning improvements."""

import sys
import os
import pygame

# Add PyLEDSimulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from pyledsimulator.devices.matrixportal_s3 import MatrixPortalS3
from pyledsimulator import displayio
from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.terminalio import FONT as terminalio_FONT


def test_kerning_visual():
    """Visual test of kerning improvements."""
    device = MatrixPortalS3(width=64, height=32)
    device.initialize()
    
    pygame.init()
    screen = pygame.display.set_mode((device.matrix.surface_width, device.matrix.surface_height))
    pygame.display.set_caption("Kerning Test")
    
    font = terminalio_FONT
    
    print("=== VISUAL KERNING TEST ===")
    print("Creating labels with proper DWIDTH kerning...")
    
    # Test with the problematic lowercase text
    main_group = displayio.Group()
    device.display.root_group = main_group
    
    # Line 1: Lowercase letters that showed spacing issues
    label1 = Label(font, text="igloo time", color=0x00FF00)
    label1.x = 2
    label1.y = 5
    main_group.append(label1)
    
    # Line 2: Mixed case
    label2 = Label(font, text="Wait: 45min", color=0x0000FF)
    label2.x = 2
    label2.y = 20
    main_group.append(label2)
    
    print(f"Label 1: '{label1.text}' - {label1.width}x{label1.height}")
    print(f"Label 2: '{label2.text}' - {label2.width}x{label2.height}")
    
    device.display.refresh()
    device.matrix.render()
    
    if hasattr(device.matrix, 'surface'):
        pygame.image.save(device.matrix.surface, "kerning_improved.png")
        print("Saved: kerning_improved.png")
        print("\\nKerning test complete! Check the image to see if spacing looks better.")
    
    pygame.time.wait(3000)
    pygame.quit()


if __name__ == "__main__":
    test_kerning_visual()