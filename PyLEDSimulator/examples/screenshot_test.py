#!/usr/bin/env python3
"""Quick screenshot of current animation state."""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3
from pyledsimulator.displayio import Group, TileGrid, Bitmap, Palette
from roller_coaster_fixed import RollerCoaster, create_cart_sprite, create_track_bitmap


def main():
    """Take a quick screenshot."""
    device = MatrixPortalS3()
    device.initialize()
    
    # Create display
    main_group = Group()
    coaster = RollerCoaster(64, 32)
    
    # Create track
    track_bitmap = create_track_bitmap(64, 32, coaster.track_points)
    track_palette = Palette(4)
    track_palette[0] = (0, 0, 0)        # Background
    track_palette[1] = (200, 200, 200)  # Track
    track_palette[2] = (100, 100, 100)  # Supports
    track_palette[3] = (255, 255, 0)    # Effects
    
    track_grid = TileGrid(track_bitmap, pixel_shader=track_palette)
    main_group.append(track_grid)
    
    # Create cart
    cart_bitmap = create_cart_sprite()
    cart_palette = Palette(2)
    cart_palette[0] = (0, 0, 0)
    cart_palette.make_transparent(0)
    cart_palette[1] = (255, 100, 100)
    
    # Update cart position for several frames
    for _ in range(20):
        coaster.update_cart()
    
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
    
    device.show(main_group)
    device.display.refresh()
    time.sleep(0.1)
    
    # Save screenshot
    screenshot_path = "/Users/czei/Projects/Disney/ThemeParkAPI/PyLEDSimulator/current_animation_state.png"
    device.save_screenshot(screenshot_path)
    print(f"Screenshot saved: {screenshot_path}")
    print(f"Cart position: ({coaster.cart_x}, {coaster.cart_y})")
    print(f"Cart velocity: {coaster.cart_velocity}")
    print(f"Cart track position: {coaster.cart_position}")


if __name__ == "__main__":
    main()