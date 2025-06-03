#!/usr/bin/env python3
"""Simple text update test for SLDK simulator."""

# Add SLDK to path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from sldk.simulator.devices import MatrixPortalS3
from sldk.simulator.displayio import Group
from sldk.simulator.adafruit_display_text import Label
from sldk.simulator.terminalio import FONT
import time

# Define colors
RED = 0xFF0000
GREEN = 0x00FF00
BLUE = 0x0000FF


def main():
    """Run simple text update test."""
    print("Creating MatrixPortal S3...")
    device = MatrixPortalS3()
    device.initialize()
    
    # Create display group
    main_group = Group()
    
    # Create a label
    label = Label(font=FONT, text="0", color=RED)
    label.x = 28
    label.y = 16
    main_group.append(label)
    
    # Show on display
    device.display.show(main_group)
    
    print("Running text update test...")
    print("Numbers should count from 0 to 9 repeatedly")
    
    # Counter
    counter = 0
    last_update = time.time()
    
    def update():
        """Update function called each frame."""
        nonlocal counter, last_update
        
        current_time = time.time()
        
        # Update every 0.5 seconds
        if current_time - last_update >= 0.5:
            last_update = current_time
            
            # Update counter
            counter = (counter + 1) % 10
            
            # Update label text
            label.text = str(counter)
            
            # Also change color
            colors = [RED, GREEN, BLUE]
            label.color = colors[counter % 3]
            
            # Force the display to redraw
            device.display.show(main_group)
            
            print(f"Updated to: {counter}")
    
    device.run(update_callback=update, title="Text Update Test")


if __name__ == "__main__":
    main()