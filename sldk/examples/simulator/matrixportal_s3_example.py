#!/usr/bin/env python3
"""Basic MatrixPortal S3 simulation example."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add SLDK to path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from sldk.simulator.devices import MatrixPortalS3
from sldk.simulator.displayio import Group
from sldk.simulator.adafruit_display_text import Label
from sldk.simulator.terminalio import FONT
# Define colors
RED = 0xFF0000
GREEN = 0x00FF00
BLUE = 0x0000FF
WHITE = 0xFFFFFF


def main():
    """Run basic MatrixPortal S3 demo."""
    # Create and initialize device
    print("Creating MatrixPortal S3...")
    device = MatrixPortalS3()
    device.initialize()
    
    # Create display group
    main_group = Group()
    
    # Create "Hello" label
    hello_label = Label(
        font=FONT,
        text="Hello",
        color=RED,
        x=2,
        y=8
    )
    main_group.append(hello_label)
    
    # Create "LED!" label
    led_label = Label(
        font=FONT,
        text="LED!",
        color=GREEN,
        x=2,
        y=20
    )
    main_group.append(led_label)
    
    # Show on display
    device.display.show(main_group)
    
    # Run the simulation
    print("Running simulation... Press ESC or close window to exit.")
    
    # Animation variables
    frame_count = 0
    
    def update():
        """Update function called each frame."""
        nonlocal frame_count
        frame_count += 1
        
        # Change colors periodically
        if frame_count % 60 == 0:  # Every second at 60 FPS
            print(f"Frame {frame_count}: Changing colors")
            hello_label.color = GREEN if hello_label.color == RED else RED
            led_label.color = BLUE if led_label.color == GREEN else GREEN
            # Force display update
            device.display.refresh(minimum_frames_per_second=0)
    
    device.run(update_callback=update, title="MatrixPortal S3 Example")
    

if __name__ == "__main__":
    main()