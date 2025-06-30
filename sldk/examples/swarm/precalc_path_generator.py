#!/usr/bin/env python3
"""
Path Pre-calculation Generator for MatrixPortal Hardware

This tool runs the egg drop swarm animation on a fast machine and records
all bird positions and states for each frame. The output is optimized for
playback on the slow MatrixPortal hardware.

Features:
- Records bird positions, visibility states, and pixel captures
- Compresses data using delta encoding and bit packing
- Outputs JSON format for easy loading
- Includes metadata for animation parameters
"""

import sys
import os
import json
import time
import struct
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'sldk', 'src'))

# Import the animation we want to pre-calculate
from theme_park_waits_swarm_egg_drop import EggDropSwarmAnimation, MATRIX_WIDTH, MATRIX_HEIGHT, MAX_BIRDS

class PathRecorder:
    """Records bird paths and pixel captures during animation."""
    
    def __init__(self):
        self.frames = []
        self.pixel_captures = []
        self.metadata = {
            'matrix_width': MATRIX_WIDTH,
            'matrix_height': MATRIX_HEIGHT,
            'max_birds': MAX_BIRDS,
            'fps': 30,
            'total_frames': 0,
            'animation_duration': 0,
            'format_version': '1.0'
        }
        
    def start_recording(self):
        """Initialize recording."""
        self.frames = []
        self.pixel_captures = []
        self.start_time = time.time()
        
    def record_frame(self, animation, frame_num):
        """Record current state of all birds and captured pixels."""
        frame_data = {
            'frame': frame_num,
            'birds': [],
            'new_pixels': []
        }
        
        # Record active birds
        for bird in animation.birds:
            if bird.active:
                # Pack position data efficiently
                # Store as integers (0-255 range) to save space
                x_int = max(0, min(255, int(bird.x * 4)))  # Sub-pixel precision
                y_int = max(0, min(255, int(bird.y * 4)))
                
                bird_data = {
                    'id': bird.sprite_index,
                    'x': x_int,
                    'y': y_int
                }
                frame_data['birds'].append(bird_data)
        
        # Record newly captured pixels this frame
        if hasattr(animation, '_last_captured_count'):
            new_count = len(animation.captured_pixels)
            if new_count > animation._last_captured_count:
                # Find new pixels
                for px, py in animation.captured_pixels:
                    if (px, py) not in animation._last_captured_set:
                        frame_data['new_pixels'].append([px, py])
                animation._last_captured_set = animation.captured_pixels.copy()
        else:
            animation._last_captured_count = 0
            animation._last_captured_set = set()
        
        animation._last_captured_count = len(animation.captured_pixels)
        
        self.frames.append(frame_data)
        
    def finish_recording(self, total_pixels):
        """Finalize recording and calculate metadata."""
        self.metadata['total_frames'] = len(self.frames)
        self.metadata['animation_duration'] = time.time() - self.start_time
        self.metadata['total_pixels'] = total_pixels
        
    def compress_data(self):
        """Compress the recorded data using delta encoding."""
        compressed_frames = []
        last_birds = {}
        
        for frame in self.frames:
            compressed_frame = {
                'f': frame['frame'],  # Short key names
                'b': [],  # birds
                'p': frame['new_pixels']  # pixels
            }
            
            # Delta encode bird positions
            for bird in frame['birds']:
                bird_id = bird['id']
                
                if bird_id in last_birds:
                    # Delta from last position
                    dx = bird['x'] - last_birds[bird_id]['x']
                    dy = bird['y'] - last_birds[bird_id]['y']
                    
                    # Only store if bird moved
                    if dx != 0 or dy != 0:
                        compressed_frame['b'].append([bird_id, dx, dy])
                else:
                    # New bird, store absolute position
                    compressed_frame['b'].append([bird_id, bird['x'], bird['y'], 1])  # 1 = new
                
                last_birds[bird_id] = bird
            
            # Remove birds that are no longer active
            active_ids = {b['id'] for b in frame['birds']}
            for bid in list(last_birds.keys()):
                if bid not in active_ids:
                    compressed_frame['b'].append([bid, 0, 0, -1])  # -1 = remove
                    del last_birds[bid]
            
            compressed_frames.append(compressed_frame)
            
        return compressed_frames
    
    def save(self, filename):
        """Save recorded paths to file."""
        data = {
            'metadata': self.metadata,
            'frames': self.compress_data()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, separators=(',', ':'))  # Compact JSON
        
        # Report compression stats
        original_size = len(json.dumps(self.frames))
        compressed_size = len(json.dumps(data))
        print(f"\nCompression ratio: {compressed_size/original_size:.2%}")
        print(f"File size: {compressed_size:,} bytes")


class PreCalcAnimation(EggDropSwarmAnimation):
    """Modified animation that records paths during execution."""
    
    def __init__(self, recorder):
        super().__init__()
        self.recorder = recorder
        self.frame_counter = 0
        self.recording_complete = False
        
    def update(self):
        """Override update to record frames."""
        # Call parent update
        super().update()
        
        # Record this frame
        if not self.recording_complete:
            self.recorder.record_frame(self, self.frame_counter)
            self.frame_counter += 1
            
            # Check if animation is complete
            if len(self.captured_pixels) >= len(self.target_pixels) and self.birds_leaving:
                # Wait for all birds to leave
                active_birds = sum(1 for b in self.birds if b.active)
                if active_birds == 0 and not self.recording_complete:
                    self.recording_complete = True
                    self.recorder.finish_recording(len(self.target_pixels))
                    print(f"\nRecording complete! {self.frame_counter} frames captured.")
                    
                    # Stop the animation
                    if hasattr(self, 'running'):
                        self.running = False


def generate_precalc_paths():
    """Generate pre-calculated paths for the egg drop animation."""
    print("=== PATH PRE-CALCULATION GENERATOR ===")
    print("Generating optimized paths for MatrixPortal hardware...")
    print()
    
    # Create recorder
    recorder = PathRecorder()
    recorder.start_recording()
    
    # Create and run animation
    animation = PreCalcAnimation(recorder)
    
    # Override the run method to stop when recording is complete
    original_run = animation.run
    
    def custom_run():
        animation.running = True
        start_time = time.time()
        max_duration = 30  # Maximum 30 seconds recording
        
        while animation.running and not animation.recording_complete:
            animation.update()
            time.sleep(1.0 / 30)  # 30 FPS recording
            
            # Timeout check
            if time.time() - start_time > max_duration:
                print(f"\nReached maximum recording duration ({max_duration}s)")
                animation.recording_complete = True
                animation.recorder.finish_recording(len(animation.target_pixels))
                break
    
    animation.run = custom_run
    
    # Run the animation
    print("Running animation and recording paths...")
    animation.run()
    
    # Save the recorded data
    output_file = "precalc_paths.json"
    print(f"\nSaving to {output_file}...")
    recorder.save(output_file)
    
    print(f"\nGeneration complete!")
    print(f"Total frames: {recorder.metadata['total_frames']}")
    print(f"Duration: {recorder.metadata['animation_duration']:.1f} seconds")
    print(f"Average FPS: {recorder.metadata['total_frames']/recorder.metadata['animation_duration']:.1f}")
    
    # Generate lightweight player code
    generate_player_code()


def generate_player_code():
    """Generate the lightweight player for CircuitPython."""
    player_code = '''#!/usr/bin/env python3
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


class PathPlayer:
    """Plays back pre-calculated paths efficiently."""
    
    def __init__(self):
        self.setup_display()
        self.load_paths()
        self.frame_index = 0
        self.bird_positions = {}  # Current positions
        self.captured_pixels = set()
        
    def setup_display(self):
        """Initialize display hardware."""
        if CIRCUITPYTHON:
            self.matrix = Matrix(width=64, height=32, bit_depth=6)
            self.display = self.matrix.display
        else:
            self.device = MatrixPortalS3()
            self.display = self.device.display
            
        # Create display groups
        self.main_group = displayio.Group()
        self.display.root_group = self.main_group
        
        # Background
        self.bg_bitmap = displayio.Bitmap(64, 32, 1)
        bg_palette = displayio.Palette(1)
        bg_palette[0] = 0x000000
        self.main_group.append(displayio.TileGrid(self.bg_bitmap, pixel_shader=bg_palette))
        
        # Text layer
        self.text_bitmap = displayio.Bitmap(64, 32, 8)
        self.text_palette = displayio.Palette(8)
        self.text_palette[0] = 0x000000  # Black
        for i in range(1, 8):
            # Simple rainbow colors
            self.text_palette[i] = (0xFF0000, 0xFFFF00, 0x00FF00, 0x00FFFF, 
                                   0x0000FF, 0xFF00FF, 0xFFFFFF)[i-1]
        self.text_grid = displayio.TileGrid(self.text_bitmap, pixel_shader=self.text_palette)
        self.main_group.append(self.text_grid)
        
        # Bird layer - simple pixels
        self.bird_bitmap = displayio.Bitmap(64, 32, 2)
        bird_palette = displayio.Palette(2)
        bird_palette[0] = 0x000000  # Transparent
        bird_palette[1] = 0xFFFFFF  # White birds
        self.bird_grid = displayio.TileGrid(self.bird_bitmap, pixel_shader=bird_palette)
        self.main_group.append(self.bird_grid)
        
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
        if self.frame_index >= len(self.frames):
            self.frame_index = 0  # Loop
            self.bird_positions.clear()
            self.captured_pixels.clear()
            # Clear bitmaps
            for y in range(32):
                for x in range(64):
                    self.text_bitmap[x, y] = 0
                    self.bird_bitmap[x, y] = 0
            
        frame = self.frames[self.frame_index]
        
        # Clear bird bitmap
        for y in range(32):
            for x in range(64):
                self.bird_bitmap[x, y] = 0
        
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
        
        # Draw birds
        for bird_id, pos in self.bird_positions.items():
            x = pos['x'] // 4  # Convert from sub-pixel
            y = pos['y'] // 4
            if 0 <= x < 64 and 0 <= y < 32:
                self.bird_bitmap[x, y] = 1
        
        # Update captured pixels
        for px, py in frame['p']:
            self.captured_pixels.add((px, py))
            if 0 <= px < 64 and 0 <= py < 32:
                color_index = 1 + ((px + py) % 7)
                self.text_bitmap[px, py] = color_index
        
        self.frame_index += 1
        
        # Force refresh on hardware
        if CIRCUITPYTHON:
            self.display.refresh()
            
    def run(self):
        """Main playback loop."""
        print("Starting playback...")
        last_frame_time = time.monotonic() if CIRCUITPYTHON else time.time()
        frame_duration = 1.0 / 30  # 30 FPS
        
        while True:
            current_time = time.monotonic() if CIRCUITPYTHON else time.time()
            
            if current_time - last_frame_time >= frame_duration:
                self.play_frame()
                last_frame_time = current_time
                
                # Periodic GC on CircuitPython
                if CIRCUITPYTHON and self.frame_index % 100 == 0:
                    gc.collect()


if __name__ == "__main__":
    player = PathPlayer()
    player.run()
'''
    
    with open('precalc_player.py', 'w') as f:
        f.write(player_code)
    
    print("\nGenerated precalc_player.py for MatrixPortal playback")


if __name__ == "__main__":
    generate_precalc_paths()