#!/usr/bin/env python3
"""
Fixed swarm animation that properly captures all pixels.

Key fixes:
1. Slower, more precise movement near targets
2. Capture detection in a small radius, not just exact position
3. Reduced randomness when close to targets
4. Birds slow down dramatically when very close to allow precise capture
"""

import sys
import os
import random
import math
import time
import gc

# Conditional imports for SLDK/CircuitPython compatibility
CIRCUITPYTHON = hasattr(sys, 'implementation') and sys.implementation.name == 'circuitpython'

if CIRCUITPYTHON:
    import board
    import displayio
    from adafruit_matrixportal.matrix import Matrix
else:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'sldk', 'src'))
    from sldk.simulator.devices import MatrixPortalS3
    from sldk.simulator.displayio import Bitmap, Palette, TileGrid, Group
    class displayio_compat:
        Bitmap = Bitmap
        Palette = Palette
        TileGrid = TileGrid
        Group = Group
    displayio = displayio_compat()

# Configuration
MATRIX_WIDTH = 64
MATRIX_HEIGHT = 32
MAX_BIRDS = 200
BIRD_SIZE = 3
PALETTE_SIZE = 16
SPAWN_INTERVAL = 0.1
BIRD_SPEED = 1.0  # Reduced for better control
UPDATE_RATE = 30

# Color indices
BLACK = 0
RAINBOW_START = 1


def hsv_to_rgb888(h, s, v):
    """Convert HSV to RGB888 format."""
    h = h % 1.0
    c = v * s
    x = c * (1 - abs((h * 6) % 2 - 1))
    m = v - c
    
    if h < 1/6:
        r, g, b = c, x, 0
    elif h < 2/6:
        r, g, b = x, c, 0
    elif h < 3/6:
        r, g, b = 0, c, x
    elif h < 4/6:
        r, g, b = 0, x, c
    elif h < 5/6:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
        
    return (int((r + m) * 255) << 16) | (int((g + m) * 255) << 8) | int((b + m) * 255)


def get_theme_park_waits_pixels():
    """Return set of (x, y) coordinates for THEME PARK WAITS text."""
    pixels = set()
    
    # THEME PARK - First line (y=3-10)
    # T (x=4)
    for x in range(4, 9): pixels.add((x, 3))
    for y in range(4, 11): pixels.add((6, y))
    
    # H (x=10)
    for y in range(3, 11): 
        pixels.add((10, y))
        pixels.add((14, y))
    for x in range(11, 14): pixels.add((x, 6))
    
    # E (x=16)
    for y in range(3, 11): pixels.add((16, y))
    for x in range(16, 20): 
        pixels.add((x, 3))
        pixels.add((x, 10))
    for x in range(16, 19): pixels.add((x, 6))
    
    # M (x=22)
    for y in range(3, 11): 
        pixels.add((22, y))
        pixels.add((27, y))
    pixels.add((23, 4))
    pixels.add((24, 5))
    pixels.add((25, 5))
    pixels.add((26, 4))
    
    # E (x=29)
    for y in range(3, 11): pixels.add((29, y))
    for x in range(29, 33): 
        pixels.add((x, 3))
        pixels.add((x, 10))
    for x in range(29, 32): pixels.add((x, 6))
    
    # P (x=36)
    for y in range(3, 11): pixels.add((36, y))
    for x in range(36, 40): 
        pixels.add((x, 3))
        pixels.add((x, 6))
    pixels.add((39, 4))
    pixels.add((39, 5))
    
    # A (x=42)
    for y in range(4, 11): 
        pixels.add((42, y))
        pixels.add((46, y))
    for x in range(43, 46): pixels.add((x, 3))
    for x in range(42, 47): pixels.add((x, 6))
    
    # R (x=48)
    for y in range(3, 11): pixels.add((48, y))
    for x in range(48, 52): 
        pixels.add((x, 3))
        pixels.add((x, 6))
    pixels.add((51, 4))
    pixels.add((51, 5))
    pixels.add((50, 7))
    pixels.add((51, 8))
    pixels.add((52, 9))
    pixels.add((53, 10))
    
    # K (x=54)
    for y in range(3, 11): pixels.add((54, y))
    pixels.add((57, 3))
    pixels.add((56, 4))
    pixels.add((55, 5))
    pixels.add((55, 6))
    pixels.add((56, 7))
    pixels.add((57, 8))
    pixels.add((58, 9))
    pixels.add((59, 10))
    
    # WAITS - Second line (y=15-30)
    # W (x=5)
    for y in range(15, 31):
        pixels.add((5, y))
        pixels.add((6, y))
        pixels.add((13, y))
        pixels.add((14, y))
    for x in range(7, 9): 
        pixels.add((x, 27))
        pixels.add((x, 28))
    for x in range(11, 13): 
        pixels.add((x, 27))
        pixels.add((x, 28))
    for y in range(23, 27): 
        pixels.add((9, y))
        pixels.add((10, y))
    
    # A (x=16)
    for y in range(17, 31): 
        pixels.add((16, y))
        pixels.add((17, y))
        pixels.add((24, y))
        pixels.add((25, y))
    for x in range(18, 24): 
        pixels.add((x, 15))
        pixels.add((x, 16))
    for x in range(16, 26): 
        pixels.add((x, 22))
        pixels.add((x, 23))
    
    # I (x=27)
    for x in range(27, 37): 
        pixels.add((x, 15))
        pixels.add((x, 16))
        pixels.add((x, 29))
        pixels.add((x, 30))
    for y in range(15, 31): 
        pixels.add((31, y))
        pixels.add((32, y))
    
    # T (x=38)
    for x in range(38, 48): 
        pixels.add((x, 15))
        pixels.add((x, 16))
    for y in range(15, 31): 
        pixels.add((42, y))
        pixels.add((43, y))
    
    # S (x=49)
    for x in range(49, 59): 
        pixels.add((x, 15))
        pixels.add((x, 16))
        pixels.add((x, 22))
        pixels.add((x, 23))
        pixels.add((x, 29))
        pixels.add((x, 30))
    for y in range(17, 22): 
        pixels.add((49, y))
        pixels.add((50, y))
    for y in range(24, 29): 
        pixels.add((57, y))
        pixels.add((58, y))
    
    return pixels


class Bird:
    """Improved bird with better capture mechanics."""
    
    def __init__(self, sprite_index):
        self.sprite_index = sprite_index
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.active = False
        self.color_index = 0
        
    def spawn(self, edge):
        """Spawn bird from specified edge."""
        self.active = True
        self.color_index = random.randint(1, PALETTE_SIZE - 1)
        
        if edge == 0:  # Left
            self.x = -BIRD_SIZE
            self.y = random.randint(5, MATRIX_HEIGHT - 5)
            self.vx = BIRD_SPEED
            self.vy = random.uniform(-0.2, 0.2)
        elif edge == 1:  # Right
            self.x = MATRIX_WIDTH + BIRD_SIZE
            self.y = random.randint(5, MATRIX_HEIGHT - 5)
            self.vx = -BIRD_SPEED
            self.vy = random.uniform(-0.2, 0.2)
        elif edge == 2:  # Top
            self.x = random.randint(5, MATRIX_WIDTH - 5)
            self.y = -BIRD_SIZE
            self.vx = random.uniform(-0.2, 0.2)
            self.vy = BIRD_SPEED
        else:  # Bottom
            self.x = random.randint(5, MATRIX_WIDTH - 5)
            self.y = MATRIX_HEIGHT + BIRD_SIZE
            self.vx = random.uniform(-0.2, 0.2)
            self.vy = -BIRD_SPEED
            
    def update(self, target_pixels, captured_pixels, attraction_center):
        """Update bird position with improved capture mechanics."""
        if not self.active:
            return False
            
        # Find closest uncaptured pixel
        min_dist = float('inf')
        closest_target = None
        
        for px, py in target_pixels:
            if (px, py) not in captured_pixels:
                dist = math.sqrt((px - self.x)**2 + (py - self.y)**2)
                if dist < min_dist:
                    min_dist = dist
                    closest_target = (px, py)
        
        # If very close to a target, use direct targeting
        if closest_target and min_dist < 3:
            # Direct targeting for precise capture
            dx = closest_target[0] - self.x
            dy = closest_target[1] - self.y
            
            # Slow down dramatically when very close
            if min_dist < 1.5:
                # Very slow, precise movement
                self.vx = dx * 0.3
                self.vy = dy * 0.3
            else:
                # Moderate speed approach
                if min_dist > 0:
                    self.vx = (dx / min_dist) * 0.5
                    self.vy = (dy / min_dist) * 0.5
            
            # Minimal randomness when close
            self.vx += random.uniform(-0.02, 0.02)
            self.vy += random.uniform(-0.02, 0.02)
            
        else:
            # Normal attraction-based movement
            if attraction_center:
                dx = attraction_center[0] - self.x
                dy = attraction_center[1] - self.y
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist > 0:
                    attraction = 0.5
                    self.vx += (dx / dist) * attraction
                    self.vy += (dy / dist) * attraction
            
            # Normal randomness
            self.vx += random.uniform(-0.1, 0.1)
            self.vy += random.uniform(-0.1, 0.1)
            
            # Speed limiting
            speed = math.sqrt(self.vx*self.vx + self.vy*self.vy)
            if speed > BIRD_SPEED:
                self.vx = (self.vx / speed) * BIRD_SPEED
                self.vy = (self.vy / speed) * BIRD_SPEED
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Improved capture detection - check in a small radius
        captured_any = False
        check_radius = 0.7  # Slightly larger than 0.5 to catch boundary cases
        
        for px, py in target_pixels:
            if (px, py) not in captured_pixels:
                # Check if bird is within capture radius of this pixel
                dist = math.sqrt((self.x - px)**2 + (self.y - py)**2)
                if dist <= check_radius:
                    captured_pixels.add((px, py))
                    captured_any = True
        
        # Deactivate if off screen
        if self.x < -20 or self.x > MATRIX_WIDTH + 20 or self.y < -20 or self.y > MATRIX_HEIGHT + 20:
            self.active = False
            
        return captured_any


class OptimizedSwarmAnimation:
    """Hardware-accelerated swarm animation with fixed capture mechanics."""
    
    def __init__(self):
        # Initialize display
        if CIRCUITPYTHON:
            self.matrix = Matrix(width=MATRIX_WIDTH, height=MATRIX_HEIGHT, bit_depth=6)
            self.display = self.matrix.display
            self.device = None
        else:
            self.device = MatrixPortalS3()
            self.device.initialize()
            self.display = self.device.display
            
        # Create main display group
        self.main_group = displayio.Group()
        
        # Animation state
        self.target_pixels = get_theme_park_waits_pixels()
        self.captured_pixels = set()
        self.birds = []
        self.last_spawn_time = 0
        self.last_update_time = 0
        self.animation_time = 0
        self.frame_count = 0
        self.completion_time = None
        self.reset_after_seconds = 20
        
        # Initialize components
        self.setup_palettes()
        self.setup_layers()
        self.setup_sprites()
        
        # Show on display
        if CIRCUITPYTHON:
            self.display.show(self.main_group)
        else:
            self.device.show(self.main_group)
            self.device.refresh()
            
        print(f"Display initialized with {len(self.target_pixels)} target pixels")
    
    def setup_palettes(self):
        """Create pre-computed color palettes."""
        self.rainbow_palette = displayio.Palette(PALETTE_SIZE)
        self.rainbow_palette[0] = 0x000000  # Black
        
        for i in range(1, PALETTE_SIZE):
            hue = (i - 1) / (PALETTE_SIZE - 1)
            self.rainbow_palette[i] = hsv_to_rgb888(hue, 1.0, 1.0)
    
    def setup_layers(self):
        """Create bitmap layers for rendering."""
        # Background layer
        self.background_bitmap = displayio.Bitmap(MATRIX_WIDTH, MATRIX_HEIGHT, 1)
        background_palette = displayio.Palette(1)
        background_palette[0] = 0x000000
        self.background_grid = displayio.TileGrid(
            self.background_bitmap, 
            pixel_shader=background_palette
        )
        self.main_group.append(self.background_grid)
        
        # Text layer
        self.text_bitmap = displayio.Bitmap(MATRIX_WIDTH, MATRIX_HEIGHT, PALETTE_SIZE)
        for y in range(MATRIX_HEIGHT):
            for x in range(MATRIX_WIDTH):
                self.text_bitmap[x, y] = 0
        
        self.text_grid = displayio.TileGrid(
            self.text_bitmap,
            pixel_shader=self.rainbow_palette
        )
        self.main_group.append(self.text_grid)
        
        # Bird sprites layer
        if CIRCUITPYTHON:
            self.bird_group = displayio.Group(max_size=MAX_BIRDS)
        else:
            self.bird_group = displayio.Group()
        self.main_group.append(self.bird_group)
    
    def setup_sprites(self):
        """Create sprite pool for birds."""
        # Create bird shape - single pixel for precision
        bird_shape = displayio.Bitmap(BIRD_SIZE, BIRD_SIZE, 2)
        bird_shape[1, 1] = 1  # Center only
        
        # Create sprite pool
        self.bird_sprites = []
        for i in range(MAX_BIRDS):
            palette = displayio.Palette(2)
            palette[0] = 0x000000  # Transparent
            palette[1] = 0xFF0000  # Will be updated
            
            sprite = displayio.TileGrid(
                bird_shape,
                pixel_shader=palette,
                x=-10,
                y=-10
            )
            self.bird_sprites.append(sprite)
            self.bird_group.append(sprite)
            
            bird = Bird(i)
            self.birds.append(bird)
    
    def find_attraction_center(self):
        """Find center of missing pixels."""
        missing = self.target_pixels - self.captured_pixels
        if not missing:
            return None
            
        # For small numbers, return exact pixel
        if len(missing) <= 5:
            return random.choice(list(missing))
            
        # Otherwise return centroid
        x_sum = sum(p[0] for p in missing)
        y_sum = sum(p[1] for p in missing)
        return (x_sum / len(missing), y_sum / len(missing))
    
    def update_palette_animation(self):
        """Update rainbow palette animation."""
        for pixel in self.captured_pixels:
            x, y = pixel
            if 0 <= x < MATRIX_WIDTH and 0 <= y < MATRIX_HEIGHT:
                wave_offset = int((x + y) / 4 + self.animation_time * 3) % (PALETTE_SIZE - 1)
                color_index = 1 + wave_offset
                self.text_bitmap[x, y] = color_index
    
    def reset_animation(self):
        """Reset the animation to start over."""
        print("\nResetting animation...\n")
        
        self.captured_pixels.clear()
        
        for bird in self.birds:
            bird.active = False
        
        for y in range(MATRIX_HEIGHT):
            for x in range(MATRIX_WIDTH):
                self.text_bitmap[x, y] = 0
        
        self.completion_time = None
        self.last_spawn_time = 0
        self.animation_time = 0
        self.frame_count = 0
        
        print(f"Starting new swarm animation with {len(self.target_pixels)} target pixels...")
    
    def update(self):
        """Update animation frame."""
        current_time = time.monotonic() if CIRCUITPYTHON else time.time()
        
        if current_time - self.last_update_time < 1.0 / UPDATE_RATE:
            return
            
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
        self.animation_time += delta_time
        self.frame_count += 1
        
        # Check if animation is complete
        if len(self.captured_pixels) >= len(self.target_pixels):
            if self.completion_time is None:
                self.completion_time = current_time
                print(f"\nTHEME PARK WAITS completed!")
                print(f"Total pixels captured: {len(self.captured_pixels)}/{len(self.target_pixels)}")
                for bird in self.birds:
                    bird.active = False
            
            if current_time - self.completion_time >= self.reset_after_seconds:
                self.reset_animation()
                return
            
            self.update_palette_animation()
            
            if self.frame_count % 90 == 0:
                remaining = self.reset_after_seconds - (current_time - self.completion_time)
                print(f"Resetting in {remaining:.1f} seconds...")
            return
        
        # Spawn new birds
        if len(self.captured_pixels) < len(self.target_pixels):
            if current_time - self.last_spawn_time > SPAWN_INTERVAL:
                active_count = sum(1 for bird in self.birds if bird.active)
                remaining_pixels = len(self.target_pixels) - len(self.captured_pixels)
                
                # Always maintain enough birds
                max_birds_needed = min(MAX_BIRDS * 0.8, max(50, remaining_pixels * 2))
                
                if active_count < max_birds_needed:
                    spawn_count = min(30, int(max_birds_needed - active_count))
                    spawned = 0
                    for _ in range(spawn_count):
                        for bird in self.birds:
                            if not bird.active:
                                edge = random.randint(0, 3)
                                bird.spawn(edge)
                                spawned += 1
                                break
                    
                    self.last_spawn_time = current_time
        
        # Find attraction center
        attraction_center = self.find_attraction_center()
        
        # Update birds
        for bird in self.birds:
            if bird.active:
                captured = bird.update(self.target_pixels, self.captured_pixels, attraction_center)
                
                if len(self.captured_pixels) >= len(self.target_pixels):
                    bird.active = False
                
                # Update sprite
                sprite = self.bird_sprites[bird.sprite_index]
                sprite.x = int(bird.x - BIRD_SIZE // 2)
                sprite.y = int(bird.y - BIRD_SIZE // 2)
                
                hue = (self.animation_time + bird.sprite_index * 0.1) % 1.0
                sprite.pixel_shader[1] = hsv_to_rgb888(hue, 1.0, 1.0)
            else:
                sprite = self.bird_sprites[bird.sprite_index]
                sprite.x = -10
                sprite.y = -10
        
        # Update text bitmap
        for pixel in self.captured_pixels:
            x, y = pixel
            if 0 <= x < MATRIX_WIDTH and 0 <= y < MATRIX_HEIGHT:
                if self.text_bitmap[x, y] == 0:
                    color_index = 1 + ((x + y) % (PALETTE_SIZE - 1))
                    self.text_bitmap[x, y] = color_index
        
        self.update_palette_animation()
        
        # Force display refresh for SLDK
        if not CIRCUITPYTHON and self.device:
            self.device.refresh()
        
        # Progress
        if self.frame_count % 60 == 0:
            active_birds = sum(1 for b in self.birds if b.active)
            missing = len(self.target_pixels) - len(self.captured_pixels)
            print(f"Progress: {len(self.captured_pixels)}/{len(self.target_pixels)} "
                  f"captured, {missing} remaining, {active_birds} birds active")
    
    def run(self):
        """Run the animation."""
        print(f"Starting optimized swarm animation...")
        print(f"Target pixels: {len(self.target_pixels)}")
        print(f"Using {'CircuitPython hardware' if CIRCUITPYTHON else 'SLDK simulator'}")
        
        if CIRCUITPYTHON:
            while True:
                self.update()
        else:
            def update_with_refresh():
                self.update()
                self.device.refresh()
            
            self.device.run(
                update_callback=update_with_refresh,
                title="Fixed THEME PARK WAITS Swarm"
            )


def main():
    """Run the fixed swarm animation."""
    gc.collect()
    animation = OptimizedSwarmAnimation()
    animation.run()


if __name__ == "__main__":
    main()