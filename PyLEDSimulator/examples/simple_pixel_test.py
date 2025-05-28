#!/usr/bin/env python3
"""Simple pixel test - directly set pixels without using displayio."""

import sys
import os
import math
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3


def main():
    """Run simple pixel test."""
    print("Creating MatrixPortal S3 for simple pixel test...")
    device = MatrixPortalS3()
    device.initialize()
    
    # Get direct access to the LED matrix
    matrix = device.display.get_matrix()
    
    print("Drawing pixel patterns directly on the LED matrix...")
    print("Press ESC or close window to exit.")
    
    frame_count = 0
    
    def update():
        """Update function called each frame."""
        nonlocal frame_count
        
        # Clear the matrix
        matrix.clear()
        
        # Draw a simple pattern based on frame count
        t = frame_count / 60.0  # Time in seconds
        
        # Draw a moving red dot
        red_x = int(32 + 20 * math.sin(t))
        red_y = int(16 + 10 * math.cos(t))
        matrix.set_pixel(red_x, red_y, (255, 0, 0))
        
        # Draw a moving green dot in opposite phase
        green_x = int(32 - 20 * math.sin(t))
        green_y = int(16 - 10 * math.cos(t))
        matrix.set_pixel(green_x, green_y, (0, 255, 0))
        
        # Draw a static blue cross in the center
        for i in range(5):
            matrix.set_pixel(32, 14 + i, (0, 0, 255))  # Vertical
            matrix.set_pixel(30 + i, 16, (0, 0, 255))  # Horizontal
        
        # Draw white corners
        matrix.set_pixel(0, 0, (255, 255, 255))  # Top-left
        matrix.set_pixel(63, 0, (255, 255, 255))  # Top-right
        matrix.set_pixel(0, 31, (255, 255, 255))  # Bottom-left
        matrix.set_pixel(63, 31, (255, 255, 255))  # Bottom-right
        
        # Draw a rainbow line at the top that flows
        for x in range(64):
            # Add frame_count * 2 to make the rainbow flow to the right
            hue = ((x * 360 / 64) + (frame_count * 2)) % 360
            r = int(255 * (1 + math.sin(math.radians(hue))) / 2)
            g = int(255 * (1 + math.sin(math.radians(hue + 120))) / 2)
            b = int(255 * (1 + math.sin(math.radians(hue + 240))) / 2)
            matrix.set_pixel(x, 2, (r, g, b))
        
        # Render the matrix
        matrix.render()
        
        frame_count += 1
    
    # Run the simulation
    device.run(update_callback=update, title="Simple Pixel Test")


if __name__ == "__main__":
    main()