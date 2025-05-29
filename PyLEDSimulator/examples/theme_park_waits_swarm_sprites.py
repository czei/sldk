#!/usr/bin/env python3
"""Sprite-based swarm animation for MatrixPortal S3 using CircuitPython.

This version uses displayio sprites for smoother animation while
maintaining memory efficiency through sprite pooling.
"""

import random
import math
import time
import gc

# CircuitPython imports
try:
    import board
    import displayio
    from adafruit_matrixportal.matrix import Matrix
    CIRCUITPYTHON = True
except ImportError:
    # For testing in simulator
    CIRCUITPYTHON = False
    print("Running in simulator mode")

# Configuration
MAX_SPRITES = 20  # Limited sprite pool
BIRD_SPEED = 1.0
SPAWN_RATE = 0.5  # Seconds between spawns
CAPTURE_DISTANCE = 1.5  # Distance to capture a pixel

# Create bird sprite bitmap (3x3 cross pattern)
def create_bird_sprite():
    """Create a small bird sprite bitmap."""
    bitmap = displayio.Bitmap(3, 3, 2)
    # Cross pattern
    bitmap[1, 0] = 1  # Top
    bitmap[0, 1] = 1  # Left
    bitmap[1, 1] = 1  # Center
    bitmap[2, 1] = 1  # Right
    bitmap[1, 2] = 1  # Bottom
    return bitmap


# Simplified text definition using run-length encoding
# Format: (x, y, direction, length) where direction is 'h' or 'v'
TEXT_RUNS = [
    # THEME (y=3-10)
    (4, 3, 'h', 5), (6, 4, 'v', 7),  # T
    (10, 3, 'v', 8), (14, 3, 'v', 8), (11, 6, 'h', 3),  # H
    (16, 3, 'v', 8), (16, 3, 'h', 4), (16, 6, 'h', 3), (16, 10, 'h', 4),  # E
    (22, 3, 'v', 8), (27, 3, 'v', 8), (23, 4, 'h', 1), (24, 5, 'h', 2), (26, 4, 'h', 1),  # M
    (29, 3, 'v', 8), (29, 3, 'h', 4), (29, 6, 'h', 3), (29, 10, 'h', 4),  # E
    
    # PARK (y=3-10)
    (36, 3, 'v', 8), (36, 3, 'h', 4), (36, 6, 'h', 4), (39, 4, 'v', 2),  # P
    (42, 4, 'v', 7), (46, 4, 'v', 7), (43, 3, 'h', 3), (42, 6, 'h', 5),  # A
    (48, 3, 'v', 8), (48, 3, 'h', 4), (48, 6, 'h', 4), (51, 4, 'v', 2),  # R
    (50, 7, 'h', 1), (51, 8, 'h', 1), (52, 9, 'h', 1), (53, 10, 'h', 1),  # R diagonal
    (54, 3, 'v', 8), (55, 5, 'h', 1), (56, 4, 'h', 1), (57, 3, 'h', 1),  # K
    (55, 6, 'h', 1), (56, 7, 'h', 1), (57, 8, 'h', 1), (58, 9, 'h', 1), (59, 10, 'h', 1),  # K
    
    # WAITS (y=15-30)
    (5, 15, 'v', 16), (6, 15, 'v', 16), (13, 15, 'v', 16), (14, 15, 'v', 16),  # W
    (7, 27, 'h', 2), (11, 27, 'h', 2), (9, 23, 'v', 4), (10, 23, 'v', 4),  # W middle
    (16, 17, 'v', 14), (17, 17, 'v', 14), (24, 17, 'v', 14), (25, 17, 'v', 14),  # A
    (18, 15, 'h', 6), (18, 16, 'h', 6), (16, 22, 'h', 10), (16, 23, 'h', 10),  # A
    (27, 15, 'h', 10), (27, 16, 'h', 10), (31, 15, 'v', 16), (32, 15, 'v', 16),  # I
    (27, 29, 'h', 10), (27, 30, 'h', 10),  # I
    (38, 15, 'h', 10), (38, 16, 'h', 10), (42, 15, 'v', 16), (43, 15, 'v', 16),  # T
    (49, 15, 'h', 10), (49, 16, 'h', 10), (49, 17, 'v', 5), (50, 17, 'v', 5),  # S
    (49, 22, 'h', 10), (49, 23, 'h', 10), (57, 24, 'v', 5), (58, 24, 'v', 5),  # S
    (49, 29, 'h', 10), (49, 30, 'h', 10),  # S
]


class Bird:
    """Lightweight bird object for sprite pool."""
    
    def __init__(self, sprite_index):
        self.sprite_index = sprite_index
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.active = False
        self.color_phase = random.uniform(0, 6.28)  # For color cycling
        
    def spawn(self, edge, width, height):
        """Spawn bird from specified edge."""
        self.active = True
        
        if edge == 0:  # Left
            self.x = -3.0
            self.y = float(random.randint(5, height - 5))
            self.vx = BIRD_SPEED
            self.vy = random.uniform(-0.3, 0.3)
        elif edge == 1:  # Right
            self.x = float(width + 3)
            self.y = float(random.randint(5, height - 5))
            self.vx = -BIRD_SPEED
            self.vy = random.uniform(-0.3, 0.3)
        elif edge == 2:  # Top
            self.x = float(random.randint(5, width - 5))
            self.y = -3.0
            self.vx = random.uniform(-0.3, 0.3)
            self.vy = BIRD_SPEED
        else:  # Bottom
            self.x = float(random.randint(5, width - 5))
            self.y = float(height + 3)
            self.vx = random.uniform(-0.3, 0.3)
            self.vy = -BIRD_SPEED
            
    def update(self, target_pixels, captured_pixels):
        """Update bird position and check for capture."""
        if not self.active:
            return False
            
        # Find nearest uncaptured pixel
        min_dist = float('inf')
        target_x = target_y = None
        
        for tx, ty in target_pixels:
            if (tx, ty) not in captured_pixels:
                dist = abs(self.x - tx) + abs(self.y - ty)
                if dist < min_dist:
                    min_dist = dist
                    target_x, target_y = tx, ty
                    
        # Steer toward target if close enough
        if target_x is not None and min_dist < 15:
            dx = target_x - self.x
            dy = target_y - self.y
            
            # Stronger steering when very close
            steer_strength = 0.2 if min_dist < 5 else 0.1
            
            if abs(dx) > 0.1:
                self.vx += steer_strength * (1 if dx > 0 else -1)
            if abs(dy) > 0.1:
                self.vy += steer_strength * (1 if dy > 0 else -1)
                
        # Add slight randomness
        self.vx += random.uniform(-0.05, 0.05)
        self.vy += random.uniform(-0.05, 0.05)
        
        # Limit speed
        speed = math.sqrt(self.vx * self.vx + self.vy * self.vy)
        if speed > BIRD_SPEED:
            self.vx = (self.vx / speed) * BIRD_SPEED
            self.vy = (self.vy / speed) * BIRD_SPEED
            
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Check for pixel capture
        pixel_x = int(round(self.x))
        pixel_y = int(round(self.y))
        
        if (pixel_x, pixel_y) in target_pixels and (pixel_x, pixel_y) not in captured_pixels:
            captured_pixels.add((pixel_x, pixel_y))
            self.active = False
            return True  # Captured a pixel
            
        # Deactivate if off screen
        if self.x < -10 or self.x > 74 or self.y < -10 or self.y > 42:
            self.active = False
            
        return False


def expand_text_runs():
    """Expand run-length encoded text to pixel set."""
    pixels = set()
    for x, y, direction, length in TEXT_RUNS:
        if direction == 'h':
            for i in range(length):
                pixels.add((x + i, y))
        else:  # 'v'
            for i in range(length):
                pixels.add((x, y + i))
    return pixels


def hsv_to_rgb565(h, s, v):
    """Convert HSV to RGB565 color format."""
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
        
    # Convert to 0-255 range
    r = int((r + m) * 255)
    g = int((g + m) * 255)
    b = int((b + m) * 255)
    
    # Convert to RGB565
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


def run_sprite_swarm():
    """Run sprite-based swarm animation."""
    if not CIRCUITPYTHON:
        print("This sprite version requires CircuitPython")
        return
        
    # Initialize matrix
    matrix = Matrix(width=64, height=32, bit_depth=6)
    display = matrix.display
    
    # Create main group
    main_group = displayio.Group()
    
    # Create background bitmap for captured text
    text_bitmap = displayio.Bitmap(64, 32, 2)
    text_palette = displayio.Palette(2)
    text_palette[0] = 0x000000  # Black
    text_palette[1] = 0xFFFF00  # Yellow
    text_grid = displayio.TileGrid(text_bitmap, pixel_shader=text_palette)
    main_group.append(text_grid)
    
    # Create sprite group for birds
    sprite_group = displayio.Group()
    main_group.append(sprite_group)
    
    # Create bird sprites
    bird_bitmap = create_bird_sprite()
    sprites = []
    birds = []
    
    for i in range(MAX_SPRITES):
        # Each bird gets its own palette for color animation
        palette = displayio.Palette(2)
        palette[0] = 0x000000  # Transparent black
        palette[1] = 0xFF0000  # Will be updated dynamically
        
        sprite = displayio.TileGrid(
            bird_bitmap,
            pixel_shader=palette,
            width=1,
            height=1,
            tile_width=3,
            tile_height=3,
            default_tile=0,
            x=-10,  # Start off-screen
            y=-10
        )
        sprites.append(sprite)
        sprite_group.append(sprite)
        birds.append(Bird(i))
    
    # Show on display
    display.root_group = main_group
    
    # Game state
    target_pixels = expand_text_runs()
    captured_pixels = set()
    last_spawn = time.monotonic()
    animation_time = 0
    
    # Main loop
    while True:
        current_time = time.monotonic()
        animation_time += 0.05
        
        # Spawn new birds
        if current_time - last_spawn > SPAWN_RATE:
            # Find inactive bird
            for bird in birds:
                if not bird.active and len(captured_pixels) < len(target_pixels):
                    edge = random.randint(0, 3)
                    bird.spawn(edge, 64, 32)
                    last_spawn = current_time
                    break
                    
        # Update birds
        for i, bird in enumerate(birds):
            if bird.active:
                captured = bird.update(target_pixels, captured_pixels)
                
                if captured:
                    # Add to text bitmap
                    px, py = int(bird.x), int(bird.y)
                    if 0 <= px < 64 and 0 <= py < 32:
                        text_bitmap[px, py] = 1
                        
                # Update sprite position
                sprites[i].x = int(bird.x) - 1
                sprites[i].y = int(bird.y) - 1
                
                # Animate bird color
                hue = (animation_time * 60 + bird.color_phase * 60) % 360
                color = hsv_to_rgb565(hue, 0.9, 0.9)
                sprites[i].pixel_shader[1] = color
            else:
                # Hide inactive sprites
                sprites[i].x = -10
                sprites[i].y = -10
                
        # Check if complete
        if len(captured_pixels) >= len(target_pixels):
            # Rainbow effect on completed text
            for _ in range(60):  # 3 seconds at 20fps
                hue = (animation_time * 60) % 360
                text_palette[1] = hsv_to_rgb565(hue, 1.0, 1.0)
                animation_time += 0.05
                time.sleep(0.05)
                
            # Reset
            captured_pixels.clear()
            text_bitmap.fill(0)
            text_palette[1] = 0xFFFF00
            gc.collect()
            
        time.sleep(0.05)  # ~20 FPS


if __name__ == "__main__":
    run_sprite_swarm()