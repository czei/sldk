"""
Configuration and fixtures for pytest.
This file sets up mocking for CircuitPython modules and provides common test fixtures.
"""
import sys
import os
import json
import pytest
from unittest.mock import MagicMock

# Add project root to path to help with imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Add fully qualified namespace paths to things that are imported, but which
# should be mocked away. For instance, modules which are available in
# CircuitPython but not standard Python.
MOCK_MODULES = [
    "board",
    "digitalio",
    "adafruit_ble.BLERadio",
    "adafruit_ble.advertising.adafruit.AdafruitRadio",
    "adafruit_matrixportal.matrixportal",
    "adafruit_matrixportal.matrix",
    "terminalio",
    "displayio",
    "socketpool",
    "wifi",
    "mdns",
    "storage",
    "rtc",
]


def mock_imported_modules():
    """
    Mocks away the modules named in MOCK_MODULES, so the module under test
    can be imported with modules which may not be available.
    """
    module_paths = set()
    for m in MOCK_MODULES:
        namespaces = m.split(".")
        ns = []
        for n in namespaces:
            ns.append(n)
            module_paths.add(".".join(ns))
    for m_path in module_paths:
        sys.modules[m_path] = MagicMock()


def pytest_runtest_setup(item):
    """
    Called immediately before any test function is called.

    Recreates afresh the mocked away modules so state between tests remains
    isolated.
    """
    mock_imported_modules()


# Initial mocking needed to stop ImportError when importing module under test.
mock_imported_modules()

@pytest.fixture
def theme_park_list_data():
    """Fixture that loads theme park list test data"""
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'theme-park-list.json')
    with open(fixture_path, 'r') as f:
        return json.load(f)

@pytest.fixture
def magic_kingdom_data():
    """Fixture that loads Magic Kingdom test data"""
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'magic-kingdom.json')
    with open(fixture_path, 'r') as f:
        return json.load(f)

@pytest.fixture
def universal_data():
    """Fixture that loads Universal test data"""
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'universal.json')
    with open(fixture_path, 'r') as f:
        return json.load(f)

@pytest.fixture
def closed_park_data():
    """Fixture that loads closed park test data"""
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'closed-park.json')
    with open(fixture_path, 'r') as f:
        return json.load(f)

@pytest.fixture
def epcot_data():
    """Fixture that loads EPCOT test data"""
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'epcot-test-data.json')
    with open(fixture_path, 'r') as f:
        return json.load(f)

@pytest.fixture
def settings_data():
    """Fixture that loads settings test data"""
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'settings.json')
    with open(fixture_path, 'r') as f:
        return json.load(f)
