#!/usr/bin/env python3
"""
Optimized swarm animation using hardware-accelerated displayio features.
Compatible with both SLDK simulator and CircuitPython hardware.

This version uses bitmap-based rendering, pre-computed palettes, and sprite pooling
for dramatically improved performance on MatrixPortal S3 hardware.
"""

import sys
import os
import random
import math
import time
import gc

# Conditional imports for SLDK/CircuitPython compatibility
# Check if we're on CircuitPython first
CIRCUITPYTHON = hasattr(sys, 'implementation') and sys.implementation.name == 'circuitpython'

if CIRCUITPYTHON:
    # CircuitPython hardware
    import board
    import displayio
    from adafruit_matrixportal.matrix import Matrix
else:
    # SLDK simulator
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'sldk', 'src'))
    from sldk.simulator.devices import MatrixPortalS3
    from sldk.simulator.displayio import Bitmap, Palette, TileGrid, Group
    # Create a displayio module namespace for compatibility
    class displayio_compat:
        Bitmap = Bitmap
        Palette = Palette
        TileGrid = TileGrid
        Group = Group
    displayio = displayio_compat()

# Configuration
MATRIX_WIDTH = 64
MATRIX_HEIGHT = 32
MAX_BIRDS = 200  # Maximum concurrent birds (increased for better coverage)
BIRD_SIZE = 3    # Bird sprite size (but only center pixel is visible)
PALETTE_SIZE = 16  # Number of colors in rainbow palette
SPAWN_INTERVAL = 0.2  # Seconds between bird spawns (slower for visible flocking)
BIRD_SPEED = 3.0  # Increased speed for more dynamic flocking
UPDATE_RATE = 30  # Target FPS
FLOCK_SPAWN_SIZE = 5  # Spawn birds in groups for better flocking

# Color indices in palettes
BLACK = 0
RAINBOW_START = 1


def hsv_to_rgb888(h, s, v):
    """Convert HSV to RGB888 format for displayio compatibility."""
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
        
    # Convert to 24-bit RGB
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
    """Lightweight bird object for sprite pooling."""
    
    def __init__(self, sprite_index):
        self.sprite_index = sprite_index
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.active = False
        self.color_index = 0
        self.stuck_counter = 0  # Track if bird gets stuck
        self.last_x = 0.0
        self.last_y = 0.0
        self.phase = random.uniform(0, 2 * math.pi)  # For wing flapping
        self.speed_multiplier = random.uniform(0.7, 1.3)  # Individual variation
        
    def spawn(self, edge):
        """Spawn bird from specified edge."""
        self.active = True
        self.color_index = random.randint(1, PALETTE_SIZE - 1)
        
        if edge == 0:  # Left
            self.x = -BIRD_SIZE
            self.y = random.randint(5, MATRIX_HEIGHT - 5)
            self.vx = BIRD_SPEED
            self.vy = random.uniform(-0.3, 0.3)
        elif edge == 1:  # Right
            self.x = MATRIX_WIDTH + BIRD_SIZE
            self.y = random.randint(5, MATRIX_HEIGHT - 5)
            self.vx = -BIRD_SPEED
            self.vy = random.uniform(-0.3, 0.3)
        elif edge == 2:  # Top
            self.x = random.randint(5, MATRIX_WIDTH - 5)
            self.y = -BIRD_SIZE
            self.vx = random.uniform(-0.3, 0.3)
            self.vy = BIRD_SPEED
        else:  # Bottom
            self.x = random.randint(5, MATRIX_WIDTH - 5)
            self.y = MATRIX_HEIGHT + BIRD_SIZE
            self.vx = random.uniform(-0.3, 0.3)
            self.vy = -BIRD_SPEED
            
    def update(self, target_pixels, captured_pixels, attraction_center, flock):
        """Update bird position with flocking behavior and capture mechanics."""
        if not self.active:
            return False
            
        # Apply flocking rules first
        separation = self.separation_rule(flock)
        alignment = self.alignment_rule(flock)
        cohesion = self.cohesion_rule(flock)
        
        # Find closest uncaptured pixel for precision targeting
        min_dist = float('inf')
        closest_target = None
        
        for px, py in target_pixels:
            if (px, py) not in captured_pixels:
                dist = math.sqrt((px - self.x)**2 + (py - self.y)**2)
                if dist < min_dist:
                    min_dist = dist
                    closest_target = (px, py)
        
        # If very close to a target, use precision mode with reduced flocking
        if closest_target and min_dist < 3:
            # Direct targeting for precise capture
            dx = closest_target[0] - self.x
            dy = closest_target[1] - self.y
            
            # Slow down dramatically when very close
            if min_dist < 1.5:
                # Very slow, precise movement - ignore flocking when capturing
                self.vx = dx * 0.3
                self.vy = dy * 0.3
            else:
                # Moderate speed approach with some flocking
                if min_dist > 0:
                    target_vx = (dx / min_dist) * 0.5
                    target_vy = (dy / min_dist) * 0.5
                    # Blend with flocking (reduced influence when close to target)
                    self.vx = target_vx * 0.7 + separation[0] * 0.2 + alignment[0] * 0.05 + cohesion[0] * 0.05
                    self.vy = target_vy * 0.7 + separation[1] * 0.2 + alignment[1] * 0.05 + cohesion[1] * 0.05
            
            # Almost no randomness when close to target
            self.vx += random.uniform(-0.01, 0.01)
            self.vy += random.uniform(-0.01, 0.01)
            
        else:
            # Normal flocking + attraction movement
            attraction_vx = 0
            attraction_vy = 0
            
            if attraction_center:
                dx = attraction_center[0] - self.x
                dy = attraction_center[1] - self.y
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist > 0:
                    attraction_strength = 0.3
                    attraction_vx = (dx / dist) * attraction_strength
                    attraction_vy = (dy / dist) * attraction_strength
            else:
                # No attraction center - encourage birds to fly away
                center_x, center_y = 32, 16
                dx = self.x - center_x
                dy = self.y - center_y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0:
                    attraction_vx = (dx / dist) * 0.1
                    attraction_vy = (dy / dist) * 0.1
            
            # Apply all forces with weights for visible flocking behavior
            # Much stronger flocking forces, weaker initial attraction
            remaining_ratio = len(captured_pixels) / len(target_pixels) if target_pixels else 0
            attraction_weight = 0.1 + remaining_ratio * 0.5  # Start weak, get stronger
            
            self.vx += separation[0] * 0.4 + alignment[0] * 0.3 + cohesion[0] * 0.2 + attraction_vx * attraction_weight
            self.vy += separation[1] * 0.4 + alignment[1] * 0.3 + cohesion[1] * 0.2 + attraction_vy * attraction_weight
            
            # Add wing flapping motion for organic movement
            self.vx += 0.15 * math.sin(self.phase + time.time() * 10) * self.speed_multiplier
            self.vy += 0.1 * math.cos(self.phase + time.time() * 8) * self.speed_multiplier
            
            # Add some randomness for natural movement
            self.vx += random.uniform(-0.1, 0.1)
            self.vy += random.uniform(-0.1, 0.1)
        
        # Limit speed
        speed = math.sqrt(self.vx*self.vx + self.vy*self.vy)
        if speed > BIRD_SPEED:
            self.vx = (self.vx / speed) * BIRD_SPEED
            self.vy = (self.vy / speed) * BIRD_SPEED
        elif speed < 0.3:  # Minimum speed to prevent getting stuck
            if speed > 0:
                self.vx = (self.vx / speed) * 0.3
                self.vy = (self.vy / speed) * 0.3
            
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Check if bird is stuck (not moving much)
        move_dist = math.sqrt((self.x - self.last_x)**2 + (self.y - self.last_y)**2)
        if move_dist < 0.1:  # Very little movement
            self.stuck_counter += 1
            if self.stuck_counter > 30:  # Stuck for 1 second at 30 FPS
                # Give it a random kick
                self.vx = random.uniform(-2, 2)
                self.vy = random.uniform(-2, 2)
                self.stuck_counter = 0
        else:
            self.stuck_counter = 0
        
        self.last_x = self.x
        self.last_y = self.y
        
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
        
        return captured_any
            
        # Deactivate if off screen (with larger margin)
        if self.x < -20 or self.x > MATRIX_WIDTH + 20 or self.y < -20 or self.y > MATRIX_HEIGHT + 20:
            self.active = False
            
        return False
    
    def separation_rule(self, flock):
        """Steer to avoid crowding local flockmates."""
        steer_x, steer_y = 0.0, 0.0
        count = 0
        separation_radius = 5.0  # Increased for more visible separation
        
        for other in flock:
            if other is self or not other.active:
                continue
            dx = self.x - other.x
            dy = self.y - other.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if 0 < distance < separation_radius:
                # Normalize and weight by distance
                steer_x += dx / distance / distance
                steer_y += dy / distance / distance
                count += 1
        
        if count > 0:
            steer_x /= count
            steer_y /= count
        
        return (steer_x, steer_y)
    
    def alignment_rule(self, flock):
        """Steer towards the average heading of neighbors."""
        avg_vx, avg_vy = 0.0, 0.0
        count = 0
        neighbor_distance = 15.0  # Increased for wider flocking awareness
        
        for other in flock:
            if other is self or not other.active:
                continue
            dx = self.x - other.x
            dy = self.y - other.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < neighbor_distance:
                avg_vx += other.vx
                avg_vy += other.vy
                count += 1
        
        if count > 0:
            avg_vx /= count
            avg_vy /= count
            # Return steering force toward average heading
            return (avg_vx - self.vx, avg_vy - self.vy)
        
        return (0.0, 0.0)
    
    def cohesion_rule(self, flock):
        """Steer to move toward the average position of local flockmates."""
        center_x, center_y = 0.0, 0.0
        count = 0
        neighbor_distance = 20.0  # Increased for stronger group cohesion
        
        for other in flock:
            if other is self or not other.active:
                continue
            dx = self.x - other.x
            dy = self.y - other.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < neighbor_distance:
                center_x += other.x
                center_y += other.y
                count += 1
        
        if count > 0:
            center_x /= count
            center_y /= count
            # Return steering force toward center
            return ((center_x - self.x) * 0.01, (center_y - self.y) * 0.01)
        
        return (0.0, 0.0)


class OptimizedSwarmAnimation:
    """Hardware-accelerated swarm animation using displayio."""
    
    def __init__(self):
        # Initialize display
        if CIRCUITPYTHON:
            # Hardware initialization
            self.matrix = Matrix(width=MATRIX_WIDTH, height=MATRIX_HEIGHT, bit_depth=6)
            self.display = self.matrix.display
            self.device = None
        else:
            # SLDK simulator initialization
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
        self.completion_time = None  # Track when animation completes
        self.reset_after_seconds = 20  # Reset after showing complete text for this long
        self.final_sweep_time = None  # Track when we start final sweep
        
        # Initialize components
        self.setup_palettes()
        self.setup_layers()
        self.setup_sprites()
        
        # Show on display
        if CIRCUITPYTHON:
            self.display.show(self.main_group)
        else:
            self.device.show(self.main_group)
            # Force initial refresh to ensure display is set up
            self.device.refresh()
            
        print(f"Display initialized with {len(self.target_pixels)} target pixels")
    
    def setup_palettes(self):
        """Create pre-computed color palettes."""
        # Rainbow palette for birds and text
        self.rainbow_palette = displayio.Palette(PALETTE_SIZE)
        self.rainbow_palette[0] = 0x000000  # Black
        
        for i in range(1, PALETTE_SIZE):
            hue = (i - 1) / (PALETTE_SIZE - 1)
            self.rainbow_palette[i] = hsv_to_rgb888(hue, 1.0, 1.0)  # Full saturation and brightness
        
        # Bird palette (will be animated)
        self.bird_palette = displayio.Palette(2)
        self.bird_palette[0] = 0x000000  # Transparent black
        self.bird_palette[1] = 0xFF0000  # Will be updated dynamically
    
    def setup_layers(self):
        """Create bitmap layers for rendering."""
        # Background layer (black)
        self.background_bitmap = displayio.Bitmap(MATRIX_WIDTH, MATRIX_HEIGHT, 1)
        background_palette = displayio.Palette(1)
        background_palette[0] = 0x000000
        self.background_grid = displayio.TileGrid(
            self.background_bitmap, 
            pixel_shader=background_palette
        )
        self.main_group.append(self.background_grid)
        
        # Bird sprites layer (add FIRST so text appears on top)
        # SLDK doesn't support max_size, but CircuitPython does
        if CIRCUITPYTHON:
            self.bird_group = displayio.Group(max_size=MAX_BIRDS)
        else:
            self.bird_group = displayio.Group()
        self.main_group.append(self.bird_group)
        
        # Text layer for captured pixels (add LAST so it's on top)
        self.text_bitmap = displayio.Bitmap(MATRIX_WIDTH, MATRIX_HEIGHT, PALETTE_SIZE)
        # Initialize all pixels to black (index 0)
        for y in range(MATRIX_HEIGHT):
            for x in range(MATRIX_WIDTH):
                self.text_bitmap[x, y] = 0
        
        self.text_grid = displayio.TileGrid(
            self.text_bitmap,
            pixel_shader=self.rainbow_palette
        )
        self.main_group.append(self.text_grid)
    
    def reset_animation(self):
        """Reset the animation to start over."""
        print("\nResetting animation...\n")
        
        # Verify all pixels were captured
        if len(self.captured_pixels) < len(self.target_pixels):
            missing = self.target_pixels - self.captured_pixels
            print(f"WARNING: Animation ended with {len(missing)} missing pixels!")
            for px, py in sorted(list(missing)[:10]):  # Show first 10
                print(f"  Missing: ({px}, {py})")
        
        # Clear captured pixels
        self.captured_pixels.clear()
        
        # Reset all birds
        for bird in self.birds:
            bird.active = False
        
        # Clear text bitmap
        for y in range(MATRIX_HEIGHT):
            for x in range(MATRIX_WIDTH):
                self.text_bitmap[x, y] = 0
        
        # Reset timing
        self.completion_time = None
        self.final_sweep_time = None
        self.last_spawn_time = 0
        self.animation_time = 0
        self.frame_count = 0
        
        print(f"Starting new swarm animation with {len(self.target_pixels)} target pixels...")
    
    def setup_sprites(self):
        """Create sprite pool for birds."""
        # Create bird shape (3x3 cross for visibility)
        bird_shape = displayio.Bitmap(BIRD_SIZE, BIRD_SIZE, 2)
        # Make a cross shape for better visibility
        bird_shape[1, 0] = 1  # Top
        bird_shape[0, 1] = 1  # Left
        bird_shape[1, 1] = 1  # Center
        bird_shape[2, 1] = 1  # Right
        bird_shape[1, 2] = 1  # Bottom
        
        # Create sprite pool
        self.bird_sprites = []
        for i in range(MAX_BIRDS):
            # Each bird gets its own palette for independent color
            palette = displayio.Palette(2)
            palette[0] = 0x000000  # Transparent
            palette[1] = 0xFF0000  # Will be updated
            
            sprite = displayio.TileGrid(
                bird_shape,
                pixel_shader=palette,
                x=-10,  # Start off-screen
                y=-10
            )
            self.bird_sprites.append(sprite)
            self.bird_group.append(sprite)
            
            # Create bird object
            bird = Bird(i)
            self.birds.append(bird)
    
    def find_attraction_center(self):
        """Find center of largest cluster of missing pixels."""
        missing = self.target_pixels - self.captured_pixels
        if not missing:
            return None
            
        # Simple centroid of all missing pixels
        if len(missing) <= 20:
            x_sum = sum(p[0] for p in missing)
            y_sum = sum(p[1] for p in missing)
            return (x_sum / len(missing), y_sum / len(missing))
        
        # For larger groups, find densest area
        best_center = None
        best_score = 0
        
        # Sample some points
        samples = random.sample(list(missing), min(20, len(missing)))  # More samples for better coverage
        for center in samples:
            score = 0
            for pixel in missing:
                dx = pixel[0] - center[0]
                dy = pixel[1] - center[1]
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < 15:
                    score += 1.0 / (dist + 1)
            
            if score > best_score:
                best_score = score
                best_center = center
        
        return best_center
    
    def update_palette_animation(self):
        """Update rainbow palette animation."""
        # Cycle rainbow colors for dynamic effect
        color_offset = int(self.animation_time * 2) % PALETTE_SIZE
        
        # Update text pixels with wave effect
        # Make a copy to avoid concurrent modification
        captured_copy = self.captured_pixels.copy()
        for pixel in captured_copy:
            x, y = pixel
            if 0 <= x < MATRIX_WIDTH and 0 <= y < MATRIX_HEIGHT:
                # Create wave effect across display
                wave_offset = int((x + y) / 4 + self.animation_time * 3) % (PALETTE_SIZE - 1)
                color_index = 1 + wave_offset
                self.text_bitmap[x, y] = color_index
    
    def update(self):
        """Update animation frame."""
        current_time = time.monotonic() if CIRCUITPYTHON else time.time()
        
        # Frame rate limiting
        if current_time - self.last_update_time < 1.0 / UPDATE_RATE:
            return
            
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
        self.animation_time += delta_time
        self.frame_count += 1
        
        # Early final sweep - start when we're close to done
        missing_count = len(self.target_pixels) - len(self.captured_pixels)
        if missing_count > 0 and missing_count <= 20 and self.final_sweep_time is None:
            self.final_sweep_time = current_time
            print(f"\nStarting final sweep for last {missing_count} pixels...")
        
        # Final sweep check - directly light up any missing pixels after timeout
        if self.final_sweep_time is not None and current_time - self.final_sweep_time > 2.0:
            missing = self.target_pixels - self.captured_pixels
            if missing:
                print(f"\nFinal sweep - directly lighting {len(missing)} stubborn pixels...")
                for px, py in sorted(missing):
                    self.captured_pixels.add((px, py))
                    if 0 <= px < MATRIX_WIDTH and 0 <= py < MATRIX_HEIGHT:
                        color_index = 1 + ((px + py) % (PALETTE_SIZE - 1))
                        self.text_bitmap[px, py] = color_index
                        print(f"  Force lit: ({px}, {py})")
        
        # Check if animation is complete
        if len(self.captured_pixels) >= len(self.target_pixels):
            # Mark completion time if not already set
            if self.completion_time is None:
                self.completion_time = current_time
                print(f"\nTHEME PARK WAITS completed! Will reset in {self.reset_after_seconds} seconds...")
                print(f"Total pixels captured: {len(self.captured_pixels)}/{len(self.target_pixels)}")
                # Force deactivate all remaining birds
                for bird in self.birds:
                    bird.active = False
                    bird.stuck_counter = 0
            
            # Check if it's time to reset
            if current_time - self.completion_time >= self.reset_after_seconds:
                self.reset_animation()
                return
            
            # Show rainbow wave
            self.update_palette_animation()
            
            # Show countdown occasionally
            if self.frame_count % 90 == 0:
                remaining = self.reset_after_seconds - (current_time - self.completion_time)
                print(f"Resetting in {remaining:.1f} seconds...")
            return
        
        # Spawn new birds only if we haven't captured all pixels
        if len(self.captured_pixels) < len(self.target_pixels):
            if current_time - self.last_spawn_time > SPAWN_INTERVAL:
                # Count active birds
                active_count = sum(1 for bird in self.birds if bird.active)
                
                # Calculate how many pixels we still need
                remaining_pixels = len(self.target_pixels) - len(self.captured_pixels)
                
                # Start with fewer birds to show flocking, increase as needed
                progress = len(self.captured_pixels) / len(self.target_pixels)
                
                if progress < 0.3:  # Early stage - fewer birds for visible flocking
                    max_birds_needed = 30
                elif progress < 0.6:  # Mid stage
                    max_birds_needed = 60
                elif remaining_pixels < 30:  # Final pixels
                    max_birds_needed = min(150, MAX_BIRDS * 0.9)
                elif remaining_pixels < 60:
                    max_birds_needed = min(100, MAX_BIRDS * 0.7)
                else:
                    max_birds_needed = 80
                
                if active_count < max_birds_needed:
                    # Spawn birds in flocks for better swarming behavior
                    spawn_count = min(FLOCK_SPAWN_SIZE, int(max_birds_needed - active_count))
                    edge = random.randint(0, 3)
                    
                    # Base position for the flock
                    if edge == 0:  # Left
                        base_x = -BIRD_SIZE
                        base_y = random.randint(10, MATRIX_HEIGHT - 10)
                    elif edge == 1:  # Right
                        base_x = MATRIX_WIDTH + BIRD_SIZE
                        base_y = random.randint(10, MATRIX_HEIGHT - 10)
                    elif edge == 2:  # Top
                        base_x = random.randint(10, MATRIX_WIDTH - 10)
                        base_y = -BIRD_SIZE
                    else:  # Bottom
                        base_x = random.randint(10, MATRIX_WIDTH - 10)
                        base_y = MATRIX_HEIGHT + BIRD_SIZE
                    
                    spawned = 0
                    inactive_birds = [b for b in self.birds if not b.active]
                    
                    # Spawn a tight group of birds
                    for i, bird in enumerate(inactive_birds[:spawn_count]):
                        # Add small offset to create a cluster
                        offset_x = random.uniform(-3, 3)
                        offset_y = random.uniform(-3, 3)
                        
                        bird.active = True
                        bird.color_index = random.randint(1, PALETTE_SIZE - 1)
                        bird.x = base_x + offset_x
                        bird.y = base_y + offset_y
                        
                        # Give them similar initial velocities for group movement
                        if edge == 0:  # Left
                            bird.vx = BIRD_SPEED * random.uniform(0.8, 1.2)
                            bird.vy = random.uniform(-0.2, 0.2)
                        elif edge == 1:  # Right
                            bird.vx = -BIRD_SPEED * random.uniform(0.8, 1.2)
                            bird.vy = random.uniform(-0.2, 0.2)
                        elif edge == 2:  # Top
                            bird.vx = random.uniform(-0.2, 0.2)
                            bird.vy = BIRD_SPEED * random.uniform(0.8, 1.2)
                        else:  # Bottom
                            bird.vx = random.uniform(-0.2, 0.2)
                            bird.vy = -BIRD_SPEED * random.uniform(0.8, 1.2)
                        
                        spawned += 1
                    
                    if spawned > 0:
                        if self.frame_count % 30 == 0:  # Reduce spawn message frequency
                            print(f"Spawned {spawned} birds, total active: {active_count + spawned}")
                    
                    self.last_spawn_time = current_time
        
        # Find attraction center
        attraction_center = self.find_attraction_center()
        
        # If no pixels left to capture, set attraction to None to encourage dispersal
        if len(self.captured_pixels) >= len(self.target_pixels):
            attraction_center = None
        
        # More aggressive handling for final pixels
        missing_count = len(self.target_pixels) - len(self.captured_pixels)
        if 0 < missing_count <= 30:  # Start earlier
            # For final pixels, directly target them
            missing = list(self.target_pixels - self.captured_pixels)
            if missing:
                # Target multiple missing pixels by cycling through them
                target_index = self.frame_count % len(missing)
                target = missing[target_index]
                attraction_center = target  # Direct coordinate
        
        # Update birds
        for bird in self.birds:
            if bird.active:
                captured = bird.update(self.target_pixels, self.captured_pixels, attraction_center, self.birds)
                
                # Deactivate bird if all pixels are captured
                if len(self.captured_pixels) >= len(self.target_pixels):
                    bird.active = False
                
                # Update sprite position and color
                sprite = self.bird_sprites[bird.sprite_index]
                sprite.x = int(bird.x - BIRD_SIZE // 2)
                sprite.y = int(bird.y - BIRD_SIZE // 2)
                
                # Animate bird color with brighter colors
                hue = (self.animation_time + bird.sprite_index * 0.1) % 1.0
                sprite.pixel_shader[1] = hsv_to_rgb888(hue, 1.0, 1.0)  # Full saturation and brightness
            else:
                # Hide inactive sprites
                sprite = self.bird_sprites[bird.sprite_index]
                sprite.x = -10
                sprite.y = -10
        
        # Update text bitmap with ALL captured pixels (not just new ones)
        # This ensures no pixels are missed due to timing issues
        # Make a copy to avoid concurrent modification
        captured_copy = self.captured_pixels.copy()
        for pixel in captured_copy:
            x, y = pixel
            if 0 <= x < MATRIX_WIDTH and 0 <= y < MATRIX_HEIGHT:
                # Always update to ensure pixel is lit
                if self.text_bitmap[x, y] == 0:  # Only if currently black
                    # Use rainbow color based on position
                    color_index = 1 + ((x + y) % (PALETTE_SIZE - 1))
                    self.text_bitmap[x, y] = color_index
        
        # Update captured text animation
        self.update_palette_animation()
        
        # Ensure all captured pixels are in the bitmap before refresh
        # This is a final safety check
        for px, py in self.captured_pixels:
            if 0 <= px < MATRIX_WIDTH and 0 <= py < MATRIX_HEIGHT:
                if self.text_bitmap[px, py] == 0:
                    # Pixel should be lit but isn't - fix it
                    color_index = 1 + ((px + py) % (PALETTE_SIZE - 1))
                    self.text_bitmap[px, py] = color_index
        
        # Force display refresh for SLDK
        if not CIRCUITPYTHON and self.device:
            self.device.refresh()
        
        # Print progress occasionally
        if self.frame_count % 60 == 0:
            active_birds = sum(1 for b in self.birds if b.active)
            print(f"Progress: {len(self.captured_pixels)}/{len(self.target_pixels)} "
                  f"captured, {active_birds} birds active")
            
            # Debug: Show some active bird positions
            if active_birds > 0:
                sample_bird = next((b for b in self.birds if b.active), None)
                if sample_bird:
                    print(f"  Sample bird at ({sample_bird.x:.1f}, {sample_bird.y:.1f})")
    
    def run(self):
        """Run the animation."""
        print(f"Starting optimized swarm animation...")
        print(f"Target pixels: {len(self.target_pixels)}")
        print(f"Using {'CircuitPython hardware' if CIRCUITPYTHON else 'SLDK simulator'}")
        
        if CIRCUITPYTHON:
            # Hardware main loop
            while True:
                self.update()
                
                # Check for completion
                if len(self.captured_pixels) >= len(self.target_pixels):
                    # Continue showing rainbow effect
                    pass
        else:
            # SLDK simulator with window management
            # We need to ensure the display refreshes each frame
            def update_with_refresh():
                self.update()
                # Ensure the displayio content is rendered to the matrix
                self.device.refresh()
                
            
            self.device.run(
                update_callback=update_with_refresh,
                title="Optimized THEME PARK WAITS Swarm"
            )


def main():
    """Run the optimized swarm animation."""
    # Force garbage collection before starting
    gc.collect()
    
    # Create and run animation
    animation = OptimizedSwarmAnimation()
    animation.run()


if __name__ == "__main__":
    main()