"""
Simplified demo for MatrixPortal S3 - Memory-safe version
Use this if the main demo has memory issues
"""

import gc
import time
import random
import displayio
from adafruit_matrixportal.matrix import Matrix

# Initialize display
matrix = Matrix(width=64, height=32, bit_depth=4)
display = matrix.display

print("MatrixPortal S3 Swarm Demo (Simple)")
print(f"Free memory: {gc.mem_free()} bytes")

# Create main display group
main_group = displayio.Group()

# Create bitmap and palette
bitmap = displayio.Bitmap(64, 32, 4)
palette = displayio.Palette(4)
palette[0] = 0x000000  # Black
palette[1] = 0xFFFF00  # Yellow
palette[2] = 0xFF0000  # Red
palette[3] = 0x00FF00  # Green

tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
main_group.append(tile_grid)
display.show(main_group)

# Simple particle system
MAX_BIRDS = 20
birds = []
for i in range(MAX_BIRDS):
    birds.append({
        'x': -5.0,
        'y': -5.0,
        'vx': 0.0,
        'vy': 0.0,
        'active': False
    })

# Target pattern - simple X
targets = set()
for i in range(8):
    targets.add((28 + i, 12 + i))
    targets.add((28 + i, 19 - i))
    targets.add((36 - i, 12 + i))
    targets.add((36 - i, 19 - i))

captured = set()
spawn_timer = 0
frame_count = 0

while True:
    frame_count += 1
    current_time = time.monotonic()
    
    # Spawn birds every 0.5 seconds
    if current_time - spawn_timer > 0.5:
        for bird in birds:
            if not bird['active'] and len(captured) < len(targets):
                bird['active'] = True
                # Random edge spawn
                edge = random.randint(0, 3)
                if edge == 0:  # Top
                    bird['x'] = random.uniform(10, 54)
                    bird['y'] = -2.0
                    bird['vx'] = random.uniform(-0.5, 0.5)
                    bird['vy'] = 1.0
                elif edge == 1:  # Bottom
                    bird['x'] = random.uniform(10, 54)
                    bird['y'] = 34.0
                    bird['vx'] = random.uniform(-0.5, 0.5)
                    bird['vy'] = -1.0
                elif edge == 2:  # Left
                    bird['x'] = -2.0
                    bird['y'] = random.uniform(5, 27)
                    bird['vx'] = 1.0
                    bird['vy'] = random.uniform(-0.5, 0.5)
                else:  # Right
                    bird['x'] = 66.0
                    bird['y'] = random.uniform(5, 27)
                    bird['vx'] = -1.0
                    bird['vy'] = random.uniform(-0.5, 0.5)
                spawn_timer = current_time
                break
    
    # Clear bitmap
    bitmap.fill(0)
    
    # Draw captured pixels
    for x, y in captured:
        bitmap[x, y] = 1
    
    # Update birds
    for bird in birds:
        if bird['active']:
            # Find nearest uncaptured target
            min_dist = 100
            target_x = target_y = None
            
            for tx, ty in targets:
                if (tx, ty) not in captured:
                    dist = abs(bird['x'] - tx) + abs(bird['y'] - ty)
                    if dist < min_dist:
                        min_dist = dist
                        target_x, target_y = tx, ty
            
            # Steer toward target
            if target_x is not None and min_dist < 20:
                dx = target_x - bird['x']
                dy = target_y - bird['y']
                
                if abs(dx) > 0.5:
                    bird['vx'] += 0.1 if dx > 0 else -0.1
                if abs(dy) > 0.5:
                    bird['vy'] += 0.1 if dy > 0 else -0.1
            
            # Limit velocity
            max_speed = 1.5
            vx, vy = bird['vx'], bird['vy']
            speed = (vx * vx + vy * vy) ** 0.5
            if speed > max_speed:
                bird['vx'] = vx / speed * max_speed
                bird['vy'] = vy / speed * max_speed
            
            # Update position
            bird['x'] += bird['vx']
            bird['y'] += bird['vy']
            
            # Draw bird
            x, y = int(bird['x']), int(bird['y'])
            if 0 <= x < 64 and 0 <= y < 32:
                # Alternate colors
                bitmap[x, y] = 2 if frame_count % 20 < 10 else 3
            
            # Check capture
            if (x, y) in targets and (x, y) not in captured:
                captured.add((x, y))
                bird['active'] = False
            
            # Deactivate if off screen
            elif bird['x'] < -5 or bird['x'] > 69 or bird['y'] < -5 or bird['y'] > 37:
                bird['active'] = False
    
    # Reset when complete
    if len(captured) >= len(targets):
        # Flash effect
        for i in range(10):
            palette[1] = 0xFFFF00 if i % 2 == 0 else 0x00FFFF
            time.sleep(0.1)
        palette[1] = 0xFFFF00
        
        # Clear and restart
        captured.clear()
        for bird in birds:
            bird['active'] = False
        time.sleep(1)
    
    # Print memory usage periodically
    if frame_count % 100 == 0:
        print(f"Frame {frame_count}, Free memory: {gc.mem_free()} bytes")
        gc.collect()
    
    # Frame rate control
    time.sleep(0.05)  # 20 FPS