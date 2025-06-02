#!/usr/bin/env python3
"""Exact pixel recreation of LED display from screenshot.

This program turns on individual yellow pixels to exactly match
the LED pattern in the provided screenshot.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3


def main():
    """Recreate the exact LED pattern from the screenshot."""
    # Create and initialize device
    print("Creating LED pixel pattern...")
    device = MatrixPortalS3()
    device.initialize()
    
    # Clear the display
    device.matrix.clear()
    
    # Yellow color for all pixels
    yellow = (255, 255, 0)
    
    # Based on careful analysis of the original image, here are all the lit pixels
    # The image shows a 64x32 display with specific pixels lit in yellow
    
    # Row by row, marking which pixels are on
    # Using 0-based indexing (x: 0-63, y: 0-31)
    
    # First line of text (roughly y=3 to y=9)
    # T
    for x in range(1, 6): device.matrix.set_pixel(x, 3, yellow)
    for y in range(4, 10): device.matrix.set_pixel(3, y, yellow)
    
    # H  
    for y in range(3, 10): device.matrix.set_pixel(8, y, yellow)
    for y in range(3, 10): device.matrix.set_pixel(12, y, yellow)
    for x in range(9, 12): device.matrix.set_pixel(x, 6, yellow)
    
    # E
    for y in range(3, 10): device.matrix.set_pixel(15, y, yellow)
    for x in range(15, 19): device.matrix.set_pixel(x, 3, yellow)
    for x in range(15, 19): device.matrix.set_pixel(x, 6, yellow)
    for x in range(15, 19): device.matrix.set_pixel(x, 9, yellow)
    
    # M
    for y in range(3, 10): device.matrix.set_pixel(21, y, yellow)
    for y in range(3, 10): device.matrix.set_pixel(26, y, yellow)
    device.matrix.set_pixel(22, 4, yellow)
    device.matrix.set_pixel(23, 5, yellow)
    device.matrix.set_pixel(24, 5, yellow)
    device.matrix.set_pixel(25, 4, yellow)
    
    # E
    for y in range(3, 10): device.matrix.set_pixel(29, y, yellow)
    for x in range(29, 33): device.matrix.set_pixel(x, 3, yellow)
    for x in range(29, 33): device.matrix.set_pixel(x, 6, yellow)
    for x in range(29, 33): device.matrix.set_pixel(x, 9, yellow)
    
    # Space
    
    # P
    for y in range(3, 10): device.matrix.set_pixel(37, y, yellow)
    for x in range(37, 41): device.matrix.set_pixel(x, 3, yellow)
    for x in range(37, 41): device.matrix.set_pixel(x, 6, yellow)
    device.matrix.set_pixel(40, 4, yellow)
    device.matrix.set_pixel(40, 5, yellow)
    
    # A
    for y in range(4, 10): device.matrix.set_pixel(43, y, yellow)
    for y in range(4, 10): device.matrix.set_pixel(47, y, yellow)
    for x in range(44, 47): device.matrix.set_pixel(x, 3, yellow)
    for x in range(43, 48): device.matrix.set_pixel(x, 6, yellow)
    
    # R
    for y in range(3, 10): device.matrix.set_pixel(50, y, yellow)
    for x in range(50, 54): device.matrix.set_pixel(x, 3, yellow)
    for x in range(50, 54): device.matrix.set_pixel(x, 6, yellow)
    device.matrix.set_pixel(53, 4, yellow)
    device.matrix.set_pixel(53, 5, yellow)
    device.matrix.set_pixel(52, 7, yellow)
    device.matrix.set_pixel(53, 8, yellow)
    device.matrix.set_pixel(54, 9, yellow)
    
    # K
    for y in range(3, 10): device.matrix.set_pixel(57, y, yellow)
    device.matrix.set_pixel(60, 3, yellow)
    device.matrix.set_pixel(59, 4, yellow)
    device.matrix.set_pixel(58, 5, yellow)
    device.matrix.set_pixel(58, 6, yellow)
    device.matrix.set_pixel(59, 7, yellow)
    device.matrix.set_pixel(60, 8, yellow)
    device.matrix.set_pixel(61, 9, yellow)
    
    # Second line (WAITS) - roughly y=17 to y=23
    # W
    for y in range(17, 24): device.matrix.set_pixel(16, y, yellow)
    for y in range(17, 24): device.matrix.set_pixel(20, y, yellow)
    for y in range(17, 24): device.matrix.set_pixel(24, y, yellow)
    device.matrix.set_pixel(17, 22, yellow)
    device.matrix.set_pixel(18, 23, yellow)
    device.matrix.set_pixel(19, 22, yellow)
    device.matrix.set_pixel(21, 22, yellow)
    device.matrix.set_pixel(22, 23, yellow)
    device.matrix.set_pixel(23, 22, yellow)
    
    # A
    for y in range(18, 24): device.matrix.set_pixel(27, y, yellow)
    for y in range(18, 24): device.matrix.set_pixel(31, y, yellow)
    for x in range(28, 31): device.matrix.set_pixel(x, 17, yellow)
    for x in range(27, 32): device.matrix.set_pixel(x, 20, yellow)
    
    # I
    for x in range(34, 38): device.matrix.set_pixel(x, 17, yellow)
    for x in range(34, 38): device.matrix.set_pixel(x, 23, yellow)
    for y in range(17, 24): device.matrix.set_pixel(36, y, yellow)
    
    # T
    for x in range(40, 45): device.matrix.set_pixel(x, 17, yellow)
    for y in range(18, 24): device.matrix.set_pixel(42, y, yellow)
    
    # S
    for x in range(47, 51): device.matrix.set_pixel(x, 17, yellow)
    device.matrix.set_pixel(47, 18, yellow)
    device.matrix.set_pixel(47, 19, yellow)
    for x in range(47, 51): device.matrix.set_pixel(x, 20, yellow)
    device.matrix.set_pixel(50, 21, yellow)
    device.matrix.set_pixel(50, 22, yellow)
    for x in range(47, 51): device.matrix.set_pixel(x, 23, yellow)
    
    # Run the simulation
    print("Displaying LED pattern... Press ESC or close window to exit.")
    device.run(title="LED Pixel Recreation")


if __name__ == "__main__":
    main()