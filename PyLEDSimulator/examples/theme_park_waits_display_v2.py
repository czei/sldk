#!/usr/bin/env python3
"""Recreation of THEME PARK WAITS LED display using proper fonts.

This program recreates the LED display showing "THEME PARK" on the first line 
and "WAITS" on the second line in yellow/amber color using actual fonts.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3
from pyledsimulator.displayio import Group
from pyledsimulator.adafruit_display_text import Label
from pyledsimulator.adafruit_bitmap_font import bitmap_font
from pyledsimulator.core import rgb888_to_rgb565


def main():
    """Run the THEME PARK WAITS display."""
    # Create and initialize device
    print("Creating THEME PARK WAITS display...")
    device = MatrixPortalS3()
    device.initialize()
    
    # Load fonts - try different sizes to match the original
    font_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts')
    
    # Try the larger font first
    try:
        # LeagueSpartan is too large, let's use the 5x8 font with scaling
        font = bitmap_font.load_font(os.path.join(font_dir, '5x8.bdf'))
        print("Loaded 5x8 font")
    except:
        # Fallback to tom-thumb
        font = bitmap_font.load_font(os.path.join(font_dir, 'tom-thumb.bdf'))
        print("Loaded tom-thumb font")
    
    # Create display group
    main_group = Group()
    
    # Yellow/amber color (matches the LED display)
    yellow_color = rgb888_to_rgb565(255, 255, 0)
    
    # Create "THEME PARK" label - top line
    # The original image shows text that fills most of the height
    theme_park_label = Label(
        font=font,
        text="THEME PARK",
        color=yellow_color,
        scale=2,  # Scale up to match the larger text in original
        x=2,      # Small left margin
        y=7       # Position for scaled text
    )
    main_group.append(theme_park_label)
    
    # Create "WAITS" label - bottom line
    waits_label = Label(
        font=font,
        text="WAITS",
        color=yellow_color,
        scale=2,  # Same scale as top line
        x=15,     # Center it horizontally
        y=22      # Position for second line with scaled text
    )
    main_group.append(waits_label)
    
    # Show on display
    device.show(main_group)
    
    # Run the simulation
    print("Displaying THEME PARK WAITS... Press ESC or close window to exit.")
    
    # Simple animation - subtle brightness variation
    frame_count = 0
    brightness_offset = 0
    
    def update():
        """Update function for animation."""
        nonlocal frame_count, brightness_offset
        
        # Create a subtle "breathing" effect
        import math
        brightness = 0.85 + 0.15 * math.sin(frame_count * 0.02)
        device.matrix.set_brightness(brightness)
        
        frame_count += 1
    
    device.run(update_callback=update, title="THEME PARK WAITS Display")


if __name__ == "__main__":
    main()