#!/usr/bin/env python3
"""Final LED pattern analyzer that properly maps to 64x32 grid."""

import sys
import os
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3


def analyze_and_create_pattern():
    """Analyze the original image and create LED pattern."""
    # Load original image
    img = Image.open(os.path.expanduser("~/Downloads/IMG_6593.jpg"))
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    img_array = np.array(img)
    height, width = img_array.shape[:2]
    
    # The image shows a physical LED matrix
    # We need to find the bounds of the actual LED area
    # Looking for the first and last yellow pixels
    
    # Find bounds of yellow region
    yellow_mask = np.zeros((height, width), dtype=bool)
    for y in range(height):
        for x in range(width):
            r, g, b = img_array[y, x][:3]
            if r > 150 and g > 150 and b < 100:  # Yellow
                yellow_mask[y, x] = True
    
    # Find bounds
    rows_with_yellow = np.any(yellow_mask, axis=1)
    cols_with_yellow = np.any(yellow_mask, axis=0)
    
    y_indices = np.where(rows_with_yellow)[0]
    x_indices = np.where(cols_with_yellow)[0]
    
    if len(y_indices) == 0 or len(x_indices) == 0:
        print("No yellow pixels found!")
        return []
    
    # Crop to LED area
    y_min, y_max = y_indices[0], y_indices[-1]
    x_min, x_max = x_indices[0], x_indices[-1]
    
    led_area_width = x_max - x_min + 1
    led_area_height = y_max - y_min + 1
    
    print(f"LED area: {led_area_width}x{led_area_height} pixels")
    print(f"Bounds: x={x_min}-{x_max}, y={y_min}-{y_max}")
    
    # Calculate LED size
    led_width = led_area_width / 64
    led_height = led_area_height / 32
    
    print(f"LED size: {led_width:.1f} x {led_height:.1f} pixels")
    
    # Map to 64x32 grid
    pixels = []
    
    for led_y in range(32):
        for led_x in range(64):
            # Calculate center of this LED in the image
            center_x = x_min + int((led_x + 0.5) * led_width)
            center_y = y_min + int((led_y + 0.5) * led_height)
            
            # Sample a small area around the center
            sample_size = 3
            lit = False
            
            for dy in range(-sample_size, sample_size + 1):
                for dx in range(-sample_size, sample_size + 1):
                    check_x = center_x + dx
                    check_y = center_y + dy
                    
                    if 0 <= check_x < width and 0 <= check_y < height:
                        r, g, b = img_array[check_y, check_x][:3]
                        if r > 150 and g > 150 and b < 100:
                            lit = True
                            break
                if lit:
                    break
            
            if lit:
                pixels.append((led_x, led_y))
    
    return pixels


def main():
    """Create the final LED display."""
    print("Analyzing LED pattern from image...")
    pixels = analyze_and_create_pattern()
    
    print(f"\nFound {len(pixels)} lit LEDs")
    
    # Create device
    device = MatrixPortalS3()
    device.initialize()
    device.matrix.clear()
    
    # Set pixels
    yellow = (255, 255, 0)
    for x, y in pixels:
        device.matrix.set_pixel(x, y, yellow)
    
    # Save the pixel pattern for reference
    with open('theme_park_waits_pixels.py', 'w') as f:
        f.write("# THEME PARK WAITS LED pixel pattern\n")
        f.write("# Extracted from image analysis\n\n")
        f.write("PIXELS = [\n")
        
        current_y = -1
        for x, y in sorted(pixels, key=lambda p: (p[1], p[0])):
            if y != current_y:
                f.write(f"    # Row {y}\n")
                current_y = y
            f.write(f"    ({x}, {y}),\n")
        
        f.write("]\n")
    
    print("Saved pattern to theme_park_waits_pixels.py")
    
    # Run display
    print("\nDisplaying pattern... Press ESC or close window to exit.")
    device.run(title="THEME PARK WAITS - Extracted Pattern")


if __name__ == "__main__":
    main()