#!/usr/bin/env python3
"""Rainbow text effect demonstration."""

import sys
import os
import math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add SLDK to path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from sldk.simulator.devices import MatrixPortalS3
from sldk.simulator.displayio import Group
from sldk.simulator.adafruit_display_text import Label
from sldk.simulator.terminalio import FONT
from sldk.simulator.adafruit_bitmap_font import bitmap_font


def rgb888_to_rgb565(r, g, b):
    """Convert RGB components to 16-bit RGB565 format.
    
    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)
        
    Returns:
        16-bit RGB565 color
    """
    # Convert to RGB565
    r5 = (r >> 3) & 0x1F
    g6 = (g >> 2) & 0x3F
    b5 = (b >> 3) & 0x1F
    
    return (r5 << 11) | (g6 << 5) | b5


def hsv_to_rgb(h, s, v):
    """Convert HSV color to RGB.
    
    Args:
        h: Hue (0-360)
        s: Saturation (0-1)
        v: Value (0-1)
        
    Returns:
        Tuple of (r, g, b) in 0-255 range
    """
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
        
    return (
        int((r + m) * 255),
        int((g + m) * 255),
        int((b + m) * 255)
    )


def main():
    """Run rainbow text effect demo."""
    # Create and initialize device
    print("Creating rainbow text effect with larger font...")
    device = MatrixPortalS3()
    device.initialize()
    
    # Load a larger font - LeagueSpartan-Bold-16 for nice medium-large text
    try:
        font_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                'fonts', 'LeagueSpartan-Bold-16.bdf')
        if os.path.exists(font_path):
            print(f"Loading LeagueSpartan-Bold-16 font")
            large_font = bitmap_font.load_font(font_path)
            # This font is already large (32px height), so we won't need scale=2
        else:
            print("Using default font")
            large_font = FONT
    except Exception as e:
        print(f"Failed to load font: {e}, using default")
        large_font = FONT
    
    # Create display group
    main_group = Group()
    
    # Create multiple labels for rainbow effect
    # Check if we're using the large font
    is_large_font = hasattr(large_font, 'height') and large_font.height > 10
    
    if is_large_font:
        # For large fonts, use single label with full text (individual chars would be too big)
        text = "RAINBOW"
        rainbow_label = Label(
            font=large_font,
            text=text,
            color=0xFFFFFF,
            scale=1,  # No scaling needed for large font
            x=2,
            y=16  # Center vertically on 32px display
        )
        main_group.append(rainbow_label)
        labels = [rainbow_label]  # Single label for color animation
        
        # No wave label for large font - not enough vertical space
        wave_label = None
    else:
        # For small fonts, use individual character labels with scaling
        text = "RAINBOW"
        labels = []
        char_spacing = 7  # Spacing between characters with scale=2
        
        for i, char in enumerate(text):
            label = Label(
                font=large_font,
                text=char,
                color=0xFFFFFF,
                scale=2,  # Make text 2x larger
                x=2 + i * char_spacing,
                y=8
            )
            labels.append(label)
            main_group.append(label)
        
        # Add wave label for small fonts
        wave_label = Label(
            font=large_font,
            text="~WAVE~",
            color=0xFFFFFF,
            scale=2,
            x=6,
            y=20
        )
        main_group.append(wave_label)
    
    # Show on display
    device.show(main_group)
    
    # Run the simulation
    print("Running rainbow text demo... Press ESC or close window to exit.")
    
    # Animation variables
    hue_offset = 0
    wave_y_base = 20  # Adjusted for larger scaled text
    
    def update():
        """Update function called each frame."""
        nonlocal hue_offset, is_large_font, device
        
        # Update rainbow colors
        if is_large_font:
            # For large font, cycle the whole text color
            hue = hue_offset % 360
            r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
            color_565 = rgb888_to_rgb565(r, g, b)
            labels[0].color = color_565
            # Debug: print color change every 60 frames
            if hue_offset % 60 == 0:
                print(f"Large font color update: hue={hue}, rgb=({r},{g},{b}), color_565=0x{color_565:04X}")
        else:
            # For small fonts, individual character colors
            for i, label in enumerate(labels):
                hue = (hue_offset + i * 60) % 360
                r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
                label.color = rgb888_to_rgb565(r, g, b)
        
        # Update wave if it exists (only for small fonts)
        if wave_label:
            # Update wave position and color
            wave_y = wave_y_base + int(math.sin(hue_offset * 0.05) * 3)
            wave_label.y = wave_y
            
            # Wave color cycles through spectrum
            wave_hue = (hue_offset * 2) % 360
            r, g, b = hsv_to_rgb(wave_hue, 0.8, 1.0)
            wave_label.color = rgb888_to_rgb565(r, g, b)
        
        # Increment hue
        hue_offset = (hue_offset + 2) % 360
        
        # Ensure display is refreshed
        device.display.show(main_group)
    
    device.run(update_callback=update, title="Rainbow Text Effect")
    

if __name__ == "__main__":
    main()