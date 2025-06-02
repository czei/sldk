#!/usr/bin/env python3
"""Roller coaster animation using sprites for PyLEDSimulator."""

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
        # Format: list of (x, y) tuples forming the track
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
            points.append((x, y))
            
        # Small hill
        for x in range(40, 50):
            t = (x - 45) / 5
            y = int(24 - 4 * (1 - t * t))
            points.append((x, y))
            
        # Final curve back to start
        for x in range(50, 55):
            y = 20 - (x - 50)
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
        self.cart_x = int(x1 + (x2 - x1) * t)
        self.cart_y = int(y1 + (y2 - y1) * t)
        
    def get_track_height_at(self, x):
        """Get track height at given x position for effects."""
        for tx, ty in self.track_points:
            if tx == x:
                return ty
        return None


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
    bitmap = Bitmap(width, height, 4)  # 4 colors
    
    # Draw track
    for x, y in track_points:
        if 0 <= x < width and 0 <= y < height:
            bitmap[x, y] = 1  # Track color
            
    # Add track supports (pillars)
    for x in range(0, width, 8):
        track_y = None
        for tx, ty in track_points:
            if tx == x:
                track_y = ty
                break
                
        if track_y is not None and track_y < height - 2:
            # Draw support pillar
            for y in range(track_y + 1, height):
                if y < height:
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


def main(test_mode=False):
    """Run roller coaster animation."""
    print("Creating MatrixPortal S3 for roller coaster animation...")
    device = MatrixPortalS3()
    device.initialize()
    
    # Create display groups
    main_group = Group()
    
    # Create roller coaster simulation
    coaster = RollerCoaster(64, 32)
    
    # Create track bitmap and palette
    track_bitmap = create_track_bitmap(64, 32, coaster.track_points)
    track_palette = Palette(4)
    track_palette[0] = 0x000000  # Background (black)
    track_palette[1] = 0x808080  # Track (gray)
    track_palette[2] = 0x404040  # Supports (dark gray)
    track_palette[3] = 0xFF0000  # Reserved for effects
    
    # Create track tilegrid
    track_grid = TileGrid(track_bitmap, pixel_shader=track_palette)
    main_group.append(track_grid)
    
    # Create cart sprite
    cart_bitmap = create_cart_sprite()
    cart_palette = Palette(2)
    cart_palette[0] = (0, 0, 0)    # Transparent
    cart_palette.make_transparent(0)  # Make index 0 transparent
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
    
    # Add sparkle effects group
    sparkle_group = Group()
    main_group.append(sparkle_group)
    
    # Create sparkle sprites
    sparkle_bitmap = Bitmap(1, 1, 2)
    sparkle_bitmap[0, 0] = 1
    
    sparkles = []
    for i in range(5):
        sparkle_palette = Palette(2)
        sparkle_palette[0] = (0, 0, 0)      # Transparent
        sparkle_palette.make_transparent(0)  # Make index 0 transparent
        sparkle_palette[1] = (255, 255, 0)  # Yellow sparkle
        
        sparkle = TileGrid(
            sparkle_bitmap,
            pixel_shader=sparkle_palette,
            x=-10,
            y=-10
        )
        sparkle_group.append(sparkle)
        sparkles.append({
            'sprite': sparkle,
            'life': 0,
            'vx': 0,
            'vy': 0,
            'x': 0.0,
            'y': 0.0
        })
    
    # Show on display
    device.show(main_group)
    
    frame_count = 0
    sparkle_timer = 0
    
    def update():
        """Update animation."""
        nonlocal frame_count, sparkle_timer
        
        # Update roller coaster physics
        coaster.update_cart()
        
        # Update cart sprite position
        cart_sprite.x = coaster.cart_x - 1
        cart_sprite.y = coaster.cart_y - 1
        
        # Animate cart color based on speed
        speed_factor = abs(coaster.cart_velocity) / 5.0
        hue = 0 if speed_factor < 0.5 else (60 - speed_factor * 60)  # Red to yellow
        r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
        cart_palette[1] = (r, g, b)  # Use tuple format for RGB888
        
        # Create sparkles when cart is moving fast
        if abs(coaster.cart_velocity) > 2.0 and sparkle_timer <= 0:
            # Find an inactive sparkle
            for sparkle in sparkles:
                if sparkle['life'] <= 0:
                    sparkle['life'] = 20
                    sparkle['x'] = float(coaster.cart_x)
                    sparkle['y'] = float(coaster.cart_y)
                    sparkle['vx'] = -coaster.cart_velocity * 0.2 + (hash(frame_count) % 100 - 50) / 100.0
                    sparkle['vy'] = -0.5 + (hash(frame_count + 1000) % 100 - 50) / 200.0
                    sparkle_timer = 3
                    break
                    
        sparkle_timer -= 1
        
        # Update sparkles
        for sparkle in sparkles:
            if sparkle['life'] > 0:
                sparkle['life'] -= 1
                sparkle['x'] += sparkle['vx']
                sparkle['y'] += sparkle['vy']
                sparkle['vy'] += 0.1  # Gravity
                
                # Update sprite position
                sparkle['sprite'].x = int(sparkle['x'])
                sparkle['sprite'].y = int(sparkle['y'])
                
                # Fade out
                brightness = sparkle['life'] / 20.0
                color = int(255 * brightness)
                sparkle['sprite'].pixel_shader[1] = (color, color, 0)  # Yellow fade
            else:
                # Hide inactive sparkles
                sparkle['sprite'].x = -10
                sparkle['sprite'].y = -10
                
        # Pulse track color slightly
        pulse = (math.sin(frame_count * 0.05) + 1) * 0.5
        gray = int(128 + 40 * pulse)
        track_palette[1] = (gray, gray, gray)  # Use tuple format
        
        frame_count += 1
    
    # Run the simulation
    device.run(update_callback=update, title="Roller Coaster Animation")


if __name__ == "__main__":
    main()