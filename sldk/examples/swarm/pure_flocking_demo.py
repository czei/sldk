#!/usr/bin/env python3
"""
Pure flocking demo with NO pixel attraction to verify flocking works.
This will show if the flocking behavior itself is working.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'sldk', 'src'))

from theme_park_waits_swarm_optimized import *

class PureFlockingAnimation(OptimizedSwarmAnimation):
    """Modified version with no pixel capture - just pure flocking."""
    
    def __init__(self):
        super().__init__()
        # Override to have no target pixels
        self.target_pixels = set()
        
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
        
        # Always spawn birds
        if current_time - self.last_spawn_time > SPAWN_INTERVAL:
            active_count = sum(1 for bird in self.birds if bird.active)
            
            if active_count < 40:  # Keep 40 birds for good flocking demo
                # Spawn birds in flocks
                spawn_count = min(FLOCK_SPAWN_SIZE, 40 - active_count)
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
                
                self.last_spawn_time = current_time
        
        # Update birds with NO attraction
        for bird in self.birds:
            if bird.active:
                # Call update with empty pixels and no attraction
                bird.update(set(), set(), None, self.birds)
                
                # Wrap birds around screen edges instead of deactivating
                if bird.x < -5:
                    bird.x = MATRIX_WIDTH + 5
                elif bird.x > MATRIX_WIDTH + 5:
                    bird.x = -5
                    
                if bird.y < -5:
                    bird.y = MATRIX_HEIGHT + 5
                elif bird.y > MATRIX_HEIGHT + 5:
                    bird.y = -5
                
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
        
        # Force display refresh for SLDK
        if not CIRCUITPYTHON and self.device:
            self.device.refresh()
        
        # Print debug info
        if self.frame_count % 60 == 0:
            active_birds = sum(1 for b in self.birds if b.active)
            print(f"Frame {self.frame_count}: {active_birds} birds active")
            
            # Show velocity stats
            if active_birds > 0:
                active = [b for b in self.birds if b.active]
                avg_vx = sum(b.vx for b in active) / len(active)
                avg_vy = sum(b.vy for b in active) / len(active)
                print(f"  Average velocity: ({avg_vx:.2f}, {avg_vy:.2f})")

if __name__ == "__main__":
    print("=== PURE FLOCKING DEMO - NO PIXEL ATTRACTION ===")
    print("This should show clear flocking behavior")
    animation = PureFlockingAnimation()
    animation.run()