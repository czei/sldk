#!/usr/bin/env python3
"""Simplified swarm animation for CircuitPython compatibility.

Creates a flowing effect where LEDs move along predefined paths from edges
to build the THEME PARK WAITS text. Uses integer math and minimal memory
for efficient CircuitPython performance.
"""

import sys
import os
import random
import time
import math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3


def get_theme_park_waits_pixels():
    """Return list of (x, y) coordinates for all LEDs in THEME PARK WAITS."""
    pixels = []
    
    # THEME PARK - First line (8 pixels tall)
    # T (x=4, y=3) - 8 LEDs tall
    for x in range(4, 9): pixels.append((x, 3))
    for y in range(4, 11): pixels.append((6, y))
    
    # H (x=10, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.append((10, y))
    for y in range(3, 11): pixels.append((14, y))
    for x in range(11, 14): pixels.append((x, 6))
    
    # E (x=16, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.append((16, y))
    for x in range(16, 20): pixels.append((x, 3))
    for x in range(16, 19): pixels.append((x, 6))
    for x in range(16, 20): pixels.append((x, 10))
    
    # M (x=22, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.append((22, y))
    for y in range(3, 11): pixels.append((27, y))
    pixels.append((23, 4))
    pixels.append((24, 5))
    pixels.append((25, 5))
    pixels.append((26, 4))
    
    # E (x=29, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.append((29, y))
    for x in range(29, 33): pixels.append((x, 3))
    for x in range(29, 32): pixels.append((x, 6))
    for x in range(29, 33): pixels.append((x, 10))
    
    # P (x=36, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.append((36, y))
    for x in range(36, 40): pixels.append((x, 3))
    for x in range(36, 40): pixels.append((x, 6))
    pixels.append((39, 4))
    pixels.append((39, 5))
    
    # A (x=42, y=3) - 8 LEDs tall
    for y in range(4, 11): pixels.append((42, y))
    for y in range(4, 11): pixels.append((46, y))
    for x in range(43, 46): pixels.append((x, 3))
    for x in range(42, 47): pixels.append((x, 6))
    
    # R (x=48, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.append((48, y))
    for x in range(48, 52): pixels.append((x, 3))
    for x in range(48, 52): pixels.append((x, 6))
    pixels.append((51, 4))
    pixels.append((51, 5))
    pixels.append((50, 7))
    pixels.append((51, 8))
    pixels.append((52, 9))
    pixels.append((53, 10))
    
    # K (x=54, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.append((54, y))
    pixels.append((57, 3))
    pixels.append((56, 4))
    pixels.append((55, 5))
    pixels.append((55, 6))
    pixels.append((56, 7))
    pixels.append((57, 8))
    pixels.append((58, 9))
    pixels.append((59, 10))
    
    # WAITS - Second line (16 pixels tall, moved right by 3 LEDs)
    # W (x=5, y=15) - exact pattern from screenshot
    # Left outer edge
    for y in range(15, 31):
        pixels.append((5, y))
        pixels.append((6, y))
    # Right outer edge
    for y in range(15, 31):
        pixels.append((13, y))
        pixels.append((14, y))

    ## CLAUDE DO NOT MODIFY
    for x in range(7, 9): pixels.append((x, 28))
    for x in range(7, 9): pixels.append((x, 27))
    for x in range(11, 13): pixels.append((x, 28))
    for x in range(11, 13): pixels.append((x, 27))
    for y in range(23, 27): pixels.append((9, y))
    for y in range(23, 27): pixels.append((10, y))
    ## End do not modify
    
    # A (x=16, y=15) - 10 LEDs wide, 16 pixels tall
    for y in range(17, 31): pixels.append((16, y))
    for y in range(17, 31): pixels.append((17, y))
    for y in range(17, 31): pixels.append((24, y))
    for y in range(17, 31): pixels.append((25, y))
    for x in range(18, 24): pixels.append((x, 15))
    for x in range(18, 24): pixels.append((x, 16))
    for x in range(16, 26): pixels.append((x, 22))
    for x in range(16, 26): pixels.append((x, 23))
    
    # I (x=27, y=15) - 10 LEDs wide, 16 pixels tall
    for x in range(27, 37): pixels.append((x, 15))
    for x in range(27, 37): pixels.append((x, 16))
    for x in range(27, 37): pixels.append((x, 29))
    for x in range(27, 37): pixels.append((x, 30))
    for y in range(15, 31): pixels.append((31, y))
    for y in range(15, 31): pixels.append((32, y))
    
    # T (x=38, y=15) - 10 LEDs wide, 16 pixels tall
    for x in range(38, 48): pixels.append((x, 15))
    for x in range(38, 48): pixels.append((x, 16))
    for y in range(15, 31): pixels.append((42, y))
    for y in range(15, 31): pixels.append((43, y))
    
    # S (x=49, y=15) - 10 LEDs wide, 16 pixels tall
    for x in range(49, 59): pixels.append((x, 15))
    for x in range(49, 59): pixels.append((x, 16))
    for y in range(17, 22): pixels.append((49, y))
    for y in range(17, 22): pixels.append((50, y))
    for x in range(49, 59): pixels.append((x, 22))
    for x in range(49, 59): pixels.append((x, 23))
    for y in range(24, 29): pixels.append((57, y))
    for y in range(24, 29): pixels.append((58, y))
    for x in range(49, 59): pixels.append((x, 29))
    for x in range(49, 59): pixels.append((x, 30))
    
    return pixels


class SimpleBird:
    """Simple bird with predefined path - no complex physics."""
    
    def __init__(self, path, target_pixel):
        self.path = path  # List of (x, y) positions
        self.target_pixel = target_pixel
        self.path_index = 0
        self.x = path[0][0] if path else 0
        self.y = path[0][1] if path else 0
        self.captured = False
        
    def update(self):
        """Move along predefined path."""
        if self.captured or self.path_index >= len(self.path):
            return False  # Bird is done
            
        # Move to next position in path
        self.path_index += 1
        if self.path_index < len(self.path):
            self.x, self.y = self.path[self.path_index]
            
        # Check if reached target
        current_pos = (int(self.x), int(self.y))
        if current_pos == self.target_pixel:
            self.captured = True
            return True  # Successfully captured
            
        return False  # Still moving
        
    def get_position(self):
        """Get current integer position."""
        return (int(self.x), int(self.y))
        
    def is_on_screen(self):
        """Check if bird is visible on screen."""
        return 0 <= self.x < 64 and 0 <= self.y < 32


def create_path_to_target(start_x, start_y, target_x, target_y):
    """Create a simple curved path from start to target using integer math."""
    path = []
    
    # Calculate number of steps (roughly 1 step per pixel of distance)
    dx = target_x - start_x
    dy = target_y - start_y
    distance = int(math.sqrt(dx*dx + dy*dy))
    steps = max(distance, 10)  # At least 10 steps for smooth movement
    
    # Add some curve to make it look more natural
    mid_x = (start_x + target_x) // 2
    mid_y = (start_y + target_y) // 2
    
    # Add curve offset based on direction
    if abs(dx) > abs(dy):  # Horizontal movement
        curve_offset = random.randint(-8, 8)
        mid_y += curve_offset
    else:  # Vertical movement
        curve_offset = random.randint(-8, 8)
        mid_x += curve_offset
    
    # Create path with simple quadratic curve
    for i in range(steps + 1):
        t = i / steps  # Parameter from 0 to 1
        
        # Quadratic Bezier curve: (1-t)²*P0 + 2(1-t)t*P1 + t²*P2
        x = int((1-t)*(1-t)*start_x + 2*(1-t)*t*mid_x + t*t*target_x)
        y = int((1-t)*(1-t)*start_y + 2*(1-t)*t*mid_y + t*t*target_y)
        
        # Keep within screen bounds
        x = max(0, min(63, x))
        y = max(0, min(31, y))
        
        path.append((x, y))
    
    return path


def find_nearest_missing_pixel(captured_pixels, target_pixels):
    """Find a missing pixel that needs to be filled."""
    missing = []
    for pixel in target_pixels:
        if pixel not in captured_pixels:
            missing.append(pixel)
    
    if not missing:
        return None
        
    # Return a random missing pixel for variety
    return random.choice(missing)


def get_spawn_point():
    """Get a random spawn point around the screen edges."""
    edge = random.choice(['left', 'right', 'top', 'bottom'])
    
    if edge == 'left':
        return (-5, random.randint(0, 31))
    elif edge == 'right':
        return (69, random.randint(0, 31))
    elif edge == 'top':
        return (random.randint(0, 63), -5)
    else:  # bottom
        return (random.randint(0, 63), 37)


def main():
    """Run the simplified swarm animation."""
    device = MatrixPortalS3()
    device.initialize()
    device.matrix.clear()
    
    yellow = (255, 255, 0)
    
    print("Starting simplified swarm animation...")
    print("LEDs will flow in from edges to build THEME PARK WAITS")
    print("Press ESC or close window to exit.")
    
    # Get target pixels
    target_pixels = get_theme_park_waits_pixels()
    target_set = set(target_pixels)
    captured_pixels = set()
    
    # Animation state
    birds = []  # List of SimpleBird objects
    start_time = time.time()
    last_update = time.time()
    last_spawn = time.time()
    spawn_interval = 0.15  # Spawn new bird every 150ms (2x faster)
    animation_complete = False
    
    print("Target: {} text LEDs".format(len(target_pixels)))
    
    def update_animation():
        nonlocal last_update, last_spawn, animation_complete
        
        current_time = time.time()
        
        # Update every 60ms for smooth movement
        if current_time - last_update < 0.06:
            return
            
        last_update = current_time
        
        # Clear screen
        device.matrix.clear()
        
        # Show captured pixels as permanent text
        for pixel in captured_pixels:
            device.matrix.set_pixel(pixel[0], pixel[1], yellow)
        
        # Spawn new bird if needed
        if (current_time - last_spawn > spawn_interval and 
            len(captured_pixels) < len(target_pixels) and
            len(birds) < 10):  # Limit active birds for performance
            
            # Find a missing pixel to target
            target_pixel = find_nearest_missing_pixel(captured_pixels, target_pixels)
            if target_pixel:
                # Create path from edge to target
                start_x, start_y = get_spawn_point()
                path = create_path_to_target(start_x, start_y, target_pixel[0], target_pixel[1])
                
                # Create new bird
                bird = SimpleBird(path, target_pixel)
                birds.append(bird)
                last_spawn = current_time
        
        # Update all birds
        birds_to_remove = []
        for i, bird in enumerate(birds):
            captured = bird.update()
            
            if captured:
                # Bird reached its target
                captured_pixels.add(bird.target_pixel)
                birds_to_remove.append(i)
                print("Captured pixel {} ({}/{})".format(
                    bird.target_pixel, len(captured_pixels), len(target_pixels)))
            elif not bird.is_on_screen() and bird.path_index >= len(bird.path):
                # Bird flew off screen without capturing
                birds_to_remove.append(i)
            else:
                # Draw moving bird
                pos = bird.get_position()
                if bird.is_on_screen():
                    device.matrix.set_pixel(pos[0], pos[1], yellow)
        
        # Remove completed birds (in reverse order to maintain indices)
        for i in reversed(birds_to_remove):
            birds.pop(i)
        
        # Check completion
        if len(captured_pixels) >= len(target_pixels):
            if not animation_complete:
                elapsed = current_time - start_time
                print("THEME PARK WAITS completed in {:.1f} seconds!".format(elapsed))
                print("Animation complete!")
                animation_complete = True
    
    # Run animation
    device.run(title="THEME PARK WAITS Simple Swarm", update_callback=update_animation)


if __name__ == "__main__":
    main()