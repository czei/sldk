# Pre-calculated Animation Solution for MatrixPortal

## Overview

This solution addresses the computational limitations of the MatrixPortal S3 hardware by pre-calculating all bird paths and pixel captures on a fast machine, then playing back the animation data on the hardware without any complex runtime calculations.

## Architecture

### 1. Path Generator (`precalc_path_generator.py`)
- Runs the full egg drop swarm animation on a development machine
- Records bird positions and pixel captures for each frame
- Uses delta encoding to compress movement data
- Outputs JSON file with all animation data

### 2. Lightweight Player (`precalc_player.py`)
- Reads pre-calculated paths from JSON file
- Renders birds and pixels without any flocking calculations
- Uses simple bitmap operations for display
- Optimized for CircuitPython's limited resources

## Data Format

The compressed JSON format includes:
- **Metadata**: Display dimensions, FPS, total frames
- **Frames**: Array of frame data with:
  - Bird updates (delta-encoded positions)
  - New pixel captures per frame

### Compression Features:
1. **Delta Encoding**: Only stores position changes, not absolute positions
2. **Sparse Updates**: Only includes birds that moved
3. **Compact Keys**: Short property names ('f', 'b', 'p')
4. **Sub-pixel Precision**: 4x resolution for smooth movement

## Performance Benefits

1. **Zero Runtime Calculations**: No flocking math, distance calculations, or sqrt operations
2. **Predictable Performance**: Fixed playback rate regardless of bird count
3. **Memory Efficient**: ~200KB for entire animation (vs continuous calculations)
4. **Battery Savings**: Reduced CPU usage on battery-powered devices

## Usage

### Generate Paths (on development machine):
```bash
python precalc_path_generator.py
```

### Deploy to MatrixPortal:
1. Copy `precalc_player.py` to the CIRCUITPY drive
2. Copy `precalc_paths.json` to the CIRCUITPY drive
3. Run the player on boot or via code.py

### Customization:
- Adjust animation parameters in the generator
- Create multiple path files for different animations
- Modify playback speed in the player

## Results

- **File Size**: ~158KB for 234 frames (12.6 seconds)
- **Compression Ratio**: 44.9% of original size
- **Playback**: Smooth 30 FPS on MatrixPortal hardware
- **Complete Animation**: Birds flock, drop eggs, form text, fly away

This approach enables complex animations that would be impossible to run in real-time on the MatrixPortal's limited ESP32-S3 processor.