#!/usr/bin/env python3
"""Dual zone display example with different content areas."""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sldk.simulator.devices import MatrixPortalS3
from sldk.simulator.displayio import Group, Bitmap, Palette, TileGrid
from sldk.simulator.adafruit_display_text import Label
from sldk.simulator.terminalio import FONT
from sldk.simulator.core import RED, GREEN, BLUE, WHITE, BLACK, YELLOW


def create_border(width, height, color):
    """Create a border bitmap."""
    bitmap = Bitmap(width, height, 2)
    palette = Palette(2)
    palette[0] = BLACK
    palette[1] = color
    
    # Draw border
    for x in range(width):
        bitmap[x, 0] = 1
        bitmap[x, height-1] = 1
    for y in range(height):
        bitmap[0, y] = 1
        bitmap[width-1, y] = 1
        
    return bitmap, palette


def main():
    """Run dual zone display demo."""
    # Create and initialize device
    print("Creating dual zone display...")
    device = MatrixPortalS3()
    device.initialize()
    
    # Create main group
    main_group = Group()
    
    # Zone 1: Status area (top half)
    status_group = Group(x=0, y=0)
    
    # Add border for status zone
    status_border, status_palette = create_border(64, 16, BLUE)
    status_border_grid = TileGrid(status_border, pixel_shader=status_palette)
    status_group.append(status_border_grid)
    
    # Add status text
    status_label = Label(
        font=FONT,
        text="STATUS: OK",
        color=GREEN,
        x=8,
        y=8
    )
    status_group.append(status_label)
    
    main_group.append(status_group)
    
    # Zone 2: Info area (bottom half)
    info_group = Group(x=0, y=16)
    
    # Add border for info zone
    info_border, info_palette = create_border(64, 16, YELLOW)
    info_border_grid = TileGrid(info_border, pixel_shader=info_palette)
    info_group.append(info_border_grid)
    
    # Add info text
    info_label = Label(
        font=FONT,
        text="Temp: 72F",
        color=WHITE,
        x=8,
        y=8
    )
    info_group.append(info_label)
    
    main_group.append(info_group)
    
    # Show on display
    device.show(main_group)
    
    # Run the simulation
    print("Running dual zone demo... Press ESC or close window to exit.")
    
    # Animation variables
    frame_count = 0
    temp = 72
    status_states = ["OK", "BUSY", "WAIT"]
    status_colors = [GREEN, YELLOW, RED]
    status_index = 0
    
    def update():
        """Update function called each frame."""
        nonlocal frame_count, temp, status_index
        frame_count += 1
        
        # Update status every 2 seconds
        if frame_count % 120 == 0:
            status_index = (status_index + 1) % len(status_states)
            status_label.text = f"STATUS: {status_states[status_index]}"
            status_label.color = status_colors[status_index]
        
        # Update temperature every second
        if frame_count % 60 == 0:
            temp = 68 + (frame_count // 60) % 10
            info_label.text = f"Temp: {temp}F"
    
    device.run(update_callback=update, title="Dual Zone Example")
    

if __name__ == "__main__":
    main()