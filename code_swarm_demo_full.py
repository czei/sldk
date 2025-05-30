"""
Demo program for MatrixPortal S3 - Runs all three swarm animation versions
Copy this file to CIRCUITPY/code.py on your MatrixPortal S3
"""

import gc
import time
import displayio
import terminalio
from adafruit_matrixportal.matrix import Matrix
from adafruit_display_text import label

# Initialize display
matrix = Matrix(width=64, height=32, bit_depth=4)
display = matrix.display

def show_text_screen(text_lines, duration=3):
    """Display text message on screen."""
    text_group = displayio.Group()
    
    # Create background
    background = displayio.Bitmap(64, 32, 1)
    bg_palette = displayio.Palette(1)
    bg_palette[0] = 0x000000  # Black
    text_group.append(displayio.TileGrid(background, pixel_shader=bg_palette))
    
    # Add text lines
    y_positions = [8, 16, 24] if len(text_lines) <= 3 else [6, 12, 18, 24]
    colors = [0x00FF00, 0xFFFF00, 0x00FFFF, 0xFF00FF]  # Green, Yellow, Cyan, Magenta
    
    for i, line in enumerate(text_lines[:4]):  # Max 4 lines
        text_label = label.Label(
            terminalio.FONT,
            text=line,
            color=colors[i % len(colors)],
            x=2,
            y=y_positions[i] if i < len(y_positions) else 24
        )
        text_group.append(text_label)
    
    display.show(text_group)
    time.sleep(duration)
    
    # Clean up
    while len(text_group) > 0:
        text_group.pop()
    gc.collect()


def run_particle_swarm_demo():
    """Run the lightweight particle system version."""
    show_text_screen([
        "PARTICLE",
        "SWARM",
        "30 birds",
        "Low RAM"
    ], 3)
    
    # Import and run particle system version
    try:
        # Import inline to save memory
        import random
        import math
        
        # Simplified particle system for demo
        MAX_BIRDS = 25
        
        # Create display elements
        main_group = displayio.Group()
        bitmap = displayio.Bitmap(64, 32, 4)
        palette = displayio.Palette(4)
        palette[0] = 0x000000  # Black
        palette[1] = 0xFFFF00  # Yellow text
        palette[2] = 0xFF0000  # Red birds
        palette[3] = 0x00FF00  # Green birds
        
        tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
        main_group.append(tile_grid)
        display.show(main_group)
        
        # Simple particle arrays
        x = [0.0] * MAX_BIRDS
        y = [0.0] * MAX_BIRDS
        vx = [0.0] * MAX_BIRDS
        vy = [0.0] * MAX_BIRDS
        active = [False] * MAX_BIRDS
        
        # Simple text "DEMO" to capture
        target_pixels = set()
        # D
        for i in range(6): target_pixels.add((10, 13+i))
        for i in range(3): target_pixels.add((11+i, 13))
        for i in range(3): target_pixels.add((11+i, 18))
        target_pixels.add((13, 14))
        target_pixels.add((13, 15))
        target_pixels.add((13, 16))
        target_pixels.add((13, 17))
        # E
        for i in range(6): target_pixels.add((16, 13+i))
        for i in range(3): target_pixels.add((17+i, 13))
        for i in range(2): target_pixels.add((17+i, 15))
        for i in range(3): target_pixels.add((17+i, 18))
        # M
        for i in range(6): target_pixels.add((21, 13+i))
        for i in range(6): target_pixels.add((25, 13+i))
        target_pixels.add((22, 14))
        target_pixels.add((23, 15))
        target_pixels.add((24, 14))
        # O
        for i in range(6): target_pixels.add((28, 13+i))
        for i in range(6): target_pixels.add((31, 13+i))
        for i in range(2): target_pixels.add((29+i, 13))
        for i in range(2): target_pixels.add((29+i, 18))
        
        captured = set()
        spawn_time = 0
        demo_time = 0
        
        # Run for 10 seconds
        start_time = time.monotonic()
        while time.monotonic() - start_time < 10:
            current_time = time.monotonic()
            
            # Spawn birds
            if current_time - spawn_time > 0.5 and len(captured) < len(target_pixels):
                for i in range(MAX_BIRDS):
                    if not active[i]:
                        active[i] = True
                        # Spawn from edges
                        edge = random.randint(0, 3)
                        if edge == 0:  # Left
                            x[i] = -2
                            y[i] = random.randint(5, 26)
                            vx[i] = 1.5
                            vy[i] = random.uniform(-0.3, 0.3)
                        elif edge == 1:  # Right
                            x[i] = 66
                            y[i] = random.randint(5, 26)
                            vx[i] = -1.5
                            vy[i] = random.uniform(-0.3, 0.3)
                        elif edge == 2:  # Top
                            x[i] = random.randint(10, 54)
                            y[i] = -2
                            vx[i] = random.uniform(-0.3, 0.3)
                            vy[i] = 1.5
                        else:  # Bottom
                            x[i] = random.randint(10, 54)
                            y[i] = 34
                            vx[i] = random.uniform(-0.3, 0.3)
                            vy[i] = -1.5
                        spawn_time = current_time
                        break
            
            # Update birds
            bitmap.fill(0)
            
            # Draw captured text
            for px, py in captured:
                bitmap[px, py] = 1
            
            # Update and draw birds
            for i in range(MAX_BIRDS):
                if active[i]:
                    # Find nearest target
                    if target_pixels - captured:
                        min_dist = 100
                        target_x = target_y = 0
                        for tx, ty in target_pixels - captured:
                            dist = abs(x[i] - tx) + abs(y[i] - ty)
                            if dist < min_dist:
                                min_dist = dist
                                target_x, target_y = tx, ty
                        
                        # Steer toward target
                        if min_dist < 20:
                            dx = target_x - x[i]
                            dy = target_y - y[i]
                            if abs(dx) > 0.5:
                                vx[i] += 0.1 if dx > 0 else -0.1
                            if abs(dy) > 0.5:
                                vy[i] += 0.1 if dy > 0 else -0.1
                    
                    # Update position
                    x[i] += vx[i]
                    y[i] += vy[i]
                    
                    # Draw bird
                    px, py = int(x[i]), int(y[i])
                    if 0 <= px < 64 and 0 <= py < 32:
                        bitmap[px, py] = 2 + (i % 2)  # Alternate colors
                    
                    # Check capture
                    if (px, py) in target_pixels and (px, py) not in captured:
                        captured.add((px, py))
                        active[i] = False
                    
                    # Remove if off screen
                    if x[i] < -5 or x[i] > 69 or y[i] < -5 or y[i] > 37:
                        active[i] = False
            
            # Reset if complete
            if len(captured) >= len(target_pixels):
                time.sleep(1)
                captured.clear()
                bitmap.fill(0)
            
            time.sleep(0.05)
        
    except Exception as e:
        show_text_screen(["PARTICLE", "ERROR:", str(e)[:10]], 2)
    
    gc.collect()


def run_sprite_swarm_demo():
    """Run the sprite-based version."""
    show_text_screen([
        "SPRITE",
        "SWARM", 
        "Smooth",
        "Colors"
    ], 3)
    
    try:
        import random
        import math
        
        # Create display
        main_group = displayio.Group()
        
        # Background for text
        text_bitmap = displayio.Bitmap(64, 32, 2)
        text_palette = displayio.Palette(2)
        text_palette[0] = 0x000000
        text_palette[1] = 0xFFFF00
        main_group.append(displayio.TileGrid(text_bitmap, pixel_shader=text_palette))
        
        # Sprite group
        sprite_group = displayio.Group()
        main_group.append(sprite_group)
        
        # Create bird sprites (3x3)
        bird_bitmap = displayio.Bitmap(3, 3, 2)
        bird_bitmap[1, 0] = 1  # Top
        bird_bitmap[0, 1] = 1  # Left
        bird_bitmap[1, 1] = 1  # Center
        bird_bitmap[2, 1] = 1  # Right
        bird_bitmap[1, 2] = 1  # Bottom
        
        # Create sprite pool
        MAX_SPRITES = 15
        sprites = []
        birds = []
        
        for i in range(MAX_SPRITES):
            palette = displayio.Palette(2)
            palette[0] = 0x000000
            palette[1] = 0xFF0000  # Will animate
            
            sprite = displayio.TileGrid(
                bird_bitmap,
                pixel_shader=palette,
                x=-10, y=-10
            )
            sprites.append(sprite)
            sprite_group.append(sprite)
            
            birds.append({
                'x': 0.0, 'y': 0.0,
                'vx': 0.0, 'vy': 0.0,
                'active': False,
                'hue': random.randint(0, 359)
            })
        
        display.show(main_group)
        
        # Simple "HI" text
        target_pixels = set()
        # H
        for i in range(7): target_pixels.add((20, 12+i))
        for i in range(7): target_pixels.add((24, 12+i))
        for i in range(3): target_pixels.add((21+i, 15))
        # I
        for i in range(5): target_pixels.add((27+i, 12))
        for i in range(5): target_pixels.add((27+i, 18))
        for i in range(7): target_pixels.add((29, 12+i))
        
        captured = set()
        spawn_time = 0
        animation_time = 0
        
        # Run for 10 seconds
        start_time = time.monotonic()
        while time.monotonic() - start_time < 10:
            animation_time += 1
            
            # Spawn birds
            if animation_time % 20 == 0 and len(captured) < len(target_pixels):
                for i, bird in enumerate(birds):
                    if not bird['active']:
                        bird['active'] = True
                        edge = random.randint(0, 3)
                        if edge == 0:  # Left
                            bird['x'] = -3.0
                            bird['y'] = float(random.randint(10, 22))
                            bird['vx'] = 1.0
                            bird['vy'] = random.uniform(-0.2, 0.2)
                        else:  # Right for simplicity
                            bird['x'] = 67.0
                            bird['y'] = float(random.randint(10, 22))
                            bird['vx'] = -1.0
                            bird['vy'] = random.uniform(-0.2, 0.2)
                        break
            
            # Update birds
            for i, bird in enumerate(birds):
                if bird['active']:
                    # Simple targeting
                    remaining = target_pixels - captured
                    if remaining:
                        # Find closest
                        min_dist = 100
                        for tx, ty in remaining:
                            dist = abs(bird['x'] - tx) + abs(bird['y'] - ty)
                            if dist < min_dist:
                                min_dist = dist
                                target_x, target_y = tx, ty
                        
                        # Steer
                        if min_dist < 15:
                            dx = target_x - bird['x']
                            dy = target_y - bird['y']
                            bird['vx'] += 0.05 if dx > 0 else -0.05
                            bird['vy'] += 0.05 if dy > 0 else -0.05
                    
                    # Limit speed
                    speed = math.sqrt(bird['vx']**2 + bird['vy']**2)
                    if speed > 1.2:
                        bird['vx'] *= 1.2 / speed
                        bird['vy'] *= 1.2 / speed
                    
                    # Update position
                    bird['x'] += bird['vx']
                    bird['y'] += bird['vy']
                    
                    # Update sprite
                    sprites[i].x = int(bird['x']) - 1
                    sprites[i].y = int(bird['y']) - 1
                    
                    # Animate color
                    bird['hue'] = (bird['hue'] + 3) % 360
                    h = bird['hue'] / 60.0
                    x = 1 - abs(h % 2 - 1)
                    if h < 1:
                        r, g, b = 1, x, 0
                    elif h < 2:
                        r, g, b = x, 1, 0
                    elif h < 3:
                        r, g, b = 0, 1, x
                    elif h < 4:
                        r, g, b = 0, x, 1
                    elif h < 5:
                        r, g, b = x, 0, 1
                    else:
                        r, g, b = 1, 0, x
                    
                    color = ((int(r*255) & 0xF8) << 8) | ((int(g*255) & 0xFC) << 3) | (int(b*255) >> 3)
                    sprites[i].pixel_shader[1] = color
                    
                    # Check capture
                    px, py = int(bird['x']), int(bird['y'])
                    if (px, py) in target_pixels and (px, py) not in captured:
                        captured.add((px, py))
                        text_bitmap[px, py] = 1
                        bird['active'] = False
                        sprites[i].x = -10
                        sprites[i].y = -10
                    
                    # Deactivate if off screen
                    if bird['x'] < -5 or bird['x'] > 69 or bird['y'] < -5 or bird['y'] > 37:
                        bird['active'] = False
                        sprites[i].x = -10
                        sprites[i].y = -10
                else:
                    sprites[i].x = -10
                    sprites[i].y = -10
            
            # Reset if complete
            if len(captured) >= len(target_pixels):
                time.sleep(1)
                captured.clear()
                text_bitmap.fill(0)
            
            time.sleep(0.05)
            
    except Exception as e:
        show_text_screen(["SPRITE", "ERROR:", str(e)[:10]], 2)
    
    gc.collect()


def run_advanced_swarm_demo():
    """Run a simplified version of the advanced effects."""
    show_text_screen([
        "ADVANCED",
        "EFFECTS",
        "Trails",
        "& More"
    ], 3)
    
    try:
        import random
        import math
        
        # Create display
        main_group = displayio.Group()
        
        # Trail bitmap
        trail_bitmap = displayio.Bitmap(64, 32, 4)
        trail_palette = displayio.Palette(4)
        trail_palette[0] = 0x000000  # Black
        trail_palette[1] = 0x400000  # Dark red
        trail_palette[2] = 0x004000  # Dark green  
        trail_palette[3] = 0x000040  # Dark blue
        main_group.append(displayio.TileGrid(trail_bitmap, pixel_shader=trail_palette))
        
        # Text bitmap
        text_bitmap = displayio.Bitmap(64, 32, 2)
        text_palette = displayio.Palette(2)
        text_palette[0] = 0x000000
        text_palette[1] = 0xFFFF00
        main_group.append(displayio.TileGrid(text_bitmap, pixel_shader=text_palette))
        
        display.show(main_group)
        
        # Simple "WOW" text
        target_pixels = set()
        # W
        for i in range(6): target_pixels.add((16, 13+i))
        for i in range(6): target_pixels.add((20, 13+i))
        target_pixels.add((17, 17))
        target_pixels.add((18, 18))
        target_pixels.add((19, 17))
        # O
        for i in range(6): target_pixels.add((23, 13+i))
        for i in range(6): target_pixels.add((26, 13+i))
        target_pixels.add((24, 13))
        target_pixels.add((25, 13))
        target_pixels.add((24, 18))
        target_pixels.add((25, 18))
        # W
        for i in range(6): target_pixels.add((29, 13+i))
        for i in range(6): target_pixels.add((33, 13+i))
        target_pixels.add((30, 17))
        target_pixels.add((31, 18))
        target_pixels.add((32, 17))
        
        # Simplified particle system with trails
        MAX_PARTICLES = 10
        particles = []
        for _ in range(MAX_PARTICLES):
            particles.append({
                'x': 0.0, 'y': 0.0,
                'vx': 0.0, 'vy': 0.0,
                'active': False,
                'trail': [],  # Trail positions
                'color': 1
            })
        
        captured = set()
        animation_time = 0
        
        # Run for 10 seconds
        start_time = time.monotonic()
        while time.monotonic() - start_time < 10:
            animation_time += 1
            
            # Spawn particles
            if animation_time % 30 == 0 and len(captured) < len(target_pixels):
                for p in particles:
                    if not p['active']:
                        p['active'] = True
                        p['trail'] = []
                        p['color'] = random.randint(1, 3)
                        # Spawn from corners
                        corner = random.randint(0, 3)
                        if corner == 0:
                            p['x'], p['y'] = 0.0, 0.0
                        elif corner == 1:
                            p['x'], p['y'] = 63.0, 0.0
                        elif corner == 2:
                            p['x'], p['y'] = 0.0, 31.0
                        else:
                            p['x'], p['y'] = 63.0, 31.0
                        
                        # Aim toward center initially
                        p['vx'] = (32 - p['x']) / 32
                        p['vy'] = (16 - p['y']) / 16
                        break
            
            # Fade trails
            if animation_time % 3 == 0:
                for y in range(32):
                    for x in range(64):
                        if trail_bitmap[x, y] > 0:
                            trail_bitmap[x, y] = 0
            
            # Update particles
            for p in particles:
                if p['active']:
                    # Add to trail
                    p['trail'].append((int(p['x']), int(p['y'])))
                    if len(p['trail']) > 5:
                        p['trail'].pop(0)
                    
                    # Find target
                    remaining = target_pixels - captured
                    if remaining:
                        # Random target for variety
                        target = random.choice(list(remaining))
                        tx, ty = target
                        
                        # Steer toward target
                        dx = tx - p['x']
                        dy = ty - p['y']
                        dist = math.sqrt(dx*dx + dy*dy)
                        
                        if dist > 1:
                            p['vx'] += (dx / dist) * 0.2
                            p['vy'] += (dy / dist) * 0.2
                        else:
                            # Capture
                            captured.add((tx, ty))
                            text_bitmap[tx, ty] = 1
                            p['active'] = False
                            continue
                    
                    # Add sine wave motion
                    p['vx'] += math.sin(animation_time * 0.1) * 0.05
                    p['vy'] += math.cos(animation_time * 0.1) * 0.05
                    
                    # Limit speed
                    speed = math.sqrt(p['vx']**2 + p['vy']**2)
                    if speed > 1.5:
                        p['vx'] *= 1.5 / speed
                        p['vy'] *= 1.5 / speed
                    
                    # Update position
                    p['x'] += p['vx']
                    p['y'] += p['vy']
                    
                    # Draw trail
                    for tx, ty in p['trail']:
                        if 0 <= tx < 64 and 0 <= ty < 32:
                            trail_bitmap[tx, ty] = p['color']
                    
                    # Deactivate if off screen
                    if p['x'] < -5 or p['x'] > 69 or p['y'] < -5 or p['y'] > 37:
                        p['active'] = False
            
            # Victory effect
            if len(captured) >= len(target_pixels):
                # Flash colors
                for i in range(20):
                    h = (i * 18) % 360
                    if h < 60:
                        r, g, b = 255, int(h * 255 / 60), 0
                    elif h < 120:
                        r, g, b = int((120 - h) * 255 / 60), 255, 0
                    elif h < 180:
                        r, g, b = 0, 255, int((h - 120) * 255 / 60)
                    elif h < 240:
                        r, g, b = 0, int((240 - h) * 255 / 60), 255
                    elif h < 300:
                        r, g, b = int((h - 240) * 255 / 60), 0, 255
                    else:
                        r, g, b = 255, 0, int((360 - h) * 255 / 60)
                    
                    text_palette[1] = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                    time.sleep(0.1)
                
                # Reset
                captured.clear()
                text_bitmap.fill(0)
                trail_bitmap.fill(0)
                text_palette[1] = 0xFFFF00
            
            time.sleep(0.05)
            
    except Exception as e:
        show_text_screen(["ADVANCED", "ERROR:", str(e)[:10]], 2)
    
    gc.collect()


# Main demo sequence
print("MatrixPortal S3 Swarm Animation Demo")
print(f"Free memory at start: {gc.mem_free()} bytes")

show_text_screen([
    "SWARM",
    "ANIMATION",
    "DEMO",
    "v1.0"
], 4)

while True:
    # Run each demo
    print("\n--- Particle System Demo ---")
    print(f"Free memory: {gc.mem_free()} bytes")
    run_particle_swarm_demo()
    gc.collect()
    
    print("\n--- Sprite System Demo ---")
    print(f"Free memory: {gc.mem_free()} bytes")
    run_sprite_swarm_demo()
    gc.collect()
    
    print("\n--- Advanced Effects Demo ---")
    print(f"Free memory: {gc.mem_free()} bytes")
    run_advanced_swarm_demo()
    gc.collect()
    
    # Show completion and restart
    show_text_screen([
        "DEMO",
        "COMPLETE",
        "Restarting",
        "..."
    ], 3)
    
    print(f"\nDemo cycle complete. Free memory: {gc.mem_free()} bytes")
    print("Restarting in 2 seconds...\n")
    time.sleep(2)