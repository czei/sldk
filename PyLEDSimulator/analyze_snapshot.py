#!/usr/bin/env python3
"""Analyze the snapshot to see what's being rendered."""

from PIL import Image
import numpy as np
from collections import Counter

# Load the image
img = Image.open("hello_led_snapshot.png")
pixels = np.array(img)

print(f"Image size: {img.size}")
print(f"Pixel array shape: {pixels.shape}")

# Get unique colors
unique_colors = set()
for y in range(pixels.shape[0]):
    for x in range(pixels.shape[1]):
        color = tuple(pixels[y, x][:3])  # RGB only
        unique_colors.add(color)

print(f"\nFound {len(unique_colors)} unique colors")

# Sort by brightness and show top colors
sorted_colors = sorted(unique_colors, key=lambda c: sum(c), reverse=True)
print("\nTop 10 brightest colors:")
for i, color in enumerate(sorted_colors[:10]):
    print(f"  {i+1}. RGB{color}")

# Count pixels by color
color_counts = Counter()
for y in range(pixels.shape[0]):
    for x in range(pixels.shape[1]):
        color = tuple(pixels[y, x][:3])
        color_counts[color] += 1

print("\nTop 10 most common colors:")
for color, count in color_counts.most_common(10):
    percentage = (count / (pixels.shape[0] * pixels.shape[1])) * 100
    print(f"  RGB{color}: {count} pixels ({percentage:.1f}%)")

# Look for specific color ranges
print("\nColor analysis:")
red_like = 0
green_like = 0
yellow_like = 0

for y in range(pixels.shape[0]):
    for x in range(pixels.shape[1]):
        r, g, b = pixels[y, x][:3]
        
        # Red-like: high red, low green and blue
        if r > 150 and g < 100 and b < 100:
            red_like += 1
            
        # Green-like: high green, low red and blue  
        if g > 150 and r < 100 and b < 100:
            green_like += 1
            
        # Yellow-like: high red and green, low blue
        if r > 150 and g > 150 and b < 100:
            yellow_like += 1

print(f"Red-like pixels: {red_like}")
print(f"Green-like pixels: {green_like}")
print(f"Yellow-like pixels: {yellow_like}")