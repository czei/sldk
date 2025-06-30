#!/usr/bin/env python3
"""Advanced hybrid swarm animation for MatrixPortal S3.

This version combines multiple techniques for the best visual effect
while maintaining performance on the MatrixPortal S3:
- Sprite pooling for active birds
- Bitmap manipulation for particle trails
- Color animation using palettes
- Memory-efficient data structures
"""

import random
import math
import time
import gc
import array

# CircuitPython imports
try:
    import board
    import displayio
    from adafruit_matrixportal.matrix import Matrix
    from adafruit_display_text import label
    from adafruit_bitmap_font import bitmap_font
    CIRCUITPYTHON = True
except ImportError:
    CIRCUITPYTHON = False
    print("Running in simulator mode")

# Configuration
SPRITE_POOL_SIZE = 15  # Number of sprite birds
PARTICLE_COUNT = 10    # Additional simple particles
TRAIL_LENGTH = 3       # Fade trail behind birds
FPS = 20              # Target frame rate

# Pre-calculated sine table for smooth motion (saves computation)
SINE_TABLE = array.array('f', [math.sin(i * math.pi / 180) for i in range(360)])


class SwarmAnimation:
    """Advanced swarm animation with multiple visual effects."""
    
    def __init__(self, width=64, height=32):
        self.width = width
        self.height = height
        
        if CIRCUITPYTHON:
            # Initialize display
            self.matrix = Matrix(width=width, height=height, bit_depth=6)
            self.display = self.matrix.display
            
            # Create display groups
            self.main_group = displayio.Group()
            
            # Layer 1: Trail effect bitmap
            self.trail_bitmap = displayio.Bitmap(width, height, 8)
            self.trail_palette = displayio.Palette(8)
            self._init_trail_palette()
            self.trail_grid = displayio.TileGrid(
                self.trail_bitmap, 
                pixel_shader=self.trail_palette
            )
            self.main_group.append(self.trail_grid)
            
            # Layer 2: Captured text bitmap
            self.text_bitmap = displayio.Bitmap(width, height, 2)
            self.text_palette = displayio.Palette(2)
            self.text_palette[0] = 0x000000  # Transparent
            self.text_palette[1] = 0xFFFF00  # Yellow
            self.text_grid = displayio.TileGrid(
                self.text_bitmap,
                pixel_shader=self.text_palette
            )
            self.main_group.append(self.text_grid)
            
            # Layer 3: Sprite birds
            self.sprite_group = displayio.Group()
            self.main_group.append(self.sprite_group)
            
            # Create sprite pool
            self._create_sprite_pool()
            
            # Show on display
            self.display.root_group = self.main_group
        
        # Animation state
        self.target_pixels = self._create_text_pixels()
        self.captured_pixels = set()
        self.animation_time = 0
        self.last_spawn = 0
        
        # Particle system for extra effects
        self.particles = []
        for _ in range(PARTICLE_COUNT):
            self.particles.append({
                'x': 0.0, 'y': 0.0,
                'vx': 0.0, 'vy': 0.0,
                'life': 0, 'active': False
            })
            
    def _init_trail_palette(self):
        """Initialize trail palette with fading colors."""
        self.trail_palette[0] = 0x000000  # Black (background)
        # Fading bird trail colors
        for i in range(1, 8):
            # Fade from bright to dark
            intensity = int(255 * (8 - i) / 8)
            # Different hues for variety
            if i < 3:
                # Red trail
                self.trail_palette[i] = (intensity << 16)
            elif i < 5:
                # Green trail
                self.trail_palette[i] = (intensity << 8)
            else:
                # Blue trail
                self.trail_palette[i] = intensity
                
    def _create_sprite_pool(self):
        """Create reusable sprite pool."""
        # Bird shape (5x5 with wing animation)
        bird_shapes = [
            # Frame 1: Wings up
            [
                [0, 1, 0, 1, 0],
                [1, 1, 1, 1, 1],
                [0, 1, 1, 1, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 0, 0, 0]
            ],
            # Frame 2: Wings middle
            [
                [0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1],
                [0, 1, 1, 1, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 0, 0, 0]
            ],
            # Frame 3: Wings down
            [
                [0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 1, 1, 1, 0],
                [1, 1, 1, 1, 1],
                [0, 1, 0, 1, 0]
            ]
        ]
        
        # Create animated bird bitmap
        self.bird_bitmap = displayio.Bitmap(5, 5 * 3, 2)  # 3 frames stacked
        for frame_idx, frame in enumerate(bird_shapes):
            for y in range(5):
                for x in range(5):
                    self.bird_bitmap[x, y + frame_idx * 5] = frame[y][x]
        
        # Create sprites
        self.sprites = []
        self.sprite_birds = []
        
        for i in range(SPRITE_POOL_SIZE):
            # Dynamic palette for each bird
            palette = displayio.Palette(2)
            palette[0] = 0x000000  # Transparent
            palette[1] = 0xFF0000  # Will be animated
            
            sprite = displayio.TileGrid(
                self.bird_bitmap,
                pixel_shader=palette,
                width=1,
                height=1,
                tile_width=5,
                tile_height=5,
                default_tile=0,
                x=-10,
                y=-10
            )
            
            self.sprites.append(sprite)
            self.sprite_group.append(sprite)
            
            # Bird data
            self.sprite_birds.append({
                'x': 0.0, 'y': 0.0,
                'vx': 0.0, 'vy': 0.0,
                'active': False,
                'phase': random.randint(0, 359),
                'frame': 0,
                'target': None
            })
            
    def _create_text_pixels(self):
        """Create target pixel set for THEME PARK WAITS."""
        pixels = set()
        
        # Simplified but recognizable text
        # Using compact representation
        text_data = [
            # THEME
            "##### #   # ##### #   # #####",
            "  #   #   # #     ## ## #    ",
            "  #   ##### ####  # # # #### ",
            "  #   #   # #     #   # #    ",
            "  #   #   # ##### #   # #####",
            "",
            # PARK
            "####  ##### ####  #   #",
            "#   # #   # #   # #  # ",
            "####  ##### ####  ### ",
            "#     #   # #   # #  # ",
            "#     #   # #   # #   #",
            "",
            # WAITS
            "#   #  ###  ##### ##### #####",
            "#   # #   #   #     #   #    ",
            "# # # #####   #     #   #### ",
            "## ## #   #   #     #       #",
            "#   # #   # #####   #   #####"
        ]
        
        # Convert to pixels
        y_offset = 3
        for line_idx, line in enumerate(text_data):
            if line:  # Skip empty lines
                y = y_offset + (line_idx % 6)
                for x, char in enumerate(line):
                    if char == '#':
                        # Adjust x position for centering
                        pixels.add((x + 2, y))
                        
            if line_idx == 5:  # After THEME
                y_offset = 12
            elif line_idx == 11:  # After PARK
                y_offset = 20
                
        return pixels
        
    def spawn_bird(self):
        """Spawn a new bird from screen edge."""
        # Find inactive sprite
        for i, bird in enumerate(self.sprite_birds):
            if not bird['active']:
                bird['active'] = True
                
                # Random edge spawn
                edge = random.randint(0, 3)
                if edge == 0:  # Left
                    bird['x'] = -5.0
                    bird['y'] = random.uniform(5, self.height - 5)
                    bird['vx'] = random.uniform(0.8, 1.2)
                    bird['vy'] = random.uniform(-0.3, 0.3)
                elif edge == 1:  # Right
                    bird['x'] = self.width + 5.0
                    bird['y'] = random.uniform(5, self.height - 5)
                    bird['vx'] = random.uniform(-1.2, -0.8)
                    bird['vy'] = random.uniform(-0.3, 0.3)
                elif edge == 2:  # Top
                    bird['x'] = random.uniform(5, self.width - 5)
                    bird['y'] = -5.0
                    bird['vx'] = random.uniform(-0.3, 0.3)
                    bird['vy'] = random.uniform(0.8, 1.2)
                else:  # Bottom
                    bird['x'] = random.uniform(5, self.width - 5)
                    bird['y'] = self.height + 5.0
                    bird['vx'] = random.uniform(-0.3, 0.3)
                    bird['vy'] = random.uniform(-1.2, -0.8)
                    
                # Assign target
                uncaptured = list(self.target_pixels - self.captured_pixels)
                if uncaptured:
                    bird['target'] = random.choice(uncaptured)
                    
                break
                
    def spawn_particle(self, x, y):
        """Spawn a particle effect."""
        for particle in self.particles:
            if not particle['active']:
                particle['x'] = x
                particle['y'] = y
                particle['vx'] = random.uniform(-1, 1)
                particle['vy'] = random.uniform(-1, 1)
                particle['life'] = 10
                particle['active'] = True
                break
                
    def update(self):
        """Update animation state."""
        self.animation_time += 1
        
        # Spawn new birds periodically
        if self.animation_time % 40 == 0:  # Every 2 seconds at 20 FPS
            if len(self.captured_pixels) < len(self.target_pixels):
                self.spawn_bird()
                
        # Fade trails
        if CIRCUITPYTHON and self.animation_time % 2 == 0:
            for y in range(self.height):
                for x in range(self.width):
                    pixel = self.trail_bitmap[x, y]
                    if pixel > 0:
                        self.trail_bitmap[x, y] = max(0, pixel - 1)
                        
        # Update sprite birds
        for i, bird in enumerate(self.sprite_birds):
            if not bird['active']:
                continue
                
            # Flocking behavior toward target
            if bird['target'] and bird['target'] not in self.captured_pixels:
                tx, ty = bird['target']
                dx = tx - bird['x']
                dy = ty - bird['y']
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist > 1:
                    # Accelerate toward target
                    bird['vx'] += (dx / dist) * 0.15
                    bird['vy'] += (dy / dist) * 0.15
                    
                    # Add sine wave motion
                    phase_rad = bird['phase'] * math.pi / 180
                    bird['vx'] += math.sin(phase_rad) * 0.05
                    bird['vy'] += math.cos(phase_rad) * 0.05
                    bird['phase'] = (bird['phase'] + 5) % 360
                else:
                    # Capture pixel
                    self.captured_pixels.add((tx, ty))
                    if CIRCUITPYTHON:
                        self.text_bitmap[tx, ty] = 1
                    self.spawn_particle(tx, ty)
                    bird['active'] = False
                    self.sprites[i].x = -10
                    self.sprites[i].y = -10
                    continue
            else:
                # Find new target
                uncaptured = list(self.target_pixels - self.captured_pixels)
                if uncaptured:
                    bird['target'] = random.choice(uncaptured)
                    
            # Limit speed
            speed = math.sqrt(bird['vx']**2 + bird['vy']**2)
            if speed > 1.5:
                bird['vx'] = (bird['vx'] / speed) * 1.5
                bird['vy'] = (bird['vy'] / speed) * 1.5
                
            # Update position
            bird['x'] += bird['vx']
            bird['y'] += bird['vy']
            
            # Update sprite
            if CIRCUITPYTHON:
                self.sprites[i].x = int(bird['x']) - 2
                self.sprites[i].y = int(bird['y']) - 2
                
                # Animate wings
                bird['frame'] = (bird['frame'] + 1) % 15
                self.sprites[i][0] = bird['frame'] // 5
                
                # Animate color
                hue = (self.animation_time * 3 + bird['phase']) % 360
                r = int(abs(SINE_TABLE[(hue) % 360]) * 255)
                g = int(abs(SINE_TABLE[(hue + 120) % 360]) * 255)
                b = int(abs(SINE_TABLE[(hue + 240) % 360]) * 255)
                color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                self.sprites[i].pixel_shader[1] = color
                
                # Draw trail
                px, py = int(bird['x']), int(bird['y'])
                if 0 <= px < self.width and 0 <= py < self.height:
                    # Color-coded trails
                    trail_color = 1 + (i % 3) * 2 + 1
                    self.trail_bitmap[px, py] = trail_color
                    
            # Deactivate if off screen
            if (bird['x'] < -10 or bird['x'] > self.width + 10 or
                bird['y'] < -10 or bird['y'] > self.height + 10):
                bird['active'] = False
                if CIRCUITPYTHON:
                    self.sprites[i].x = -10
                    self.sprites[i].y = -10
                    
        # Update particles
        for particle in self.particles:
            if particle['active']:
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                particle['vy'] += 0.1  # Gravity
                particle['life'] -= 1
                
                if particle['life'] <= 0:
                    particle['active'] = False
                elif CIRCUITPYTHON:
                    # Draw particle
                    px, py = int(particle['x']), int(particle['y'])
                    if 0 <= px < self.width and 0 <= py < self.height:
                        self.trail_bitmap[px, py] = 7  # Bright particle
                        
        # Check completion
        if len(self.captured_pixels) >= len(self.target_pixels):
            # Victory animation
            if CIRCUITPYTHON:
                for i in range(60):  # 3 seconds
                    # Rainbow text
                    hue = (i * 6) % 360
                    r = int(abs(SINE_TABLE[hue]) * 255)
                    g = int(abs(SINE_TABLE[(hue + 120) % 360]) * 255)
                    b = int(abs(SINE_TABLE[(hue + 240) % 360]) * 255)
                    self.text_palette[1] = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                    time.sleep(0.05)
                    
            # Reset
            self.captured_pixels.clear()
            if CIRCUITPYTHON:
                self.text_bitmap.fill(0)
                self.trail_bitmap.fill(0)
                self.text_palette[1] = 0xFFFF00
            gc.collect()
            
            
def run_advanced_swarm():
    """Run the advanced swarm animation."""
    if not CIRCUITPYTHON:
        print("This advanced version requires CircuitPython on MatrixPortal S3")
        print("Features demonstrated:")
        print("- Sprite pooling with wing animation")
        print("- Particle trail effects")
        print("- Dynamic color animation")
        print("- Memory-efficient flocking")
        return
        
    animation = SwarmAnimation()
    
    # Main loop
    while True:
        start_time = time.monotonic()
        
        animation.update()
        
        # Maintain frame rate
        elapsed = time.monotonic() - start_time
        sleep_time = (1.0 / FPS) - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)
            

if __name__ == "__main__":
    run_advanced_swarm()