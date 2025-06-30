# Pre-calculated Path Player - Usage Guide

## What's Happening

When you run `precalc_player.py`, it:

1. **Opens a pygame window** displaying a 64x32 LED matrix simulation
2. **Loads the animation data** from `precalc_paths.json` (234 frames)
3. **Plays the animation** at 30 FPS in a continuous loop

## What You Should See

The animation shows:
- **Yellow/white birds** flying around the display (bird layer)
- **Green/rainbow text** forming "THEME PARK WAITS" (text layer)
- Birds start from edges, flock together, drop "eggs" to form text
- After ~12 seconds, all birds fly away
- The animation then loops

## Running the Player

```bash
# Run the player (opens pygame window)
python precalc_player.py

# The pygame window shows the LED matrix simulation
# Press Ctrl+C in terminal to stop
```

## Troubleshooting

If you don't see anything:
1. Check if a pygame window opened (might be behind other windows)
2. Look for the window titled "SLDK Simulator - MatrixPortal S3"
3. The display is 64x32 pixels, so it's quite small

## Console Output

The player prints status updates every 30 frames:
```
Loaded 234 frames
Starting playback of 234 frames...
Frame 30: 30 birds, 186 pixels captured
Frame 60: 50 birds, 360 pixels captured
Frame 90: 50 birds, 411 pixels captured
...
Animation complete! Looping...
```

## Performance

- Uses simple bitmap updates (no complex math)
- Suitable for slow CircuitPython hardware
- ~158KB data file contains entire animation
- Zero runtime calculations - just position lookups

## For CircuitPython Deployment

1. Copy both files to CIRCUITPY drive:
   - `precalc_player.py`
   - `precalc_paths.json`

2. Modify `code.py` to import and run:
   ```python
   from precalc_player import PathPlayer
   player = PathPlayer()
   player.run()
   ```

The animation will play on the actual LED matrix hardware!