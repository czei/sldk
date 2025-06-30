#!/usr/bin/env python3
"""
Swarm animation where birds flock around and "drop eggs" to form text.
Birds converge on empty pixels but maintain flocking behavior.
When complete, all birds fly away.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'sldk', 'src'))

from theme_park_waits_swarm_optimized import *

class EggDropSwarmAnimation(OptimizedSwarmAnimation):
    """Birds drop eggs as they fly over pixels, then leave when done."""
    
    def __init__(self):
        super().__init__()
        self.animation_start_time = time.time() if not CIRCUITPYTHON else time.monotonic()
        self.target_completion_time = 10.0
        self.birds_leaving = False  # Flag for when birds should fly away
        self.leave_start_time = None
        
    def setup_layers(self):
        """Birds on top so they're always visible."""
        # Background
        self.background_bitmap = displayio.Bitmap(MATRIX_WIDTH, MATRIX_HEIGHT, 1)
        background_palette = displayio.Palette(1)
        background_palette[0] = 0x000000
        self.background_grid = displayio.TileGrid(
            self.background_bitmap, 
            pixel_shader=background_palette
        )
        self.main_group.append(self.background_grid)
        
        # Text layer (the "eggs")
        self.text_bitmap = displayio.Bitmap(MATRIX_WIDTH, MATRIX_HEIGHT, PALETTE_SIZE)
        for y in range(MATRIX_HEIGHT):
            for x in range(MATRIX_WIDTH):
                self.text_bitmap[x, y] = 0
        
        self.text_grid = displayio.TileGrid(
            self.text_bitmap,
            pixel_shader=self.rainbow_palette
        )
        self.main_group.append(self.text_grid)
        
        # Birds on TOP
        if CIRCUITPYTHON:
            self.bird_group = displayio.Group(max_size=MAX_BIRDS)
        else:
            self.bird_group = displayio.Group()
        self.main_group.append(self.bird_group)
    
    def setup_sprites(self):
        """Create bird sprites that look like birds."""
        # Bird shape - small V or triangle
        bird_shape = displayio.Bitmap(BIRD_SIZE, BIRD_SIZE, 2)
        # V-shaped bird
        bird_shape[0, 0] = 1
        bird_shape[1, 1] = 1
        bird_shape[2, 0] = 1
        
        # Create sprite pool
        self.bird_sprites = []
        for i in range(MAX_BIRDS):
            palette = displayio.Palette(2)
            palette[0] = 0x000000  # Transparent
            # Various bird colors
            bird_colors = [0xFFFFFF, 0xCCCCCC, 0xFFFF99, 0x99CCFF]
            palette[1] = bird_colors[i % len(bird_colors)]
            
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
    
    def find_nearest_exit(self, bird):
        """Find the nearest screen edge for bird to exit."""
        # Distance to each edge
        left = bird.x
        right = MATRIX_WIDTH - bird.x
        top = bird.y
        bottom = MATRIX_HEIGHT - bird.y
        
        min_dist = min(left, right, top, bottom)
        
        if min_dist == left:
            return (-10, bird.y)  # Exit left
        elif min_dist == right:
            return (MATRIX_WIDTH + 10, bird.y)  # Exit right
        elif min_dist == top:
            return (bird.x, -10)  # Exit top
        else:
            return (bird.x, MATRIX_HEIGHT + 10)  # Exit bottom
    
    def update(self):
        """Update with egg-dropping behavior."""
        current_time = time.monotonic() if CIRCUITPYTHON else time.time()
        
        if current_time - self.last_update_time < 1.0 / UPDATE_RATE:
            return
            
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
        self.animation_time += delta_time
        self.frame_count += 1
        
        # Calculate progress
        elapsed = current_time - self.animation_start_time
        pixel_progress = len(self.captured_pixels) / len(self.target_pixels) if self.target_pixels else 0
        
        # Check if all eggs have been dropped
        if len(self.captured_pixels) >= len(self.target_pixels) and not self.birds_leaving:
            self.birds_leaving = True
            self.leave_start_time = current_time
            print(f"\nAll eggs dropped in {elapsed:.1f} seconds! Birds flying away...")
        
        # Check if all birds have left
        if self.birds_leaving:
            active_birds = sum(1 for b in self.birds if b.active)
            if active_birds == 0:
                if self.completion_time is None:
                    self.completion_time = current_time
                    print(f"All birds have left!")
                
                if current_time - self.completion_time >= self.reset_after_seconds:
                    self.reset_animation()
                    self.animation_start_time = current_time
                    self.birds_leaving = False
                    self.leave_start_time = None
                    return
                
                # Just show the rainbow text animation
                self.update_palette_animation()
                if not CIRCUITPYTHON and self.device:
                    self.device.refresh()
                return
        
        # Spawn birds if not leaving
        if not self.birds_leaving and current_time - self.last_spawn_time > 0.15:
            active_count = sum(1 for bird in self.birds if bird.active)
            
            # Progressive bird count
            if elapsed < 2:
                target_birds = 30  # Start with visible flocking
            elif elapsed < 5:
                target_birds = 50
            else:
                target_birds = 80  # More birds to finish quickly
            
            if active_count < target_birds:
                spawn_count = min(5, target_birds - active_count)
                
                # Spawn from random edge
                edge = random.randint(0, 3)
                base_positions = {
                    0: (-5, random.randint(5, MATRIX_HEIGHT-5)),  # Left
                    1: (MATRIX_WIDTH+5, random.randint(5, MATRIX_HEIGHT-5)),  # Right
                    2: (random.randint(5, MATRIX_WIDTH-5), -5),  # Top
                    3: (random.randint(5, MATRIX_WIDTH-5), MATRIX_HEIGHT+5)  # Bottom
                }
                base_x, base_y = base_positions[edge]
                
                for _ in range(spawn_count):
                    for bird in self.birds:
                        if not bird.active:
                            bird.active = True
                            bird.x = base_x + random.uniform(-3, 3)
                            bird.y = base_y + random.uniform(-3, 3)
                            
                            # Initial velocity toward center area
                            if edge == 0:  # From left
                                bird.vx = random.uniform(2, 3)
                                bird.vy = random.uniform(-0.5, 0.5)
                            elif edge == 1:  # From right
                                bird.vx = random.uniform(-3, -2)
                                bird.vy = random.uniform(-0.5, 0.5)
                            elif edge == 2:  # From top
                                bird.vx = random.uniform(-0.5, 0.5)
                                bird.vy = random.uniform(2, 3)
                            else:  # From bottom
                                bird.vx = random.uniform(-0.5, 0.5)
                                bird.vy = random.uniform(-3, -2)
                            break
                
                self.last_spawn_time = current_time
        
        # Find attraction center (empty pixels)
        attraction_center = None
        if not self.birds_leaving and len(self.captured_pixels) < len(self.target_pixels):
            remaining = len(self.target_pixels) - len(self.captured_pixels)
            
            # For final pixels, target them directly
            if remaining < 10:
                missing = list(self.target_pixels - self.captured_pixels)
                if missing:
                    # Cycle through missing pixels
                    target_index = self.frame_count % len(missing)
                    attraction_center = missing[target_index]
            else:
                attraction_center = self.find_attraction_center()
        
        # Update each bird
        for bird in self.birds:
            if bird.active:
                if self.birds_leaving:
                    # Birds fly away to nearest edge
                    exit_point = self.find_nearest_exit(bird)
                    dx = exit_point[0] - bird.x
                    dy = exit_point[1] - bird.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    
                    if dist < 5:  # Close to exit
                        bird.active = False
                        continue
                    
                    # Fly toward exit
                    exit_speed = 4.0
                    bird.vx = (dx / dist) * exit_speed
                    bird.vy = (dy / dist) * exit_speed
                    
                else:
                    # Normal flocking behavior
                    sep = bird.separation_rule(self.birds)
                    ali = bird.alignment_rule(self.birds)
                    coh = bird.cohesion_rule(self.birds)
                    
                    # Attraction to empty pixels
                    att_x = att_y = 0
                    if attraction_center:
                        dx = attraction_center[0] - bird.x
                        dy = attraction_center[1] - bird.y
                        dist = math.sqrt(dx*dx + dy*dy)
                        
                        # Moderate attraction that increases over time
                        remaining = len(self.target_pixels) - len(self.captured_pixels)
                        
                        # Strong attraction for final pixels
                        if remaining < 20:
                            attraction_strength = 1.0  # Very strong for final pixels
                        else:
                            attraction_strength = 0.2 + (elapsed / self.target_completion_time) * 0.3
                        
                        if dist > 0:
                            att_x = (dx / dist) * attraction_strength
                            att_y = (dy / dist) * attraction_strength
                    
                    # Apply forces - maintain visible flocking
                    bird.vx += sep[0] * 0.4 + ali[0] * 0.3 + coh[0] * 0.2 + att_x
                    bird.vy += sep[1] * 0.4 + ali[1] * 0.3 + coh[1] * 0.2 + att_y
                    
                    # Organic movement
                    bird.vx += 0.2 * math.sin(bird.phase + time.time() * 10)
                    bird.vy += 0.15 * math.cos(bird.phase + time.time() * 8)
                    
                    # Some randomness
                    bird.vx += random.uniform(-0.1, 0.1)
                    bird.vy += random.uniform(-0.1, 0.1)
                    
                    # Speed limit
                    speed = math.sqrt(bird.vx**2 + bird.vy**2)
                    max_speed = 3.5
                    if speed > max_speed:
                        bird.vx = (bird.vx / speed) * max_speed
                        bird.vy = (bird.vy / speed) * max_speed
                    
                    # Keep birds on screen with soft boundaries
                    margin = 8
                    if bird.x < margin:
                        bird.vx += 0.5
                    elif bird.x > MATRIX_WIDTH - margin:
                        bird.vx -= 0.5
                    if bird.y < margin:
                        bird.vy += 0.5
                    elif bird.y > MATRIX_HEIGHT - margin:
                        bird.vy -= 0.5
                
                # Update position
                bird.x += bird.vx
                bird.y += bird.vy
                
                # Drop eggs when flying over empty pixels
                if not self.birds_leaving:
                    bird_x = int(round(bird.x))
                    bird_y = int(round(bird.y))
                    
                    # Check a small area around the bird
                    remaining = len(self.target_pixels) - len(self.captured_pixels)
                    check_range = 2 if remaining < 20 else 1  # Larger range for final pixels
                    
                    for dx in range(-check_range, check_range + 1):
                        for dy in range(-check_range, check_range + 1):
                            check_x = bird_x + dx
                            check_y = bird_y + dy
                            
                            if (check_x, check_y) in self.target_pixels and \
                               (check_x, check_y) not in self.captured_pixels:
                                # Drop an egg!
                                self.captured_pixels.add((check_x, check_y))
                                # Immediate visual feedback
                                if 0 <= check_x < MATRIX_WIDTH and 0 <= check_y < MATRIX_HEIGHT:
                                    color_index = 1 + ((check_x + check_y) % (PALETTE_SIZE - 1))
                                    self.text_bitmap[check_x, check_y] = color_index
                    
                    # Force capture if very close to a missing pixel (for stubborn pixels)
                    if remaining < 10:
                        for px, py in self.target_pixels:
                            if (px, py) not in self.captured_pixels:
                                dist = math.sqrt((bird.x - px)**2 + (bird.y - py)**2)
                                if dist < 2.0:  # Within 2 pixels
                                    self.captured_pixels.add((px, py))
                                    if 0 <= px < MATRIX_WIDTH and 0 <= py < MATRIX_HEIGHT:
                                        color_index = 1 + ((px + py) % (PALETTE_SIZE - 1))
                                        self.text_bitmap[px, py] = color_index
                
                # Update sprite
                sprite = self.bird_sprites[bird.sprite_index]
                sprite.x = int(bird.x - BIRD_SIZE // 2)
                sprite.y = int(bird.y - BIRD_SIZE // 2)
        
        # Update any remaining text pixels
        for pixel in self.captured_pixels:
            x, y = pixel
            if 0 <= x < MATRIX_WIDTH and 0 <= y < MATRIX_HEIGHT:
                if self.text_bitmap[x, y] == 0:
                    color_index = 1 + ((x + y) % (PALETTE_SIZE - 1))
                    self.text_bitmap[x, y] = color_index
        
        # Update palette animation
        if len(self.captured_pixels) >= len(self.target_pixels):
            self.update_palette_animation()
        
        # Force display refresh
        if not CIRCUITPYTHON and self.device:
            self.device.refresh()
        
        # Progress
        if self.frame_count % 30 == 0 and not self.birds_leaving:
            active_birds = sum(1 for b in self.birds if b.active)
            print(f"Time: {elapsed:.1f}s, Eggs dropped: {len(self.captured_pixels)}/{len(self.target_pixels)} "
                  f"({pixel_progress*100:.1f}%), {active_birds} birds flocking")

if __name__ == "__main__":
    print("=== EGG DROP SWARM ANIMATION ===")
    print("- Birds flock visibly around the display")
    print("- Birds converge on empty pixel areas")
    print("- Birds 'drop eggs' as they fly over empty pixels")
    print("- When all eggs are dropped, birds fly away")
    print("- Completes in ~10 seconds")
    animation = EggDropSwarmAnimation()
    animation.run()