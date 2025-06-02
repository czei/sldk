# PyLEDSimulator Integration for Theme Park Waits

## Overview

The Theme Park Waits application now supports the PyLEDSimulator library as an alternative to the simple pygame-based simulator. PyLEDSimulator provides a more accurate simulation of the MatrixPortal S3 hardware, including proper displayio support and LED matrix rendering.

## Usage

### Command Line Options

The application now supports several command line options for choosing the display mode:

```bash
# Use PyLEDSimulator (default for development mode)
python main.py --dev

# Explicitly use PyLEDSimulator
python main.py --dev --pyled

# Use the simple pygame simulator
python main.py --dev --simple-sim
```

### Display Selection Logic

1. **CircuitPython Hardware**: When running on actual MatrixPortal S3 hardware
2. **Development Mode (`--dev`)**: 
   - Default: Uses PyLEDSimulator for accurate simulation
   - With `--simple-sim`: Uses the original pygame simulator
3. **Desktop without `--dev`**: Attempts PyLEDSimulator, falls back to simple simulator

## Features

The PyLEDSimulator display implementation (`pyledsimulator_display.py`) provides:

- Full displayio API compatibility
- Accurate text rendering with proper scaling
- Support for bitmap fonts (tom-thumb.bdf)
- Proper centering of wait times (including 3-digit times)
- Splash screen display
- Scrolling text support
- Color management from settings

## Implementation Details

### Display Class: PyLEDSimulatorDisplay

Located in `src/ui/pyledsimulator_display.py`, this class implements the `DisplayInterface` and provides:

- **Initialization**: Creates a MatrixPortal S3 device with 64x32 LED matrix
- **Display Groups**: Manages multiple displayio groups for different content types
- **Text Centering**: Properly accounts for scale factor when centering text
- **Color Support**: Integrates with the settings manager for color customization

### Key Methods

- `initialize()`: Sets up the PyLEDSimulator display and all display groups
- `show_splash()`: Displays the startup splash screen
- `show_ride_name()`: Shows ride names with scrolling if needed
- `show_ride_wait_time()`: Displays wait times with proper centering
- `show_ride_closed()`: Shows "Closed" status for rides
- `show_scroll_message()`: Displays scrolling messages
- `_center_text()`: Centers text accounting for scale factor

## Testing

To test the PyLEDSimulator integration:

```bash
# Run the test script
python test/test_pyledsimulator_integration.py

# Run the main application with PyLEDSimulator
python main.py --dev
```

## Advantages over Simple Simulator

1. **Accurate Rendering**: Uses actual displayio API for pixel-perfect simulation
2. **Font Support**: Proper bitmap font rendering including small fonts
3. **Scale Support**: Correctly handles scaled text (e.g., scale=2 for wait times)
4. **Better Visual**: More realistic LED matrix appearance
5. **CircuitPython Compatibility**: Code is more transferable to hardware

## Dependencies

The PyLEDSimulator library is included in the `PyLEDSimulator/` directory and requires:
- Python 3.7+
- pygame (for window rendering)
- Pillow (for image support)

## Future Enhancements

- Reveal-style splash animation support
- Performance optimizations for scrolling
- Additional visual effects
- Screenshot capabilities for documentation