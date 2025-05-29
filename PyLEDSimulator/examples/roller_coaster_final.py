#!/usr/bin/env python3
"""Final polished roller coaster animation with perfect physics."""

import sys
import os
import math
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3
from pyledsimulator.displayio import Group, TileGrid, Bitmap, Palette


class RollerCoaster:
    """Roller coaster track and cart physics simulation."""
    
    def __init__(self, width=64, height=32):
        self.width = width
        self.height = height
        
        # Track points - create a fun roller coaster path
        self.track_points = []
        self._generate_track()
        
        # Cart physics
        self.cart_position = 0.0  # Position along track (0 to len(track_points))
        self.cart_velocity = 2.0  # Start with some speed
        self.gravity = 0.4
        self.friction = 0.995  # Very slight friction
        self.min_speed = 0.3  # Minimum speed to prevent getting stuck
        
        # Track the cart sprite position
        self.cart_x = 0
        self.cart_y = 0
        
    def _generate_track(self):
        """Generate roller coaster track points."""
        points = []
        
        # Start from left side, gradual climb
        for x in range(5, 18):
            y = 26 - (x - 5) // 2
            points.append((x, y))
            
        # Big hill with smoother curve
        for x in range(18, 32):
            t = (x - 25) / 7.0
            y = int(16 + 6 * (1 - t * t))
            y = max(8, min(26, y))
            points.append((x, y))
            
        # Fast drop
        for x in range(32, 38):
            y = 16 + (x - 32) * 2
            y = max(8, min(26, y))
            points.append((x, y))
            
        # Small hill
        for x in range(38, 48):
            t = (x - 43) / 5.0
            y = int(24 - 3 * (1 - t * t))
            y = max(8, min(26, y))
            points.append((x, y))
            
        # Gentle curve to flat
        for x in range(48, 55):
            y = 22 - (x - 48) // 2
            y = max(8, min(26, y))
            points.append((x, y))
            
        # Bottom straight section
        for x in range(55, 5, -1):
            points.append((x, 26))
            
        # Close the loop - climb back up
        for y in range(26, 19, -1):
            points.append((5, y))
            
        self.track_points = points
        
    def update_cart(self):
        """Update cart position based on physics."""
        if len(self.track_points) < 2:
            return
            
        # Get current and next track positions
        current_idx = int(self.cart_position) % len(self.track_points)
        next_idx = (current_idx + 1) % len(self.track_points)
        
        # Calculate slope between current and next point
        x1, y1 = self.track_points[current_idx]
        x2, y2 = self.track_points[next_idx]
        
        # Height difference (positive = going down)
        height_diff = y2 - y1
        
        # Apply gravity based on slope
        acceleration = height_diff * self.gravity / 8.0
        
        # Update velocity and position
        self.cart_velocity += acceleration
        self.cart_velocity *= self.friction
        
        # Ensure minimum speed to prevent getting stuck
        if abs(self.cart_velocity) < self.min_speed:
            self.cart_velocity = self.min_speed if self.cart_velocity >= 0 else -self.min_speed
        
        # Limit max speed
        self.cart_velocity = max(-6.0, min(6.0, self.cart_velocity))
        
        # Update position
        self.cart_position += self.cart_velocity
        
        # Wrap around track
        if self.cart_position >= len(self.track_points):
            self.cart_position -= len(self.track_points)
        elif self.cart_position < 0:
            self.cart_position += len(self.track_points)
            
        # Interpolate cart position
        t = self.cart_position - current_idx
        if t < 0:
            t = 0
        elif t > 1:
            t = 1
            
        self.cart_x = int(x1 + (x2 - x1) * t)
        self.cart_y = int(y1 + (y2 - y1) * t)


def create_cart_sprite():
    """Create a cart sprite bitmap (3x2 pixels)."""
    bitmap = Bitmap(3, 2, 2)
    # Cart shape
    bitmap[0, 0] = 1
    bitmap[1, 0] = 1
    bitmap[2, 0] = 1
    bitmap[0, 1] = 1
    bitmap[2, 1] = 1
    return bitmap


def create_track_bitmap(width, height, track_points):
    """Create bitmap with track drawn on it."""
    bitmap = Bitmap(width, height, 4)
    
    # Draw track points
    for x, y in track_points:
        if 0 <= x < width and 0 <= y < height:
            bitmap[x, y] = 1
            
    # Add track supports every 6 pixels
    for x in range(6, width, 6):
        track_y = None
        for tx, ty in track_points:
            if tx == x:
                track_y = ty
                break
                
        if track_y is not None and track_y < height - 2:
            for y in range(track_y + 1, height):
                if 0 <= x < width and 0 <= y < height:
                    bitmap[x, y] = 2
                    
    return bitmap


def hsv_to_rgb(h, s, v):
    """Convert HSV to RGB color."""
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
        
    return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))


def main():
    """Run final roller coaster animation."""
    print("🎢 ROLLER COASTER ANIMATION 🎢")
    print("==============================")
    device = MatrixPortalS3()
    device.initialize()
    
    # Create display groups
    main_group = Group()
    
    # Create roller coaster simulation
    coaster = RollerCoaster(64, 32)
    print(f"✓ Generated track with {len(coaster.track_points)} points")
    
    # Create track with bright, visible colors
    track_bitmap = create_track_bitmap(64, 32, coaster.track_points)
    track_palette = Palette(4)
    track_palette[0] = (0, 0, 0)        # Background
    track_palette[1] = (220, 220, 220)  # Bright track
    track_palette[2] = (120, 120, 120)  # Support pillars
    track_palette[3] = (255, 255, 100)  # Effects
    
    track_grid = TileGrid(track_bitmap, pixel_shader=track_palette)
    main_group.append(track_grid)
    
    # Create bright cart
    cart_bitmap = create_cart_sprite()
    cart_palette = Palette(2)
    cart_palette[0] = (0, 0, 0)
    cart_palette.make_transparent(0)
    cart_palette[1] = (255, 80, 80)  # Bright red
    
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
    
    # Create sparkle effects
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
    
    # Show on display
    device.show(main_group)
    
    print("✓ Animation ready!")
    print("\n🎯 What you should see:")
    print("  • Bright gray roller coaster track with hills")
    print("  • Red cart moving smoothly around the track")
    print("  • Cart speeds up downhill, slows uphill")
    print("  • Yellow sparkles when moving fast")
    print("  • Pulsing track brightness")
    print("\n⌨️  Press ESC or close window to exit")
    print("\n📊 Performance data:")
    
    frame_count = 0
    sparkle_timer = 0
    last_print_time = time.time()
    
    def update():
        """Update animation with enhanced effects."""
        nonlocal frame_count, sparkle_timer, last_print_time
        
        # Update physics
        coaster.update_cart()
        
        # Update cart position with bounds checking
        cart_sprite.x = max(0, min(61, coaster.cart_x - 1))
        cart_sprite.y = max(0, min(30, coaster.cart_y - 1))
        
        # Dynamic cart color based on speed
        speed_factor = min(1.0, abs(coaster.cart_velocity) / 4.0)
        if speed_factor > 0.4:
            # Fast: red to yellow gradient
            hue = 60 - speed_factor * 60
            r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
            cart_palette[1] = (r, g, b)
        else:
            # Slow: bright red
            cart_palette[1] = (255, 80, 80)
        
        # Enhanced sparkle effects
        if speed_factor > 0.6 and sparkle_timer <= 0:
            for sparkle_data in sparkles:
                if sparkle_data['life'] <= 0:
                    sparkle_data['life'] = 40
                    sparkle_data['x'] = float(coaster.cart_x)
                    sparkle_data['y'] = float(coaster.cart_y)
                    # Create sparkle burst pattern
                    angle = (frame_count * 73) % 360
                    speed = 0.3 + speed_factor * 0.4
                    sparkle_data['vx'] = math.cos(math.radians(angle)) * speed
                    sparkle_data['vy'] = math.sin(math.radians(angle)) * speed - 0.1
                    sparkle_timer = 3
                    break
                    
        sparkle_timer = max(0, sparkle_timer - 1)
        
        # Update sparkles with physics
        for sparkle_data in sparkles:
            if sparkle_data['life'] > 0:
                sparkle_data['life'] -= 1
                sparkle_data['x'] += sparkle_data['vx']
                sparkle_data['y'] += sparkle_data['vy']
                sparkle_data['vy'] += 0.03  # Gentle gravity
                
                # Position sprite
                sx = max(-10, min(70, int(sparkle_data['x'])))
                sy = max(-10, min(40, int(sparkle_data['y'])))
                sparkle_data['sprite'].x = sx
                sparkle_data['sprite'].y = sy
                
                # Fade sparkle
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
        
        # Print status every 3 seconds
        current_time = time.time()
        if current_time - last_print_time >= 3.0:
            print(f"🏎️  Cart: ({coaster.cart_x:2d},{coaster.cart_y:2d}) Speed: {coaster.cart_velocity:+.1f} Frame: {frame_count}")
            last_print_time = current_time
    
    # Run the animation
    device.run(update_callback=update, title="🎢 Roller Coaster Animation 🎢")


if __name__ == "__main__":
    main()