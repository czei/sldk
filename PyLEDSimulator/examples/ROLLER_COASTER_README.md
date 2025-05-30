# Roller Coaster Animation

This directory contains a roller coaster animation demo designed for LED matrix displays.

## Features

### Cart Design
- **Size**: Approximately 1/3 of the display height (~10 pixels on a 32-pixel display)
- **Sprite-based**: Uses CircuitPython sprites for optimized performance
- **Visual details**: Red body, yellow stripes, gray wheels, pointed front

### Track System
- **Dynamic path**: Includes climbs, drops, loops, and hills
- **Multiple rails**: Upper and lower rails for realistic appearance
- **Smooth interpolation**: Seamless movement along track segments

### Physics Simulation
- **Speed variation**: Cart moves slower uphill, faster downhill
- **Realistic momentum**: Speed changes based on track slope
- **Continuous motion**: Cart loops around the track indefinitely

## Usage

### Basic Integration
```python
from src.ui.roller_coaster_animation import show_roller_coaster_animation

# Show animation for 10 seconds
await show_roller_coaster_animation(display, duration=10)
```

### Advanced Usage
```python
from src.ui.roller_coaster_animation import RollerCoasterAnimation

# Create custom animation
coaster = RollerCoasterAnimation(width=64, height=32)

# For hardware displays with displayio
if coaster.init_display(display):
    while running:
        coaster.update()
        await asyncio.sleep(0.05)  # 20 FPS
```

## Hardware Compatibility

### CircuitPython/Hardware Mode
- Uses `displayio.TileGrid` sprites for maximum performance
- Optimized sprite updates reduce memory usage
- Supports MatrixPortal S3 and similar devices

### Simulator Mode
- Direct pygame rendering for development
- Pixel-perfect LED simulation
- Real-time visualization of sprite positioning

## Technical Details

### Cart Dimensions
- Height: `max(8, display_height // 3)` pixels
- Width: `cart_height * 1.5` pixels
- Minimum 8 pixels high for visibility

### Performance
- 20 FPS animation rate
- Efficient sprite updates
- Memory-conscious design for CircuitPython

### Track Generation
- Procedural track creation
- Multiple track segments (climbs, drops, curves)
- Configurable track complexity

## Examples

Run the demo:
```bash
cd PyLEDSimulator/examples
python roller_coaster_example.py
```

Or integrate into your own project:
```python
# Short animation (5 seconds)
await show_roller_coaster_animation(display, duration=5)

# Longer demo (30 seconds)
await show_roller_coaster_animation(display, duration=30)
```

## Files

- `roller_coaster_example.py` - Complete demo with setup
- `../src/ui/roller_coaster_animation.py` - Main animation class
- This README - Documentation and usage examples