# Swarm Animation Frame System

This system allows you to pre-generate complex swarm animations on a powerful computer and then play them back on CircuitPython devices with limited memory and processing power.

## Files

1. **generate_swarm_frames.py** - Runs the full swarm animation and saves each frame
2. **play_swarm_frames.py** - Plays the animation (works in both simulator and CircuitPython)
3. **circuitpython_swarm_player.py** - Simplified player optimized for CircuitPython hardware
4. **swarm_animation_frames.json** - The generated animation data (created by generate_swarm_frames.py)

## Usage

### Step 1: Generate Animation Frames

On your computer with the PyLEDSimulator installed:

```bash
cd PyLEDSimulator/examples
python generate_swarm_frames.py
```

This will:
- Run the full swarm animation with flocking behavior
- Capture each frame as the birds build "THEME PARK WAITS"
- Save frames in a compressed format to `swarm_animation_frames.json`
- Takes about 10 seconds to generate ~200 frames
- Creates a ~400KB JSON file

### Step 2: Test in Simulator (Optional)

```bash
python play_swarm_frames.py
```

This will play the animation in the LED simulator window.

### Step 3: Deploy to CircuitPython

1. Copy these files to your CIRCUITPY drive:
   - `circuitpython_swarm_player.py` → rename to `code.py`
   - `swarm_animation_frames.json`

2. The animation will start playing automatically

## Technical Details

### Frame Compression

Frames are stored using run-length encoding (RLE) to reduce memory usage:
- Each run is: `[x, y, color_index, count]`
- Consecutive pixels of the same color are combined
- Color palette supports 22 colors (black + 20 rainbow colors + yellow)

### Memory Management

The player loads frames in chunks to work within CircuitPython's memory limits:
- Default chunk size: 50 frames for hardware, 100 for simulator
- Automatically loads new chunks as needed
- Uses garbage collection between loops

### Customization

You can modify the animation by editing `generate_swarm_frames.py`:
- Change bird behavior (speed, flocking parameters)
- Adjust spawn rates and patterns
- Modify color schemes
- Change text or layout

## Performance

- Generation: ~20 seconds for full animation
- File size: ~400KB for 200+ frames
- Playback: Smooth 20 FPS on MatrixPortal S3
- Memory usage: Under 100KB on CircuitPython

## Advantages

1. **Complex animations** - Full flocking algorithm that would be too slow on hardware
2. **Consistent timing** - No frame drops due to processing
3. **Easy testing** - Preview on computer before deploying
4. **Reusable** - Generate once, play many times
5. **Customizable** - Easy to create variations

## Creating Your Own Animations

To create custom pre-calculated animations:

1. Copy `generate_swarm_frames.py` as a template
2. Modify the animation logic in `generate_frames()`
3. Keep the same frame capture structure
4. Use the same color palette format
5. Test with `play_swarm_frames.py`
6. Deploy with `circuitpython_swarm_player.py`