#!/usr/bin/env python3
"""Swarming LED animation that builds THEME PARK WAITS display and saves as GIF.

This is a modified version that captures frames during the animation to create
an animated GIF of the swarm building the text.
"""

import sys
import os
import random
import time
import math
import shutil
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3
from PIL import Image
import pygame


def get_theme_park_waits_pixels():
    """Return set of (x, y) coordinates for all LEDs in THEME PARK WAITS."""
    pixels = set()
    
    # THEME PARK - First line (8 pixels tall)
    # T (x=4, y=3) - 8 LEDs tall
    for x in range(4, 9): pixels.add((x, 3))
    for y in range(4, 11): pixels.add((6, y))
    
    # H (x=10, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.add((10, y))
    for y in range(3, 11): pixels.add((14, y))
    for x in range(11, 14): pixels.add((x, 6))
    
    # E (x=16, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.add((16, y))
    for x in range(16, 20): pixels.add((x, 3))
    for x in range(16, 19): pixels.add((x, 6))
    for x in range(16, 20): pixels.add((x, 10))
    
    # M (x=22, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.add((22, y))
    for y in range(3, 11): pixels.add((27, y))
    pixels.add((23, 4))
    pixels.add((24, 5))
    pixels.add((25, 5))
    pixels.add((26, 4))
    
    # E (x=29, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.add((29, y))
    for x in range(29, 33): pixels.add((x, 3))
    for x in range(29, 32): pixels.add((x, 6))
    for x in range(29, 33): pixels.add((x, 10))
    
    # P (x=36, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.add((36, y))
    for x in range(36, 40): pixels.add((x, 3))
    for x in range(36, 40): pixels.add((x, 6))
    pixels.add((39, 4))
    pixels.add((39, 5))
    
    # A (x=42, y=3) - 8 LEDs tall
    for y in range(4, 11): pixels.add((42, y))
    for y in range(4, 11): pixels.add((46, y))
    for x in range(43, 46): pixels.add((x, 3))
    for x in range(42, 47): pixels.add((x, 6))
    
    # R (x=48, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.add((48, y))
    for x in range(48, 52): pixels.add((x, 3))
    for x in range(48, 52): pixels.add((x, 6))
    pixels.add((51, 4))
    pixels.add((51, 5))
    pixels.add((50, 7))
    pixels.add((51, 8))
    pixels.add((52, 9))
    pixels.add((53, 10))
    
    # K (x=54, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.add((54, y))
    pixels.add((57, 3))
    pixels.add((56, 4))
    pixels.add((55, 5))
    pixels.add((55, 6))
    pixels.add((56, 7))
    pixels.add((57, 8))
    pixels.add((58, 9))
    pixels.add((59, 10))
    
    # WAITS - Second line (16 pixels tall, moved right by 3 LEDs)
    # W (x=5, y=15) - exact pattern from screenshot
    # Left outer edge
    ## CLAUDE ## DO NOT EDIT
    for y in range(15, 31):
        pixels.add((5, y))
        pixels.add((6, y))
    # Right outer edge
    for y in range(15, 31):
        pixels.add((13, y))
        pixels.add((14, y))
    # Middle V of W
    for x in range(7, 9): pixels.add((x, 28))
    for x in range(7, 9): pixels.add((x, 27))
    for x in range(11, 13): pixels.add((x, 28))
    for x in range(11, 13): pixels.add((x, 27))
    for y in range(23, 27): pixels.add((9, y))
    for y in range(23, 27): pixels.add((10, y))
    # END of CLAUDE DO NOT EDIT
    
    # A (x=16, y=15) - 10 LEDs wide, 16 pixels tall
    for y in range(17, 31): pixels.add((16, y))
    for y in range(17, 31): pixels.add((17, y))
    for y in range(17, 31): pixels.add((24, y))
    for y in range(17, 31): pixels.add((25, y))
    for x in range(18, 24): pixels.add((x, 15))
    for x in range(18, 24): pixels.add((x, 16))
    for x in range(16, 26): pixels.add((x, 22))
    for x in range(16, 26): pixels.add((x, 23))
    
    # I (x=27, y=15) - 10 LEDs wide, 16 pixels tall
    for x in range(27, 37): pixels.add((x, 15))
    for x in range(27, 37): pixels.add((x, 16))
    for x in range(27, 37): pixels.add((x, 29))
    for x in range(27, 37): pixels.add((x, 30))
    for y in range(15, 31): pixels.add((31, y))
    for y in range(15, 31): pixels.add((32, y))
    
    # T (x=38, y=15) - 10 LEDs wide, 16 pixels tall
    for x in range(38, 48): pixels.add((x, 15))
    for x in range(38, 48): pixels.add((x, 16))
    for y in range(15, 31): pixels.add((42, y))
    for y in range(15, 31): pixels.add((43, y))
    
    # S (x=49, y=15) - 10 LEDs wide, 16 pixels tall
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


class FlockBird:
    """A single bird in the flock with position and flocking behavior."""
    
    def __init__(self, x, y, direction):
        self.x = float(x)
        self.y = float(y)
        # Flight direction and speed
        self.vx = direction[0] * random.uniform(0.8, 1.2)
        self.vy = direction[1] * random.uniform(0.8, 1.2)
        # Individual characteristics
        self.phase = random.uniform(0, 2 * math.pi)
        self.speed_multiplier = random.uniform(0.7, 1.3)
        self.separation_radius = random.uniform(2.0, 4.0)
        
    def get_pixel_pos(self):
        """Get integer pixel position."""
        return (int(round(self.x)), int(round(self.y)))
    
    def is_on_screen(self):
        """Check if bird is currently visible on screen."""
        return 0 <= self.x < 64 and 0 <= self.y < 32
    
    def update_flocking(self, flock, target_pixels, captured_pixels, attraction_center):
        """Update position using flocking behavior (boids algorithm)."""
        # Flocking rules
        separation = self.separation_rule(flock)
        alignment = self.alignment_rule(flock)
        cohesion = self.cohesion_rule(flock)
        attraction = self.attraction_rule(target_pixels, captured_pixels, attraction_center)
        
        # Apply flocking forces with weights
        self.vx += separation[0] * 0.15 + alignment[0] * 0.1 + cohesion[0] * 0.05 + attraction[0] * 0.3
        self.vy += separation[1] * 0.15 + alignment[1] * 0.1 + cohesion[1] * 0.05 + attraction[1] * 0.3
        
        # Add some wing-flapping motion
        self.vx += 0.05 * math.sin(self.phase + time.time() * 8) * self.speed_multiplier
        self.vy += 0.03 * math.cos(self.phase + time.time() * 6) * self.speed_multiplier
        
        # Limit velocity
        max_vel = 3.0
        vel_mag = math.sqrt(self.vx*self.vx + self.vy*self.vy)
        if vel_mag > max_vel:
            self.vx = (self.vx / vel_mag) * max_vel
            self.vy = (self.vy / vel_mag) * max_vel
        
        # Update position
        self.x += self.vx * 0.4
        self.y += self.vy * 0.4
    
    def separation_rule(self, flock):
        """Steer to avoid crowding local flockmates."""
        steer_x, steer_y = 0.0, 0.0
        count = 0
        
        for other in flock:
            if other is self:
                continue
            dx = self.x - other.x
            dy = self.y - other.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if 0 < distance < self.separation_radius:
                # Normalize and weight by distance
                steer_x += dx / distance / distance
                steer_y += dy / distance / distance
                count += 1
        
        if count > 0:
            steer_x /= count
            steer_y /= count
        
        return (steer_x, steer_y)
    
    def alignment_rule(self, flock):
        """Steer towards the average heading of neighbors."""
        avg_vx, avg_vy = 0.0, 0.0
        count = 0
        neighbor_distance = 8.0
        
        for other in flock:
            if other is self:
                continue
            dx = self.x - other.x
            dy = self.y - other.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < neighbor_distance:
                avg_vx += other.vx
                avg_vy += other.vy
                count += 1
        
        if count > 0:
            avg_vx /= count
            avg_vy /= count
            # Return steering force toward average heading
            return (avg_vx - self.vx, avg_vy - self.vy)
        
        return (0.0, 0.0)
    
    def cohesion_rule(self, flock):
        """Steer to move toward the average position of local flockmates."""
        center_x, center_y = 0.0, 0.0
        count = 0
        neighbor_distance = 12.0
        
        for other in flock:
            if other is self:
                continue
            dx = self.x - other.x
            dy = self.y - other.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < neighbor_distance:
                center_x += other.x
                center_y += other.y
                count += 1
        
        if count > 0:
            center_x /= count
            center_y /= count
            # Return steering force toward center
            return ((center_x - self.x) * 0.01, (center_y - self.y) * 0.01)
        
        return (0.0, 0.0)
    
    def attraction_rule(self, target_pixels, captured_pixels, attraction_center):
        """Steer toward areas with missing LEDs."""
        if attraction_center is None:
            return (0.0, 0.0)
        
        # Attraction to densest missing area
        dx = attraction_center[0] - self.x
        dy = attraction_center[1] - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # Normalize and scale attraction
            attraction_strength = 0.5
            return (dx / distance * attraction_strength, dy / distance * attraction_strength)
        
        return (0.0, 0.0)


def find_largest_missing_clump(target_pixels, captured_pixels):
    """Find the center of the largest clump of missing LEDs."""
    missing_pixels = target_pixels - captured_pixels
    if not missing_pixels:
        return None
    
    # If only a few pixels remain, target them directly
    if len(missing_pixels) <= 10:
        # Return the centroid of all missing pixels
        center_x = sum(pixel[0] for pixel in missing_pixels) / len(missing_pixels)
        center_y = sum(pixel[1] for pixel in missing_pixels) / len(missing_pixels)
        return (center_x, center_y)
    
    # For larger groups, find the biggest clump using clustering
    best_center = None
    best_clump_size = 0
    
    # Check each missing pixel as a potential clump center
    for center_pixel in missing_pixels:
        clump_pixels = []
        clump_weight = 0
        
        # Find all missing pixels within clump radius
        for pixel in missing_pixels:
            dx = pixel[0] - center_pixel[0]
            dy = pixel[1] - center_pixel[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance <= 12:  # Clump radius
                clump_pixels.append(pixel)
                # Weight by inverse distance - closer pixels matter more
                weight = 1.0 / (distance + 1)
                clump_weight += weight
        
        # This clump is better if it has more weighted pixels
        if clump_weight > best_clump_size:
            best_clump_size = clump_weight
            # Calculate weighted centroid of this clump
            if clump_pixels:
                total_weight = 0
                weighted_x = 0
                weighted_y = 0
                
                for pixel in clump_pixels:
                    dx = pixel[0] - center_pixel[0]
                    dy = pixel[1] - center_pixel[1]
                    distance = math.sqrt(dx*dx + dy*dy)
                    weight = 1.0 / (distance + 1)
                    
                    weighted_x += pixel[0] * weight
                    weighted_y += pixel[1] * weight
                    total_weight += weight
                
                if total_weight > 0:
                    best_center = (weighted_x / total_weight, weighted_y / total_weight)
    
    return best_center


def find_best_entry_point(direction, target_pixels, captured_pixels):
    """Find the best entry point along an edge to target missing LEDs."""
    missing_pixels = target_pixels - captured_pixels
    if not missing_pixels:
        return 32  # Default center if no missing pixels
    
    best_entry = 32
    best_score = 0
    
    # Sample entry points along the edge
    if direction in ["left", "right"]:
        # Vertical edge - sample Y coordinates
        for entry_y in range(0, 32, 2):
            score = 0
            for pixel in missing_pixels:
                # Weight by inverse distance from entry point
                distance = abs(pixel[1] - entry_y)
                # Also weight by horizontal proximity for left/right entries
                if direction == "left":
                    distance += abs(pixel[0] - 0) * 0.3  # Prefer LEDs closer to left edge
                else:
                    distance += abs(pixel[0] - 63) * 0.3  # Prefer LEDs closer to right edge
                
                if distance < 20:  # Within reasonable targeting range
                    score += 1.0 / (distance + 1)
            
            if score > best_score:
                best_score = score
                best_entry = entry_y
                
    elif direction in ["top", "bottom"]:
        # Horizontal edge - sample X coordinates
        for entry_x in range(0, 64, 4):
            score = 0
            for pixel in missing_pixels:
                # Weight by inverse distance from entry point
                distance = abs(pixel[0] - entry_x)
                # Also weight by vertical proximity for top/bottom entries
                if direction == "top":
                    distance += abs(pixel[1] - 0) * 0.3  # Prefer LEDs closer to top edge
                else:
                    distance += abs(pixel[1] - 31) * 0.3  # Prefer LEDs closer to bottom edge
                
                if distance < 20:  # Within reasonable targeting range
                    score += 1.0 / (distance + 1)
            
            if score > best_score:
                best_score = score
                best_entry = entry_x
    
    # For diagonal entries, find the best corner area
    else:
        corner_scores = {}
        for pixel in missing_pixels:
            if direction == "top_left":
                score = 1.0 / (pixel[0] + pixel[1] + 1)
            elif direction == "top_right":
                score = 1.0 / ((63 - pixel[0]) + pixel[1] + 1)
            elif direction == "bottom_left":
                score = 1.0 / (pixel[0] + (31 - pixel[1]) + 1)
            else:  # bottom_right
                score = 1.0 / ((63 - pixel[0]) + (31 - pixel[1]) + 1)
            
            corner_scores[pixel] = corner_scores.get(pixel, 0) + score
        
        if corner_scores:
            # Find the centroid of high-scoring pixels
            total_score = sum(corner_scores.values())
            weighted_x = sum(pixel[0] * score for pixel, score in corner_scores.items()) / total_score
            weighted_y = sum(pixel[1] * score for pixel, score in corner_scores.items()) / total_score
            best_entry = (weighted_x, weighted_y)
        else:
            best_entry = (32, 16)  # Default center
    
    return best_entry


def create_flock_from_direction(num_birds, direction, target_pixels, captured_pixels):
    """Create a flock of birds entering from a specific direction, targeting missing LEDs."""
    flock = []
    
    # Get optimal entry point based on missing LEDs
    entry_point = find_best_entry_point(direction, target_pixels, captured_pixels)
    
    # Entry points based on direction
    if direction == "left":
        base_x, base_y = -10, entry_point
        flight_dir = (2.0, random.uniform(-0.5, 0.5))
    elif direction == "right":
        base_x, base_y = 74, entry_point
        flight_dir = (-2.0, random.uniform(-0.5, 0.5))
    elif direction == "top":
        base_x, base_y = entry_point, -10
        flight_dir = (random.uniform(-0.5, 0.5), 2.0)
    elif direction == "bottom":
        base_x, base_y = entry_point, 42
        flight_dir = (random.uniform(-0.5, 0.5), -2.0)
    else:  # diagonal entries
        if isinstance(entry_point, tuple):
            target_x, target_y = entry_point
        else:
            target_x, target_y = 32, 16
            
        if direction == "top_left":
            base_x, base_y = -10, -10
            # Aim toward the target area
            flight_dir = ((target_x + 10) / 20, (target_y + 10) / 20)
        elif direction == "top_right":
            base_x, base_y = 74, -10
            flight_dir = ((target_x - 74) / 20, (target_y + 10) / 20)
        elif direction == "bottom_left":
            base_x, base_y = -10, 42
            flight_dir = ((target_x + 10) / 20, (target_y - 42) / 20)
        else:  # bottom_right
            base_x, base_y = 74, 42
            flight_dir = ((target_x - 74) / 20, (target_y - 42) / 20)
    
    # Create formation
    for i in range(num_birds):
        # V-formation offset
        row = i // 8
        col = i % 8
        offset_x = (col - 4) * 2 + random.uniform(-1, 1)
        offset_y = row * 3 + random.uniform(-1, 1)
        
        bird_x = base_x + offset_x
        bird_y = base_y + offset_y
        
        flock.append(FlockBird(bird_x, bird_y, flight_dir))
    
    return flock


def main():
    """Run the flocking bird animation and save as GIF."""
    # Create output directory for frames
    frames_dir = "swarm_frames"
    if os.path.exists(frames_dir):
        shutil.rmtree(frames_dir)
    os.makedirs(frames_dir)
    
    device = MatrixPortalS3()
    device.initialize()
    device.matrix.clear()
    
    yellow = (255, 255, 0)
    
    # Get target pixels for THEME PARK WAITS
    target_pixels = get_theme_park_waits_pixels()
    captured_pixels = set()
    
    # Flocking state
    flock = []
    num_needed = len(target_pixels)
    
    # Flight patterns
    directions = ["left", "right", "top", "bottom", "top_left", "top_right", "bottom_left", "bottom_right"]
    current_direction_idx = 0
    last_spawn_time = 0
    spawn_interval = 3.0  # Seconds between new flocks
    
    print(f"Starting bird flock animation with {num_needed} LEDs needed...")
    print("Capturing frames for GIF generation...")
    print("Press ESC or close window to exit.")
    
    # Animation state
    start_time = time.time()
    frame_count = 0
    animation_complete = False
    last_update = time.time()
    completion_time = None
    
    # Frame capture settings
    frame_number = 0
    capture_interval = 3  # Capture every 3rd frame for smoother GIF
    captured_frames = []
    
    def update_animation():
        nonlocal frame_count, animation_complete, last_update
        nonlocal flock, current_direction_idx, last_spawn_time, completion_time
        nonlocal frame_number
        
        current_time = time.time()
        # Update every ~50ms for smooth movement
        if current_time - last_update < 0.05:
            return
        
        time_elapsed = current_time - start_time
        last_update = current_time
        
        # Check if all text is complete
        text_complete = len(captured_pixels) >= len(target_pixels)
        
        if text_complete and completion_time is None:
            # Mark the completion time
            completion_time = current_time
            elapsed = current_time - start_time
            print(f"THEME PARK WAITS completed in {elapsed:.1f} seconds!")
            print("Capturing final frames...")
        
        # End program 2 seconds after completion (to capture a bit more)
        if completion_time is not None and current_time - completion_time >= 2.0:
            print("Animation complete!")
            animation_complete = True
            return
        
        # If text is complete but we're in the grace period, make birds fly out
        if text_complete and len(flock) > 0:
            # Change behavior: make remaining birds fly toward exits
            for bird in flock:
                # Find nearest exit and fly toward it
                exits = [
                    (-20, bird.y),  # Left exit
                    (84, bird.y),   # Right exit  
                    (bird.x, -20),  # Top exit
                    (bird.x, 52)    # Bottom exit
                ]
                
                # Find closest exit
                closest_exit = min(exits, key=lambda exit_pos: 
                    math.sqrt((bird.x - exit_pos[0])**2 + (bird.y - exit_pos[1])**2))
                
                # Fly toward exit with increased speed
                dx = closest_exit[0] - bird.x
                dy = closest_exit[1] - bird.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance > 0:
                    # Override flocking behavior - head straight for exit
                    exit_speed = 6.0  # Even faster exit speed
                    bird.vx = (dx / distance) * exit_speed
                    bird.vy = (dy / distance) * exit_speed
                
                # Update position with faster movement
                bird.x += bird.vx * 0.8
                bird.y += bird.vy * 0.8
                
        elif not text_complete:
            # Normal flocking behavior when text is not complete
            frame_count += 1
            
            # Calculate remaining LEDs
            remaining_leds = len(target_pixels) - len(captured_pixels)
            
            # Adjust spawn behavior for final LEDs
            if remaining_leds <= 15:  # Trigger urgency mode earlier
                # For final few LEDs, spawn more frequently and from all directions
                spawn_interval_adjusted = 0.5  # Spawn every half second
                max_flock_size = 500  # Allow even more birds
            else:
                spawn_interval_adjusted = spawn_interval
                max_flock_size = 200  # Doubled from 100
            
            # Spawn new flock if needed and there are still LEDs to capture
            if (remaining_leds > 0 and 
                time_elapsed - last_spawn_time > spawn_interval_adjusted and
                len(flock) < max_flock_size):
                
                # Calculate how many birds to spawn
                if remaining_leds <= 15:
                    # For final LEDs, spawn many more birds to ensure quick completion
                    birds_to_spawn = min(100, remaining_leds * 30)  # Massive swarm
                else:
                    birds_to_spawn = min(100, remaining_leds)  # Doubled from 50
                
                direction = directions[current_direction_idx]
                
                new_flock = create_flock_from_direction(birds_to_spawn, direction, target_pixels, captured_pixels)
                flock.extend(new_flock)
                
                if remaining_leds <= 15:
                    print(f"URGENT: {birds_to_spawn} birds targeting final {remaining_leds} LEDs from {direction}")
                else:
                    print(f"Flock of {birds_to_spawn} birds flying in from {direction} ({remaining_leds} LEDs remaining)")
                
                current_direction_idx = (current_direction_idx + 1) % len(directions)
                last_spawn_time = time_elapsed
            
            # Find the largest clump of missing LEDs for attraction
            attraction_center = find_largest_missing_clump(target_pixels, captured_pixels)
            
            # Special behavior for final LEDs
            missing_pixels = target_pixels - captured_pixels
            few_remaining = len(missing_pixels) <= 15  # Increased threshold
            
            # Update bird positions 
            for bird in flock:
                if few_remaining:
                    # AGGRESSIVE direct targeting - completely override flocking
                    if missing_pixels:
                        closest_missing = min(missing_pixels, 
                            key=lambda pixel: math.sqrt((bird.x - pixel[0])**2 + (bird.y - pixel[1])**2))
                        
                        # Calculate direct path to target
                        dx = closest_missing[0] - bird.x
                        dy = closest_missing[1] - bird.y
                        distance = math.sqrt(dx*dx + dy*dy)
                        
                        if distance > 0:
                            # Use very high speed and direct path
                            target_speed = 4.0  # Much faster
                            bird.vx = (dx / distance) * target_speed
                            bird.vy = (dy / distance) * target_speed
                            
                            # NO random component - pure targeting
                        
                        # Update position with much faster movement
                        bird.x += bird.vx * 1.2  # Even faster position updates
                        bird.y += bird.vy * 1.2
                else:
                    # Normal flocking behavior
                    bird.update_flocking(flock, target_pixels, captured_pixels, attraction_center)
        
        # Check for LED lighting (only when text is not complete)
        if not text_complete:
            for bird in flock:
                if bird.is_on_screen():
                    pixel_pos = bird.get_pixel_pos()
                    if pixel_pos in target_pixels and pixel_pos not in captured_pixels:
                        # Light up this LED but bird stays in flock
                        captured_pixels.add(pixel_pos)
                        print(f"LED lit at {pixel_pos} ({len(captured_pixels)}/{len(target_pixels)})")
        
        # Remove birds that have flown too far off screen
        birds_to_remove = []
        for i, bird in enumerate(flock):
            if (bird.x < -25 or bird.x > 89 or 
                bird.y < -25 or bird.y > 57):
                birds_to_remove.append(i)
        
        for i in reversed(birds_to_remove):
            flock.pop(i)
        
        # Update display
        device.matrix.clear()
        
        # Draw captured text pixels (permanently on)
        for pixel in captured_pixels:
            device.matrix.set_pixel(pixel[0], pixel[1], yellow)
        
        # Draw birds
        for bird in flock:
            if bird.is_on_screen():
                bird_x, bird_y = bird.get_pixel_pos()
                device.matrix.set_pixel(bird_x, bird_y, yellow)
        
        # Capture frame for GIF
        if frame_count % capture_interval == 0:
            frame_path = os.path.join(frames_dir, f"frame_{frame_number:04d}.png")
            device.matrix.save_screenshot(frame_path)
            captured_frames.append(frame_path)
            frame_number += 1
            
            if frame_number % 10 == 0:
                print(f"Captured {frame_number} frames...")
        
        # Show progress every 100 frames
        if frame_count % 100 == 0:
            elapsed = time.time() - start_time
            print(f"Progress: {len(captured_pixels)}/{len(target_pixels)} captured, {len(flock)} birds flying - {elapsed:.1f}s")
    
    # Run with animation callback
    device.run(title="THEME PARK WAITS Bird Flock", update_callback=update_animation)
    
    # Create GIF from captured frames
    if captured_frames:
        print(f"\nCreating GIF from {len(captured_frames)} frames...")
        
        # Load all frames
        images = []
        for frame_path in captured_frames:
            img = Image.open(frame_path)
            images.append(img)
        
        # Save as animated GIF
        gif_path = "theme_park_waits_swarm.gif"
        if images:
            # Duration is in milliseconds, so 50ms per frame = 20fps
            images[0].save(
                gif_path,
                save_all=True,
                append_images=images[1:],
                duration=50,
                loop=0,
                optimize=True
            )
            
            print(f"GIF saved as: {gif_path}")
            print(f"GIF size: {os.path.getsize(gif_path) / 1024:.1f} KB")
        
        # Clean up frames directory
        shutil.rmtree(frames_dir)
    else:
        print("No frames captured!")


if __name__ == "__main__":
    main()