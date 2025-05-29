#!/usr/bin/env python3
"""Test drawing directly to the LED matrix bypassing displayio."""

import sys
import os
import math
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3


def main():
    """Test direct matrix drawing."""
    print("Testing direct matrix drawing...")
    device = MatrixPortalS3()
    device.initialize()
    
    # Get direct access to the LED matrix
    matrix = device.display.get_matrix()
    
    print("Drawing directly to matrix...")
    print("You should see bright colors and moving patterns!")
    
    frame_count = 0
    
    def update():
        """Update function with direct matrix drawing."""
        nonlocal frame_count
        
        # Clear the matrix
        matrix.clear()
        
        # Draw a bright roller coaster track
        # Track points - simplified version
        track_points = []
        
        # Create simple track
        for x in range(5, 60):
            if x < 20:
                y = 25 - (x - 5) // 3  # Climb
            elif x < 35:
                y = int(15 + 8 * math.sin((x - 20) * 0.3))  # Hill
            elif x < 45:
                y = 20 + (x - 35) // 2  # Drop
            else:
                y = 25  # Flat
            
            track_points.append((x, y))
        
        # Draw track in bright white
        for x, y in track_points:
            if 0 <= x < 64 and 0 <= y < 32:
                matrix.set_pixel(x, y, (255, 255, 255))  # Bright white
        
        # Draw support pillars in gray
        for x in range(8, 60, 8):
            # Find track height
            track_y = 25
            for tx, ty in track_points:
                if tx == x:
                    track_y = ty
                    break
            
            # Draw pillar
            for y in range(track_y + 1, 30):
                matrix.set_pixel(x, y, (128, 128, 128))  # Gray
        
        # Calculate cart position
        cart_x = int(30 + 20 * math.sin(frame_count * 0.1))
        cart_y = int(20 + 5 * math.sin(frame_count * 0.07))
        
        # Clamp cart position
        cart_x = max(1, min(62, cart_x))
        cart_y = max(1, min(30, cart_y))
        
        # Draw bright red cart (3x2 pixels)
        cart_color = (255, 0, 0)  # Bright red
        for dy in range(2):
            for dx in range(3):
                px = cart_x + dx - 1
                py = cart_y + dy
                if 0 <= px < 64 and 0 <= py < 32:
                    matrix.set_pixel(px, py, cart_color)
        
        # Draw some sparkles
        for i in range(5):
            sparkle_x = int(32 + 25 * math.sin(frame_count * 0.2 + i))
            sparkle_y = int(16 + 10 * math.cos(frame_count * 0.15 + i))
            if 0 <= sparkle_x < 64 and 0 <= sparkle_y < 32:
                matrix.set_pixel(sparkle_x, sparkle_y, (255, 255, 0))  # Yellow
        
        # Draw corner markers to verify the display is working
        matrix.set_pixel(0, 0, (0, 255, 0))    # Green top-left
        matrix.set_pixel(63, 0, (0, 0, 255))   # Blue top-right
        matrix.set_pixel(0, 31, (255, 0, 255)) # Magenta bottom-left
        matrix.set_pixel(63, 31, (0, 255, 255))# Cyan bottom-right
        
        # Render the matrix
        matrix.render()
        
        frame_count += 1
        
        # Print debug info occasionally
        if frame_count % 60 == 0:
            print(f"Frame {frame_count}: Cart at ({cart_x}, {cart_y})")
            print(f"  Matrix size: {matrix.width}x{matrix.height}")
            print(f"  Surface size: {matrix.surface_width}x{matrix.surface_height}")
    
    # Take a screenshot first
    print("Taking initial screenshot...")
    device.display.refresh()
    
    # Save screenshot manually
    try:
        screenshot_path = "/Users/czei/Projects/Disney/ThemeParkAPI/PyLEDSimulator/direct_matrix_test.png"
        # Run one update to draw something
        update()
        device.save_screenshot(screenshot_path)
        print(f"Screenshot saved to: {screenshot_path}")
    except Exception as e:
        print(f"Could not save screenshot: {e}")
    
    # Run the simulation
    print("Starting direct matrix animation...")
    device.run(update_callback=update, title="Direct Matrix Test - Should Show Bright Colors")


if __name__ == "__main__":
    main()