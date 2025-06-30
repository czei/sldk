#!/usr/bin/env python3
"""
Swarm animation with TRULY VISIBLE birds that complete in ~10 seconds.
Birds are rendered separately from text so they're always visible.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'sldk', 'src'))

from theme_park_waits_swarm_optimized import *

class TrulyVisibleSwarmAnimation(OptimizedSwarmAnimation):
    """Birds are always visible - they don't disappear into the text."""
    
    def __init__(self):
        super().__init__()
        self.animation_start_time = time.time() if not CIRCUITPYTHON else time.monotonic()
        self.target_completion_time = 10.0
        
    def setup_layers(self):
        """Create layers with birds ALWAYS on top."""
        # Background layer (black)
        self.background_bitmap = displayio.Bitmap(MATRIX_WIDTH, MATRIX_HEIGHT, 1)
        background_palette = displayio.Palette(1)
        background_palette[0] = 0x000000
        self.background_grid = displayio.TileGrid(
            self.background_bitmap, 
            pixel_shader=background_palette
        )
        self.main_group.append(self.background_grid)
        
        # Text layer for captured pixels
        self.text_bitmap = displayio.Bitmap(MATRIX_WIDTH, MATRIX_HEIGHT, PALETTE_SIZE)
        for y in range(MATRIX_HEIGHT):
            for x in range(MATRIX_WIDTH):
                self.text_bitmap[x, y] = 0
        
        self.text_grid = displayio.TileGrid(
            self.text_bitmap,
            pixel_shader=self.rainbow_palette
        )
        self.main_group.append(self.text_grid)
        
        # Bird sprites layer - ALWAYS ON TOP
        if CIRCUITPYTHON:
            self.bird_group = displayio.Group(max_size=MAX_BIRDS)
        else:
            self.bird_group = displayio.Group()
        self.main_group.append(self.bird_group)
    
    def setup_sprites(self):
        """Create BRIGHT, VISIBLE bird sprites."""
        # Create multiple bird shapes for variety
        bird_shapes = []
        
        # Shape 1: Solid square
        shape1 = displayio.Bitmap(BIRD_SIZE, BIRD_SIZE, 2)
        for x in range(BIRD_SIZE):
            for y in range(BIRD_SIZE):
                shape1[x, y] = 1
        bird_shapes.append(shape1)
        
        # Shape 2: Plus sign
        shape2 = displayio.Bitmap(BIRD_SIZE, BIRD_SIZE, 2)
        for i in range(BIRD_SIZE):
            shape2[1, i] = 1  # Vertical
            shape2[i, 1] = 1  # Horizontal
        bird_shapes.append(shape2)
        
        # Shape 3: X pattern
        shape3 = displayio.Bitmap(BIRD_SIZE, BIRD_SIZE, 2)
        shape3[0, 0] = 1
        shape3[1, 1] = 1
        shape3[2, 2] = 1
        shape3[0, 2] = 1
        shape3[2, 0] = 1
        bird_shapes.append(shape3)
        
        # Create sprite pool
        self.bird_sprites = []
        for i in range(MAX_BIRDS):
            # Each bird gets a random shape
            bird_shape = bird_shapes[i % len(bird_shapes)]
            
            # Bright palette
            palette = displayio.Palette(2)
            palette[0] = 0x000000  # Transparent
            # Start with different bright colors
            colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0xFF00FF, 0x00FFFF, 0xFFFFFF]
            palette[1] = colors[i % len(colors)]
            
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
    
    def update(self):
        """Update with birds that stay visible."""
        current_time = time.monotonic() if CIRCUITPYTHON else time.time()
        
        if current_time - self.last_update_time < 1.0 / UPDATE_RATE:
            return
            
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
        self.animation_time += delta_time
        self.frame_count += 1
        
        # Calculate progress
        elapsed = current_time - self.animation_start_time
        time_progress = min(1.0, elapsed / self.target_completion_time)
        pixel_progress = len(self.captured_pixels) / len(self.target_pixels) if self.target_pixels else 0
        
        # Check completion
        if len(self.captured_pixels) >= len(self.target_pixels):
            if self.completion_time is None:
                self.completion_time = current_time
                print(f"\nCompleted in {elapsed:.1f} seconds!")
                # Keep ALL birds flying around for visual effect
            
            if current_time - self.completion_time >= self.reset_after_seconds:
                self.reset_animation()
                self.animation_start_time = current_time
                return
            
            self.update_palette_animation()
        
        # Spawn birds progressively
        if current_time - self.last_spawn_time > 0.1:  # Fast spawn
            active_count = sum(1 for bird in self.birds if bird.active)
            
            # Many birds for visibility
            target_birds = int(20 + time_progress * 80)  # 20 to 100 birds
            
            if active_count < target_birds:
                spawn_count = min(10, target_birds - active_count)
                
                for _ in range(spawn_count):
                    # Find inactive bird
                    for bird in self.birds:
                        if not bird.active:
                            # Random edge spawn
                            edge = random.randint(0, 3)
                            bird.spawn(edge)
                            # Give birds more initial speed
                            bird.vx *= 1.5
                            bird.vy *= 1.5
                            break
                
                self.last_spawn_time = current_time
        
        # Update birds
        attraction_center = self.find_attraction_center() if len(self.captured_pixels) < len(self.target_pixels) else None
        
        for i, bird in enumerate(self.birds):
            if bird.active:
                # Custom update for visibility
                sep = bird.separation_rule(self.birds)
                ali = bird.alignment_rule(self.birds)
                coh = bird.cohesion_rule(self.birds)
                
                # Progressive attraction
                if attraction_center:
                    dx = attraction_center[0] - bird.x
                    dy = attraction_center[1] - bird.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    
                    # Attraction increases over time
                    attraction_strength = 0.2 + time_progress * 0.5
                    
                    if dist > 0:
                        att_x = (dx / dist) * attraction_strength
                        att_y = (dy / dist) * attraction_strength
                    else:
                        att_x = att_y = 0
                else:
                    att_x = att_y = 0
                
                # Apply forces - always maintain some flocking
                bird.vx += sep[0] * 0.3 + ali[0] * 0.2 + coh[0] * 0.1 + att_x
                bird.vy += sep[1] * 0.3 + ali[1] * 0.2 + coh[1] * 0.1 + att_y
                
                # Constant wing flapping for movement
                bird.vx += 0.3 * math.sin(bird.phase + time.time() * 15)
                bird.vy += 0.2 * math.cos(bird.phase + time.time() * 12)
                
                # Some randomness
                bird.vx += random.uniform(-0.2, 0.2)
                bird.vy += random.uniform(-0.2, 0.2)
                
                # Speed limit
                speed = math.sqrt(bird.vx**2 + bird.vy**2)
                max_speed = 4.0  # Faster birds
                if speed > max_speed:
                    bird.vx = (bird.vx / speed) * max_speed
                    bird.vy = (bird.vy / speed) * max_speed
                
                # Update position
                bird.x += bird.vx
                bird.y += bird.vy
                
                # Wrap around screen edges
                if bird.x < -5:
                    bird.x = MATRIX_WIDTH + 5
                elif bird.x > MATRIX_WIDTH + 5:
                    bird.x = -5
                if bird.y < -5:
                    bird.y = MATRIX_HEIGHT + 5
                elif bird.y > MATRIX_HEIGHT + 5:
                    bird.y = -5
                
                # Capture pixels when passing over them
                for px, py in self.target_pixels:
                    if (px, py) not in self.captured_pixels:
                        dist = math.sqrt((bird.x - px)**2 + (bird.y - py)**2)
                        # Larger capture radius that increases over time
                        capture_radius = 2.0 + time_progress * 1.0
                        if dist <= capture_radius:
                            self.captured_pixels.add((px, py))
                
                # Update sprite position
                sprite = self.bird_sprites[bird.sprite_index]
                sprite.x = int(bird.x - BIRD_SIZE // 2)
                sprite.y = int(bird.y - BIRD_SIZE // 2)
                
                # Cycle through bright colors
                colors = [0xFF0000, 0xFFFF00, 0x00FF00, 0x00FFFF, 0x0000FF, 0xFF00FF, 0xFFFFFF]
                color_index = int((self.animation_time * 3 + i * 0.5)) % len(colors)
                sprite.pixel_shader[1] = colors[color_index]
        
        # Update text bitmap
        for pixel in self.captured_pixels:
            x, y = pixel
            if 0 <= x < MATRIX_WIDTH and 0 <= y < MATRIX_HEIGHT:
                if self.text_bitmap[x, y] == 0:
                    color_index = 1 + ((x + y) % (PALETTE_SIZE - 1))
                    self.text_bitmap[x, y] = color_index
        
        # Update palette animation
        self.update_palette_animation()
        
        # Force display refresh
        if not CIRCUITPYTHON and self.device:
            self.device.refresh()
        
        # Progress
        if self.frame_count % 30 == 0:
            active_birds = sum(1 for b in self.birds if b.active)
            print(f"Time: {elapsed:.1f}s, Progress: {len(self.captured_pixels)}/{len(self.target_pixels)} "
                  f"({pixel_progress*100:.1f}%), {active_birds} VISIBLE birds flocking!")

if __name__ == "__main__":
    print("=== TRULY VISIBLE SWARM ANIMATION ===")
    print("- Birds are ALWAYS visible on top layer")
    print("- Multiple bird shapes and bright colors")
    print("- Birds wrap around screen edges")
    print("- Completes in ~10 seconds")
    print("- Continuous flocking throughout")
    animation = TrulyVisibleSwarmAnimation()
    animation.run()