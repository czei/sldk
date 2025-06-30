#!/usr/bin/env python3
"""Play pre-calculated swarm animation frames on CircuitPython.

This script reads compressed frame data and displays it on the LED matrix.
Designed to work within CircuitPython's memory constraints.
"""

import time
import gc
import json

# CircuitPython imports
try:
    import board
    import displayio
    from adafruit_matrixportal.matrix import Matrix
    CIRCUITPYTHON = True
except (ImportError, NotImplementedError):
    # For testing in simulator
    CIRCUITPYTHON = False
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..' if 'PyLEDSimulator' in __file__ else '.', 'sldk', 'src'))

from sldk.simulator.devices import MatrixPortalS3


class FramePlayer:
    """Play pre-calculated animation frames with minimal memory usage."""
    
    def __init__(self, width=64, height=32):
        self.width = width
        self.height = height
        self.frame_index = 0
        self.fps = 20
        self.frame_time = 1.0 / self.fps
        self.last_frame_time = 0
        
        # For CircuitPython
        self.bitmap = None
        self.palette = None
        self.tile_grid = None
        
        # Frame data (loaded in chunks)
        self.frames = None
        self.frame_count = 0
        self.current_chunk_start = 0
        self.chunk_size = 100  # Load 100 frames at a time
        
    def load_animation_file(self, filename):
        """Load animation data from JSON file."""
        print(f"Loading animation from {filename}...")
        
        with open(filename, 'r') as f:
            data = json.load(f)
        
        self.fps = data.get('fps', 20)
        self.frame_time = 1.0 / self.fps
        self.frame_count = data['frame_count']
        
        # Create palette
        if CIRCUITPYTHON:
            self.palette = displayio.Palette(len(data['palette']))
            for i, color in enumerate(data['palette']):
                self.palette[i] = (color[0] << 16) | (color[1] << 8) | color[2]
        else:
            self.palette = data['palette']
        
        # Store frames reference
        self.all_frames = data['frames']
        
        # Load first chunk
        self.load_frame_chunk(0)
        
        print(f"Loaded {self.frame_count} frames at {self.fps} fps")
        gc.collect()
        
    def load_frame_chunk(self, start_index):
        """Load a chunk of frames into memory."""
        end_index = min(start_index + self.chunk_size, self.frame_count)
        self.frames = self.all_frames[start_index:end_index]
        self.current_chunk_start = start_index
        gc.collect()
        
    def get_frame(self, index):
        """Get a specific frame, loading new chunk if needed."""
        if index >= self.frame_count:
            return None
            
        # Check if we need to load a new chunk
        chunk_index = index - self.current_chunk_start
        if chunk_index < 0 or chunk_index >= len(self.frames):
            # Load the chunk containing this frame
            new_chunk_start = (index // self.chunk_size) * self.chunk_size
            self.load_frame_chunk(new_chunk_start)
            chunk_index = index - self.current_chunk_start
            
        return self.frames[chunk_index]
        
    def draw_frame(self, frame_data):
        """Draw a single frame from RLE data."""
        if CIRCUITPYTHON:
            # Clear bitmap
            self.bitmap.fill(0)
            
            # Draw pixels from RLE data
            for run in frame_data:
                x, y, color, count = run
                for i in range(count):
                    px = x + i
                    py = y
                    
                    # Handle wrapping to next line
                    while px >= self.width:
                        px -= self.width
                        py += 1
                    
                    if 0 <= px < self.width and 0 <= py < self.height:
                        self.bitmap[px, py] = color
        else:
            # Simulator version
            self.device.matrix.clear()
            
            # Draw pixels from RLE data
            for run in frame_data:
                x, y, color_idx, count = run
                color = self.palette[color_idx]
                rgb = (color[0], color[1], color[2])
                
                for i in range(count):
                    px = x + i
                    py = y
                    
                    # Handle wrapping to next line
                    while px >= self.width:
                        px -= self.width
                        py += 1
                    
                    if 0 <= px < self.width and 0 <= py < self.height:
                        self.device.matrix.set_pixel(px, py, rgb)
    
    def play_circuitpython(self):
        """Play animation on CircuitPython hardware."""
        # Initialize matrix
        matrix = Matrix(width=self.width, height=self.height, bit_depth=4)
        display = matrix.display
        
        # Create display objects
        main_group = displayio.Group()
        self.bitmap = displayio.Bitmap(self.width, self.height, len(self.palette))
        self.tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.palette)
        main_group.append(self.tile_grid)
        display.root_group = main_group
        
        # Play animation loop
        print("Playing animation... Press Ctrl+C to stop")
        self.frame_index = 0
        self.last_frame_time = time.monotonic()
        
        while True:
            current_time = time.monotonic()
            
            # Check if it's time for next frame
            if current_time - self.last_frame_time >= self.frame_time:
                # Get and draw frame
                frame_data = self.get_frame(self.frame_index)
                if frame_data is not None:
                    self.draw_frame(frame_data)
                    
                    # Update frame index
                    self.frame_index += 1
                    if self.frame_index >= self.frame_count:
                        # Loop animation
                        self.frame_index = 0
                        print("Looping animation...")
                        gc.collect()
                    
                    self.last_frame_time = current_time
                    
                    # Progress indicator every second
                    if self.frame_index % self.fps == 0:
                        print(f"Frame {self.frame_index}/{self.frame_count}")
            
            # Small delay to prevent busy waiting
            time.sleep(0.001)
    
    def play_simulator(self):
        """Play animation in simulator."""
        self.device = MatrixPortalS3()
        self.device.initialize()
        
        print("Playing animation in simulator...")
        self.frame_index = 0
        
        def update_animation():
            current_time = time.time()
            
            # Initialize last frame time on first call
            if not hasattr(self, '_sim_last_frame'):
                self._sim_last_frame = current_time
            
            # Check if it's time for next frame
            if current_time - self._sim_last_frame >= self.frame_time:
                # Get and draw frame
                frame_data = self.get_frame(self.frame_index)
                if frame_data is not None:
                    self.draw_frame(frame_data)
                    
                    # Update frame index
                    self.frame_index += 1
                    if self.frame_index >= self.frame_count:
                        # Loop animation
                        self.frame_index = 0
                        print("Looping animation...")
                    
                    self._sim_last_frame = current_time
                    
                    # Progress indicator
                    if self.frame_index % (self.fps * 5) == 0:  # Every 5 seconds
                        print(f"Frame {self.frame_index}/{self.frame_count}")
        
        # Run with animation callback
        self.device.run(title="Swarm Animation Player", update_callback=update_animation)
    
    def play(self):
        """Play the animation."""
        if CIRCUITPYTHON:
            self.play_circuitpython()
        else:
            self.play_simulator()


def main():
    """Main entry point."""
    player = FramePlayer()
    
    # Load animation file
    animation_file = "swarm_animation_frames.json"
    
    try:
        player.load_animation_file(animation_file)
    except Exception as e:
        print(f"Error loading animation: {e}")
        print("Make sure to run generate_swarm_frames.py first!")
        return
    
    # Play animation
    try:
        player.play()
    except KeyboardInterrupt:
        print("\nAnimation stopped by user")


if __name__ == "__main__":
    main()