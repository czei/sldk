#!/usr/bin/env python3
"""Manually recreated THEME PARK WAITS display based on visual inspection.

Based on careful observation of the original image, this recreates
the exact LED pattern with proper sizing and positioning.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3


def main():
    """Create THEME PARK WAITS display with correct sizing."""
    device = MatrixPortalS3()
    device.initialize()
    device.matrix.clear()
    
    yellow = (255, 255, 0)
    
    # Based on the original image analysis:
    # - Text appears to use approximately 8-10 pixel tall letters
    # - "WAITS" is indeed larger/bolder than "THEME PARK"
    # - The display fills most of the 32 pixel height
    
    # THEME PARK - First line (8 pixels tall)
    # Moved down 1 LED (y+1) and right 2 LEDs (x+2)
    # Each character is exactly 8 LEDs tall (y=3 to y=10)
    
    # T (x=4, y=3) - 8 LEDs tall
    for x in range(4, 9): device.matrix.set_pixel(x, 3, yellow)
    for y in range(4, 11): device.matrix.set_pixel(6, y, yellow)
    
    # H (x=10, y=3) - 8 LEDs tall
    for y in range(3, 11): device.matrix.set_pixel(10, y, yellow)
    for y in range(3, 11): device.matrix.set_pixel(14, y, yellow)
    for x in range(11, 14): device.matrix.set_pixel(x, 6, yellow)
    
    # E (x=16, y=3) - 8 LEDs tall
    for y in range(3, 11): device.matrix.set_pixel(16, y, yellow)
    for x in range(16, 20): device.matrix.set_pixel(x, 3, yellow)
    for x in range(16, 19): device.matrix.set_pixel(x, 6, yellow)
    for x in range(16, 20): device.matrix.set_pixel(x, 10, yellow)
    
    # M (x=22, y=3) - 8 LEDs tall
    for y in range(3, 11): device.matrix.set_pixel(22, y, yellow)
    for y in range(3, 11): device.matrix.set_pixel(27, y, yellow)
    device.matrix.set_pixel(23, 4, yellow)
    device.matrix.set_pixel(24, 5, yellow)
    device.matrix.set_pixel(25, 5, yellow)
    device.matrix.set_pixel(26, 4, yellow)
    
    # E (x=29, y=3) - 8 LEDs tall
    for y in range(3, 11): device.matrix.set_pixel(29, y, yellow)
    for x in range(29, 33): device.matrix.set_pixel(x, 3, yellow)
    for x in range(29, 32): device.matrix.set_pixel(x, 6, yellow)
    for x in range(29, 33): device.matrix.set_pixel(x, 10, yellow)
    
    # Space
    
    # P (x=36, y=3) - 8 LEDs tall
    for y in range(3, 11): device.matrix.set_pixel(36, y, yellow)
    for x in range(36, 40): device.matrix.set_pixel(x, 3, yellow)
    for x in range(36, 40): device.matrix.set_pixel(x, 6, yellow)
    device.matrix.set_pixel(39, 4, yellow)
    device.matrix.set_pixel(39, 5, yellow)
    
    # A (x=42, y=3) - 8 LEDs tall
    for y in range(4, 11): device.matrix.set_pixel(42, y, yellow)
    for y in range(4, 11): device.matrix.set_pixel(46, y, yellow)
    for x in range(43, 46): device.matrix.set_pixel(x, 3, yellow)
    for x in range(42, 47): device.matrix.set_pixel(x, 6, yellow)
    
    # R (x=48, y=3) - 8 LEDs tall
    for y in range(3, 11): device.matrix.set_pixel(48, y, yellow)
    for x in range(48, 52): device.matrix.set_pixel(x, 3, yellow)
    for x in range(48, 52): device.matrix.set_pixel(x, 6, yellow)
    device.matrix.set_pixel(51, 4, yellow)
    device.matrix.set_pixel(51, 5, yellow)
    device.matrix.set_pixel(50, 7, yellow)
    device.matrix.set_pixel(51, 8, yellow)
    device.matrix.set_pixel(52, 9, yellow)
    device.matrix.set_pixel(53, 10, yellow)
    
    # K (x=54, y=3) - 8 LEDs tall
    for y in range(3, 11): device.matrix.set_pixel(54, y, yellow)
    device.matrix.set_pixel(57, 3, yellow)
    device.matrix.set_pixel(56, 4, yellow)
    device.matrix.set_pixel(55, 5, yellow)
    device.matrix.set_pixel(55, 6, yellow)
    device.matrix.set_pixel(56, 7, yellow)
    device.matrix.set_pixel(57, 8, yellow)
    device.matrix.set_pixel(58, 9, yellow)
    device.matrix.set_pixel(59, 10, yellow)
    
    # WAITS - Second line (much larger text - 16 pixels tall!)
    # Moved up 1 LED: now starts at y=15 and goes to y=30 (16 pixels tall)
    # Each character is 10 LEDs wide with 1 LED spacing
    # Moved right by 3 LEDs total
    
    # W (x=5, y=15) - 10 LEDs wide, 16 pixels tall
    # Mapping exact LEDs from screenshot pixel by pixel
    
    # Left outer edge - 2 LEDs wide, full height
    for y in range(15, 31):
        device.matrix.set_pixel(5, y, yellow)
        device.matrix.set_pixel(6, y, yellow)
    
    # Right outer edge - 2 LEDs wide, full height  
    for y in range(15, 31):
        device.matrix.set_pixel(13, y, yellow)
        device.matrix.set_pixel(14, y, yellow)
    
    # Inner left diagonal - starts at x=8, goes down and inward
    device.matrix.set_pixel(8, 15, yellow)
    device.matrix.set_pixel(8, 16, yellow)
    device.matrix.set_pixel(8, 17, yellow)
    device.matrix.set_pixel(8, 18, yellow)
    device.matrix.set_pixel(8, 19, yellow)
    device.matrix.set_pixel(8, 20, yellow)
    device.matrix.set_pixel(8, 21, yellow)
    device.matrix.set_pixel(8, 22, yellow)
    device.matrix.set_pixel(9, 23, yellow)  # Start angling in
    device.matrix.set_pixel(9, 24, yellow)
    device.matrix.set_pixel(9, 25, yellow)
    device.matrix.set_pixel(9, 26, yellow)
    device.matrix.set_pixel(9, 27, yellow)
    device.matrix.set_pixel(9, 28, yellow)
    device.matrix.set_pixel(9, 29, yellow)
    device.matrix.set_pixel(9, 30, yellow)
    
    # Inner right diagonal - starts at x=11, goes down and inward
    device.matrix.set_pixel(11, 15, yellow)
    device.matrix.set_pixel(11, 16, yellow)
    device.matrix.set_pixel(11, 17, yellow)
    device.matrix.set_pixel(11, 18, yellow)
    device.matrix.set_pixel(11, 19, yellow)
    device.matrix.set_pixel(11, 20, yellow)
    device.matrix.set_pixel(11, 21, yellow)
    device.matrix.set_pixel(11, 22, yellow)
    device.matrix.set_pixel(10, 23, yellow)  # Start angling in
    device.matrix.set_pixel(10, 24, yellow)
    device.matrix.set_pixel(10, 25, yellow)
    device.matrix.set_pixel(10, 26, yellow)
    device.matrix.set_pixel(10, 27, yellow)
    device.matrix.set_pixel(10, 28, yellow)
    device.matrix.set_pixel(10, 29, yellow)
    device.matrix.set_pixel(10, 30, yellow)
    
    # A (x=16, y=15) - 10 LEDs wide, 16 pixels tall
    # Left line
    for y in range(17, 31):
        device.matrix.set_pixel(16, y, yellow)
        device.matrix.set_pixel(17, y, yellow)
    # Right line
    for y in range(17, 31):
        device.matrix.set_pixel(24, y, yellow)
        device.matrix.set_pixel(25, y, yellow)
    # Top peak
    for x in range(18, 24):
        device.matrix.set_pixel(x, 15, yellow)
        device.matrix.set_pixel(x, 16, yellow)
    # Middle crossbar
    for x in range(16, 26):
        device.matrix.set_pixel(x, 22, yellow)
        device.matrix.set_pixel(x, 23, yellow)
    
    # I (x=27, y=15) - 10 LEDs wide, 16 pixels tall
    # Top bar (2 LEDs thick)
    for x in range(27, 37):
        device.matrix.set_pixel(x, 15, yellow)
        device.matrix.set_pixel(x, 16, yellow)
    # Bottom bar (2 LEDs thick)
    for x in range(27, 37):
        device.matrix.set_pixel(x, 29, yellow)
        device.matrix.set_pixel(x, 30, yellow)
    # Center vertical
    for y in range(15, 31):
        device.matrix.set_pixel(31, y, yellow)
        device.matrix.set_pixel(32, y, yellow)
    
    # T (x=38, y=15) - 10 LEDs wide, 16 pixels tall
    # Top bar (2 LEDs thick)
    for x in range(38, 48):
        device.matrix.set_pixel(x, 15, yellow)
        device.matrix.set_pixel(x, 16, yellow)
    # Center vertical
    for y in range(15, 31):
        device.matrix.set_pixel(42, y, yellow)
        device.matrix.set_pixel(43, y, yellow)
    
    # S (x=49, y=15) - 10 LEDs wide, 16 pixels tall
    # Top horizontal (2 LEDs thick)
    for x in range(49, 59):
        device.matrix.set_pixel(x, 15, yellow)
        device.matrix.set_pixel(x, 16, yellow)
    # Top left vertical
    for y in range(17, 22):
        device.matrix.set_pixel(49, y, yellow)
        device.matrix.set_pixel(50, y, yellow)
    # Middle horizontal (2 LEDs thick)
    for x in range(49, 59):
        device.matrix.set_pixel(x, 22, yellow)
        device.matrix.set_pixel(x, 23, yellow)
    # Bottom right vertical
    for y in range(24, 29):
        device.matrix.set_pixel(57, y, yellow)
        device.matrix.set_pixel(58, y, yellow)
    # Bottom horizontal (2 LEDs thick)
    for x in range(49, 59):
        device.matrix.set_pixel(x, 29, yellow)
        device.matrix.set_pixel(x, 30, yellow)
    
    print("Displaying THEME PARK WAITS... Press ESC or close window to exit.")
    device.run(title="THEME PARK WAITS")


if __name__ == "__main__":
    main()