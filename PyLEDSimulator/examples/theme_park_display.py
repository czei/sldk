#!/usr/bin/env python3
"""Example showing how PyLEDSimulator can be used with ThemeParkAPI."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3
from pyledsimulator.displayio import Group
from pyledsimulator.adafruit_display_text import Label, ScrollingLabel
from pyledsimulator.terminalio import FONT
from pyledsimulator.core import RED, GREEN, YELLOW, WHITE


def main():
    """Simulate a theme park wait times display."""
    # Create and initialize device
    print("Creating theme park wait times display...")
    device = MatrixPortalS3()
    device.initialize()
    
    # Create display group
    main_group = Group()
    
    # Park name at top
    park_label = Label(
        font=FONT,
        text="Magic Kingdom",
        color=WHITE,
        x=2,
        y=6
    )
    main_group.append(park_label)
    
    # Scrolling ride info
    ride_scroll = ScrollingLabel(
        font=FONT,
        text="Space Mountain: 45 min | Thunder Mountain: 30 min | Pirates: 15 min",
        max_characters=15,
        color=YELLOW,
        x=0,
        y=16,
        animate_time=0.2
    )
    ride_scroll.start_scrolling()
    main_group.append(ride_scroll)
    
    # Status indicator
    status_label = Label(
        font=FONT,
        text="UPDATING...",
        color=GREEN,
        x=2,
        y=26
    )
    main_group.append(status_label)
    
    # Show on display
    device.show(main_group)
    
    # Run the simulation
    print("Running theme park display simulation...")
    print("This demonstrates how the LED simulator could be integrated")
    print("with the ThemeParkAPI to show wait times on an LED matrix.")
    print("\nPress ESC or close window to exit.")
    
    # Animation variables
    frame_count = 0
    status_messages = ["UPDATING...", "CONNECTED", "REFRESHING"]
    status_colors = [GREEN, WHITE, YELLOW]
    status_index = 0
    
    def update():
        """Update function called each frame."""
        nonlocal frame_count, status_index
        frame_count += 1
        
        # Update scrolling text
        ride_scroll.update()
        
        # Change status every 3 seconds
        if frame_count % 180 == 0:
            status_index = (status_index + 1) % len(status_messages)
            status_label.text = status_messages[status_index]
            status_label.color = status_colors[status_index]
    
    device.run(update_callback=update, title="Theme Park Wait Times Display")
    

if __name__ == "__main__":
    main()