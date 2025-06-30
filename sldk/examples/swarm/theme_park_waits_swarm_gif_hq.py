#!/usr/bin/env python3
"""High-quality version of the swarm animation with dynamic colors.

This version captures more frames and generates an MP4 video file
with dynamic rainbow colors for both the birds and the captured text.
Also creates a preview GIF for quick viewing.
"""

import sys
import os
import random
import time
import math
import shutil
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..' if 'PyLEDSimulator' in __file__ else '.', 'sldk', 'src'))

from sldk.simulator.devices import MatrixPortalS3
from sldk.simulator.core import DisplayManager
from PIL import Image
import pygame
import imageio


def hsv_to_rgb(h, s, v):
    """Convert HSV color to RGB."""
    h = h % 1.0
    c = v * s
    x = c * (1 - abs((h * 6) % 2 - 1))
    m = v - c
    
    if h < 1/6:
        r, g, b = c, x, 0
    elif h < 2/6:
        r, g, b = x, c, 0
    elif h < 3/6:
        r, g, b = 0, c, x
    elif h < 4/6:
        r, g, b = 0, x, c
    elif h < 5/6:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
        
    return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))


def get_dynamic_flock_color(time_elapsed, bird_index=0):
    """Generate dynamic colors for the bird flock based on time and position.
    
    Args:
        time_elapsed: Time since animation started
        bird_index: Optional index of the bird for variation
        
    Returns:
        (r, g, b) color tuple
    """
    # Create a rainbow effect that cycles over time
    # Different birds get slightly offset colors for variety
    hue_offset = (time_elapsed * 0.5 + bird_index * 0.1) % 1.0
    
    # Create a vibrant rainbow effect
    return hsv_to_rgb(hue_offset, 0.9, 0.8)


def get_dynamic_text_color(time_elapsed, pixel_pos):
    """Generate dynamic colors for the captured text based on time and position.
    
    Args:
        time_elapsed: Time since animation started
        pixel_pos: (x, y) position of the pixel for spatial variation
        
    Returns:
        (r, g, b) color tuple
    """
    # Create a wave effect across the text
    # Color changes based on position and time for a flowing rainbow
    x, y = pixel_pos
    # Normalize position to create a wave effect across the display
    position_offset = (x / 64.0 + y / 32.0) * 0.3
    
    # Slower color cycle for text (0.2x speed) with position-based offset
    hue = (time_elapsed * 0.2 + position_offset) % 1.0
    
    # Full saturation and brightness for vibrant text
    return hsv_to_rgb(hue, 1.0, 1.0)


# Copy all the helper functions from the original file
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
    for y in range(15, 31):
        pixels.add((5, y))
        pixels.add((6, y))
    for y in range(15, 31):
        pixels.add((13, y))
        pixels.add((14, y))
    for x in range(7, 9): pixels.add((x, 28))
    for x in range(7, 9): pixels.add((x, 27))
    for x in range(11, 13): pixels.add((x, 28))
    for x in range(11, 13): pixels.add((x, 27))
    for y in range(23, 27): pixels.add((9, y))
    for y in range(23, 27): pixels.add((10, y))
    
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
        self.vx = direction[0] * random.uniform(0.8, 1.2)
        self.vy = direction[1] * random.uniform(0.8, 1.2)
        self.phase = random.uniform(0, 2 * math.pi)
        self.speed_multiplier = random.uniform(0.7, 1.3)
        self.separation_radius = random.uniform(2.0, 4.0)
        
    def get_pixel_pos(self):
        return (int(round(self.x)), int(round(self.y)))
    
    def is_on_screen(self):
        return 0 <= self.x < 64 and 0 <= self.y < 32
    
    def update_flocking(self, flock, target_pixels, captured_pixels, attraction_center):
        separation = self.separation_rule(flock)
        alignment = self.alignment_rule(flock)
        cohesion = self.cohesion_rule(flock)
        attraction = self.attraction_rule(target_pixels, captured_pixels, attraction_center)
        
        self.vx += separation[0] * 0.15 + alignment[0] * 0.1 + cohesion[0] * 0.05 + attraction[0] * 0.3
        self.vy += separation[1] * 0.15 + alignment[1] * 0.1 + cohesion[1] * 0.05 + attraction[1] * 0.3
        
        self.vx += 0.05 * math.sin(self.phase + time.time() * 8) * self.speed_multiplier
        self.vy += 0.03 * math.cos(self.phase + time.time() * 6) * self.speed_multiplier
        
        max_vel = 3.0
        vel_mag = math.sqrt(self.vx*self.vx + self.vy*self.vy)
        if vel_mag > max_vel:
            self.vx = (self.vx / vel_mag) * max_vel
            self.vy = (self.vy / vel_mag) * max_vel
        
        self.x += self.vx * 0.4
        self.y += self.vy * 0.4
    
    def separation_rule(self, flock):
        steer_x, steer_y = 0.0, 0.0
        count = 0
        
        for other in flock:
            if other is self:
                continue
            dx = self.x - other.x
            dy = self.y - other.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if 0 < distance < self.separation_radius:
                steer_x += dx / distance / distance
                steer_y += dy / distance / distance
                count += 1
        
        if count > 0:
            steer_x /= count
            steer_y /= count
        
        return (steer_x, steer_y)
    
    def alignment_rule(self, flock):
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
            return (avg_vx - self.vx, avg_vy - self.vy)
        
        return (0.0, 0.0)
    
    def cohesion_rule(self, flock):
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
            return ((center_x - self.x) * 0.01, (center_y - self.y) * 0.01)
        
        return (0.0, 0.0)
    
    def attraction_rule(self, target_pixels, captured_pixels, attraction_center):
        if attraction_center is None:
            return (0.0, 0.0)
        
        dx = attraction_center[0] - self.x
        dy = attraction_center[1] - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            attraction_strength = 0.5
            return (dx / distance * attraction_strength, dy / distance * attraction_strength)
        
        return (0.0, 0.0)


def find_largest_missing_clump(target_pixels, captured_pixels):
    missing_pixels = target_pixels - captured_pixels
    if not missing_pixels:
        return None
    
    if len(missing_pixels) <= 10:
        center_x = sum(pixel[0] for pixel in missing_pixels) / len(missing_pixels)
        center_y = sum(pixel[1] for pixel in missing_pixels) / len(missing_pixels)
        return (center_x, center_y)
    
    best_center = None
    best_clump_size = 0
    
    for center_pixel in missing_pixels:
        clump_pixels = []
        clump_weight = 0
        
        for pixel in missing_pixels:
            dx = pixel[0] - center_pixel[0]
            dy = pixel[1] - center_pixel[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance <= 12:
                clump_pixels.append(pixel)
                weight = 1.0 / (distance + 1)
                clump_weight += weight
        
        if clump_weight > best_clump_size:
            best_clump_size = clump_weight
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
    missing_pixels = target_pixels - captured_pixels
    if not missing_pixels:
        return 32
    
    best_entry = 32
    best_score = 0
    
    if direction in ["left", "right"]:
        for entry_y in range(0, 32, 2):
            score = 0
            for pixel in missing_pixels:
                distance = abs(pixel[1] - entry_y)
                if direction == "left":
                    distance += abs(pixel[0] - 0) * 0.3
                else:
                    distance += abs(pixel[0] - 63) * 0.3
                
                if distance < 20:
                    score += 1.0 / (distance + 1)
            
            if score > best_score:
                best_score = score
                best_entry = entry_y
                
    elif direction in ["top", "bottom"]:
        for entry_x in range(0, 64, 4):
            score = 0
            for pixel in missing_pixels:
                distance = abs(pixel[0] - entry_x)
                if direction == "top":
                    distance += abs(pixel[1] - 0) * 0.3
                else:
                    distance += abs(pixel[1] - 31) * 0.3
                
                if distance < 20:
                    score += 1.0 / (distance + 1)
            
            if score > best_score:
                best_score = score
                best_entry = entry_x
    else:
        corner_scores = {}
        for pixel in missing_pixels:
            if direction == "top_left":
                score = 1.0 / (pixel[0] + pixel[1] + 1)
            elif direction == "top_right":
                score = 1.0 / ((63 - pixel[0]) + pixel[1] + 1)
            elif direction == "bottom_left":
                score = 1.0 / (pixel[0] + (31 - pixel[1]) + 1)
            else:
                score = 1.0 / ((63 - pixel[0]) + (31 - pixel[1]) + 1)
            
            corner_scores[pixel] = corner_scores.get(pixel, 0) + score
        
        if corner_scores:
            total_score = sum(corner_scores.values())
            weighted_x = sum(pixel[0] * score for pixel, score in corner_scores.items()) / total_score
            weighted_y = sum(pixel[1] * score for pixel, score in corner_scores.items()) / total_score
            best_entry = (weighted_x, weighted_y)
        else:
            best_entry = (32, 16)
    
    return best_entry


def create_flock_from_direction(num_birds, direction, target_pixels, captured_pixels):
    flock = []
    entry_point = find_best_entry_point(direction, target_pixels, captured_pixels)
    
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
    else:
        if isinstance(entry_point, tuple):
            target_x, target_y = entry_point
        else:
            target_x, target_y = 32, 16
            
        if direction == "top_left":
            base_x, base_y = -10, -10
            flight_dir = ((target_x + 10) / 20, (target_y + 10) / 20)
        elif direction == "top_right":
            base_x, base_y = 74, -10
            flight_dir = ((target_x - 74) / 20, (target_y + 10) / 20)
        elif direction == "bottom_left":
            base_x, base_y = -10, 42
            flight_dir = ((target_x + 10) / 20, (target_y - 42) / 20)
        else:
            base_x, base_y = 74, 42
            flight_dir = ((target_x - 74) / 20, (target_y - 42) / 20)
    
    for i in range(num_birds):
        row = i // 8
        col = i % 8
        offset_x = (col - 4) * 2 + random.uniform(-1, 1)
        offset_y = row * 3 + random.uniform(-1, 1)
        
        bird_x = base_x + offset_x
        bird_y = base_y + offset_y
        
        flock.append(FlockBird(bird_x, bird_y, flight_dir))
    
    return flock


def main():
    """Run the flocking bird animation and save as high-quality MP4."""
    frames_dir = "swarm_frames_hq"
    if os.path.exists(frames_dir):
        shutil.rmtree(frames_dir)
    os.makedirs(frames_dir)
    
    device = MatrixPortalS3()
    device.initialize()
    device.matrix.clear()
    
    # Initialize display manager
    device.display_manager = DisplayManager()
    device.display_manager.add_display(device.matrix)
    device.display_manager.create_window(title="THEME PARK WAITS Bird Flock (HQ)")
    
    target_pixels = get_theme_park_waits_pixels()
    captured_pixels = set()
    
    flock = []
    num_needed = len(target_pixels)
    
    directions = ["left", "right", "top", "bottom", "top_left", "top_right", "bottom_left", "bottom_right"]
    current_direction_idx = 0
    last_spawn_time = 0
    spawn_interval = 3.0
    
    print(f"Starting high-quality bird flock animation with {num_needed} LEDs needed...")
    print("Dynamic rainbow colors for both birds and text!")
    print("Capturing frames for MP4 video generation...")
    print("Press ESC or close window to exit.")
    
    start_time = time.time()
    frame_count = 0
    animation_complete = False
    last_update = time.time()
    completion_time = None
    
    # Higher quality settings - capture every frame for 24fps video
    frame_number = 0
    capture_interval = 1  # Capture every frame for maximum frames
    captured_frames = []
    
    def update_animation():
        nonlocal frame_count, animation_complete, last_update
        nonlocal flock, current_direction_idx, last_spawn_time, completion_time
        nonlocal frame_number
        
        current_time = time.time()
        if current_time - last_update < 0.05:
            return
        
        time_elapsed = current_time - start_time
        last_update = current_time
        
        text_complete = len(captured_pixels) >= len(target_pixels)
        
        if text_complete and completion_time is None:
            completion_time = current_time
            elapsed = current_time - start_time
            print(f"THEME PARK WAITS completed in {elapsed:.1f} seconds!")
            print("Capturing final frames...")
        
        if completion_time is not None and current_time - completion_time >= 3.0:  # Capture 3 seconds after completion
            print("Animation complete!")
            animation_complete = True
            # Don't return here - let the frame be captured and updated
            # return
        
        if text_complete and len(flock) > 0:
            for bird in flock:
                exits = [
                    (-20, bird.y),
                    (84, bird.y),
                    (bird.x, -20),
                    (bird.x, 52)
                ]
                
                closest_exit = min(exits, key=lambda exit_pos: 
                    math.sqrt((bird.x - exit_pos[0])**2 + (bird.y - exit_pos[1])**2))
                
                dx = closest_exit[0] - bird.x
                dy = closest_exit[1] - bird.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance > 0:
                    exit_speed = 6.0
                    bird.vx = (dx / distance) * exit_speed
                    bird.vy = (dy / distance) * exit_speed
                
                bird.x += bird.vx * 0.8
                bird.y += bird.vy * 0.8
                
        elif not text_complete:
            frame_count += 1
            
            remaining_leds = len(target_pixels) - len(captured_pixels)
            
            if remaining_leds <= 15:
                spawn_interval_adjusted = 0.5
                max_flock_size = 500
            else:
                spawn_interval_adjusted = spawn_interval
                max_flock_size = 200
            
            if (remaining_leds > 0 and 
                time_elapsed - last_spawn_time > spawn_interval_adjusted and
                len(flock) < max_flock_size):
                
                if remaining_leds <= 15:
                    birds_to_spawn = min(100, remaining_leds * 30)
                else:
                    birds_to_spawn = min(100, remaining_leds)
                
                direction = directions[current_direction_idx]
                
                new_flock = create_flock_from_direction(birds_to_spawn, direction, target_pixels, captured_pixels)
                flock.extend(new_flock)
                
                current_direction_idx = (current_direction_idx + 1) % len(directions)
                last_spawn_time = time_elapsed
            
            attraction_center = find_largest_missing_clump(target_pixels, captured_pixels)
            
            missing_pixels = target_pixels - captured_pixels
            few_remaining = len(missing_pixels) <= 15
            
            for bird in flock:
                if few_remaining:
                    if missing_pixels:
                        closest_missing = min(missing_pixels, 
                            key=lambda pixel: math.sqrt((bird.x - pixel[0])**2 + (bird.y - pixel[1])**2))
                        
                        dx = closest_missing[0] - bird.x
                        dy = closest_missing[1] - bird.y
                        distance = math.sqrt(dx*dx + dy*dy)
                        
                        if distance > 0:
                            target_speed = 4.0
                            bird.vx = (dx / distance) * target_speed
                            bird.vy = (dy / distance) * target_speed
                        
                        bird.x += bird.vx * 1.2
                        bird.y += bird.vy * 1.2
                else:
                    bird.update_flocking(flock, target_pixels, captured_pixels, attraction_center)
        
        if not text_complete:
            for bird in flock:
                if bird.is_on_screen():
                    pixel_pos = bird.get_pixel_pos()
                    if pixel_pos in target_pixels and pixel_pos not in captured_pixels:
                        captured_pixels.add(pixel_pos)
        
        birds_to_remove = []
        for i, bird in enumerate(flock):
            if (bird.x < -25 or bird.x > 89 or 
                bird.y < -25 or bird.y > 57):
                birds_to_remove.append(i)
        
        for i in reversed(birds_to_remove):
            flock.pop(i)
        
        device.matrix.clear()
        
        # Draw captured text pixels with dynamic colors
        for pixel in captured_pixels:
            text_color = get_dynamic_text_color(time_elapsed, pixel)
            device.matrix.set_pixel(pixel[0], pixel[1], text_color)
        
        # Draw birds with dynamic colors
        for i, bird in enumerate(flock):
            if bird.is_on_screen():
                bird_x, bird_y = bird.get_pixel_pos()
                bird_color = get_dynamic_flock_color(time_elapsed, i)
                device.matrix.set_pixel(bird_x, bird_y, bird_color)
        
        # Capture frames with higher frequency
        if frame_count % capture_interval == 0:
            frame_path = os.path.join(frames_dir, f"frame_{frame_number:04d}.png")
            device.matrix.save_screenshot(frame_path)
            captured_frames.append(frame_path)
            frame_number += 1
            
            if frame_number % 20 == 0:
                print(f"Captured {frame_number} frames...")
    
    # Run the animation until complete
    while not animation_complete:
        # Handle events
        if not device.display_manager.handle_events():
            break
            
        # Update animation
        update_animation()
        
        # Update the display
        device.display_manager.update()
        
    print("Animation loop finished, saving video...")
    
    if captured_frames:
        print(f"\nCreating high-quality video from {len(captured_frames)} frames...")
        
        # Load frames and skip duplicates
        images = []
        last_img_data = None
        skipped = 0
        
        for i, frame_path in enumerate(captured_frames):
            # Skip if file doesn't exist (can happen with frame numbering issues)
            if not os.path.exists(frame_path):
                continue
            img = Image.open(frame_path)
            
            # Convert to comparable format
            img_data = img.convert('RGB').tobytes()
            
            # Skip if identical to previous frame
            if img_data != last_img_data:
                images.append(img)
                last_img_data = img_data
            else:
                skipped += 1
                
        print(f"Loaded {len(images)} unique frames (skipped {skipped} duplicates)")
        
        video_path = "theme_park_waits_swarm_hq.mp4"
        if len(images) > 1:
            # 24fps for smooth playback with 6 second duration
            target_duration = 6.0  # seconds
            fps = 24
            
            # If we have more frames than needed, sample them
            frames_needed = int(target_duration * fps)  # 144 frames for 6 seconds
            if len(images) > frames_needed:
                # Sample frames evenly
                indices = [int(i * len(images) / frames_needed) for i in range(frames_needed)]
                sampled_images = [images[i] for i in indices]
                print(f"Sampled {len(sampled_images)} frames from {len(images)} total frames")
            elif len(images) < frames_needed:
                # Need to interpolate/duplicate frames to reach target
                sampled_images = []
                for i in range(frames_needed):
                    source_index = int(i * len(images) / frames_needed)
                    sampled_images.append(images[min(source_index, len(images) - 1)])
                print(f"Interpolated to {len(sampled_images)} frames from {len(images)} source frames")
            else:
                sampled_images = images
                
            print(f"Saving {len(sampled_images)} frames to MP4 at 24fps (6 second duration)...")
            
            # Save as MP4 with ffmpeg backend at 24fps
            with imageio.get_writer(video_path, fps=fps, codec='libx264', quality=8) as writer:
                for img in sampled_images:
                    # Convert PIL image to numpy array
                    img_array = np.array(img.convert('RGB'))
                    writer.append_data(img_array)
            
            print(f"High-quality MP4 saved as: {video_path}")
            print(f"MP4 size: {os.path.getsize(video_path) / 1024:.1f} KB")
            print(f"Video duration: {len(sampled_images) / fps:.1f} seconds at {fps}fps")
            
            # Also save a preview GIF with fewer frames for quick viewing
            preview_gif_path = "theme_park_waits_swarm_preview.gif"
            preview_frames = images[::5]  # Every 5th frame
            print(f"\nCreating preview GIF with {len(preview_frames)} frames...")
            
            with imageio.get_writer(preview_gif_path, mode='I', duration=0.3, loop=0) as writer:
                for img in preview_frames:
                    img_array = np.array(img.convert('RGB'))
                    writer.append_data(img_array)
            
            print(f"Preview GIF saved as: {preview_gif_path}")
            print(f"Preview size: {os.path.getsize(preview_gif_path) / 1024:.1f} KB")
        else:
            print(f"ERROR: Only {len(images)} image(s) captured, cannot create video")
        
        shutil.rmtree(frames_dir)
    else:
        print("No frames captured!")


if __name__ == "__main__":
    main()