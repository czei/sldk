#!/usr/bin/env python3
"""Test the examples by running them and capturing snapshots."""

import sys
import os
import time
import subprocess
import pygame
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3
from pyledsimulator.displayio import Group
from pyledsimulator.adafruit_display_text import Label
from pyledsimulator.terminalio import FONT
from pyledsimulator.core import RED, GREEN


def test_hello_led_snapshot():
    """Test the Hello LED example and capture a snapshot."""
    print("Testing Hello LED example...")
    
    # Initialize pygame
    pygame.init()
    
    # Create device
    device = MatrixPortalS3()
    device.initialize()
    
    # Create display group
    main_group = Group()
    
    # Create "Hello" label
    hello_label = Label(
        font=FONT,
        text="Hello",
        color=RED,
        x=2,
        y=8
    )
    main_group.append(hello_label)
    
    # Create "LED!" label
    led_label = Label(
        font=FONT,
        text="LED!",
        color=GREEN,
        x=2,
        y=20
    )
    main_group.append(led_label)
    
    # Show on display
    device.show(main_group)
    device.refresh()
    
    # Render the display
    matrix = device.display.get_matrix()
    matrix.render()
    
    # Save screenshot
    output_path = "hello_led_snapshot.png"
    matrix.save_screenshot(output_path)
    print(f"Saved snapshot to: {output_path}")
    
    # Also get the pixel data to verify
    surface = matrix.get_surface()
    pixels = pygame.surfarray.array3d(surface)
    
    # Check if there are any non-background pixels
    background_color = np.array([10, 10, 10])
    non_background_pixels = 0
    
    for y in range(pixels.shape[1]):
        for x in range(pixels.shape[0]):
            pixel = pixels[x, y]
            if not np.array_equal(pixel, background_color):
                non_background_pixels += 1
                
    print(f"Found {non_background_pixels} non-background pixels")
    
    # Check for red pixels (Hello text)
    red_pixels = 0
    for y in range(pixels.shape[1]):
        for x in range(pixels.shape[0]):
            pixel = pixels[x, y]
            if pixel[0] > 200 and pixel[1] < 100 and pixel[2] < 100:
                red_pixels += 1
                
    print(f"Found {red_pixels} red pixels")
    
    # Check for green pixels (LED! text)
    green_pixels = 0
    for y in range(pixels.shape[1]):
        for x in range(pixels.shape[0]):
            pixel = pixels[x, y]
            if pixel[0] < 100 and pixel[1] > 200 and pixel[2] < 100:
                green_pixels += 1
                
    print(f"Found {green_pixels} green pixels")
    
    # Verify the display is working
    success = non_background_pixels > 1000 and red_pixels > 100 and green_pixels > 100
    
    if success:
        print("✅ Display is working correctly!")
    else:
        print("❌ Display is not showing expected content")
        
    return success


def main():
    """Run the snapshot test."""
    success = test_hello_led_snapshot()
    
    if success:
        print("\nThe LED simulator is now working correctly!")
        print("The examples should display properly when run interactively.")
    else:
        print("\nThere may still be issues with the display.")
        
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())