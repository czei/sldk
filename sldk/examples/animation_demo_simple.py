#!/usr/bin/env python3
"""Simple animation demo for SLDK using direct simulator."""

import sys
import os
import time
import math

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sldk.simulator.devices import MatrixPortalS3
from sldk.simulator.displayio import Group
from sldk.simulator.adafruit_display_text import Label
from sldk.simulator.terminalio import FONT


def main():
    """Run animation demos."""
    print("SLDK Simple Animation Demo")
    print("=" * 40)
    
    # Create and initialize device
    device = MatrixPortalS3()
    device.initialize()
    
    # Animation state
    animation_index = 0
    animation_start = time.time()
    animations = [
        ("scrolling", "Welcome to SLDK!", 5),
        ("bouncing", None, 8),
        ("rainbow", None, 8),
        ("scrolling", "Thanks for watching!", 5)
    ]
    
    def update_animation():
        """Update callback for animations."""
        nonlocal animation_index, animation_start
        
        if animation_index >= len(animations):
            return False  # Stop
        
        anim_type, param, duration = animations[animation_index]
        elapsed = time.time() - animation_start
        
        if elapsed >= duration:
            animation_index += 1
            animation_start = time.time()
            if animation_index < len(animations):
                print(f"\nStarting: {animations[animation_index][0]}")
            return True
        
        # Run current animation frame
        if anim_type == "scrolling":
            # Simple scrolling text
            text = param
            x_offset = int((elapsed * 30) % (len(text) * 6 + device.width)) - device.width
            device.matrix.fill(0x000000)
            # Draw text manually since we can't use async here
            for i, char in enumerate(text):
                char_x = x_offset + i * 6
                if -6 < char_x < device.width:
                    # Simplified - just show position
                    if 0 <= char_x < device.width:
                        device.matrix.set_pixel(char_x, 16, 0xFFFF00)
        
        elif anim_type == "bouncing":
            # Bouncing ball
            x = 10 + elapsed * 20
            y = 10 + math.sin(elapsed * 3) * 8
            x = x % device.width
            device.matrix.fill(0x000000)
            # Draw ball
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    px, py = int(x) + dx, int(y) + dy
                    if 0 <= px < device.width and 0 <= py < device.height:
                        if dx*dx + dy*dy <= 4:
                            device.matrix.set_pixel(px, py, 0xFF0000)
        
        elif anim_type == "rainbow":
            # Rainbow effect
            offset = int(elapsed * 30)
            for y in range(device.height):
                for x in range(device.width):
                    hue = (x * 10 + y * 5 + offset) % 360
                    # Simple color based on hue
                    if hue < 120:
                        color = 0xFF0000  # Red
                    elif hue < 240:
                        color = 0x00FF00  # Green
                    else:
                        color = 0x0000FF  # Blue
                    device.matrix.set_pixel(x, y, color)
        
        return True
    
    # Run with window
    device.run(update_callback=update_animation, title="SLDK Animation Demo")


if __name__ == "__main__":
    main()