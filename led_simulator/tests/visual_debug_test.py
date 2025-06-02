#!/usr/bin/env python3
"""Visual debugging test to verify rendering is working."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from pyledsimulator.devices import MatrixPortalS3
from pyledsimulator.displayio import Group, Bitmap, Palette, TileGrid
from pyledsimulator.adafruit_display_text import Label
from pyledsimulator.terminalio import FONT


def save_display_screenshot(display, filename):
    """Save a screenshot of the display's LED matrix."""
    matrix = display.get_matrix()
    matrix.render()
    surface = matrix.get_surface()
    if surface:
        pygame.image.save(surface, filename)
        print(f"Saved screenshot: {filename}")
        
        # Also print some pixel values for debugging
        pixels = pygame.surfarray.array3d(surface)
        print(f"Surface size: {surface.get_size()}")
        print(f"Pixel array shape: {pixels.shape}")
        print(f"Sample pixels:")
        print(f"  (0,0): {pixels[0, 0]}")
        print(f"  (10,10): {pixels[10, 10] if pixels.shape[0] > 10 else 'N/A'}")


def test_simple_pixels():
    """Test rendering simple pixels."""
    print("\n=== Testing Simple Pixels ===")
    
    device = MatrixPortalS3()
    device.initialize()
    
    # Set some pixels directly on the matrix
    matrix = device.display.get_matrix()
    matrix.set_pixel(0, 0, (255, 0, 0))  # Red
    matrix.set_pixel(10, 5, (0, 255, 0))  # Green
    matrix.set_pixel(20, 10, (0, 0, 255))  # Blue
    
    # Render and save
    matrix.render()
    save_display_screenshot(device.display, "debug_simple_pixels.png")


def test_bitmap_rendering():
    """Test rendering through displayio."""
    print("\n=== Testing Bitmap Rendering ===")
    
    device = MatrixPortalS3()
    device.initialize()
    
    # Create a simple bitmap
    bitmap = Bitmap(10, 10, 2)
    for i in range(10):
        bitmap[i, i] = 1  # Diagonal line
        
    palette = Palette(2)
    palette[0] = 0x000000  # Black
    palette[1] = 0xFFFF00  # Yellow
    
    tilegrid = TileGrid(bitmap, pixel_shader=palette, x=5, y=5)
    
    # Show and render
    device.display.show(tilegrid)
    device.display.refresh()
    
    save_display_screenshot(device.display, "debug_bitmap.png")


def test_label_rendering():
    """Test label rendering."""
    print("\n=== Testing Label Rendering ===")
    
    device = MatrixPortalS3()
    device.initialize()
    
    # Create a simple label
    label = Label(
        font=FONT,
        text="TEST",
        color=0x00FF00,  # Green
        x=5,
        y=16
    )
    
    # Show the label
    device.display.show(label)
    device.display.refresh()
    
    # Debug: Check if label has content
    print(f"Label text: {label.text}")
    print(f"Label color: {label.color}")
    print(f"Label position: ({label.x}, {label.y})")
    print(f"Label has bitmap: {label._bitmap is not None}")
    print(f"Label has tilegrid: {label._tilegrid is not None}")
    
    if label._bitmap:
        print(f"Label bitmap size: {label._bitmap.width}x{label._bitmap.height}")
        # Check some bitmap pixels
        for y in range(min(5, label._bitmap.height)):
            for x in range(min(10, label._bitmap.width)):
                val = label._bitmap[x, y]
                if val > 0:
                    print(f"  Bitmap pixel ({x},{y}) = {val}")
    
    save_display_screenshot(device.display, "debug_label.png")


def test_group_rendering():
    """Test group rendering."""
    print("\n=== Testing Group Rendering ===")
    
    device = MatrixPortalS3()
    device.initialize()
    
    # Create a group with multiple items
    main_group = Group()
    
    # Add background
    bg_bitmap = Bitmap(64, 32, 2)
    bg_bitmap.fill(1)
    bg_palette = Palette(2)
    bg_palette[0] = 0x000000
    bg_palette[1] = 0x000080  # Dark blue
    main_group.append(TileGrid(bg_bitmap, pixel_shader=bg_palette))
    
    # Add some colored squares
    for i, color in enumerate([0xFF0000, 0x00FF00, 0x0000FF]):
        bitmap = Bitmap(8, 8, 2)
        bitmap.fill(1)
        palette = Palette(2)
        palette[0] = 0x000000
        palette[1] = color
        tilegrid = TileGrid(bitmap, pixel_shader=palette, x=10 + i*15, y=12)
        main_group.append(tilegrid)
    
    # Show and render
    device.display.show(main_group)
    device.display.refresh()
    
    save_display_screenshot(device.display, "debug_group.png")


def main():
    """Run all visual debugging tests."""
    pygame.init()
    
    try:
        test_simple_pixels()
        test_bitmap_rendering()
        test_label_rendering()
        test_group_rendering()
        
        print("\n=== Visual Debug Complete ===")
        print("Check the generated PNG files to see the rendered output.")
        
    except Exception as e:
        print(f"\nError during visual debugging: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()