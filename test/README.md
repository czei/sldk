# ThemeParkAPI Tests

This directory contains the test suite for the ThemeParkAPI application.

## Running Tests

Tests can be run using the standard unittest framework:

```bash
python -m unittest test/test-suite.py
```

## Test Data

The test directory includes several JSON files used as test data:

- `theme-park-list.json` - List of available theme parks
- `magic-kingdom.json` - Wait time data for Disney Magic Kingdom
- `universal.json` - Wait time data for Universal Studios
- `closed-park.json` - Data for a closed theme park
- `epcot-test-data.json` - Data for EPCOT including "Meet & Greet" attractions

## Test Structure

The test suite includes tests for:

1. Fetching and parsing theme park lists
2. Fetching and parsing ride data
3. Vacation countdown calculation
4. Park parameter parsing
5. Settings management
6. HTTP requests
7. URL utilities

## Notes

- Some tests require internet connectivity
- Network-related tests may fail if network conditions are poor
- Some tests are skipped on non-hardware platforms (e.g., system clock setting)