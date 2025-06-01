#!/usr/bin/env python3
"""Test font scaling issues and fix."""

import sys
import os
import pygame

# Add PyLEDSimulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'PyLEDSimulator'))

from pyledsimulator.devices.matrixportal_s3 import MatrixPortalS3
from pyledsimulator import displayio
from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.terminalio import FONT as terminalio_FONT

def test_scale_behavior():
    device = MatrixPortalS3(width=64, height=32)
    device.initialize()
    
    pygame.init()
    screen = pygame.display.set_mode((device.matrix.surface_width, device.matrix.surface_height))
    
    # Test what fonts are being used
    label1 = Label(terminalio_FONT, text="Test", scale=1)
    label2 = Label(terminalio_FONT, text="Test", scale=2)
    
    print(f"Scale 1 font: {label1.font.name if hasattr(label1.font, 'name') else 'Unknown'}")
    print(f"Scale 1 font height: {label1.font.height}, ascent: {label1.font.ascent}")
    
    print(f"Scale 2 font: {label2.font.name if hasattr(label2.font, 'name') else 'Unknown'}")  
    print(f"Scale 2 font height: {label2.font.height}, ascent: {label2.font.ascent}")
    
    # Clear display and test positioning
    main_group = displayio.Group()
    device.display.root_group = main_group
    
    # Test just scale 1 first
    label = Label(terminalio_FONT, text="Hello", color=0xFFFFFF, scale=1)
    label.x = 5
    label.y = 10
    main_group.append(label)
    
    device.display.refresh()
    device.matrix.render()
    
    if hasattr(device.matrix, 'surface'):
        screen.blit(device.matrix.surface, (0, 0))
        pygame.display.flip()
        pygame.image.save(device.matrix.surface, "scale1_test.png")
        print("Scale 1 screenshot saved: scale1_test.png")
    
    pygame.time.wait(1000)
    
    # Now test scale 2 with explicit font to avoid font switching
    main_group.pop()  # Remove previous label
    
    # Use the same font with manual scaling instead of font switching
    label2 = Label(terminalio_FONT, text="Hi", color=0xFF0000, scale=1)  # Keep scale=1 but font will be rendered larger
    label2.x = 5
    label2.y = 15
    main_group.append(label2)
    
    device.display.refresh()
    device.matrix.render()
    
    if hasattr(device.matrix, 'surface'):
        screen.blit(device.matrix.surface, (0, 0))
        pygame.display.flip()
        pygame.image.save(device.matrix.surface, "manual_scale_test.png")
        print("Manual scale screenshot saved: manual_scale_test.png")
    
    pygame.time.wait(2000)
    pygame.quit()

if __name__ == "__main__":
    test_scale_behavior()