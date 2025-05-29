#!/usr/bin/env python3
"""Take a live screenshot of the running animation."""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3
from pyledsimulator.displayio import Group, TileGrid, Bitmap, Palette
from roller_coaster_final import RollerCoaster, create_cart_sprite, create_track_bitmap, hsv_to_rgb
import math


def capture_live_animation():
    """Capture the animation exactly as it's running."""
    print("📸 Capturing LIVE roller coaster animation...")
    
    device = MatrixPortalS3()
    device.initialize()
    
    # Set up animation exactly like the running version
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
    
    # Create sparkles
    sparkle_group = Group()
    main_group.append(sparkle_group)
    
    sparkle_bitmap = Bitmap(1, 1, 2)
    sparkle_bitmap[0, 0] = 1
    
    sparkles = []
    for i in range(10):
        sparkle_palette = Palette(2)
        sparkle_palette[0] = (0, 0, 0)
        sparkle_palette.make_transparent(0)
        sparkle_palette[1] = (255, 255, 150)
        
        sparkle_sprite = TileGrid(
            sparkle_bitmap,
            pixel_shader=sparkle_palette,
            x=-10,
            y=-10
        )
        sparkle_group.append(sparkle_sprite)
        sparkles.append({
            'sprite': sparkle_sprite,
            'life': 0,
            'vx': 0,
            'vy': 0,
            'x': 0.0,
            'y': 0.0
        })
    
    device.show(main_group)
    
    # Run animation for a realistic amount of time
    frame_count = 0
    sparkle_timer = 0
    
    # Simulate 3 seconds of animation (180 frames at 60fps)
    for _ in range(180):
        # Update physics
        coaster.update_cart()
        
        # Update cart position
        cart_sprite.x = max(0, min(61, coaster.cart_x - 1))
        cart_sprite.y = max(0, min(30, coaster.cart_y - 1))
        
        # Dynamic cart color based on speed
        speed_factor = min(1.0, abs(coaster.cart_velocity) / 4.0)
        if speed_factor > 0.4:
            hue = 60 - speed_factor * 60
            r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
            cart_palette[1] = (r, g, b)
        else:
            cart_palette[1] = (255, 80, 80)
        
        # Enhanced sparkle effects
        if speed_factor > 0.6 and sparkle_timer <= 0:
            for sparkle_data in sparkles:
                if sparkle_data['life'] <= 0:
                    sparkle_data['life'] = 40
                    sparkle_data['x'] = float(coaster.cart_x)
                    sparkle_data['y'] = float(coaster.cart_y)
                    angle = (frame_count * 73) % 360
                    speed = 0.3 + speed_factor * 0.4
                    sparkle_data['vx'] = math.cos(math.radians(angle)) * speed
                    sparkle_data['vy'] = math.sin(math.radians(angle)) * speed - 0.1
                    sparkle_timer = 3
                    break
                    
        sparkle_timer = max(0, sparkle_timer - 1)
        
        # Update sparkles
        for sparkle_data in sparkles:
            if sparkle_data['life'] > 0:
                sparkle_data['life'] -= 1
                sparkle_data['x'] += sparkle_data['vx']
                sparkle_data['y'] += sparkle_data['vy']
                sparkle_data['vy'] += 0.03
                
                sx = max(-10, min(70, int(sparkle_data['x'])))
                sy = max(-10, min(40, int(sparkle_data['y'])))
                sparkle_data['sprite'].x = sx
                sparkle_data['sprite'].y = sy
                
                brightness = sparkle_data['life'] / 40.0
                yellow = int(255 * brightness)
                sparkle_data['sprite'].pixel_shader[1] = (yellow, yellow, yellow // 2)
            else:
                sparkle_data['sprite'].x = -10
                sparkle_data['sprite'].y = -10
        
        # Animated track brightness
        pulse = (math.sin(frame_count * 0.08) + 1) * 0.5
        gray = int(180 + 40 * pulse)
        track_palette[1] = (gray, gray, gray)
        
        frame_count += 1
        device.display.refresh()
    
    # Take the screenshot
    screenshot_path = "/Users/czei/Projects/Disney/ThemeParkAPI/PyLEDSimulator/live_animation_capture.png"
    device.save_screenshot(screenshot_path)
    
    print(f"✅ LIVE CAPTURE COMPLETE!")
    print(f"📸 Screenshot saved: live_animation_capture.png")
    print(f"🎯 Final state: Cart at ({coaster.cart_x}, {coaster.cart_y}), Speed: {coaster.cart_velocity:.1f}")
    print(f"🎬 Frames processed: {frame_count}")
    print(f"⚡ This shows exactly what your animation looks like when running!")
    
    return screenshot_path


if __name__ == "__main__":
    capture_live_animation()