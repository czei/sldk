#!/usr/bin/env python3
"""Simple test to debug roller coaster rendering."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3


def main():
    """Test basic pixel rendering."""
    print("Creating MatrixPortal S3 for simple test...")
    device = MatrixPortalS3()
    device.initialize()
    
    # Get direct access to the LED matrix
    matrix = device.display.get_matrix()
    
    print("Drawing simple track pattern...")
    
    def update():
        """Update function."""
        # Clear matrix
        matrix.clear()
        
        # Draw a simple roller coaster track shape
        # Big hill
        for x in range(10, 30):
            y = 20 - abs(x - 20) // 2
            if 0 <= x < 64 and 0 <= y < 32:
                matrix.set_pixel(x, y, (128, 128, 128))  # Gray track
                
        # Drop
        for x in range(30, 40):
            y = 15 + (x - 30)
            if 0 <= x < 64 and 0 <= y < 32:
                matrix.set_pixel(x, y, (128, 128, 128))
                
        # Bottom
        for x in range(40, 50):
            y = 25
            if 0 <= x < 64 and 0 <= y < 32:
                matrix.set_pixel(x, y, (128, 128, 128))
                
        # Draw a red cart at position 20, 10
        matrix.set_pixel(20, 10, (255, 0, 0))
        matrix.set_pixel(21, 10, (255, 0, 0))
        matrix.set_pixel(20, 11, (255, 0, 0))
        matrix.set_pixel(21, 11, (255, 0, 0))
        
        # Render
        matrix.render()
    
    # Run the simulation
    device.run(update_callback=update, title="Simple Roller Coaster Test")


if __name__ == "__main__":
    main()