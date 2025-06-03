#!/usr/bin/env python3
"""Manual scrolling text demo for SLDK simulator."""

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
CYAN = 0x00FFFF
YELLOW = 0xFFFF00
RED = 0xFF0000


def main():
    """Run manual scrolling demo."""
    # Create and initialize device
    print("Creating MatrixPortal S3 with manual scrolling...")
    device = MatrixPortalS3()
    device.initialize()
    
    # Create display group
    main_group = Group()
    
    # Full messages
    message1 = "Welcome to SLDK! This is a scrolling message demo... "
    message2 = "Theme Park Waits - LED Matrix Display System "
    
    # Create labels
    label1 = Label(font=FONT, text="", color=CYAN)
    label1.x = 0
    label1.y = 10
    main_group.append(label1)
    
    label2 = Label(font=FONT, text="", color=YELLOW)
    label2.x = 0
    label2.y = 22
    main_group.append(label2)
    
    # Show on display
    device.display.show(main_group)
    
    # Run the simulation
    print("Running manual scrolling demo...")
    print("Text will scroll character by character")
    
    # Scrolling state
    pos1 = 0
    pos2 = 0
    last_update = time.time()
    chars_to_show = 10  # How many characters fit on screen
    
    def update():
        """Update function called each frame."""
        nonlocal pos1, pos2, last_update
        
        current_time = time.time()
        
        # Update every 0.1 seconds
        if current_time - last_update >= 0.1:
            last_update = current_time
            
            # Update positions
            pos1 = (pos1 + 1) % len(message1)
            pos2 = (pos2 + 1) % len(message2)
            
            # Extract visible portions
            visible1 = ""
            visible2 = ""
            
            for i in range(chars_to_show):
                visible1 += message1[(pos1 + i) % len(message1)]
                visible2 += message2[(pos2 + i) % len(message2)]
            
            # Update labels
            label1.text = visible1
            label2.text = visible2
            
            # Force display refresh
            device.display.refresh(minimum_frames_per_second=0)
            
            # Debug output every 10 updates
            if pos1 % 10 == 0:
                print(f"Position: {pos1}, Showing: '{visible1}'")
    
    device.run(update_callback=update, title="Manual Scrolling Demo")


if __name__ == "__main__":
    main()