#!/usr/bin/env python3
"""Scrolling text demo for SLDK simulator."""

# Add SLDK to path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from sldk.simulator.devices import MatrixPortalS3
from sldk.simulator.displayio import Group
from sldk.simulator.adafruit_display_text.scrolling_label import ScrollingLabel
from sldk.simulator.terminalio import FONT

# Define colors
RED = 0xFF0000
GREEN = 0x00FF00
BLUE = 0x0000FF
WHITE = 0xFFFFFF
YELLOW = 0xFFFF00
CYAN = 0x00FFFF


def main():
    """Run scrolling text demo."""
    # Create and initialize device
    print("Creating MatrixPortal S3 with scrolling text...")
    device = MatrixPortalS3()
    device.initialize()
    
    # Create display group
    main_group = Group()
    
    # Create scrolling text
    scrolling_text = ScrollingLabel(
        font=FONT,
        text="Welcome to SLDK! This is a scrolling message demo... ",
        color=CYAN,
        max_characters=20,  # How many characters fit on screen
        animate_time=0.2   # Speed of scrolling
    )
    scrolling_text.x = 0
    scrolling_text.y = 10
    main_group.append(scrolling_text)
    
    # Create another scrolling text
    scrolling_text2 = ScrollingLabel(
        font=FONT,
        text="Theme Park Waits - LED Matrix Display ",
        color=YELLOW,
        max_characters=20,
        animate_time=0.15
    )
    scrolling_text2.x = 0
    scrolling_text2.y = 22
    main_group.append(scrolling_text2)
    
    # Show on display
    device.display.show(main_group)
    
    # Start scrolling
    scrolling_text._is_scrolling = True
    scrolling_text2._is_scrolling = True
    
    # Run the simulation
    print("Running scrolling text demo... Press ESC or close window to exit.")
    
    def update():
        """Update function called each frame."""
        # Update scrolling labels
        scrolling_text.update()
        scrolling_text2.update()
        
        # Force display refresh
        device.display.show(main_group)
    
    device.run(update_callback=update, title="SLDK Scrolling Text Demo")


if __name__ == "__main__":
    main()