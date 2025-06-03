#!/usr/bin/env python3
"""Color animation demo for SLDK simulator."""

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
YELLOW = 0xFFFF00
CYAN = 0x00FFFF
MAGENTA = 0xFF00FF
WHITE = 0xFFFFFF

# Color sequence
COLORS = [RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, WHITE]


def main():
    """Run color animation demo."""
    # Create and initialize device
    print("Creating MatrixPortal S3 with color animation...")
    device = MatrixPortalS3()
    device.initialize()
    
    # Create display group
    main_group = Group()
    
    # Create labels with initial colors
    label1 = Label(
        font=FONT,
        text="COLOR",
        color=RED,
        x=10,
        y=8
    )
    main_group.append(label1)
    
    label2 = Label(
        font=FONT,
        text="DEMO",
        color=BLUE,
        x=15,
        y=20
    )
    main_group.append(label2)
    
    # Show on display
    device.display.show(main_group)
    
    # Run the simulation
    print("Running color animation demo...")
    print("The text colors will cycle through: RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, WHITE")
    
    # Animation variables
    color_index1 = 0
    color_index2 = 3  # Start at different color
    last_update = time.time()
    
    def update():
        """Update function called each frame."""
        nonlocal color_index1, color_index2, last_update
        
        current_time = time.time()
        
        # Update every 0.5 seconds
        if current_time - last_update >= 0.5:
            last_update = current_time
            
            # Update colors
            color_index1 = (color_index1 + 1) % len(COLORS)
            color_index2 = (color_index2 + 1) % len(COLORS)
            
            new_color1 = COLORS[color_index1]
            new_color2 = COLORS[color_index2]
            
            label1.color = new_color1
            label2.color = new_color2
            
            # Force display refresh
            device.display.show(main_group)
            
            # Print color names for debugging
            color_names = ["RED", "GREEN", "BLUE", "YELLOW", "CYAN", "MAGENTA", "WHITE"]
            print(f"Colors: {color_names[color_index1]} / {color_names[color_index2]}")
    
    device.run(update_callback=update, title="Color Animation Demo")


if __name__ == "__main__":
    main()