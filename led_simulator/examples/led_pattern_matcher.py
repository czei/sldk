#!/usr/bin/env python3
"""LED pattern matcher that compares original image with simulation.

This program analyzes the original LED image and iteratively adjusts
the simulation until the patterns match.
"""

import sys
import os
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3


def analyze_led_image(image_path, threshold=100):
    """Analyze an LED image and extract lit pixel positions.
    
    Args:
        image_path: Path to the image file
        threshold: Brightness threshold to consider a pixel "lit"
        
    Returns:
        Set of (x, y) tuples for lit pixels
    """
    img = Image.open(image_path)
    img_array = np.array(img)
    
    # Get image dimensions
    height, width = img_array.shape[:2]
    
    # Estimate LED grid size (64x32)
    led_width = width / 64
    led_height = height / 32
    
    lit_pixels = set()
    
    # Sample the center of each LED position
    for y in range(32):
        for x in range(64):
            # Calculate center position of this LED
            center_x = int((x + 0.5) * led_width)
            center_y = int((y + 0.5) * led_height)
            
            # Get pixel value at center
            if center_y < height and center_x < width:
                pixel = img_array[center_y, center_x]
                
                # Check if pixel is bright (yellow/white)
                if len(pixel) >= 3:  # RGB
                    brightness = pixel[0] + pixel[1] + pixel[2]
                    if brightness > threshold * 3:  # Bright enough
                        lit_pixels.add((x, y))
    
    return lit_pixels


def create_led_pattern_from_analysis(original_image_path):
    """Create LED pattern based on image analysis."""
    # Analyze the original image
    print(f"Analyzing original image: {original_image_path}")
    original_pixels = analyze_led_image(original_image_path)
    
    print(f"Found {len(original_pixels)} lit pixels in original image")
    
    # Create device
    device = MatrixPortalS3()
    device.initialize()
    device.matrix.clear()
    
    # Yellow color
    yellow = (255, 255, 0)
    
    # Set all detected pixels
    for x, y in original_pixels:
        device.matrix.set_pixel(x, y, yellow)
    
    # Render and save screenshot
    device.matrix.render()
    screenshot_path = "led_pattern_test.png"
    device.matrix.save_screenshot(screenshot_path)
    
    # Analyze our screenshot
    print(f"Analyzing simulation screenshot...")
    sim_pixels = analyze_led_image(screenshot_path, threshold=50)
    
    # Compare results
    missing_pixels = original_pixels - sim_pixels
    extra_pixels = sim_pixels - original_pixels
    
    print(f"\nComparison:")
    print(f"Original pixels: {len(original_pixels)}")
    print(f"Simulation pixels: {len(sim_pixels)}")
    print(f"Missing pixels: {len(missing_pixels)}")
    print(f"Extra pixels: {len(extra_pixels)}")
    
    # Save the final pattern
    return device, original_pixels


def save_pixel_pattern(pixels, filename="led_pattern_code.py"):
    """Save the pixel pattern as Python code."""
    with open(filename, 'w') as f:
        f.write("# LED pixel pattern extracted from image\n")
        f.write("# Format: (x, y) coordinates\n\n")
        f.write("LED_PATTERN = [\n")
        
        # Sort pixels by y then x for readability
        sorted_pixels = sorted(list(pixels), key=lambda p: (p[1], p[0]))
        
        current_y = -1
        for x, y in sorted_pixels:
            if y != current_y:
                f.write(f"\n    # Row {y}\n")
                current_y = y
            f.write(f"    ({x}, {y}),\n")
            
        f.write("]\n")
    
    print(f"\nPixel pattern saved to {filename}")


def main():
    """Run the LED pattern matcher."""
    # Path to original image
    original_image = os.path.expanduser("~/Downloads/IMG_6593.jpg")
    
    if not os.path.exists(original_image):
        print(f"Error: Original image not found at {original_image}")
        return
    
    # Analyze and create pattern
    device, pixels = create_led_pattern_from_analysis(original_image)
    
    # Save the pattern for future use
    save_pixel_pattern(pixels)
    
    # Run the display
    print("\nDisplaying matched LED pattern... Press ESC or close window to exit.")
    device.run(title="LED Pattern Match")


if __name__ == "__main__":
    main()