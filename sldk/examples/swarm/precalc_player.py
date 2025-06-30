#!/usr/bin/env python3
"""
Lightweight Pre-calculated Path Player for MatrixPortal

This player reads pre-calculated bird paths and renders them efficiently
on the MatrixPortal hardware without any complex calculations.
"""

import sys
import os
import json
import time
import gc

# CircuitPython detection and imports
CIRCUITPYTHON = hasattr(sys, 'implementation') and sys.implementation.name == 'circuitpython'

if CIRCUITPYTHON:
    import board
    import displayio
    from adafruit_matrixportal.matrix import Matrix
else:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'sldk', 'src'))
    from sldk.simulator.devices import MatrixPortalS3
    from sldk.simulator.displayio import Bitmap, Palette, TileGrid, Group
    displayio = type('', (), {'Bitmap': Bitmap, 'Palette': Palette, 'TileGrid': TileGrid, 'Group': Group})()


def hsv_to_rgb888(h, s, v):
    """Convert HSV to RGB888 format for displayio compatibility."""
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
        
    # Convert to 24-bit RGB
    return (int((r + m) * 255) << 16) | (int((g + m) * 255) << 8) | int((b + m) * 255)


class PathPlayer:
    """Plays back pre-calculated paths efficiently."""
    
    def __init__(self):
        self.setup_display()
        self.load_paths()
        self.frame_index = 0
        self.bird_positions = {}  # Current positions
        self.captured_pixels = set()
        self.running = True
        self.animation_complete = False
        self.birds_leaving = False
        self.completion_time = None
        self.reset_after_seconds = 20  # Show complete text for 20 seconds
        
    def setup_display(self):
        """Initialize display hardware."""
        if CIRCUITPYTHON:
            self.matrix = Matrix(width=64, height=32, bit_depth=6)
            self.display = self.matrix.display
        else:
            self.device = MatrixPortalS3()
            self.device.initialize()
            self.display = self.device.display
            
        # Create display groups
        self.main_group = displayio.Group()
        
        # Set root group properly
        if CIRCUITPYTHON:
            self.display.root_group = self.main_group
        else:
            self.device.show(self.main_group)
            # Force initial refresh to ensure display is set up (like working animation)
            self.device.refresh()
        
        # Background
        self.bg_bitmap = displayio.Bitmap(64, 32, 1)
        bg_palette = displayio.Palette(1)
        bg_palette[0] = 0x000000
        self.main_group.append(displayio.TileGrid(self.bg_bitmap, pixel_shader=bg_palette))
        
        # Text layer with expanded palette to utilize 6-bit color depth
        PALETTE_SIZE = 64  # Take advantage of 6-bit color depth (64 colors)
        self.text_bitmap = displayio.Bitmap(64, 32, PALETTE_SIZE)
        self.rainbow_palette = displayio.Palette(PALETTE_SIZE)
        self.rainbow_palette[0] = 0x000000  # Black
        
        # Generate smooth 64-color rainbow utilizing full 6-bit color depth
        # This creates much smoother color transitions than 16-color version
        for i in range(1, PALETTE_SIZE):
            hue = (i - 1) / (PALETTE_SIZE - 1)
            # Use full saturation and brightness for rich colors
            saturation = 1.0
            brightness = 1.0
            self.rainbow_palette[i] = hsv_to_rgb888(hue, saturation, brightness)
            
        print(f"Generated {PALETTE_SIZE-1} rainbow colors utilizing 6-bit color depth")
        
        self.text_grid = displayio.TileGrid(self.text_bitmap, pixel_shader=self.rainbow_palette)
        self.main_group.append(self.text_grid)
        
        # Animation timing for palette effects
        self.animation_time = 0.0
        
        # Bird layer - using sprites like the working animation
        if CIRCUITPYTHON:
            self.bird_group = displayio.Group(max_size=200)
        else:
            self.bird_group = displayio.Group()
        self.main_group.append(self.bird_group)
        
        # Create bird sprites with shared palette (MEMORY EFFICIENT!)
        self.bird_sprites = []
        
        # Shared bird palette (only 2 colors, saves memory!)
        self.bird_palette = displayio.Palette(2)
        self.bird_palette[0] = 0x000000  # Transparent
        self.bird_palette[1] = 0xFFFFFF  # White (will be updated dynamically)
        
        # Bird shape (cross pattern for visibility)
        bird_shape = displayio.Bitmap(3, 3, 2)
        bird_shape[1, 0] = 1  # Top
        bird_shape[0, 1] = 1  # Left
        bird_shape[1, 1] = 1  # Center
        bird_shape[2, 1] = 1  # Right
        bird_shape[1, 2] = 1  # Bottom
        
        # Create sprites using shared palette
        for i in range(200):  # Max birds
            sprite = displayio.TileGrid(
                bird_shape,
                pixel_shader=self.bird_palette,  # SHARED PALETTE!
                x=-10,  # Off screen initially
                y=-10
            )
            self.bird_sprites.append(sprite)
            self.bird_group.append(sprite)
        
    def make_birds_fly_away(self):
        """Make all visible birds fly off screen."""
        import random
        
        # Move all visible birds toward screen edges
        for sprite in self.bird_sprites:
            if sprite.x > -10:  # Bird is visible
                # Determine nearest edge and move toward it
                center_x, center_y = 32, 16
                
                # Distance to each edge
                left_dist = sprite.x
                right_dist = 64 - sprite.x
                top_dist = sprite.y
                bottom_dist = 32 - sprite.y
                
                # Find closest edge
                min_dist = min(left_dist, right_dist, top_dist, bottom_dist)
                
                # Move toward that edge
                if min_dist == left_dist:
                    sprite.x -= 2  # Move left
                elif min_dist == right_dist:
                    sprite.x += 2  # Move right
                elif min_dist == top_dist:
                    sprite.y -= 2  # Move up
                else:
                    sprite.y += 2  # Move down
                
                # Hide bird if it's off screen
                if sprite.x < -5 or sprite.x > 70 or sprite.y < -5 or sprite.y > 37:
                    sprite.x = -10
                    sprite.y = -10
    
    def update_color_animation(self):
        """Update rainbow color animation for text and birds."""
        # Update animation timing
        self.animation_time += 0.033  # ~30 FPS timing
        
        # Update text colors with smooth wave effect using 64 colors
        PALETTE_SIZE = 64
        for px, py in self.captured_pixels:
            if 0 <= px < 64 and 0 <= py < 32:
                # Create smooth animated wave effect with 64 color gradations
                wave_offset = int((px + py) / 2 + self.animation_time * 8) % (PALETTE_SIZE - 1)
                color_index = 1 + wave_offset
                self.text_bitmap[px, py] = color_index
        
        # Update bird color animation 
        if int(self.animation_time * 30) % 10 == 0:  # Update every 10 frames
            # Cycle through rainbow colors for birds
            color_offset = int(self.animation_time * 2) % 16
            hue = color_offset / 15.0
            self.bird_palette[1] = hsv_to_rgb888(hue, 1.0, 1.0)
        
        # Force display refresh for color changes
        if not CIRCUITPYTHON and self.device and self.device.display:
            self.device.display.refresh()
        
    def load_paths(self):
        """Load pre-calculated paths from file."""
        try:
            with open('precalc_paths.json', 'r') as f:
                data = json.loads(f.read())
            self.metadata = data['metadata']
            self.frames = data['frames']
            print(f"Loaded {len(self.frames)} frames")
        except Exception as e:
            print(f"Error loading paths: {e}")
            self.frames = []
            
    def play_frame(self):
        """Render the current frame."""
        import time
        current_time = time.monotonic() if CIRCUITPYTHON else time.time()
        
        # Check if animation should reset
        if self.completion_time and current_time - self.completion_time >= self.reset_after_seconds:
            print(f"\nResetting animation after {self.reset_after_seconds} seconds...")
            self.frame_index = 0
            self.bird_positions.clear()
            self.captured_pixels.clear()
            self.animation_complete = False
            self.birds_leaving = False
            self.completion_time = None
            self.animation_time = 0.0  # Reset animation timing too
            # Clear text bitmap for fresh start
            for y in range(32):
                for x in range(64):
                    self.text_bitmap[x, y] = 0
            # Hide all bird sprites
            for sprite in self.bird_sprites:
                sprite.x = -10
                sprite.y = -10
            return
        
        if self.frame_index >= len(self.frames):
            if not self.animation_complete:
                print(f"\nText complete! Birds flying away...")
                self.animation_complete = True
                self.birds_leaving = True
            
            # If birds are leaving, make them fly away
            if self.birds_leaving:
                self.make_birds_fly_away()
                # Check if all birds have left
                active_birds = sum(1 for sprite in self.bird_sprites if sprite.x > -10)
                if active_birds == 0 and self.completion_time is None:
                    self.completion_time = current_time
                    print(f"All birds have left! Text will reset in {self.reset_after_seconds} seconds.")
            
            # CONTINUE color animation even when birds are gone!
            self.update_color_animation()
            return
            
        frame = self.frames[self.frame_index]
        
        # Hide all bird sprites first
        for sprite in self.bird_sprites:
            sprite.x = -10
            sprite.y = -10
        
        # Update bird positions
        for bird_data in frame['b']:
            bird_id = bird_data[0]
            
            if len(bird_data) == 4 and bird_data[3] == 1:  # New bird
                self.bird_positions[bird_id] = {'x': bird_data[1], 'y': bird_data[2]}
            elif len(bird_data) == 4 and bird_data[3] == -1:  # Remove bird
                if bird_id in self.bird_positions:
                    del self.bird_positions[bird_id]
            else:  # Delta update
                if bird_id in self.bird_positions:
                    self.bird_positions[bird_id]['x'] += bird_data[1]
                    self.bird_positions[bird_id]['y'] += bird_data[2]
        
        # Position bird sprites
        for bird_id, pos in self.bird_positions.items():
            if bird_id < len(self.bird_sprites):  # Ensure sprite exists
                x = pos['x'] // 4  # Convert from sub-pixel
                y = pos['y'] // 4
                if 0 <= x < 64 and 0 <= y < 32:
                    sprite = self.bird_sprites[bird_id]
                    sprite.x = x - 1  # Center the 3x3 sprite
                    sprite.y = y - 1
        
        # Update captured pixels
        for px, py in frame['p']:
            self.captured_pixels.add((px, py))
            
        self.frame_index += 1
        
        # Update color animation (text wave effects and bird colors)
        self.update_color_animation()
        
        # Periodic status update
        if self.frame_index % 30 == 0:
            print(f"Frame {self.frame_index}: {len(self.bird_positions)} birds, {len(self.captured_pixels)} pixels captured")
            
        # Debug text rendering
        if frame['p'] and self.frame_index < 50:  # First 50 frames
            print(f"Frame {self.frame_index}: Adding {len(frame['p'])} new pixels: {frame['p'][:3]}...")
        
        # Refresh display
        if CIRCUITPYTHON:
            self.display.refresh()
        else:
            # In SLDK simulator, we still need to refresh the display content
            # The device.run() only handles the window update
            if self.device and self.device.display:
                self.device.display.refresh()
            
    def run(self):
        """Main playback loop."""
        print("Starting playback...")
        
        if CIRCUITPYTHON:
            # CircuitPython - run directly
            last_frame_time = time.monotonic()
            frame_duration = 1.0 / 30  # 30 FPS
            
            while self.running:
                current_time = time.monotonic()
                
                if current_time - last_frame_time >= frame_duration:
                    self.play_frame()
                    last_frame_time = current_time
                    
                    # Periodic GC on CircuitPython
                    if self.frame_index % 100 == 0:
                        gc.collect()
        else:
            # SLDK simulator - use device.run() to create window
            def update_callback():
                """Called each frame by the display manager."""
                self.play_frame()
                
            # Run the device with our update callback
            self.device.run(update_callback, title="SLDK Simulator - MatrixPortal S3")


if __name__ == "__main__":
    try:
        player = PathPlayer()
        print(f"Starting playback of {len(player.frames)} frames...")
        player.run()
    except KeyboardInterrupt:
        print("\nPlayback stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
