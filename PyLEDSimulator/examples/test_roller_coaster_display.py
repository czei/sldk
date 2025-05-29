#!/usr/bin/env python3
"""Test roller coaster display without infinite loop."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3
from pyledsimulator.displayio import Group, TileGrid, Bitmap, Palette
from roller_coaster_animation import RollerCoaster, create_cart_sprite, create_track_bitmap


def main():
    """Test roller coaster display for a few frames."""
    print("Testing roller coaster display...")
    device = MatrixPortalS3()
    device.initialize()
    
    # Create display groups
    main_group = Group()
    
    # Create roller coaster simulation
    coaster = RollerCoaster(64, 32)
    
    # Create track bitmap and palette
    track_bitmap = create_track_bitmap(64, 32, coaster.track_points)
    track_palette = Palette(4)
    track_palette[0] = (0, 0, 0)      # Background (black)
    track_palette[1] = (128, 128, 128)  # Track (gray)
    track_palette[2] = (64, 64, 64)     # Supports (dark gray)
    track_palette[3] = (255, 0, 0)      # Reserved for effects
    
    # Create track tilegrid
    track_grid = TileGrid(track_bitmap, pixel_shader=track_palette)
    main_group.append(track_grid)
    
    # Create cart sprite
    cart_bitmap = create_cart_sprite()
    cart_palette = Palette(2)
    cart_palette[0] = (0, 0, 0)    # Transparent
    cart_palette[1] = (255, 0, 0)  # Cart (red)
    
    cart_sprite = TileGrid(
        cart_bitmap,
        pixel_shader=cart_palette,
        width=1,
        height=1,
        tile_width=3,
        tile_height=2,
        x=0,
        y=0
    )
    main_group.append(cart_sprite)
    
    # Show on display
    device.show(main_group)
    
    print("Testing animation for 10 frames...")
    
    # Test animation for a few frames
    for frame in range(10):
        # Update roller coaster physics
        coaster.update_cart()
        
        # Update cart sprite position
        cart_sprite.x = coaster.cart_x - 1
        cart_sprite.y = coaster.cart_y - 1
        
        print(f"Frame {frame}: Cart at ({coaster.cart_x}, {coaster.cart_y}), sprite at ({cart_sprite.x}, {cart_sprite.y})")
        
        # Force display refresh
        device.display.refresh()
    
    print("Display test complete! The track and cart should be visible.")
    print("Run roller_coaster_animation.py for the full interactive animation.")


if __name__ == "__main__":
    main()