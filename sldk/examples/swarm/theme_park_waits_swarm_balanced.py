#!/usr/bin/env python3
"""
Balanced swarm animation - visible flocking AND completes in ~10 seconds.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'sldk', 'src'))

from theme_park_waits_swarm_optimized import *

class BalancedSwarmAnimation(OptimizedSwarmAnimation):
    """Balanced version - visible flocking that completes quickly."""
    
    def __init__(self):
        super().__init__()
        self.animation_start_time = time.time() if not CIRCUITPYTHON else time.monotonic()
        self.target_completion_time = 10.0  # Complete in 10 seconds
        
    def setup_sprites(self):
        """Create more visible bird sprites."""
        # Larger, brighter bird shape
        bird_shape = displayio.Bitmap(BIRD_SIZE, BIRD_SIZE, 2)
        # Full 3x3 square for maximum visibility
        for x in range(BIRD_SIZE):
            for y in range(BIRD_SIZE):
                bird_shape[x, y] = 1
        
        # Create sprite pool
        self.bird_sprites = []
        for i in range(MAX_BIRDS):
            palette = displayio.Palette(2)
            palette[0] = 0x000000  # Transparent
            palette[1] = 0xFFFFFF  # Start with white, will be updated
            
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
        """Update with progressive capture rate."""
        current_time = time.monotonic() if CIRCUITPYTHON else time.time()
        
        # Frame rate limiting
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
        
        # Check if animation is complete
        if len(self.captured_pixels) >= len(self.target_pixels):
            if self.completion_time is None:
                self.completion_time = current_time
                actual_time = elapsed
                print(f"\nTHEME PARK WAITS completed in {actual_time:.1f} seconds!")
                print(f"Will reset in {self.reset_after_seconds} seconds...")
                # Keep some birds flying for visual effect
                for i, bird in enumerate(self.birds):
                    if i > 20:  # Keep first 20 birds active
                        bird.active = False
            
            if current_time - self.completion_time >= self.reset_after_seconds:
                self.reset_animation()
                self.animation_start_time = current_time
                return
            
            self.update_palette_animation()
            # Don't return - keep updating birds for visual effect
        
        # Progressive spawn rate - more birds as time goes on
        if current_time - self.last_spawn_time > SPAWN_INTERVAL:
            active_count = sum(1 for bird in self.birds if bird.active)
            
            # Ramp up bird count over time
            if time_progress < 0.2:  # First 2 seconds - few birds for visible flocking
                max_birds_needed = 30
            elif time_progress < 0.5:  # Next 3 seconds - moderate
                max_birds_needed = 60
            elif time_progress < 0.8:  # Next 3 seconds - many
                max_birds_needed = 100
            else:  # Final 2 seconds - maximum
                max_birds_needed = 150
            
            if active_count < max_birds_needed:
                # Spawn birds in flocks
                spawn_count = min(FLOCK_SPAWN_SIZE * 2, int(max_birds_needed - active_count))
                edge = random.randint(0, 3)
                
                # Base position for the flock
                if edge == 0:  # Left
                    base_x = -BIRD_SIZE
                    base_y = random.randint(5, MATRIX_HEIGHT - 5)
                elif edge == 1:  # Right
                    base_x = MATRIX_WIDTH + BIRD_SIZE
                    base_y = random.randint(5, MATRIX_HEIGHT - 5)
                elif edge == 2:  # Top
                    base_x = random.randint(5, MATRIX_WIDTH - 5)
                    base_y = -BIRD_SIZE
                else:  # Bottom
                    base_x = random.randint(5, MATRIX_WIDTH - 5)
                    base_y = MATRIX_HEIGHT + BIRD_SIZE
                
                inactive_birds = [b for b in self.birds if not b.active]
                
                for i, bird in enumerate(inactive_birds[:spawn_count]):
                    offset_x = random.uniform(-5, 5)
                    offset_y = random.uniform(-5, 5)
                    
                    bird.active = True
                    bird.color_index = random.randint(1, PALETTE_SIZE - 1)
                    bird.x = base_x + offset_x
                    bird.y = base_y + offset_y
                    
                    # Initial velocity toward center area
                    center_x, center_y = MATRIX_WIDTH / 2, MATRIX_HEIGHT / 2
                    dx = center_x - bird.x
                    dy = center_y - bird.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist > 0:
                        bird.vx = (dx / dist) * BIRD_SPEED * random.uniform(0.5, 1.5)
                        bird.vy = (dy / dist) * BIRD_SPEED * random.uniform(0.5, 1.5)
                
                self.last_spawn_time = current_time
        
        # Find attraction center
        attraction_center = self.find_attraction_center()
        
        # Update birds with modified behavior
        for bird in self.birds:
            if bird.active:
                # Get flocking forces
                separation = bird.separation_rule(self.birds)
                alignment = bird.alignment_rule(self.birds)
                cohesion = bird.cohesion_rule(self.birds)
                
                # Calculate attraction to pixels with progressive strength
                attraction_vx = 0
                attraction_vy = 0
                
                # Find closest uncaptured pixel
                min_dist = float('inf')
                closest_target = None
                
                for px, py in self.target_pixels:
                    if (px, py) not in self.captured_pixels:
                        dist = math.sqrt((px - bird.x)**2 + (py - bird.y)**2)
                        if dist < min_dist:
                            min_dist = dist
                            closest_target = (px, py)
                
                if closest_target:
                    dx = closest_target[0] - bird.x
                    dy = closest_target[1] - bird.y
                    
                    # Progressive attraction - gets stronger over time
                    base_attraction = 0.1 + time_progress * 0.4  # 0.1 to 0.5
                    
                    # Very strong attraction when close
                    if min_dist < 5:
                        attraction_strength = 1.0
                    elif min_dist < 10:
                        attraction_strength = base_attraction * 2
                    else:
                        attraction_strength = base_attraction
                    
                    if min_dist > 0:
                        attraction_vx = (dx / min_dist) * attraction_strength
                        attraction_vy = (dy / min_dist) * attraction_strength
                
                # Balance flocking and attraction based on time
                if time_progress < 0.3:  # First 3 seconds - strong flocking
                    flocking_weight = 0.8
                    attraction_weight = 0.2
                else:  # After 3 seconds - increasing attraction
                    flocking_weight = 0.4
                    attraction_weight = 0.6
                
                # Apply forces
                bird.vx += (separation[0] * 0.4 + alignment[0] * 0.3 + cohesion[0] * 0.3) * flocking_weight
                bird.vy += (separation[1] * 0.4 + alignment[1] * 0.3 + cohesion[1] * 0.3) * flocking_weight
                bird.vx += attraction_vx * attraction_weight
                bird.vy += attraction_vy * attraction_weight
                
                # Wing flapping for visual interest
                bird.vx += 0.1 * math.sin(bird.phase + time.time() * 12) * bird.speed_multiplier
                bird.vy += 0.08 * math.cos(bird.phase + time.time() * 10) * bird.speed_multiplier
                
                # Less randomness as time goes on
                random_factor = 0.1 * (1 - time_progress)
                bird.vx += random.uniform(-random_factor, random_factor)
                bird.vy += random.uniform(-random_factor, random_factor)
                
                # Limit speed
                speed = math.sqrt(bird.vx*bird.vx + bird.vy*bird.vy)
                max_speed = BIRD_SPEED * (1 + time_progress)  # Speed up over time
                if speed > max_speed:
                    bird.vx = (bird.vx / speed) * max_speed
                    bird.vy = (bird.vy / speed) * max_speed
                
                # Update position
                bird.x += bird.vx
                bird.y += bird.vy
                
                # Capture pixels - progressive capture rate
                capture_radius = 1.0 + time_progress * 0.5  # 1.0 to 1.5
                for px, py in self.target_pixels:
                    if (px, py) not in self.captured_pixels:
                        dist = math.sqrt((bird.x - px)**2 + (bird.y - py)**2)
                        if dist <= capture_radius:
                            self.captured_pixels.add((px, py))
                
                # Keep birds on screen with soft boundaries
                margin = 10
                turn_force = 0.5
                if bird.x < margin:
                    bird.vx += turn_force
                elif bird.x > MATRIX_WIDTH - margin:
                    bird.vx -= turn_force
                if bird.y < margin:
                    bird.vy += turn_force
                elif bird.y > MATRIX_HEIGHT - margin:
                    bird.vy -= turn_force
                
                # Hard boundaries
                bird.x = max(-5, min(MATRIX_WIDTH + 5, bird.x))
                bird.y = max(-5, min(MATRIX_HEIGHT + 5, bird.y))
                
                # Update sprite
                sprite = self.bird_sprites[bird.sprite_index]
                sprite.x = int(bird.x - BIRD_SIZE // 2)
                sprite.y = int(bird.y - BIRD_SIZE // 2)
                
                # Bright, cycling colors
                hue = (self.animation_time * 2 + bird.sprite_index * 0.1) % 1.0
                sprite.pixel_shader[1] = hsv_to_rgb888(hue, 0.8, 1.0)
        
        # Update text bitmap
        captured_copy = self.captured_pixels.copy()
        for pixel in captured_copy:
            x, y = pixel
            if 0 <= x < MATRIX_WIDTH and 0 <= y < MATRIX_HEIGHT:
                if self.text_bitmap[x, y] == 0:
                    color_index = 1 + ((x + y) % (PALETTE_SIZE - 1))
                    self.text_bitmap[x, y] = color_index
        
        # Update palette animation
        self.update_palette_animation()
        
        # Ensure all captured pixels are lit
        for px, py in self.captured_pixels:
            if 0 <= px < MATRIX_WIDTH and 0 <= py < MATRIX_HEIGHT:
                if self.text_bitmap[px, py] == 0:
                    color_index = 1 + ((px + py) % (PALETTE_SIZE - 1))
                    self.text_bitmap[px, py] = color_index
        
        # Force display refresh
        if not CIRCUITPYTHON and self.device:
            self.device.refresh()
        
        # Progress
        if self.frame_count % 30 == 0:
            active_birds = sum(1 for b in self.birds if b.active)
            print(f"Time: {elapsed:.1f}s, Progress: {len(self.captured_pixels)}/{len(self.target_pixels)} "
                  f"({pixel_progress*100:.1f}%), {active_birds} birds active")

if __name__ == "__main__":
    print("=== BALANCED SWARM ANIMATION ===")
    print("- Visible flocking for first 3 seconds")
    print("- Progressive capture rate increases over time")
    print("- Completes in approximately 10 seconds")
    print("- Birds use 3x3 squares for better visibility")
    animation = BalancedSwarmAnimation()
    animation.run()