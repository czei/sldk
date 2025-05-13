# LED Matrix Display Simulator

The ThemeParkAPI project includes a display simulator that allows you to develop and test your application on macOS/desktop without needing to constantly deploy to CircuitPython hardware.

## Overview

The display architecture is designed with the following components:

1. **DisplayInterface (Abstract Base Class)**: Defines the common interface for all display implementations
2. **SimulatedLEDMatrix**: Pygame-based simulator for desktop development
3. **MatrixDisplay**: Hardware implementation for CircuitPython devices
4. **DisplayFactory**: Creates the appropriate display implementation based on the current platform

## Usage

### Running in Development Mode

To run the application with the simulator:

```bash
# Install development dependencies
make install-dev-deps

# Run in development mode
make dev
```

This will launch the application with the simulated LED matrix display in a Pygame window.

### Keyboard Controls

In the simulator window:
- **ESC**: Exit the simulator
- **Close button**: Exit the simulator

## Architecture Details

### DisplayInterface (display_interface.py)

This is the abstract base class that defines the interface for all display implementations. It includes methods for:

- Initializing the display
- Setting text and colors
- Scrolling content
- Clearing the display
- Showing images
- Setting brightness and rotation

### SimulatedLEDMatrix (simulator_display.py)

This is the Pygame-based simulator implementation that mimics the behavior of the LED matrix. It provides:

- A visual representation of the LED matrix with configurable dimensions
- Text display with scrolling
- Image display
- Brightness control
- Async compatibility with `run_async()` method

### MatrixDisplay (hardware_display.py)

This is the implementation for actual CircuitPython hardware. It uses:

- Adafruit's display libraries
- Hardware-specific configuration for MatrixPortal S3
- Methods that match the DisplayInterface

### DisplayFactory (display_factory.py)

This factory creates the appropriate display based on:

- Whether the code is running on CircuitPython or a desktop OS
- If the `--dev` flag is set in command-line arguments
- Platform-specific considerations

## Implementation Notes

1. The simulator uses Pygame to render a grid of "LEDs" that visually represent the hardware display
2. Both implementations support the same methods, making the code compatible across platforms
3. The main application detects the platform and initializes the appropriate display
4. In development mode, an async task is created to update the simulator display

## Adding New Features

When adding new display features:

1. First add the method to the `DisplayInterface` class
2. Implement the method in both `SimulatedLEDMatrix` and `MatrixDisplay`
3. For hardware-specific features, provide a reasonable simulation in `SimulatedLEDMatrix`

## Limitations

The simulator has some limitations:

1. Font rendering is different between Pygame and CircuitPython
2. Some specialized CircuitPython display features may not be perfectly replicated
3. Hardware-specific libraries (like MatrixPortal) are mocked rather than fully implemented

Despite these limitations, the simulator provides a much faster development workflow than constantly deploying to hardware.