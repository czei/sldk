#!/usr/bin/env python3
"""Test character spacing and alignment improvements."""

import sys
import os
import pygame

# Add PyLEDSimulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'PyLEDSimulator'))

from pyledsimulator.devices.matrixportal_s3 import MatrixPortalS3
from pyledsimulator import displayio
from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.terminalio import FONT as terminalio_FONT


def test_spacing_and_alignment():
    """Test the improved character spacing and alignment."""
    device = MatrixPortalS3(width=64, height=32)
    device.initialize()
    
    pygame.init()
    screen = pygame.display.set_mode((device.matrix.surface_width, device.matrix.surface_height))
    pygame.display.set_caption("Character Spacing and Alignment Test")
    
    font = terminalio_FONT
    
    print("=== CHARACTER SPACING AND ALIGNMENT TEST ===")
    
    # Test 1: Default spacing (character_spacing=1)
    print("\n=== Test 1: Default spacing ===")
    main_group = displayio.Group()
    device.display.root_group = main_group
    
    # Test with lowercase letters that have different heights
    label = Label(font, text="igloo time", color=0x00FF00, character_spacing=1)
    label.x = 2
    label.y = 5
    main_group.append(label)
    
    device.display.refresh()
    device.matrix.render()
    
    if hasattr(device.matrix, 'surface'):
        pygame.image.save(device.matrix.surface, "spacing_default.png")
        print("Saved: spacing_default.png")
    
    pygame.time.wait(2000)
    
    # Test 2: Increased spacing (character_spacing=2)
    print("\n=== Test 2: Increased spacing ===")
    main_group = displayio.Group()
    device.display.root_group = main_group
    
    label = Label(font, text="igloo time", color=0x00FF00, character_spacing=2)
    label.x = 2
    label.y = 5
    main_group.append(label)
    
    device.display.refresh()
    device.matrix.render()
    
    if hasattr(device.matrix, 'surface'):
        pygame.image.save(device.matrix.surface, "spacing_increased.png")
        print("Saved: spacing_increased.png")
    
    pygame.time.wait(2000)
    
    # Test 3: No extra spacing (character_spacing=0)
    print("\n=== Test 3: No extra spacing ===")
    main_group = displayio.Group()
    device.display.root_group = main_group
    
    label = Label(font, text="igloo time", color=0x00FF00, character_spacing=0)
    label.x = 2
    label.y = 5
    main_group.append(label)
    
    device.display.refresh()
    device.matrix.render()
    
    if hasattr(device.matrix, 'surface'):
        pygame.image.save(device.matrix.surface, "spacing_none.png")
        print("Saved: spacing_none.png")
    
    pygame.time.wait(2000)
    pygame.quit()


if __name__ == "__main__":
    test_spacing_and_alignment()