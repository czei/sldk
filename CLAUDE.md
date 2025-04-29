# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build Commands
* `make copy_to_circuitpy` - Deploy to MatrixPortal S3 device
* `make release` - Copy files to release archive

## Testing
* Run all tests: `python -m pytest test/test-suite.py -v`
* Run single test: `python -m pytest test/test-suite.py::Test::test_method_name -v`
* Test files are in the `test/` directory with `test_` prefix or `-test` suffix

## Code Style
* **Imports**: Group by stdlib, third-party (Adafruit), then project modules
* **Classes**: PascalCase (e.g., `ThemeParkList`)
* **Functions/Variables**: snake_case (e.g., `get_park_by_id`, `park_list`)
* **Constants**: UPPERCASE (e.g., `REQUIRED_MESSAGE`)
* **Error Handling**: Use try/except blocks with specific exceptions
* **Logging**: Use `ErrorHandler` class for centralized error logging
* **Documentation**: Use docstrings for classes and methods
* **Hardware Abstraction**: Include fallbacks when hardware components aren't available

## CircuitPython Development
* Support both running on actual hardware and testing in standard Python environment
* Test functionality in isolation before deploying to hardware
* Ensure tests properly mock CircuitPython-specific modules
* Separate functionality that could be applied to any CircuitPython project from the specific functionality of this project. The ultimate goal is to refactor into an open source library.