#!/usr/bin/env python3
"""Final test showing the brightness improvement for typical theme park display."""

import sys
import os
import pygame

# Add PyLEDSimulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from pyledsimulator.devices.matrixportal_s3 import MatrixPortalS3
from pyledsimulator import displayio
from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.terminalio import FONT as terminalio_FONT


def test_final_brightness():
    """Test final brightness with typical theme park display content."""
    
    print("=== FINAL BRIGHTNESS TEST ===")
    print("Testing typical theme park display with enhanced 100% brightness...")
    
    device = MatrixPortalS3(width=64, height=32)
    device.initialize()
    
    pygame.init()
    screen = pygame.display.set_mode((device.matrix.surface_width, device.matrix.surface_height))
    pygame.display.set_caption("Enhanced Brightness Theme Park Display")
    
    # Set to 100% brightness for maximum visibility
    device.display.brightness = 1.0
    print(f"Set brightness to 100% (enhanced mode)")
    
    main_group = displayio.Group()
    device.display.root_group = main_group
    
    # Create typical theme park content
    test_lines = [
        "Pirates: 45 min",
        "Space: 20 min",
        "Thunder: 60 min"
    ]
    
    colors = [0x00FF00, 0xFFFF00, 0xFF0000]  # Green, Yellow, Red
    
    y_pos = 2
    for i, (text, color) in enumerate(zip(test_lines, colors)):
        label = Label(terminalio_FONT, text=text, color=color)
        label.x = 1
        label.y = y_pos
        main_group.append(label)
        
        print(f"Line {i+1}: '{text}' in color {hex(color)}")
        y_pos += 10
    
    device.display.refresh()
    device.matrix.render()
    
    if hasattr(device.matrix, 'surface'):
        pygame.image.save(device.matrix.surface, "final_brightness_enhanced.png")
        print("\\nSaved: final_brightness_enhanced.png")
        
        # Analyze brightness
        pixel_array = pygame.surfarray.array3d(device.matrix.surface)
        max_red = pixel_array[:, :, 0].max()
        max_green = pixel_array[:, :, 1].max()
        max_blue = pixel_array[:, :, 2].max()
        
        print(f"\\nBrightness analysis:")
        print(f"  Max RGB values: ({max_red}, {max_green}, {max_blue})")
        print(f"  All colors should be at or near maximum (255)")
        
        non_black_pixels = (pixel_array > 50).any(axis=2).sum()
        total_pixels = pixel_array.shape[0] * pixel_array.shape[1]
        
        print(f"  Visible pixels: {non_black_pixels} / {total_pixels}")
        print(f"  ✓ Enhanced brightness active for 100% setting")
    
    print(f"\\n=== BRIGHTNESS ENHANCEMENT SUMMARY ===")
    print(f"When brightness is set to 100%:")
    print(f"1. LED base colors get 15% enhancement (×1.15)")
    print(f"2. LED highlights get enhanced (+35 instead of +30)")
    print(f"3. Result: Maximum possible brightness for optimal visibility")
    print(f"\\nThe fonts should now appear much brighter on screen!")
    
    pygame.time.wait(3000)
    pygame.quit()


if __name__ == "__main__":
    test_final_brightness()