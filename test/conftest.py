"""
Pytest configuration and fixtures for the ThemeParkAPI test suite.
"""
import pytest
import json
import os

@pytest.fixture
def magic_kingdom_data():
    """Load Magic Kingdom test data from fixture file"""
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    magic_kingdom_file = os.path.join(fixtures_dir, 'magic-kingdom.json')
    
    with open(magic_kingdom_file, 'r') as f:
        return json.load(f)

@pytest.fixture
def epcot_data():
    """Load EPCOT test data from fixture file"""
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    epcot_file = os.path.join(fixtures_dir, 'epcot-test-data.json')
    
    with open(epcot_file, 'r') as f:
        return json.load(f)

@pytest.fixture
def theme_park_list_data():
    """Load theme park list test data from fixture file"""
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    parks_file = os.path.join(fixtures_dir, 'theme-park-list.json')
    
    with open(parks_file, 'r') as f:
        return json.load(f)

@pytest.fixture
def settings_data():
    """Load settings test data from fixture file"""
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    settings_file = os.path.join(fixtures_dir, 'settings.json')
    
    with open(settings_file, 'r') as f:
        return json.load(f)

@pytest.fixture
def closed_park_data():
    """Load closed park test data from fixture file"""
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    closed_park_file = os.path.join(fixtures_dir, 'closed-park.json')
    
    with open(closed_park_file, 'r') as f:
        return json.load(f)

@pytest.fixture
def universal_data():
    """Load Universal test data from fixture file"""
    fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    universal_file = os.path.join(fixtures_dir, 'universal.json')
    
    with open(universal_file, 'r') as f:
        return json.load(f)