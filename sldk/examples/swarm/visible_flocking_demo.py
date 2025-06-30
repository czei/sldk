#!/usr/bin/env python3
"""
Visible flocking demo - birds stay on screen with strong flocking behavior.
"""

import sys
import os
import random
import math
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'sldk', 'src'))
from sldk.simulator.devices import MatrixPortalS3
from sldk.simulator.displayio import Bitmap, Palette, TileGrid, Group

# Configuration  
MATRIX_WIDTH = 64
MATRIX_HEIGHT = 32
NUM_BIRDS = 15  # Fewer birds to see individual movement
BIRD_SPEED = 1.5
UPDATE_RATE = 30

class VisibleBird:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        # Random initial velocity
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * BIRD_SPEED
        self.vy = math.sin(angle) * BIRD_SPEED
        self.color = random.randint(1, 7)  # Different colors
        
    def update(self, flock):
        # Store old velocity for smooth turning
        old_vx, old_vy = self.vx, self.vy
        
        # Apply flocking rules
        sep = self.separation(flock)
        ali = self.alignment(flock) 
        coh = self.cohesion(flock)
        
        # Strong flocking forces
        self.vx += sep[0] * 0.8 + ali[0] * 0.5 + coh[0] * 0.3
        self.vy += sep[1] * 0.8 + ali[1] * 0.5 + coh[1] * 0.3
        
        # Smooth turning
        self.vx = old_vx * 0.8 + self.vx * 0.2
        self.vy = old_vy * 0.8 + self.vy * 0.2
        
        # Limit speed
        speed = math.sqrt(self.vx**2 + self.vy**2)
        if speed > BIRD_SPEED:
            self.vx = (self.vx / speed) * BIRD_SPEED
            self.vy = (self.vy / speed) * BIRD_SPEED
        elif speed < BIRD_SPEED * 0.5:  # Minimum speed
            if speed > 0:
                self.vx = (self.vx / speed) * BIRD_SPEED * 0.5
                self.vy = (self.vy / speed) * BIRD_SPEED * 0.5
            
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Soft boundaries - turn away from edges
        margin = 5
        turn_force = 0.5
        
        if self.x < margin:
            self.vx += turn_force
        elif self.x > MATRIX_WIDTH - margin:
            self.vx -= turn_force
            
        if self.y < margin:
            self.vy += turn_force
        elif self.y > MATRIX_HEIGHT - margin:
            self.vy -= turn_force
        
        # Hard boundaries
        self.x = max(0, min(MATRIX_WIDTH - 1, self.x))
        self.y = max(0, min(MATRIX_HEIGHT - 1, self.y))
    
    def separation(self, flock):
        """Avoid crowding neighbors."""
        steer_x, steer_y = 0, 0
        count = 0
        
        for other in flock:
            if other is self:
                continue
            dx = self.x - other.x
            dy = self.y - other.y
            d = math.sqrt(dx**2 + dy**2)
            
            if 0 < d < 8:  # Separation radius
                # Stronger repulsion when closer
                force = 1.0 / (d * d)
                steer_x += (dx / d) * force
                steer_y += (dy / d) * force
                count += 1
        
        if count > 0:
            steer_x /= count
            steer_y /= count
            
        return (steer_x, steer_y)
    
    def alignment(self, flock):
        """Align with neighbors."""
        avg_vx, avg_vy = 0, 0
        count = 0
        
        for other in flock:
            if other is self:
                continue
            dx = self.x - other.x
            dy = self.y - other.y
            d = math.sqrt(dx**2 + dy**2)
            
            if d < 12:  # Alignment radius
                avg_vx += other.vx
                avg_vy += other.vy
                count += 1
        
        if count > 0:
            avg_vx /= count
            avg_vy /= count
            # Steer towards average heading
            return ((avg_vx - self.vx) * 0.1, (avg_vy - self.vy) * 0.1)
            
        return (0, 0)
    
    def cohesion(self, flock):
        """Move toward center of neighbors."""
        center_x, center_y = 0, 0
        count = 0
        
        for other in flock:
            if other is self:
                continue
            dx = self.x - other.x
            dy = self.y - other.y
            d = math.sqrt(dx**2 + dy**2)
            
            if d < 15:  # Cohesion radius
                center_x += other.x
                center_y += other.y
                count += 1
        
        if count > 0:
            center_x /= count
            center_y /= count
            # Steer toward center
            dx = center_x - self.x
            dy = center_y - self.y
            return (dx * 0.01, dy * 0.01)
            
        return (0, 0)

def main():
    device = MatrixPortalS3()
    device.initialize()
    
    # Create display elements
    bitmap = Bitmap(MATRIX_WIDTH, MATRIX_HEIGHT, 8)
    palette = Palette(8)
    palette[0] = 0x000000  # Black background
    palette[1] = 0xFF0000  # Red
    palette[2] = 0x00FF00  # Green  
    palette[3] = 0x0000FF  # Blue
    palette[4] = 0xFFFF00  # Yellow
    palette[5] = 0xFF00FF  # Magenta
    palette[6] = 0x00FFFF  # Cyan
    palette[7] = 0xFFFFFF  # White
    
    tilegrid = TileGrid(bitmap, pixel_shader=palette)
    group = Group()
    group.append(tilegrid)
    device.show(group)
    
    # Create flock with birds starting in groups
    birds = []
    
    # Spawn 3 groups
    for group_i in range(3):
        # Random group position
        group_x = random.randint(10, MATRIX_WIDTH - 10)
        group_y = random.randint(10, MATRIX_HEIGHT - 10)
        
        # Add 5 birds per group
        for _ in range(5):
            x = group_x + random.uniform(-5, 5)
            y = group_y + random.uniform(-5, 5)
            birds.append(VisibleBird(x, y))
    
    frame = 0
    
    def update():
        nonlocal frame
        frame += 1
        
        # Clear bitmap
        for y in range(MATRIX_HEIGHT):
            for x in range(MATRIX_WIDTH):
                bitmap[x, y] = 0
        
        # Update and draw birds
        for bird in birds:
            bird.update(birds)
            
            # Draw bird as small cross
            x = int(bird.x)
            y = int(bird.y)
            
            # Center pixel
            if 0 <= x < MATRIX_WIDTH and 0 <= y < MATRIX_HEIGHT:
                bitmap[x, y] = bird.color
                
            # Cross pattern for visibility
            for dx, dy in [(0, -1), (-1, 0), (1, 0), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < MATRIX_WIDTH and 0 <= ny < MATRIX_HEIGHT:
                    bitmap[nx, ny] = bird.color
        
        # Debug info
        if frame % 60 == 0:
            # Calculate average position and velocity
            avg_x = sum(b.x for b in birds) / len(birds)
            avg_y = sum(b.y for b in birds) / len(birds)
            avg_vx = sum(b.vx for b in birds) / len(birds)
            avg_vy = sum(b.vy for b in birds) / len(birds)
            
            print(f"Frame {frame}: Center ({avg_x:.1f}, {avg_y:.1f}), "
                  f"Avg velocity ({avg_vx:.2f}, {avg_vy:.2f})")
        
        device.refresh()
    
    print("=== VISIBLE FLOCKING DEMO ===")
    print("Watch how birds move in coordinated groups!")
    print("- Red, green, blue, yellow, magenta, cyan birds")
    print("- They avoid each other (separation)")  
    print("- They align their direction (alignment)")
    print("- They stick together (cohesion)")
    
    device.run(update_callback=update, title="Visible Flocking Demo")

if __name__ == "__main__":
    main()