#!/usr/bin/env python3
"""Fixed roller coaster animation with enhanced visibility."""

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
        self.cart_velocity = 0.0  # Speed along track
        self.gravity = 0.3
        self.friction = 0.99  # Slight friction
        self.boost_power = 3.0  # Initial boost at start
        
        # Track the cart sprite position
        self.cart_x = 0
        self.cart_y = 0
        
    def _generate_track(self):
        """Generate roller coaster track points."""
        # Create a loop with hills and valleys
        points = []
        
        # Start from left side, go up
        for x in range(5, 20):
            y = 25 - (x - 5) // 2
            points.append((x, y))
            
        # First big hill
        for x in range(20, 35):
            # Parabolic hill
            t = (x - 27.5) / 7.5
            y = int(15 + 5 * (1 - t * t))  # Make hill less extreme
            y = max(5, min(28, y))  # Clamp to screen bounds
            points.append((x, y))
            
        # Drop down
        for x in range(35, 40):
            y = 18 + (x - 35) * 2
            y = max(5, min(28, y))
            points.append((x, y))
            
        # Small hill
        for x in range(40, 50):
            t = (x - 45) / 5
            y = int(24 - 4 * (1 - t * t))
            y = max(5, min(28, y))
            points.append((x, y))
            
        # Final curve back to start
        for x in range(50, 55):
            y = 20 - (x - 50)
            y = max(5, min(28, y))
            points.append((x, y))
            
        # Bottom return
        for x in range(55, 5, -1):
            points.append((x, 28))
            
        # Close the loop - go back up to start
        for y in range(28, 17, -1):
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
        # Going down increases velocity, going up decreases it
        acceleration = height_diff * self.gravity / 5.0
        
        # Apply boost at the start
        if self.cart_position < 5 and self.cart_velocity < 1.0:
            acceleration += self.boost_power
            
        # Update velocity and position
        self.cart_velocity += acceleration
        self.cart_velocity *= self.friction  # Apply friction
        
        # Limit max speed
        self.cart_velocity = max(-5.0, min(5.0, self.cart_velocity))
        
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
    # Cart shape - make sure it has pixels
    bitmap[0, 0] = 1
    bitmap[1, 0] = 1
    bitmap[2, 0] = 1
    bitmap[0, 1] = 1
    bitmap[2, 1] = 1  # Leave middle bottom transparent for wheels effect
    return bitmap


def create_track_bitmap(width, height, track_points):
    """Create bitmap with track drawn on it."""
    bitmap = Bitmap(width, height, 4)  # 4 colors
    
    # Draw track points
    for x, y in track_points:
        if 0 <= x < width and 0 <= y < height:
            bitmap[x, y] = 1  # Track color
            
    # Add track supports (pillars) every 8 pixels
    for x in range(0, width, 8):
        track_y = None
        # Find track height at this x position
        for tx, ty in track_points:
            if tx == x:
                track_y = ty
                break
                
        if track_y is not None and track_y < height - 2:
            # Draw support pillar from track down to bottom
            for y in range(track_y + 1, height):
                if 0 <= x < width and 0 <= y < height:
                    bitmap[x, y] = 2  # Support color
                    
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
    """Run enhanced roller coaster animation."""
    print("Creating Enhanced Roller Coaster Animation...")
    device = MatrixPortalS3()
    device.initialize()
    
    # Create display groups
    main_group = Group()
    
    # Create roller coaster simulation
    coaster = RollerCoaster(64, 32)
    print(f"Generated track with {len(coaster.track_points)} points")
    
    # Create track bitmap and palette with brighter colors
    track_bitmap = create_track_bitmap(64, 32, coaster.track_points)
    track_palette = Palette(4)
    track_palette[0] = (0, 0, 0)        # Background (black)
    track_palette[1] = (200, 200, 200)  # Track (bright gray)
    track_palette[2] = (100, 100, 100)  # Supports (medium gray)
    track_palette[3] = (255, 255, 0)    # Reserved for effects (yellow)
    
    # Create track tilegrid
    track_grid = TileGrid(track_bitmap, pixel_shader=track_palette)
    main_group.append(track_grid)
    
    # Create cart sprite with brighter colors
    cart_bitmap = create_cart_sprite()
    cart_palette = Palette(2)
    cart_palette[0] = (0, 0, 0)    # Transparent
    cart_palette.make_transparent(0)  # Make index 0 transparent
    cart_palette[1] = (255, 100, 100)  # Bright red cart
    
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
    
    # Add sparkle effects
    sparkle_group = Group()
    main_group.append(sparkle_group)
    
    # Create sparkle sprites
    sparkle_bitmap = Bitmap(1, 1, 2)
    sparkle_bitmap[0, 0] = 1
    
    sparkles = []
    for i in range(8):  # More sparkles
        sparkle_palette = Palette(2)
        sparkle_palette[0] = (0, 0, 0)      # Transparent
        sparkle_palette.make_transparent(0)
        sparkle_palette[1] = (255, 255, 100)  # Bright yellow sparkle
        
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
    print("Animation started! You should see:")
    print("- Gray roller coaster track with hills")
    print("- Red cart moving around the track")
    print("- Yellow sparkles when cart moves fast")
    print("- Pulsing track brightness")
    print("\nPress ESC or close window to exit.")
    
    frame_count = 0
    sparkle_timer = 0
    
    def update():
        """Update animation."""
        nonlocal frame_count, sparkle_timer
        
        # Update roller coaster physics
        coaster.update_cart()
        
        # Update cart sprite position
        cart_sprite.x = max(0, min(61, coaster.cart_x - 1))  # Clamp to screen
        cart_sprite.y = max(0, min(30, coaster.cart_y - 1))
        
        # Animate cart color based on speed
        speed_factor = min(1.0, abs(coaster.cart_velocity) / 3.0)
        if speed_factor > 0.3:
            # High speed: bright yellow-red
            hue = 60 - speed_factor * 60  # Yellow to red
            r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
            cart_palette[1] = (r, g, b)
        else:
            # Low speed: red
            cart_palette[1] = (255, 100, 100)
        
        # Create sparkles when cart is moving fast
        if speed_factor > 0.5 and sparkle_timer <= 0:
            # Find an inactive sparkle
            for sparkle_data in sparkles:
                if sparkle_data['life'] <= 0:
                    sparkle_data['life'] = 30  # Longer life
                    sparkle_data['x'] = float(coaster.cart_x)
                    sparkle_data['y'] = float(coaster.cart_y)
                    # Random sparkle direction
                    angle = (frame_count * 47) % 360  # Pseudo-random
                    sparkle_data['vx'] = math.cos(math.radians(angle)) * 0.5
                    sparkle_data['vy'] = math.sin(math.radians(angle)) * 0.5 - 0.2  # Slight upward bias
                    sparkle_timer = 5
                    break
                    
        sparkle_timer = max(0, sparkle_timer - 1)
        
        # Update sparkles
        for sparkle_data in sparkles:
            if sparkle_data['life'] > 0:
                sparkle_data['life'] -= 1
                sparkle_data['x'] += sparkle_data['vx']
                sparkle_data['y'] += sparkle_data['vy']
                sparkle_data['vy'] += 0.05  # Gravity
                
                # Update sprite position
                sx = int(sparkle_data['x'])
                sy = int(sparkle_data['y'])
                sparkle_data['sprite'].x = max(-10, min(70, sx))
                sparkle_data['sprite'].y = max(-10, min(40, sy))
                
                # Fade out
                brightness = sparkle_data['life'] / 30.0
                color_val = int(255 * brightness)
                sparkle_data['sprite'].pixel_shader[1] = (color_val, color_val, 0)
            else:
                # Hide inactive sparkles
                sparkle_data['sprite'].x = -10
                sparkle_data['sprite'].y = -10
                
        # Pulse track color
        pulse = (math.sin(frame_count * 0.1) + 1) * 0.5
        gray = int(150 + 50 * pulse)  # Brighter pulsing
        track_palette[1] = (gray, gray, gray)
        
        frame_count += 1
        
        # Print debug info occasionally
        if frame_count % 120 == 0:  # Every 2 seconds
            print(f"Cart at ({coaster.cart_x}, {coaster.cart_y}), speed: {coaster.cart_velocity:.1f}")
    
    # Run the simulation
    device.run(update_callback=update, title="Enhanced Roller Coaster Animation")


if __name__ == "__main__":
    main()