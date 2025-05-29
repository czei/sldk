"""CircuitPython code to play pre-generated swarm animation frames.

Copy this file to your CircuitPython device as code.py along with:
- swarm_animation_frames.json

This plays the pre-calculated animation on actual MatrixPortal S3 hardware.
"""

import time
import gc
import json
import board
import displayio
from adafruit_matrixportal.matrix import Matrix


class FramePlayer:
    """Lightweight frame player for CircuitPython."""
    
    def __init__(self, width=64, height=32):
        self.width = width
        self.height = height
        self.frame_index = 0
        self.fps = 20
        self.frame_time = 1.0 / self.fps
        self.last_frame_time = 0
        
        # Display objects
        self.matrix = None
        self.bitmap = None
        self.palette = None
        self.tile_grid = None
        
        # Frame data
        self.frames = None
        self.frame_count = 0
        self.current_chunk_start = 0
        self.chunk_size = 50  # Smaller chunks for limited memory
        
    def load_animation(self, filename="swarm_animation_frames.json"):
        """Load animation data."""
        print(f"Loading {filename}...")
        
        with open(filename, 'r') as f:
            data = json.load(f)
        
        self.fps = data.get('fps', 20)
        self.frame_time = 1.0 / self.fps
        self.frame_count = data['frame_count']
        
        # Create palette
        self.palette = displayio.Palette(len(data['palette']))
        for i, color in enumerate(data['palette']):
            self.palette[i] = (color[0] << 16) | (color[1] << 8) | color[2]
        
        # Store frames reference
        self.all_frames = data['frames']
        
        # Load first chunk
        self.load_chunk(0)
        
        print(f"Loaded {self.frame_count} frames")
        gc.collect()
        
    def load_chunk(self, start_index):
        """Load a chunk of frames."""
        end_index = min(start_index + self.chunk_size, self.frame_count)
        self.frames = self.all_frames[start_index:end_index]
        self.current_chunk_start = start_index
        gc.collect()
        
    def get_frame(self, index):
        """Get frame data, loading new chunk if needed."""
        if index >= self.frame_count:
            return None
            
        chunk_index = index - self.current_chunk_start
        if chunk_index < 0 or chunk_index >= len(self.frames):
            new_chunk_start = (index // self.chunk_size) * self.chunk_size
            self.load_chunk(new_chunk_start)
            chunk_index = index - self.current_chunk_start
            
        return self.frames[chunk_index]
        
    def draw_frame(self, frame_data):
        """Draw frame from RLE data."""
        # Clear bitmap
        self.bitmap.fill(0)
        
        # Draw pixels
        for run in frame_data:
            x, y, color, count = run
            for i in range(count):
                px = x + i
                py = y
                
                # Handle line wrapping
                while px >= self.width:
                    px -= self.width
                    py += 1
                
                if 0 <= px < self.width and 0 <= py < self.height:
                    self.bitmap[px, py] = color
    
    def play(self):
        """Main playback loop."""
        # Initialize display
        self.matrix = Matrix(width=self.width, height=self.height, bit_depth=4)
        display = self.matrix.display
        
        # Create display objects
        main_group = displayio.Group()
        self.bitmap = displayio.Bitmap(self.width, self.height, len(self.palette))
        self.tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.palette)
        main_group.append(self.tile_grid)
        display.root_group = main_group
        
        print("Playing animation...")
        self.frame_index = 0
        self.last_frame_time = time.monotonic()
        
        while True:
            current_time = time.monotonic()
            
            # Time for next frame?
            if current_time - self.last_frame_time >= self.frame_time:
                frame_data = self.get_frame(self.frame_index)
                if frame_data is not None:
                    self.draw_frame(frame_data)
                    
                    self.frame_index += 1
                    if self.frame_index >= self.frame_count:
                        # Loop
                        self.frame_index = 0
                        gc.collect()
                    
                    self.last_frame_time = current_time
                    
                    # Progress every 5 seconds
                    if self.frame_index % (self.fps * 5) == 0:
                        print(f"Frame {self.frame_index}")
            
            # Small delay
            time.sleep(0.001)


# Main code
player = FramePlayer()
player.load_animation()
player.play()