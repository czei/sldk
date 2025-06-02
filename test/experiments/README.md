# Test Experiments Directory

This directory contains experimental tests, debugging tools, and verification scripts that are not part of the main unit test suite. These tests are organized by their primary function.

## Recent Cleanup
Several experimental tests have been removed after serving their purpose:
- Text centering issues have been resolved
- PyLEDSimulator integration is complete
- CircuitPython bugs have been addressed
- Web server and GitHub repo checks are no longer needed

## Directory Structure

### 📺 display/
Display and graphics-related experiments for LED matrix rendering.

#### Files:
- **bitmap_test.py** - Tests basic bitmap display functionality on the LED matrix
- **bitmap_text_test.py** - Experiments with text rendering on bitmaps, includes font and color testing
- **pixel-dust-test.py** - Creates a "pixel dust" animation effect with random falling pixels
- **sparkle_test.py** - Tests sparkle/glitter animation effects on the display
- **splash-test.py** - Tests splash screen display with logo and animations
- **test_display.py** - General display functionality testing with scrolling text
- **test_image-processor.py** - Tests image loading and processing for LED display

### 🌐 network/
Network, HTTP, and web server testing experiments.

#### Files:
- **code-http-test.py** - Tests CircuitPython's HTTP capabilities and API calls
- **final_web_test.py** - Comprehensive web server functionality test
- **test_dev_server.py** - Tests the development web server endpoints
- **test_live_data.py** - Verifies live API data fetching from queue-times.com
- **test_mock_vs_live.py** - Compares mock data vs live API responses
- **verify_live_data.py** - Simple script to verify HTTP client uses live data

### ⚙️ system/
System-level and hardware-specific experiments.

#### Files:
- **code_entry.py** - Tests the main entry point and initialization
- **code-ota-test.py** - Tests over-the-air update functionality
- **test_filesystem.py** - Tests filesystem operations on CircuitPython

### 🔧 integration/
Full system integration tests that exercise multiple components.

#### Files:
- **test-suite.py** - Original comprehensive test suite using unittest framework
- **test_full_run.py** - Tests complete application flow from start to finish
- **test_theme_park_service_integration.py** - Integration test for theme park API service
- **run_and_test_detailed.py** - Runs the app with detailed debug output
- **run_dev_test.py** - Tests running in development environment
- **simple_run_test.py** - Basic smoke test for application startup
- **test_with_debugging.py** - Runs tests with extensive debug logging
- **test_with_progress.py** - Tests with progress indicators

## Usage

These experimental tests are not run as part of the standard test suite (`make test-unit`). They are used for:

1. **Debugging** - When tracking down specific issues
2. **Hardware Testing** - When testing on actual CircuitPython hardware
3. **Feature Development** - When experimenting with new features
4. **Integration Verification** - When testing the full system

### Running Tests

To run a specific experiment:
```bash
# Run a display experiment
python test/experiments/display/sparkle_test.py

# Run a network test
python test/experiments/network/test_live_data.py

# Run an integration test
python test/experiments/integration/simple_run_test.py
```

### Requirements

- **Display tests**: May require PyLEDSimulator or actual MatrixPortal hardware
- **Network tests**: Require internet connection and may need API keys
- **System tests**: Some require CircuitPython hardware
- **Integration tests**: May require full environment setup

## Notes

- These tests may have dependencies not listed in requirements.txt
- Some tests are interactive and require user observation
- Hardware tests will fail gracefully when run without hardware
- Network tests may fail due to API rate limits or connectivity issues