#!/usr/bin/env python3
"""Complete swarm demo showing all four approaches until full completion."""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..' if 'PyLEDSimulator' in __file__ else '.', 'sldk', 'src'))

from sldk.simulator.devices import MatrixPortalS3
from sldk.simulator.displayio import Group, Bitmap, Palette, TileGrid
from sldk.simulator.adafruit_display_text import Label
from sldk.simulator.terminalio import FONT
from sldk.simulator.core import RED, GREEN, BLUE, WHITE, YELLOW


def get_theme_park_waits_pixels():
    """Return complete THEME PARK WAITS pixel set."""
    pixels = set()
    
    # THEME (y=3-10)
    # T
    for x in range(4, 9): pixels.add((x, 3))
    for y in range(4, 11): pixels.add((6, y))
    
    # H
    for y in range(3, 11): pixels.add((10, y))
    for y in range(3, 11): pixels.add((14, y))
    for x in range(11, 14): pixels.add((x, 6))
    
    # E
    for y in range(3, 11): pixels.add((16, y))
    for x in range(16, 20): pixels.add((x, 3))
    for x in range(16, 19): pixels.add((x, 6))
    for x in range(16, 20): pixels.add((x, 10))
    
    # M
    for y in range(3, 11): pixels.add((22, y))
    for y in range(3, 11): pixels.add((27, y))
    pixels.add((23, 4))
    pixels.add((24, 5))
    pixels.add((25, 5))
    pixels.add((26, 4))
    
    # E
    for y in range(3, 11): pixels.add((29, y))
    for x in range(29, 33): pixels.add((x, 3))
    for x in range(29, 32): pixels.add((x, 6))
    for x in range(29, 33): pixels.add((x, 10))
    
    # PARK (y=3-10)
    # P
    for y in range(3, 11): pixels.add((36, y))
    for x in range(36, 40): pixels.add((x, 3))
    for x in range(36, 40): pixels.add((x, 6))
    pixels.add((39, 4))
    pixels.add((39, 5))
    
    # A
    for y in range(4, 11): pixels.add((42, y))
    for y in range(4, 11): pixels.add((46, y))
    for x in range(43, 46): pixels.add((x, 3))
    for x in range(42, 47): pixels.add((x, 6))
    
    # R
    for y in range(3, 11): pixels.add((48, y))
    for x in range(48, 52): pixels.add((x, 3))
    for x in range(48, 52): pixels.add((x, 6))
    pixels.add((51, 4))
    pixels.add((51, 5))
    pixels.add((50, 7))
    pixels.add((51, 8))
    pixels.add((52, 9))
    pixels.add((53, 10))
    
    # K
    for y in range(3, 11): pixels.add((54, y))
    pixels.add((57, 3))
    pixels.add((56, 4))
    pixels.add((55, 5))
    pixels.add((55, 6))
    pixels.add((56, 7))
    pixels.add((57, 8))
    pixels.add((58, 9))
    pixels.add((59, 10))
    
    # WAITS (y=15-30)
    # W
    for y in range(15, 31): pixels.add((5, y))
    for y in range(15, 31): pixels.add((6, y))
    for y in range(15, 31): pixels.add((13, y))
    for y in range(15, 31): pixels.add((14, y))
    for x in range(7, 9): pixels.add((x, 28))
    for x in range(7, 9): pixels.add((x, 27))
    for x in range(11, 13): pixels.add((x, 28))
    for x in range(11, 13): pixels.add((x, 27))
    for y in range(23, 27): pixels.add((9, y))
    for y in range(23, 27): pixels.add((10, y))
    
    # A
    for y in range(17, 31): pixels.add((16, y))
    for y in range(17, 31): pixels.add((17, y))
    for y in range(17, 31): pixels.add((24, y))
    for y in range(17, 31): pixels.add((25, y))
    for x in range(18, 24): pixels.add((x, 15))
    for x in range(18, 24): pixels.add((x, 16))
    for x in range(16, 26): pixels.add((x, 22))
    for x in range(16, 26): pixels.add((x, 23))
    
    # I
    for x in range(27, 37): pixels.add((x, 15))
    for x in range(27, 37): pixels.add((x, 16))
    for x in range(27, 37): pixels.add((x, 29))
    for x in range(27, 37): pixels.add((x, 30))
    for y in range(15, 31): pixels.add((31, y))
    for y in range(15, 31): pixels.add((32, y))
    
    # T
    for x in range(38, 48): pixels.add((x, 15))
    for x in range(38, 48): pixels.add((x, 16))
    for y in range(15, 31): pixels.add((42, y))
    for y in range(15, 31): pixels.add((43, y))
    
    # S
    for x in range(49, 59): pixels.add((x, 15))
    for x in range(49, 59): pixels.add((x, 16))
    for y in range(17, 22): pixels.add((49, y))
    for y in range(17, 22): pixels.add((50, y))
    for x in range(49, 59): pixels.add((x, 22))
    for x in range(49, 59): pixels.add((x, 23))
    for y in range(24, 29): pixels.add((57, y))
    for y in range(24, 29): pixels.add((58, y))
    for x in range(49, 59): pixels.add((x, 29))
    for x in range(49, 59): pixels.add((x, 30))
    
    return pixels


def run_particle_demo(device):
    """Run optimized particle system demo."""
    print("Running Particle System Demo...")
    
    import random
    
    # Create display
    main_group = Group()
    bitmap = Bitmap(64, 32, 4)
    palette = Palette(4)
    palette[0] = 0x000000  # Black
    palette[1] = YELLOW    # Text
    palette[2] = RED       # Birds
    palette[3] = GREEN     # Birds
    
    tile_grid = TileGrid(bitmap, pixel_shader=palette)
    main_group.append(tile_grid)
    
    # Add title
    title = Label(
        font=FONT,
        text="PARTICLE SYSTEM",
        color=WHITE,
        x=1,
        y=8
    )
    main_group.append(title)
    
    device.display.root_group = main_group
    device.refresh()
    time.sleep(2)
    
    # Remove title for animation
    main_group.pop()
    
    # Particle system
    MAX_BIRDS = 30
    x = [0.0] * MAX_BIRDS
    y = [0.0] * MAX_BIRDS
    vx = [0.0] * MAX_BIRDS
    vy = [0.0] * MAX_BIRDS
    active = [False] * MAX_BIRDS
    
    target_pixels = get_theme_park_waits_pixels()
    captured = set()
    spawn_time = time.time()
    
    start_time = time.time()
    frame_count = 0
    
    while len(captured) < len(target_pixels):
        current_time = time.time()
        frame_count += 1
        
        # Spawn birds
        if current_time - spawn_time > 0.2 and len(captured) < len(target_pixels):
            for i in range(MAX_BIRDS):
                if not active[i]:
                    active[i] = True
                    edge = random.randint(0, 3)
                    if edge == 0:  # Left
                        x[i] = -2
                        y[i] = random.randint(0, 31)
                        vx[i] = 2.5
                        vy[i] = random.uniform(-0.5, 0.5)
                    elif edge == 1:  # Right
                        x[i] = 66
                        y[i] = random.randint(0, 31)
                        vx[i] = -2.5
                        vy[i] = random.uniform(-0.5, 0.5)
                    elif edge == 2:  # Top
                        x[i] = random.randint(0, 63)
                        y[i] = -2
                        vx[i] = random.uniform(-0.5, 0.5)
                        vy[i] = 2.5
                    else:  # Bottom
                        x[i] = random.randint(0, 63)
                        y[i] = 34
                        vx[i] = random.uniform(-0.5, 0.5)
                        vy[i] = -2.5
                    spawn_time = current_time
                    break
        
        # Clear and redraw
        bitmap.fill(0)
        
        # Draw captured text
        for px, py in captured:
            bitmap[px, py] = 1
        
        # Update birds
        for i in range(MAX_BIRDS):
            if active[i]:
                # Find nearest target
                remaining = target_pixels - captured
                if remaining:
                    min_dist = 1000
                    target_x = target_y = 32
                    for tx, ty in remaining:
                        dist = abs(x[i] - tx) + abs(y[i] - ty)
                        if dist < min_dist:
                            min_dist = dist
                            target_x, target_y = tx, ty
                    
                    # Steer toward target
                    if min_dist < 30:
                        dx = target_x - x[i]
                        dy = target_y - y[i]
                        if abs(dx) > 0.5:
                            vx[i] += 0.2 if dx > 0 else -0.2
                        if abs(dy) > 0.5:
                            vy[i] += 0.2 if dy > 0 else -0.2
                
                # Update position
                x[i] += vx[i]
                y[i] += vy[i]
                
                # Draw bird
                px, py = int(x[i]), int(y[i])
                if 0 <= px < 64 and 0 <= py < 32:
                    bitmap[px, py] = 2 + (i % 2)
                
                # Check capture
                if (px, py) in target_pixels and (px, py) not in captured:
                    captured.add((px, py))
                    active[i] = False
                    print(f"Particle captured: {len(captured)}/{len(target_pixels)}")
                
                # Remove if off screen
                if x[i] < -5 or x[i] > 69 or y[i] < -5 or y[i] > 37:
                    active[i] = False
        
        device.refresh()
        time.sleep(0.016)  # ~60 FPS
    
    elapsed = time.time() - start_time
    fps = frame_count / elapsed
    print(f"Particle Demo: {elapsed:.1f}s, {fps:.1f} FPS")
    time.sleep(3)


def run_sprite_demo(device):
    """Run sprite-based demo with color animation."""
    print("Running Sprite System Demo...")
    
    import random
    import math
    
    # This demo would use sprites if available
    # For now, simulate with enhanced particle system
    main_group = Group()
    bitmap = Bitmap(64, 32, 8)
    palette = Palette(8)
    palette[0] = 0x000000  # Black
    palette[1] = YELLOW    # Text
    palette[2] = RED       # Birds
    palette[3] = GREEN     # Birds  
    palette[4] = BLUE      # Birds
    palette[5] = 0xFF00FF  # Magenta
    palette[6] = 0x00FFFF  # Cyan
    palette[7] = 0xFFFF00  # Yellow
    
    tile_grid = TileGrid(bitmap, pixel_shader=palette)
    main_group.append(tile_grid)
    
    # Add title
    title = Label(
        font=FONT,
        text="SPRITE SYSTEM",
        color=WHITE,
        x=1,
        y=8
    )
    main_group.append(title)
    
    device.display.root_group = main_group
    device.refresh()
    time.sleep(2)
    
    # Remove title
    main_group.pop()
    
    # Enhanced particle system with color cycling
    MAX_BIRDS = 20
    birds = []
    for i in range(MAX_BIRDS):
        birds.append({
            'x': 0.0, 'y': 0.0,
            'vx': 0.0, 'vy': 0.0,
            'active': False,
            'color': 2 + (i % 6),
            'hue': random.randint(0, 359)
        })
    
    target_pixels = get_theme_park_waits_pixels()
    captured = set()
    spawn_time = time.time()
    animation_time = 0
    
    start_time = time.time()
    frame_count = 0
    
    while len(captured) < len(target_pixels):
        current_time = time.time()
        frame_count += 1
        animation_time += 1
        
        # Spawn birds
        if animation_time % 20 == 0 and len(captured) < len(target_pixels):
            for bird in birds:
                if not bird['active']:
                    bird['active'] = True
                    edge = random.randint(0, 3)
                    if edge == 0:  # Left
                        bird['x'] = -3.0
                        bird['y'] = float(random.randint(0, 31))
                        bird['vx'] = 2.0
                        bird['vy'] = random.uniform(-0.3, 0.3)
                    elif edge == 1:  # Right
                        bird['x'] = 67.0
                        bird['y'] = float(random.randint(0, 31))
                        bird['vx'] = -2.0
                        bird['vy'] = random.uniform(-0.3, 0.3)
                    elif edge == 2:  # Top
                        bird['x'] = float(random.randint(0, 63))
                        bird['y'] = -3.0
                        bird['vx'] = random.uniform(-0.3, 0.3)
                        bird['vy'] = 2.0
                    else:  # Bottom
                        bird['x'] = float(random.randint(0, 63))
                        bird['y'] = 34.0
                        bird['vx'] = random.uniform(-0.3, 0.3)
                        bird['vy'] = -2.0
                    break
        
        # Clear and redraw
        bitmap.fill(0)
        
        # Draw captured text
        for px, py in captured:
            bitmap[px, py] = 1
        
        # Update birds
        for bird in birds:
            if bird['active']:
                # Find target
                remaining = target_pixels - captured
                if remaining:
                    min_dist = 1000
                    target_x = target_y = 32
                    for tx, ty in remaining:
                        dist = abs(bird['x'] - tx) + abs(bird['y'] - ty)
                        if dist < min_dist:
                            min_dist = dist
                            target_x, target_y = tx, ty
                    
                    # Steer
                    if min_dist < 25:
                        dx = target_x - bird['x']
                        dy = target_y - bird['y']
                        bird['vx'] += 0.1 if dx > 0 else -0.1
                        bird['vy'] += 0.1 if dy > 0 else -0.1
                
                # Update position
                bird['x'] += bird['vx']
                bird['y'] += bird['vy']
                
                # Animate color
                bird['hue'] = (bird['hue'] + 5) % 360
                bird['color'] = 2 + (bird['hue'] // 60)
                
                # Draw bird (3x3 for sprite effect)
                px, py = int(bird['x']), int(bird['y'])
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if 0 <= px+dx < 64 and 0 <= py+dy < 32:
                            if abs(dx) + abs(dy) <= 1:  # Cross pattern
                                bitmap[px+dx, py+dy] = bird['color']
                
                # Check capture
                if (px, py) in target_pixels and (px, py) not in captured:
                    captured.add((px, py))
                    bird['active'] = False
                    print(f"Sprite captured: {len(captured)}/{len(target_pixels)}")
                
                # Remove if off screen
                if bird['x'] < -5 or bird['x'] > 69 or bird['y'] < -5 or bird['y'] > 37:
                    bird['active'] = False
        
        device.refresh()
        time.sleep(0.02)  # ~50 FPS
    
    elapsed = time.time() - start_time
    fps = frame_count / elapsed
    print(f"Sprite Demo: {elapsed:.1f}s, {fps:.1f} FPS")
    time.sleep(3)


def run_advanced_demo(device):
    """Run advanced effects demo with trails."""
    print("Running Advanced Effects Demo...")
    
    import random
    import math
    
    # Create multi-layer display
    main_group = Group()
    
    # Trail layer
    trail_bitmap = Bitmap(64, 32, 8)
    trail_palette = Palette(8)
    trail_palette[0] = 0x000000  # Black
    trail_palette[1] = 0x400000  # Dark red
    trail_palette[2] = 0x800000  # Medium red
    trail_palette[3] = 0xFF0000  # Bright red
    trail_palette[4] = 0x004000  # Dark green
    trail_palette[5] = 0x008000  # Medium green
    trail_palette[6] = 0x00FF00  # Bright green
    trail_palette[7] = 0x0000FF  # Blue
    
    trail_grid = TileGrid(trail_bitmap, pixel_shader=trail_palette)
    main_group.append(trail_grid)
    
    # Text layer
    text_bitmap = Bitmap(64, 32, 2)
    text_palette = Palette(2)
    text_palette[0] = 0x000000  # Transparent
    text_palette[1] = YELLOW    # Text
    
    text_grid = TileGrid(text_bitmap, pixel_shader=text_palette)
    main_group.append(text_grid)
    
    # Add title
    title = Label(
        font=FONT,
        text="ADVANCED EFFECTS",
        color=WHITE,
        x=1,
        y=8
    )
    main_group.append(title)
    
    device.display.root_group = main_group
    device.refresh()
    time.sleep(2)
    
    # Remove title
    main_group.pop()
    
    # Advanced particle system with trails
    MAX_PARTICLES = 15
    particles = []
    for i in range(MAX_PARTICLES):
        particles.append({
            'x': 0.0, 'y': 0.0,
            'vx': 0.0, 'vy': 0.0,
            'active': False,
            'trail': [],
            'color': 1 + (i % 7)
        })
    
    target_pixels = get_theme_park_waits_pixels()
    captured = set()
    animation_time = 0
    
    start_time = time.time()
    frame_count = 0
    
    while len(captured) < len(target_pixels):
        frame_count += 1
        animation_time += 1
        
        # Spawn particles
        if animation_time % 25 == 0 and len(captured) < len(target_pixels):
            for p in particles:
                if not p['active']:
                    p['active'] = True
                    p['trail'] = []
                    # Spawn from corners and edges
                    spawn_type = random.randint(0, 7)
                    if spawn_type < 4:  # Corners
                        corners = [(0, 0), (63, 0), (0, 31), (63, 31)]
                        p['x'], p['y'] = corners[spawn_type]
                        p['vx'] = (32 - p['x']) / 20
                        p['vy'] = (16 - p['y']) / 20
                    else:  # Edges
                        if spawn_type == 4:  # Left
                            p['x'], p['y'] = -2.0, float(random.randint(5, 26))
                            p['vx'], p['vy'] = 2.0, random.uniform(-0.5, 0.5)
                        elif spawn_type == 5:  # Right
                            p['x'], p['y'] = 66.0, float(random.randint(5, 26))
                            p['vx'], p['vy'] = -2.0, random.uniform(-0.5, 0.5)
                        elif spawn_type == 6:  # Top
                            p['x'], p['y'] = float(random.randint(10, 53)), -2.0
                            p['vx'], p['vy'] = random.uniform(-0.5, 0.5), 2.0
                        else:  # Bottom
                            p['x'], p['y'] = float(random.randint(10, 53)), 34.0
                            p['vx'], p['vy'] = random.uniform(-0.5, 0.5), -2.0
                    break
        
        # Fade trails
        if animation_time % 3 == 0:
            for y in range(32):
                for x in range(64):
                    pixel = trail_bitmap[x, y]
                    if pixel > 0:
                        trail_bitmap[x, y] = max(0, pixel - 1)
        
        # Update particles
        for p in particles:
            if p['active']:
                # Add to trail
                p['trail'].append((int(p['x']), int(p['y'])))
                if len(p['trail']) > 8:
                    p['trail'].pop(0)
                
                # Find target
                remaining = target_pixels - captured
                if remaining:
                    if random.randint(0, 4) == 0:  # 20% random target
                        target = random.choice(list(remaining))
                    else:  # 80% nearest target
                        min_dist = 1000
                        target = None
                        for tx, ty in remaining:
                            dist = abs(p['x'] - tx) + abs(p['y'] - ty)
                            if dist < min_dist:
                                min_dist = dist
                                target = (tx, ty)
                    
                    if target:
                        tx, ty = target
                        dx = tx - p['x']
                        dy = ty - p['y']
                        dist = math.sqrt(dx*dx + dy*dy)
                        
                        if dist > 1:
                            p['vx'] += (dx / dist) * 0.3
                            p['vy'] += (dy / dist) * 0.3
                        else:
                            # Capture
                            captured.add((tx, ty))
                            text_bitmap[tx, ty] = 1
                            p['active'] = False
                            print(f"Advanced captured: {len(captured)}/{len(target_pixels)}")
                            continue
                
                # Add organic motion
                p['vx'] += math.sin(animation_time * 0.2 + p['x'] * 0.1) * 0.1
                p['vy'] += math.cos(animation_time * 0.2 + p['y'] * 0.1) * 0.1
                
                # Limit speed
                speed = math.sqrt(p['vx']**2 + p['vy']**2)
                if speed > 2.5:
                    p['vx'] *= 2.5 / speed
                    p['vy'] *= 2.5 / speed
                
                # Update position
                p['x'] += p['vx']
                p['y'] += p['vy']
                
                # Draw trail with fading
                for i, (tx, ty) in enumerate(p['trail']):
                    if 0 <= tx < 64 and 0 <= ty < 32:
                        intensity = min(7, p['color'] + i // 2)
                        trail_bitmap[tx, ty] = intensity
                
                # Remove if off screen
                if p['x'] < -10 or p['x'] > 74 or p['y'] < -10 or p['y'] > 42:
                    p['active'] = False
        
        device.refresh()
        time.sleep(0.025)  # ~40 FPS
    
    elapsed = time.time() - start_time
    fps = frame_count / elapsed
    print(f"Advanced Demo: {elapsed:.1f}s, {fps:.1f} FPS")
    
    # Victory animation
    for i in range(60):
        h = (i * 6) % 360
        # Simple RGB color cycling
        if h < 120:
            r, g, b = 255, int(h * 255 / 120), 0
        elif h < 240:
            r, g, b = int((240 - h) * 255 / 120), 255, int((h - 120) * 255 / 120)
        else:
            r, g, b = int((h - 240) * 255 / 120), int((360 - h) * 255 / 120), 255
        
        color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        text_palette[1] = color
        device.refresh()
        time.sleep(0.05)
    
    time.sleep(3)


def run_original_demo(device):
    """Run original complex swarm algorithm for comparison."""
    print("Running Original Swarm Demo (SLOW!)...")
    
    import random
    import math
    
    class Vector2:
        def __init__(self, x, y):
            self.x = x
            self.y = y
        
        def add(self, other):
            self.x += other.x
            self.y += other.y
        
        def sub(self, other):
            self.x -= other.x
            self.y -= other.y
        
        def mult(self, scalar):
            self.x *= scalar
            self.y *= scalar
        
        def div(self, scalar):
            if scalar != 0:
                self.x /= scalar
                self.y /= scalar
        
        def normalize(self):
            mag = math.sqrt(self.x**2 + self.y**2)
            if mag > 0:
                self.div(mag)
        
        def limit(self, max_val):
            mag = math.sqrt(self.x**2 + self.y**2)
            if mag > max_val:
                self.normalize()
                self.mult(max_val)
        
        @staticmethod
        def sub_static(v1, v2):
            return Vector2(v1.x - v2.x, v1.y - v2.y)
    
    class OriginalBird:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.vx = random.uniform(-1, 1)
            self.vy = random.uniform(-1, 1)
            self.max_speed = 2.0
            self.max_force = 0.03
            self.vision_radius = 12.0
            self.separation_radius = 6.0
        
        def flock(self, birds):
            sep = self.separate(birds)
            ali = self.align(birds)
            coh = self.cohesion(birds)
            
            sep.mult(1.5)
            ali.mult(1.0)
            coh.mult(1.0)
            
            self.apply_force(sep)
            self.apply_force(ali)
            self.apply_force(coh)
        
        def separate(self, birds):
            steer = Vector2(0, 0)
            count = 0
            
            for other in birds:
                if other is not self:
                    d = self.distance_to(other)
                    if 0 < d < self.separation_radius:
                        diff = Vector2(self.x - other.x, self.y - other.y)
                        diff.normalize()
                        diff.div(d)
                        steer.add(diff)
                        count += 1
            
            if count > 0:
                steer.div(count)
                steer.normalize()
                steer.mult(self.max_speed)
                steer.sub(Vector2(self.vx, self.vy))
                steer.limit(self.max_force)
            
            return steer
        
        def align(self, birds):
            sum_vel = Vector2(0, 0)
            count = 0
            
            for other in birds:
                if other is not self:
                    d = self.distance_to(other)
                    if 0 < d < self.vision_radius:
                        sum_vel.add(Vector2(other.vx, other.vy))
                        count += 1
            
            if count > 0:
                sum_vel.div(count)
                sum_vel.normalize()
                sum_vel.mult(self.max_speed)
                steer = Vector2.sub_static(sum_vel, Vector2(self.vx, self.vy))
                steer.limit(self.max_force)
                return steer
            
            return Vector2(0, 0)
        
        def cohesion(self, birds):
            sum_pos = Vector2(0, 0)
            count = 0
            
            for other in birds:
                if other is not self:
                    d = self.distance_to(other)
                    if 0 < d < self.vision_radius:
                        sum_pos.add(Vector2(other.x, other.y))
                        count += 1
            
            if count > 0:
                sum_pos.div(count)
                return self.seek(sum_pos)
            
            return Vector2(0, 0)
        
        def seek(self, target):
            desired = Vector2.sub_static(target, Vector2(self.x, self.y))
            desired.normalize()
            desired.mult(self.max_speed)
            
            steer = Vector2.sub_static(desired, Vector2(self.vx, self.vy))
            steer.limit(self.max_force)
            return steer
        
        def apply_force(self, force):
            self.vx += force.x
            self.vy += force.y
        
        def update(self):
            speed = math.sqrt(self.vx**2 + self.vy**2)
            if speed > self.max_speed:
                self.vx = (self.vx / speed) * self.max_speed
                self.vy = (self.vy / speed) * self.max_speed
            
            self.x += self.vx
            self.y += self.vy
        
        def distance_to(self, other):
            return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    # Create display
    main_group = Group()
    bitmap = Bitmap(64, 32, 4)
    palette = Palette(4)
    palette[0] = 0x000000  # Black
    palette[1] = YELLOW    # Text
    palette[2] = RED       # Birds
    palette[3] = GREEN     # Birds
    
    tile_grid = TileGrid(bitmap, pixel_shader=palette)
    main_group.append(tile_grid)
    
    # Add title
    title = Label(
        font=FONT,
        text="ORIGINAL (SLOW)",
        color=WHITE,
        x=1,
        y=8
    )
    main_group.append(title)
    
    device.display.root_group = main_group
    device.refresh()
    time.sleep(2)
    
    # Remove title
    main_group.pop()
    
    # Create fewer birds due to O(n²) complexity
    MAX_BIRDS = 6
    birds = []
    for i in range(MAX_BIRDS):
        x = random.uniform(10, 54)
        y = random.uniform(10, 22)
        birds.append(OriginalBird(x, y))
    
    target_pixels = get_theme_park_waits_pixels()
    captured = set()
    
    start_time = time.time()
    frame_count = 0
    timeout = 60  # 1 minute timeout
    
    while len(captured) < len(target_pixels) and (time.time() - start_time) < timeout:
        frame_count += 1
        
        # Apply flocking to all birds (expensive!)
        for bird in birds:
            bird.flock(birds)
            
            # Seek nearest target
            remaining = target_pixels - captured
            if remaining:
                min_dist = 1000
                nearest_target = None
                for tx, ty in remaining:
                    dist = math.sqrt((bird.x - tx)**2 + (bird.y - ty)**2)
                    if dist < min_dist:
                        min_dist = dist
                        nearest_target = Vector2(tx, ty)
                
                if nearest_target and min_dist < 25:
                    seek_force = bird.seek(nearest_target)
                    seek_force.mult(3.0)  # Strong seeking
                    bird.apply_force(seek_force)
            
            bird.update()
            
            # Wrap around edges
            if bird.x < 0:
                bird.x = 63
            elif bird.x > 63:
                bird.x = 0
            if bird.y < 0:
                bird.y = 31
            elif bird.y > 31:
                bird.y = 0
        
        # Clear and redraw
        bitmap.fill(0)
        
        # Draw captured text
        for px, py in captured:
            bitmap[px, py] = 1
        
        # Draw birds
        for i, bird in enumerate(birds):
            px, py = int(bird.x), int(bird.y)
            if 0 <= px < 64 and 0 <= py < 32:
                bitmap[px, py] = 2 + (i % 2)
                
                # Check capture
                if (px, py) in target_pixels and (px, py) not in captured:
                    captured.add((px, py))
                    print(f"Original captured: {len(captured)}/{len(target_pixels)}")
        
        device.refresh()
        time.sleep(0.05)  # ~20 FPS (if we can achieve it)
    
    elapsed = time.time() - start_time
    fps = frame_count / elapsed if elapsed > 0 else 0
    
    if len(captured) >= len(target_pixels):
        print(f"Original Demo: COMPLETED in {elapsed:.1f}s, {fps:.1f} FPS")
    else:
        print(f"Original Demo: TIMED OUT after {elapsed:.1f}s, {fps:.1f} FPS")
        print(f"Only captured {len(captured)}/{len(target_pixels)} pixels")
    
    time.sleep(3)


def main():
    """Run all swarm demos until completion."""
    print("Creating MatrixPortal S3 Simulator...")
    device = MatrixPortalS3()
    device.initialize()
    
    # Create title screen
    main_group = Group()
    
    title1 = Label(
        font=FONT,
        text="SWARM",
        color=RED,
        x=15,
        y=8
    )
    main_group.append(title1)
    
    title2 = Label(
        font=FONT,
        text="COMPARISON",
        color=GREEN,
        x=5,
        y=20
    )
    main_group.append(title2)
    
    device.display.root_group = main_group
    device.refresh()
    time.sleep(3)
    
    # Run all demos
    demos = [
        ("Particle System", run_particle_demo),
        ("Sprite System", run_sprite_demo),
        ("Advanced Effects", run_advanced_demo),
        ("Original Algorithm", run_original_demo)
    ]
    
    while True:
        print("\n" + "="*50)
        print("STARTING COMPLETE DEMO CYCLE")
        print("="*50)
        
        for name, demo_func in demos:
            print(f"\n--- {name} ---")
            start_time = time.time()
            demo_func(device)
            elapsed = time.time() - start_time
            print(f"{name} total time: {elapsed:.1f} seconds")
        
        print("\n" + "="*50)
        print("ALL DEMOS COMPLETE - RESTARTING IN 5 SECONDS")
        print("="*50)
        time.sleep(5)


if __name__ == "__main__":
    main()