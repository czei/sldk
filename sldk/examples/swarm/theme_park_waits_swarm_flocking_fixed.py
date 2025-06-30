#!/usr/bin/env python3
"""
Fixed swarm animation that shows visible flocking before pixel capture.
Birds flock around for a while before starting to capture pixels.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'sldk', 'src'))

from theme_park_waits_swarm_optimized import *

class FlockingSwarmAnimation(OptimizedSwarmAnimation):
    """Modified to show flocking behavior before pixel capture."""
    
    def __init__(self):
        super().__init__()
        self.flocking_duration = 5.0  # Flock for 5 seconds before capturing
        self.start_time = time.time() if not CIRCUITPYTHON else time.monotonic()
        
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
        
        # Calculate if we're in flocking phase or capture phase
        elapsed = current_time - self.start_time
        in_flocking_phase = elapsed < self.flocking_duration
        
        # Early final sweep - start when we're close to done
        missing_count = len(self.target_pixels) - len(self.captured_pixels)
        if missing_count > 0 and missing_count <= 20 and self.final_sweep_time is None and not in_flocking_phase:
            self.final_sweep_time = current_time
            print(f"\nStarting final sweep for last {missing_count} pixels...")
        
        # Final sweep check
        if self.final_sweep_time is not None and current_time - self.final_sweep_time > 2.0:
            missing = self.target_pixels - self.captured_pixels
            if missing:
                print(f"\nFinal sweep - directly lighting {len(missing)} stubborn pixels...")
                for px, py in sorted(missing):
                    self.captured_pixels.add((px, py))
                    if 0 <= px < MATRIX_WIDTH and 0 <= py < MATRIX_HEIGHT:
                        color_index = 1 + ((px + py) % (PALETTE_SIZE - 1))
                        self.text_bitmap[px, py] = color_index
        
        # Check if animation is complete
        if len(self.captured_pixels) >= len(self.target_pixels):
            if self.completion_time is None:
                self.completion_time = current_time
                print(f"\nTHEME PARK WAITS completed! Will reset in {self.reset_after_seconds} seconds...")
                for bird in self.birds:
                    bird.active = False
                    bird.stuck_counter = 0
            
            if current_time - self.completion_time >= self.reset_after_seconds:
                self.reset_animation()
                self.start_time = current_time  # Reset flocking timer
                return
            
            self.update_palette_animation()
            return
        
        # Spawn new birds
        if current_time - self.last_spawn_time > SPAWN_INTERVAL:
            active_count = sum(1 for bird in self.birds if bird.active)
            
            # During flocking phase, maintain 30-40 birds
            # During capture phase, use normal logic
            if in_flocking_phase:
                max_birds_needed = 40
            else:
                remaining_pixels = len(self.target_pixels) - len(self.captured_pixels)
                progress = len(self.captured_pixels) / len(self.target_pixels)
                
                if progress < 0.3:
                    max_birds_needed = 30
                elif progress < 0.6:
                    max_birds_needed = 60
                elif remaining_pixels < 30:
                    max_birds_needed = min(150, MAX_BIRDS * 0.9)
                elif remaining_pixels < 60:
                    max_birds_needed = min(100, MAX_BIRDS * 0.7)
                else:
                    max_birds_needed = 80
            
            if active_count < max_birds_needed:
                # Spawn birds in flocks
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
                
                self.last_spawn_time = current_time
        
        # Find attraction center (but only use it after flocking phase)
        attraction_center = None
        if not in_flocking_phase:
            attraction_center = self.find_attraction_center()
            
            if len(self.captured_pixels) >= len(self.target_pixels):
                attraction_center = None
            
            missing_count = len(self.target_pixels) - len(self.captured_pixels)
            if 0 < missing_count <= 30:
                missing = list(self.target_pixels - self.captured_pixels)
                if missing:
                    target_index = self.frame_count % len(missing)
                    target = missing[target_index]
                    attraction_center = target
        
        # Update birds
        for bird in self.birds:
            if bird.active:
                # During flocking phase, pass empty pixels and no attraction
                if in_flocking_phase:
                    captured = bird.update(set(), set(), None, self.birds)
                    
                    # Wrap around edges during flocking phase
                    if bird.x < -5:
                        bird.x = MATRIX_WIDTH + 5
                    elif bird.x > MATRIX_WIDTH + 5:
                        bird.x = -5
                    if bird.y < -5:
                        bird.y = MATRIX_HEIGHT + 5
                    elif bird.y > MATRIX_HEIGHT + 5:
                        bird.y = -5
                else:
                    # Normal capture behavior
                    captured = bird.update(self.target_pixels, self.captured_pixels, attraction_center, self.birds)
                    
                    if len(self.captured_pixels) >= len(self.target_pixels):
                        bird.active = False
                
                # Update sprite position and color
                sprite = self.bird_sprites[bird.sprite_index]
                sprite.x = int(bird.x - BIRD_SIZE // 2)
                sprite.y = int(bird.y - BIRD_SIZE // 2)
                
                # Animate bird color
                hue = (self.animation_time + bird.sprite_index * 0.1) % 1.0
                sprite.pixel_shader[1] = hsv_to_rgb888(hue, 1.0, 1.0)
            else:
                # Hide inactive sprites
                sprite = self.bird_sprites[bird.sprite_index]
                sprite.x = -10
                sprite.y = -10
        
        # Update text bitmap with captured pixels
        captured_copy = self.captured_pixels.copy()
        for pixel in captured_copy:
            x, y = pixel
            if 0 <= x < MATRIX_WIDTH and 0 <= y < MATRIX_HEIGHT:
                if self.text_bitmap[x, y] == 0:
                    color_index = 1 + ((x + y) % (PALETTE_SIZE - 1))
                    self.text_bitmap[x, y] = color_index
        
        # Update captured text animation
        self.update_palette_animation()
        
        # Final safety check
        for px, py in self.captured_pixels:
            if 0 <= px < MATRIX_WIDTH and 0 <= py < MATRIX_HEIGHT:
                if self.text_bitmap[px, py] == 0:
                    color_index = 1 + ((px + py) % (PALETTE_SIZE - 1))
                    self.text_bitmap[px, py] = color_index
        
        # Force display refresh for SLDK
        if not CIRCUITPYTHON and self.device:
            self.device.refresh()
        
        # Print progress
        if self.frame_count % 60 == 0:
            active_birds = sum(1 for b in self.birds if b.active)
            if in_flocking_phase:
                print(f"FLOCKING PHASE: {self.flocking_duration - elapsed:.1f}s remaining, "
                      f"{active_birds} birds swarming")
            else:
                print(f"CAPTURE PHASE: {len(self.captured_pixels)}/{len(self.target_pixels)} "
                      f"captured, {active_birds} birds active")

if __name__ == "__main__":
    print("=== SWARM ANIMATION WITH VISIBLE FLOCKING ===")
    print("Birds will flock around for 5 seconds before starting to capture pixels")
    animation = FlockingSwarmAnimation()
    animation.run()