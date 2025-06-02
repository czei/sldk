# ThemeParkAPI Tests

This directory contains the test suite for the ThemeParkAPI application.

## Test Structure

The tests are organized following these patterns:

- `unit/`: Contains unit tests organized by module (models, network, utils, etc.)
- `integration/`: Contains tests that verify multiple components working together (currently empty)
- `experiments/`: Contains experimental tests, debugging tools, and verification scripts
- `fixtures/` and `data/`: Contains test data and shared fixtures
- `helpers.py`: Contains utility functions to simplify test writing
- `conftest.py`: Contains pytest fixtures and CircuitPython mocking

## Running Tests

Tests can be run using pytest:

```bash
# Run all tests
python -m pytest

# Run tests for a specific module
python -m pytest test/unit/models

# Run a specific test file
python -m pytest test/unit/models/test_theme_park.py

# Run a specific test
python -m pytest test/unit/models/test_theme_park.py::TestThemePark::test_initialization

# Run tests with verbose output
python -m pytest -v
```

## Test Data

The test directory includes several JSON files used as test data:

- `theme-park-list.json` - List of available theme parks
- `magic-kingdom.json` - Wait time data for Disney Magic Kingdom
- `universal.json` - Wait time data for Universal Studios
- `closed-park.json` - Data for a closed theme park
- `epcot-test-data.json` - Data for EPCOT including "Meet & Greet" attractions

## Test Functionality

The test suite includes tests for:

1. Fetching and parsing theme park lists
2. Fetching and parsing ride data
3. Vacation countdown calculation
4. Park parameter parsing
5. Settings management
6. HTTP requests
7. URL utilities
8. Error handling and logging

## Writing New Tests

When writing new tests:

1. Use pytest fixtures from conftest.py to get access to test data
2. Use the helpers from helpers.py for common test patterns
3. Create tests that mirror the directory structure of the source code
4. Mock CircuitPython-specific modules as needed

### Example:

```python
import pytest
from src.models.theme_park import ThemePark

class TestThemePark:
    def test_initialization(self, magic_kingdom_data):
        park = ThemePark(magic_kingdom_data, "Disney Magic Kingdom", 6)
        assert park.name == "Disney Magic Kingdom"
        assert len(park.rides) > 0
```

## Notes

- Some tests require internet connectivity
- Network-related tests may fail if network conditions are poor
- Some tests are skipped on non-hardware platforms (e.g., system clock setting)
- When testing code that accesses hardware, use the MockHardwareContext from helpers.py