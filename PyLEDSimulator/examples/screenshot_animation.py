#!/usr/bin/env python3
"""View the roller coaster animation through automatic screenshots."""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from roller_coaster_final import main as run_roller_coaster
from pyledsimulator.devices import MatrixPortalS3
from pyledsimulator.displayio import Group, TileGrid, Bitmap, Palette
from roller_coaster_final import RollerCoaster, create_cart_sprite, create_track_bitmap, hsv_to_rgb
import math


def create_animation_screenshots():
    """Create a series of screenshots showing the animation."""
    print("🎬 Creating Roller Coaster Animation Screenshots...")
    print("   (Since the pygame window isn't visible in this environment)")
    
    device = MatrixPortalS3()
    device.initialize()
    
    # Set up the animation exactly like the final version
    main_group = Group()
    coaster = RollerCoaster(64, 32)
    
    # Create track
    track_bitmap = create_track_bitmap(64, 32, coaster.track_points)
    track_palette = Palette(4)
    track_palette[0] = (0, 0, 0)        # Background
    track_palette[1] = (220, 220, 220)  # Bright track
    track_palette[2] = (120, 120, 120)  # Support pillars
    track_palette[3] = (255, 255, 100)  # Effects
    
    track_grid = TileGrid(track_bitmap, pixel_shader=track_palette)
    main_group.append(track_grid)
    
    # Create cart
    cart_bitmap = create_cart_sprite()
    cart_palette = Palette(2)
    cart_palette[0] = (0, 0, 0)
    cart_palette.make_transparent(0)
    cart_palette[1] = (255, 80, 80)
    
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
    
    device.show(main_group)
    
    # Create 10 screenshots at different points
    screenshots = []
    frame_count = 0
    
    for screenshot_num in range(10):
        # Run animation for 30 frames
        for _ in range(30):
            # Update physics
            coaster.update_cart()
            
            # Update cart position
            cart_sprite.x = max(0, min(61, coaster.cart_x - 1))
            cart_sprite.y = max(0, min(30, coaster.cart_y - 1))
            
            # Dynamic cart color
            speed_factor = min(1.0, abs(coaster.cart_velocity) / 4.0)
            if speed_factor > 0.4:
                hue = 60 - speed_factor * 60
                r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
                cart_palette[1] = (r, g, b)
            else:
                cart_palette[1] = (255, 80, 80)
            
            # Animated track brightness
            pulse = (math.sin(frame_count * 0.08) + 1) * 0.5
            gray = int(180 + 40 * pulse)
            track_palette[1] = (gray, gray, gray)
            
            frame_count += 1
            device.display.refresh()
        
        # Take screenshot
        screenshot_path = f"/Users/czei/Projects/Disney/ThemeParkAPI/PyLEDSimulator/animation_sequence_{screenshot_num:02d}.png"
        device.save_screenshot(screenshot_path)
        screenshots.append(screenshot_path)
        
        print(f"📸 Frame {screenshot_num:2d}: Cart at ({coaster.cart_x:2d},{coaster.cart_y:2d}) Speed: {coaster.cart_velocity:+.1f}")
    
    print(f"\n✅ Created {len(screenshots)} animation screenshots!")
    print("🎯 Each screenshot shows the cart at a different position on the roller coaster.")
    print("📁 Files saved as: animation_sequence_00.png through animation_sequence_09.png")
    
    return screenshots


if __name__ == "__main__":
    create_animation_screenshots()