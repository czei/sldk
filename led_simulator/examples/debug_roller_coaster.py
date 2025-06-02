#!/usr/bin/env python3
"""Debug version of roller coaster animation with screenshots."""

import sys
import os
import math
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3
from pyledsimulator.displayio import Group, TileGrid, Bitmap, Palette
from roller_coaster_animation import RollerCoaster, create_cart_sprite, create_track_bitmap


def debug_bitmap_contents(bitmap, name):
    """Debug bitmap contents."""
    print(f"\n=== {name} Bitmap Debug ===")
    print(f"Size: {bitmap.width}x{bitmap.height}, values: {bitmap.value_count}")
    
    non_zero_pixels = 0
    for y in range(min(10, bitmap.height)):  # Check first 10 rows
        row_pixels = []
        for x in range(min(20, bitmap.width)):  # Check first 20 columns
            value = bitmap[x, y]
            row_pixels.append(str(value))
            if value != 0:
                non_zero_pixels += 1
        if any(p != '0' for p in row_pixels):
            print(f"Row {y}: {' '.join(row_pixels)}")
    
    print(f"Non-zero pixels found: {non_zero_pixels}")


def debug_palette_contents(palette, name):
    """Debug palette contents."""
    print(f"\n=== {name} Palette Debug ===")
    for i in range(len(palette)):
        color = palette[i]
        rgb = palette.get_rgb888(i)
        transparent = palette.is_transparent(i)
        print(f"Index {i}: {color:04X} -> RGB{rgb} {'(transparent)' if transparent else ''}")


def main():
    """Debug roller coaster rendering."""
    print("Creating MatrixPortal S3 for debug...")
    device = MatrixPortalS3()
    device.initialize()
    
    # Create roller coaster simulation
    coaster = RollerCoaster(64, 32)
    print(f"Track has {len(coaster.track_points)} points")
    print(f"First 10 track points: {coaster.track_points[:10]}")
    
    # Test track bitmap creation
    print("\nCreating track bitmap...")
    track_bitmap = create_track_bitmap(64, 32, coaster.track_points)
    debug_bitmap_contents(track_bitmap, "Track")
    
    # Test track palette
    track_palette = Palette(4)
    track_palette[0] = (0, 0, 0)        # Background (black)
    track_palette[1] = (128, 128, 128)  # Track (gray)
    track_palette[2] = (64, 64, 64)     # Supports (dark gray)
    track_palette[3] = (255, 0, 0)      # Reserved for effects
    debug_palette_contents(track_palette, "Track")
    
    # Test cart bitmap
    print("\nCreating cart bitmap...")
    cart_bitmap = create_cart_sprite()
    debug_bitmap_contents(cart_bitmap, "Cart")
    
    # Test cart palette
    cart_palette = Palette(2)
    cart_palette[0] = (0, 0, 0)    # Transparent
    cart_palette.make_transparent(0)
    cart_palette[1] = (255, 0, 0)  # Cart (red)
    debug_palette_contents(cart_palette, "Cart")
    
    # Create display groups
    main_group = Group()
    
    # Create track tilegrid
    track_grid = TileGrid(track_bitmap, pixel_shader=track_palette)
    main_group.append(track_grid)
    print(f"Track grid position: ({track_grid.x}, {track_grid.y})")
    
    # Position cart at a known location
    coaster.cart_x = 25
    coaster.cart_y = 15
    
    cart_sprite = TileGrid(
        cart_bitmap,
        pixel_shader=cart_palette,
        width=1,
        height=1,
        tile_width=3,
        tile_height=2,
        x=coaster.cart_x - 1,
        y=coaster.cart_y - 1
    )
    main_group.append(cart_sprite)
    print(f"Cart sprite position: ({cart_sprite.x}, {cart_sprite.y})")
    
    # Show on display
    device.show(main_group)
    print(f"\nDisplay root group has {len(main_group)} items")
    
    # Take initial screenshot
    print("\nTaking initial screenshot...")
    device.display.refresh()
    
    # Save screenshot 
    screenshot_path = "/Users/czei/Projects/Disney/ThemeParkAPI/PyLEDSimulator/debug_roller_coaster_screenshot.png"
    try:
        device.save_screenshot(screenshot_path)
        print(f"Screenshot saved to: {screenshot_path}")
    except Exception as e:
        print(f"Could not save screenshot: {e}")
    
    # Test a few animation frames
    print("\nTesting animation frames...")
    for frame in range(5):
        coaster.update_cart()
        cart_sprite.x = coaster.cart_x - 1
        cart_sprite.y = coaster.cart_y - 1
        
        print(f"Frame {frame}: Cart at ({coaster.cart_x}, {coaster.cart_y}), sprite at ({cart_sprite.x}, {cart_sprite.y})")
        
        device.display.refresh()
        
        # Save frame screenshot
        frame_path = f"/Users/czei/Projects/Disney/ThemeParkAPI/PyLEDSimulator/debug_frame_{frame}.png"
        try:
            device.save_screenshot(frame_path)
            print(f"Frame {frame} screenshot saved to: {frame_path}")
        except Exception as e:
            print(f"Could not save frame {frame} screenshot: {e}")
        
        time.sleep(0.1)
    
    print("\nDebug complete. Check the screenshot files to see if anything is rendered.")


if __name__ == "__main__":
    main()