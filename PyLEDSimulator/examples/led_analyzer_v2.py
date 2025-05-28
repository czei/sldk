#!/usr/bin/env python3
"""Improved LED pattern analyzer with visual debugging."""

import sys
import os
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3


def analyze_led_image_detailed(image_path):
    """Analyze LED image with detailed debugging."""
    img = Image.open(image_path)
    
    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    img_array = np.array(img)
    height, width = img_array.shape[:2]
    
    print(f"Image size: {width}x{height}")
    
    # Create a binary mask for yellow/bright pixels
    # Yellow pixels have high R and G, low B
    mask = np.zeros((height, width), dtype=bool)
    
    for y in range(height):
        for x in range(width):
            r, g, b = img_array[y, x][:3]
            # Check for yellow/amber (high red and green, low blue)
            if r > 150 and g > 150 and b < 100:
                mask[y, x] = True
    
    # Save debug image
    debug_img = Image.new('RGB', (width, height))
    for y in range(height):
        for x in range(width):
            if mask[y, x]:
                debug_img.putpixel((x, y), (255, 255, 0))
            else:
                debug_img.putpixel((x, y), (0, 0, 0))
    debug_img.save('led_mask_debug.png')
    print(f"Saved debug mask to led_mask_debug.png")
    
    # Now map to 64x32 grid
    led_grid = np.zeros((32, 64), dtype=bool)
    
    # Calculate LED size
    led_width = width / 64
    led_height = height / 32
    
    print(f"LED size estimate: {led_width:.1f} x {led_height:.1f} pixels")
    
    # For each LED position, check if it's lit
    for led_y in range(32):
        for led_x in range(64):
            # Define region for this LED
            x_start = int(led_x * led_width)
            x_end = int((led_x + 1) * led_width)
            y_start = int(led_y * led_height)
            y_end = int((led_y + 1) * led_height)
            
            # Count bright pixels in this region
            region = mask[y_start:y_end, x_start:x_end]
            bright_count = np.sum(region)
            total_pixels = region.size
            
            # If more than 30% of the region is bright, consider LED on
            if total_pixels > 0 and bright_count / total_pixels > 0.3:
                led_grid[led_y, led_x] = True
    
    # Extract pixel coordinates
    lit_pixels = []
    for y in range(32):
        for x in range(64):
            if led_grid[y, x]:
                lit_pixels.append((x, y))
    
    return lit_pixels


def create_final_display(pixel_list):
    """Create the final LED display from pixel list."""
    device = MatrixPortalS3()
    device.initialize()
    device.matrix.clear()
    
    yellow = (255, 255, 0)
    
    for x, y in pixel_list:
        device.matrix.set_pixel(x, y, yellow)
    
    return device


def main():
    """Analyze and recreate LED pattern."""
    original_image = os.path.expanduser("~/Downloads/IMG_6593.jpg")
    
    if not os.path.exists(original_image):
        print(f"Error: Original image not found at {original_image}")
        return
    
    # Analyze image
    print("Analyzing LED pattern...")
    pixels = analyze_led_image_detailed(original_image)
    
    print(f"\nFound {len(pixels)} lit LEDs")
    
    # Save pixel pattern
    with open('led_pixels_extracted.py', 'w') as f:
        f.write("# Extracted LED pixel pattern\n\n")
        f.write("PIXELS = [\n")
        
        current_y = -1
        for x, y in sorted(pixels, key=lambda p: (p[1], p[0])):
            if y != current_y:
                f.write(f"    # Row {y}\n")
                current_y = y
            f.write(f"    ({x}, {y}),\n")
        
        f.write("]\n")
    
    print("Saved pattern to led_pixels_extracted.py")
    
    # Create display
    device = create_final_display(pixels)
    
    # Run display
    print("\nDisplaying extracted pattern... Press ESC or close window to exit.")
    device.run(title="Extracted LED Pattern")


if __name__ == "__main__":
    main()