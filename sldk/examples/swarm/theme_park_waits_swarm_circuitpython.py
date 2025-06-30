#!/usr/bin/env python3
"""CircuitPython-compatible swarm animation for MatrixPortal S3.

This version is optimized for the hardware constraints:
- Limited RAM (512KB)
- No true multithreading
- Slower processor

Strategy:
- Use a particle system with arrays instead of objects
- Limit to 30 birds maximum
- Direct bitmap manipulation instead of sprites
- Simplified flocking algorithm
- Pre-calculated text positions
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
MAX_BIRDS = 30  # Limited for memory
BIRD_SPEED = 1.5  # Pixels per frame
TEXT_COLOR = 0xFFFF00  # Yellow
BIRD_COLORS = [
    0xFF0000,  # Red
    0x00FF00,  # Green
    0x0000FF,  # Blue
    0xFF00FF,  # Magenta
    0x00FFFF,  # Cyan
    0xFFFF00,  # Yellow
]

# Pre-calculated THEME PARK WAITS pixel positions (compressed format)
# Format: start_x, y, length for horizontal lines, or x, start_y, end_y for vertical
TEXT_PIXELS = [
    # THEME PARK (y=3-10)
    # T
    (4, 3, 5),   # Top horizontal
    (6, 4, 10),  # Vertical
    # H
    (10, 3, 10), # Left vertical
    (14, 3, 10), # Right vertical
    (11, 6, 3),  # Middle horizontal
    # E
    (16, 3, 10), # Left vertical
    (16, 3, 4),  # Top horizontal
    (16, 6, 3),  # Middle horizontal
    (16, 10, 4), # Bottom horizontal
    # M
    (22, 3, 10), # Left vertical
    (27, 3, 10), # Right vertical
    (23, 4, 1), (24, 5, 1), (25, 5, 1), (26, 4, 1), # M shape
    # E
    (29, 3, 10), # Left vertical
    (29, 3, 4),  # Top horizontal
    (29, 6, 3),  # Middle horizontal
    (29, 10, 4), # Bottom horizontal
    # Space, then P
    (36, 3, 10), # Left vertical
    (36, 3, 4),  # Top horizontal
    (36, 6, 4),  # Middle horizontal
    (39, 4, 5),  # Right vertical (partial)
    # A
    (42, 4, 10), # Left vertical
    (46, 4, 10), # Right vertical
    (43, 3, 3),  # Top horizontal
    (42, 6, 5),  # Middle horizontal
    # R
    (48, 3, 10), # Left vertical
    (48, 3, 4),  # Top horizontal
    (48, 6, 4),  # Middle horizontal
    (51, 4, 5),  # Right vertical (partial)
    (50, 7, 1), (51, 8, 1), (52, 9, 1), (53, 10, 1), # Diagonal
    # K
    (54, 3, 10), # Left vertical
    (57, 3, 1), (56, 4, 1), (55, 5, 1), (55, 6, 1), # Top diagonal
    (56, 7, 1), (57, 8, 1), (58, 9, 1), (59, 10, 1), # Bottom diagonal
    
    # WAITS (y=15-30) - Simplified
    # W - simplified as two verticals
    (5, 15, 30), (6, 15, 30),   # Left
    (13, 15, 30), (14, 15, 30), # Right
    (9, 23, 27), (10, 23, 27),  # Middle V
    # A
    (16, 17, 30), (17, 17, 30), # Left
    (24, 17, 30), (25, 17, 30), # Right
    (18, 15, 6),  # Top horizontal
    (16, 22, 10), # Middle horizontal
    # I
    (27, 15, 10), # Top horizontal
    (31, 15, 30), (32, 15, 30), # Middle vertical
    (27, 29, 10), # Bottom horizontal
    # T
    (38, 15, 10), # Top horizontal
    (42, 15, 30), (43, 15, 30), # Middle vertical
    # S - simplified
    (49, 15, 10), # Top
    (49, 17, 5),  # Left top
    (49, 22, 10), # Middle
    (57, 24, 5),  # Right bottom
    (49, 29, 10), # Bottom
]


class ParticleSwarm:
    """Lightweight particle system for bird swarm."""
    
    def __init__(self, matrix_width=64, matrix_height=32):
        self.width = matrix_width
        self.height = matrix_height
        
        # Particle arrays (structure of arrays for memory efficiency)
        self.x = [0.0] * MAX_BIRDS
        self.y = [0.0] * MAX_BIRDS
        self.vx = [0.0] * MAX_BIRDS
        self.vy = [0.0] * MAX_BIRDS
        self.color_index = [0] * MAX_BIRDS
        self.active = [False] * MAX_BIRDS
        self.num_active = 0
        
        # Target pixels
        self.target_pixels = self._expand_text_pixels()
        self.captured_pixels = set()
        
        # Timing
        self.last_spawn = 0
        self.spawn_interval = 2.0  # Seconds between spawns
        
    def _expand_text_pixels(self):
        """Expand compressed text format to set of (x, y) tuples."""
        pixels = set()
        for item in TEXT_PIXELS:
            if len(item) == 3:
                if item[2] <= 15:  # Horizontal line
                    for x in range(item[0], item[0] + item[2]):
                        pixels.add((x, item[1]))
                else:  # Vertical line
                    for y in range(item[1], item[2]):
                        pixels.add((item[0], y))
        return pixels
    
    def spawn_birds(self, count=5):
        """Spawn new birds from screen edge."""
        if self.num_active + count > MAX_BIRDS:
            count = MAX_BIRDS - self.num_active
            
        if count <= 0:
            return
            
        # Choose random edge
        edge = random.randint(0, 3)
        
        for i in range(MAX_BIRDS):
            if not self.active[i] and count > 0:
                self.active[i] = True
                self.color_index[i] = random.randint(0, len(BIRD_COLORS) - 1)
                
                # Set position based on edge
                if edge == 0:  # Left
                    self.x[i] = -2
                    self.y[i] = random.randint(0, self.height - 1)
                    self.vx[i] = BIRD_SPEED
                    self.vy[i] = random.uniform(-0.5, 0.5)
                elif edge == 1:  # Right
                    self.x[i] = self.width + 2
                    self.y[i] = random.randint(0, self.height - 1)
                    self.vx[i] = -BIRD_SPEED
                    self.vy[i] = random.uniform(-0.5, 0.5)
                elif edge == 2:  # Top
                    self.x[i] = random.randint(0, self.width - 1)
                    self.y[i] = -2
                    self.vx[i] = random.uniform(-0.5, 0.5)
                    self.vy[i] = BIRD_SPEED
                else:  # Bottom
                    self.x[i] = random.randint(0, self.width - 1)
                    self.y[i] = self.height + 2
                    self.vx[i] = random.uniform(-0.5, 0.5)
                    self.vy[i] = -BIRD_SPEED
                    
                count -= 1
                self.num_active += 1
                
    def update(self):
        """Update particle positions with simple flocking."""
        current_time = time.monotonic()
        
        # Spawn new birds periodically
        if current_time - self.last_spawn > self.spawn_interval:
            remaining = len(self.target_pixels) - len(self.captured_pixels)
            if remaining > 0:
                spawn_count = min(5, remaining // 10 + 1)
                self.spawn_birds(spawn_count)
                self.last_spawn = current_time
        
        # Update each active bird
        for i in range(MAX_BIRDS):
            if not self.active[i]:
                continue
                
            # Simple attraction to nearest missing pixel
            if self.target_pixels - self.captured_pixels:
                closest_dist = float('inf')
                target_x, target_y = self.x[i], self.y[i]
                
                # Find closest missing pixel (limited search for performance)
                search_count = 0
                for px, py in self.target_pixels - self.captured_pixels:
                    if search_count > 20:  # Limit search
                        break
                    dist = abs(self.x[i] - px) + abs(self.y[i] - py)  # Manhattan distance
                    if dist < closest_dist:
                        closest_dist = dist
                        target_x, target_y = px, py
                    search_count += 1
                
                # Steer toward target
                if closest_dist < 30:
                    dx = target_x - self.x[i]
                    dy = target_y - self.y[i]
                    if abs(dx) > 0.1:
                        self.vx[i] += 0.1 if dx > 0 else -0.1
                    if abs(dy) > 0.1:
                        self.vy[i] += 0.1 if dy > 0 else -0.1
            
            # Limit velocity
            speed = math.sqrt(self.vx[i]**2 + self.vy[i]**2)
            if speed > BIRD_SPEED:
                self.vx[i] = (self.vx[i] / speed) * BIRD_SPEED
                self.vy[i] = (self.vy[i] / speed) * BIRD_SPEED
            
            # Update position
            self.x[i] += self.vx[i]
            self.y[i] += self.vy[i]
            
            # Check for pixel capture
            px, py = int(self.x[i]), int(self.y[i])
            if (px, py) in self.target_pixels and (px, py) not in self.captured_pixels:
                self.captured_pixels.add((px, py))
                self.active[i] = False
                self.num_active -= 1
                
            # Remove if off screen
            elif (self.x[i] < -5 or self.x[i] > self.width + 5 or
                  self.y[i] < -5 or self.y[i] > self.height + 5):
                self.active[i] = False
                self.num_active -= 1
                
    def draw(self, bitmap):
        """Draw particles to bitmap."""
        # Clear bitmap
        bitmap.fill(0)
        
        # Draw captured text pixels
        for x, y in self.captured_pixels:
            if 0 <= x < self.width and 0 <= y < self.height:
                bitmap[x, y] = 1  # Palette index for yellow
        
        # Draw active birds
        for i in range(MAX_BIRDS):
            if self.active[i]:
                x, y = int(self.x[i]), int(self.y[i])
                if 0 <= x < self.width and 0 <= y < self.height:
                    # Use color palette index (2-7 for bird colors)
                    bitmap[x, y] = self.color_index[i] + 2


def run_swarm_animation():
    """Run the swarm animation on MatrixPortal S3."""
    if CIRCUITPYTHON:
        # Initialize matrix
        matrix = Matrix(width=64, height=32, bit_depth=4)
        display = matrix.display
        
        # Create main group
        main_group = displayio.Group()
        
        # Create bitmap and palette
        bitmap = displayio.Bitmap(64, 32, 8)  # 8 colors max
        palette = displayio.Palette(8)
        palette[0] = 0x000000  # Black background
        palette[1] = TEXT_COLOR  # Yellow for text
        # Bird colors
        for i, color in enumerate(BIRD_COLORS):
            palette[i + 2] = color
            
        # Create TileGrid
        tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
        main_group.append(tile_grid)
        
        # Show on display
        display.root_group = main_group
        
        # Create swarm
        swarm = ParticleSwarm(64, 32)
        
        # Main loop
        while True:
            swarm.update()
            swarm.draw(bitmap)
            
            # Check if animation complete
            if len(swarm.captured_pixels) >= len(swarm.target_pixels):
                # Hold for 2 seconds then restart
                time.sleep(2)
                swarm.captured_pixels.clear()
                gc.collect()  # Force garbage collection
                
            time.sleep(0.05)  # ~20 FPS
    else:
        print("This code is designed for CircuitPython on MatrixPortal S3")
        print("Use the full swarm animation in the simulator instead")


if __name__ == "__main__":
    run_swarm_animation()