#!/usr/bin/env python3
"""Generate pre-calculated animation frames from the swarm animation.

This script runs the swarm animation and saves each frame as compressed data
that can be replayed on CircuitPython hardware with limited memory.
"""

import sys
import os
import json
import time
import math
import random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..' if 'PyLEDSimulator' in __file__ else '.', 'sldk', 'src'))

from sldk.simulator.devices import MatrixPortalS3
from theme_park_waits_swarm import (
    get_theme_park_waits_pixels, 
    FlockBird,
    create_flock_from_direction,
    find_largest_missing_clump,
    hsv_to_rgb
)


class FrameCapture:
    """Capture animation frames for later playback."""
    
    def __init__(self, width=64, height=32):
        self.width = width
        self.height = height
        self.frames = []
        self.frame_count = 0
        self.max_frames = 1200  # ~60 seconds at 20fps
        
    def add_frame(self, pixels_data):
        """Add a frame with run-length encoding for compression.
        
        pixels_data: list of (x, y, color_index) tuples
        """
        if self.frame_count >= self.max_frames:
            return False
            
        # Convert to run-length encoded format
        # Sort by position for better compression
        sorted_pixels = sorted(pixels_data, key=lambda p: p[1] * 64 + p[0])
        
        # Simple RLE: count consecutive pixels of same color
        if not sorted_pixels:
            self.frames.append([])
            self.frame_count += 1
            return True
            
        rle_data = []
        current_run = [sorted_pixels[0][0], sorted_pixels[0][1], sorted_pixels[0][2], 1]
        
        for i in range(1, len(sorted_pixels)):
            x, y, color = sorted_pixels[i]
            prev_x, prev_y = sorted_pixels[i-1][0], sorted_pixels[i-1][1]
            
            # Check if this pixel continues the run
            if (color == current_run[2] and 
                ((y == prev_y and x == prev_x + 1) or 
                 (y == prev_y + 1 and x == 0 and prev_x == 63))):
                current_run[3] += 1
            else:
                # End current run, start new one
                rle_data.append(current_run)
                current_run = [x, y, color, 1]
        
        # Don't forget the last run
        rle_data.append(current_run)
        
        self.frames.append(rle_data)
        self.frame_count += 1
        return True
        
    def save_frames(self, filename):
        """Save frames to a JSON file."""
        # Create color palette
        palette = [
            [0, 0, 0],      # 0: Black (background)
            [255, 255, 0],  # 1: Yellow (text base)
        ]
        
        # Add rainbow colors for dynamic effects
        for i in range(20):  # 20 rainbow colors
            hue = i / 20.0
            r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
            palette.append([r, g, b])
        
        data = {
            'width': self.width,
            'height': self.height,
            'fps': 20,
            'frame_count': self.frame_count,
            'palette': palette,
            'frames': self.frames
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, separators=(',', ':'))
        
        print(f"Saved {self.frame_count} frames to {filename}")
        
        # Calculate file size
        file_size = os.path.getsize(filename)
        print(f"File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")


def get_color_index(color, time_elapsed, is_text=False, pixel_pos=None):
    """Map RGB color to palette index."""
    if color == (0, 0, 0):
        return 0  # Black
    
    if is_text and pixel_pos:
        # Dynamic text color based on position and time
        x, y = pixel_pos
        position_offset = (x / 64.0 + y / 32.0) * 0.3
        hue = (time_elapsed * 0.2 + position_offset) % 1.0
        # Map to rainbow palette indices (2-21)
        return 2 + int(hue * 19)
    else:
        # Bird colors - use time-based rainbow
        # Birds get dynamic colors that cycle through rainbow
        hue = (time_elapsed * 0.5) % 1.0
        return 2 + int(hue * 19)


def generate_frames():
    """Generate animation frames."""
    print("Generating swarm animation frames...")
    
    # Initialize capture
    capture = FrameCapture()
    
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
    
    # Animation timing
    start_time = 0
    time_step = 0.05  # 50ms per frame (20 fps)
    current_time = 0
    
    print(f"Need to capture {num_needed} pixels")
    
    # Run animation loop
    while current_time < 60.0:  # Max 60 seconds
        time_elapsed = current_time
        
        # Check if all text is complete
        text_complete = len(captured_pixels) >= len(target_pixels)
        
        if text_complete:
            print(f"Animation completed at {current_time:.1f} seconds")
            # Add a few more frames of the complete text
            for _ in range(20):
                pixels_data = []
                
                # All text pixels with dynamic colors
                for pixel in captured_pixels:
                    color_idx = get_color_index(None, time_elapsed, True, pixel)
                    pixels_data.append((pixel[0], pixel[1], color_idx))
                
                if not capture.add_frame(pixels_data):
                    break
                    
                current_time += time_step
                time_elapsed = current_time
            break
        
        # Normal animation logic
        remaining_leds = len(target_pixels) - len(captured_pixels)
        
        # Adjust spawn behavior for final LEDs
        if remaining_leds <= 15:
            spawn_interval_adjusted = 0.5
            max_flock_size = 500
        else:
            spawn_interval_adjusted = spawn_interval
            max_flock_size = 200
        
        # Spawn new flock if needed
        if (remaining_leds > 0 and 
            time_elapsed - last_spawn_time > spawn_interval_adjusted and
            len(flock) < max_flock_size):
            
            birds_to_spawn = min(100 if remaining_leds > 15 else remaining_leds * 30, remaining_leds)
            direction = directions[current_direction_idx]
            
            new_flock = create_flock_from_direction(birds_to_spawn, direction, target_pixels, captured_pixels)
            flock.extend(new_flock)
            
            print(f"[{current_time:.1f}s] Spawned {birds_to_spawn} birds from {direction} ({remaining_leds} pixels left)")
            
            current_direction_idx = (current_direction_idx + 1) % len(directions)
            last_spawn_time = time_elapsed
        
        # Find attraction center
        attraction_center = find_largest_missing_clump(target_pixels, captured_pixels)
        
        # Update bird positions
        missing_pixels = target_pixels - captured_pixels
        few_remaining = len(missing_pixels) <= 15
        
        for bird in flock:
            if few_remaining and missing_pixels:
                # Direct targeting for final pixels
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
                # Normal flocking
                bird.update_flocking(flock, target_pixels, captured_pixels, attraction_center)
        
        # Check for LED captures
        for bird in flock:
            if bird.is_on_screen():
                pixel_pos = bird.get_pixel_pos()
                if pixel_pos in target_pixels and pixel_pos not in captured_pixels:
                    captured_pixels.add(pixel_pos)
                    print(f"[{current_time:.1f}s] Captured pixel at {pixel_pos} ({len(captured_pixels)}/{len(target_pixels)})")
        
        # Remove off-screen birds
        flock = [bird for bird in flock if not (
            bird.x < -25 or bird.x > 89 or bird.y < -25 or bird.y > 57)]
        
        # Create frame data
        pixels_data = []
        
        # Add captured text pixels
        for pixel in captured_pixels:
            color_idx = get_color_index(None, time_elapsed, True, pixel)
            pixels_data.append((pixel[0], pixel[1], color_idx))
        
        # Add birds
        for i, bird in enumerate(flock):
            if bird.is_on_screen():
                bird_x, bird_y = bird.get_pixel_pos()
                # Bird colors cycle through rainbow
                color_idx = get_color_index(None, time_elapsed + i * 0.1, False)
                pixels_data.append((bird_x, bird_y, color_idx))
        
        # Add frame
        if not capture.add_frame(pixels_data):
            print("Reached maximum frame count")
            break
        
        # Update time
        current_time += time_step
        
        # Progress update
        if int(current_time * 10) % 10 == 0:  # Every second
            print(f"Progress: {current_time:.0f}s, {capture.frame_count} frames")
    
    # Save frames
    output_file = "swarm_animation_frames.json"
    capture.save_frames(output_file)
    
    return output_file


if __name__ == "__main__":
    generate_frames()