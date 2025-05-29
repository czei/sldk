# Theme Park API Simulator

This document provides an overview of the LED Matrix simulator implementation for the Theme Park API project. The simulator allows developers to run the application on desktop platforms without needing to deploy to CircuitPython hardware for every change.

## Implementation Summary

The simulator implementation includes the following key components:

1. **Abstract Interface Layer**: Created `DisplayInterface` to define a common interface for both hardware and simulated displays
2. **Platform Detection**: Added functions to detect CircuitPython environment and development mode
3. **Factory Pattern**: Implemented a display factory to create the appropriate display implementation 
4. **Simulated Display**: Created a Pygame-based LED matrix simulator that replicates the hardware display
5. **WiFi Simulation**: Modified the WiFi manager to work in development mode
6. **Mock API Data**: Enhanced the HTTP client to provide mock park and ride data in development mode
7. **Application Adaptation**: Updated app.py to support running in development mode

## Key Files

- `/src/ui/display_interface.py` - Abstract base class for all display implementations
- `/src/ui/simulator_display.py` - Pygame-based simulator for desktop development
- `/src/ui/display_factory.py` - Factory that selects the appropriate display implementation
- `/src/ui/hardware_display.py` - Hardware implementation for MatrixPortal S3
- `/src/network/wifi_manager.py` - WiFi manager with development mode support
- `/src/network/http_client.py` - HTTP client with mock data for development mode
- `/src/app.py` - Main application with development mode adaptations

## Development Workflow

The new development workflow using the simulator:

1. Make code changes on your desktop
2. Run `make dev` to test changes with the simulator
3. Once working, deploy to hardware with `make copy_to_circuitpy`

This approach speeds up development cycles significantly compared to the previous workflow which required copying files to hardware for each change.

## Mock Data

The simulator provides mock data for:

1. Theme park list (including Disney Magic Kingdom, Epcot, Universal Studios)
2. Ride information with wait times for selected parks
3. Other API endpoints as needed

The mock data is provided by the HTTP client when running in development mode and detecting API URLs.

## Known Issues and Limitations

1. The simulator's font rendering doesn't exactly match the hardware display
2. Some CircuitPython hardware features don't translate perfectly to desktop
3. Performance characteristics differ between simulator and hardware
4. The web server functionality is disabled in development mode

## Next Steps and Enhancements

Possible future enhancements for the simulator:

1. **Test Data Editor**: Tool to create and modify mock data for testing
2. **State Persistence**: Save application state between runs
3. **Improved Visuals**: Better visual match with the hardware display
4. **Simulated Web Server**: Enable web configuration in development mode
5. **Automated Tests**: Use the simulator for automated UI testing

## Usage Instructions

To use the simulator:

```bash
# Install dependencies
make install-dev-deps

# Run in development mode
make dev
```

For more details, see `/src/ui/README.md`