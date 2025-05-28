#!/usr/bin/env python3
"""Basic MatrixPortal S3 simulation example."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3
from pyledsimulator.displayio import Group
from pyledsimulator.adafruit_display_text import Label
from pyledsimulator.terminalio import FONT
from pyledsimulator.core import RED, GREEN, BLUE, WHITE


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
    device.show(main_group)
    
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
            hello_label.color = GREEN if hello_label.color == RED else RED
            led_label.color = BLUE if led_label.color == GREEN else GREEN
    
    device.run(update_callback=update, title="MatrixPortal S3 Example")
    

if __name__ == "__main__":
    main()