#!/usr/bin/env python3
"""Scrolling text demonstration."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sldk.simulator.devices import MatrixPortalS3
from sldk.simulator.displayio import Group
from sldk.simulator.adafruit_display_text import ScrollingLabel
from sldk.simulator.terminalio import FONT
from sldk.simulator.core import CYAN, MAGENTA, YELLOW


def main():
    """Run scrolling text demo."""
    # Create and initialize device
    print("Creating MatrixPortal S3 with scrolling text...")
    device = MatrixPortalS3()
    device.initialize()
    
    # Create display group
    main_group = Group()
    
    # Create scrolling labels
    top_scroll = ScrollingLabel(
        font=FONT,
        text="Welcome to SLDK Simulator! This is a long scrolling message...",
        max_characters=13,  # Show 13 characters at a time
        color=CYAN,
        x=0,
        y=8,
        animate_time=0.2  # Scroll every 0.2 seconds
    )
    main_group.append(top_scroll)
    
    middle_scroll = ScrollingLabel(
        font=FONT,
        text="*** Breaking News: LEDs are awesome! ***",
        max_characters=10,
        color=YELLOW,
        x=0,
        y=16,
        animate_time=0.15
    )
    main_group.append(middle_scroll)
    
    bottom_scroll = ScrollingLabel(
        font=FONT,
        text="Visit github.com/yourusername/sldk",
        max_characters=12,
        color=MAGENTA,
        x=0,
        y=24,
        animate_time=0.25
    )
    main_group.append(bottom_scroll)
    
    # Start scrolling animations
    top_scroll.start_scrolling()
    middle_scroll.start_scrolling()
    bottom_scroll.start_scrolling()
    
    # Show on display
    device.show(main_group)
    
    # Run the simulation
    print("Running scrolling text demo... Press ESC or close window to exit.")
    
    def update():
        """Update function called each frame."""
        # Update all scrolling labels
        top_scroll.update()
        middle_scroll.update()
        bottom_scroll.update()
    
    device.run(update_callback=update, title="Scrolling Text Example")
    

if __name__ == "__main__":
    main()