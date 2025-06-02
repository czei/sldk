"""
Test for ThemeParkService to verify API endpoints work
"""
import sys
import os
import pytest
import asyncio
import json
from unittest.mock import MagicMock, patch

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.theme_park_service import ThemeParkService
from src.network.http_client import HttpClient, Response
from src.config.settings_manager import SettingsManager

# Mock data for testing
MOCK_PARK_LIST_JSON = """[
    {
        "name": "Disney Parks",
        "parks": [
            {"id": 6, "name": "Disney Magic Kingdom", "latitude": 28.4177, "longitude": -81.5812},
            {"id": 5, "name": "Disney's EPCOT", "latitude": 28.3747, "longitude": -81.5494}
        ]
    },
    {
        "name": "Universal Parks",
        "parks": [
            {"id": 3, "name": "Universal Studios Florida", "latitude": 28.4749, "longitude": -81.4664}
        ]
    }
]"""

MOCK_PARK_DATA_JSON = """{
    "lands": [
        {
            "id": 1,
            "name": "Main Street USA",
            "rides": [
                {"id": 101, "name": "Space Mountain", "is_open": true, "wait_time": 45},
                {"id": 102, "name": "Haunted Mansion", "is_open": true, "wait_time": 30},
                {"id": 103, "name": "Pirates of the Caribbean", "is_open": false, "wait_time": 0}
            ]
        }
    ],
    "rides": [
        {"id": 104, "name": "Jungle Cruise", "is_open": true, "wait_time": 20}
    ]
}"""

class MockHttpClient:
    """Mock HTTP client for testing"""
    async def get(self, url, headers=None, max_retries=3):
        """Mock GET method that returns different responses based on URL"""
        if "parks.json" in url:
            return Response(status_code=200, text=MOCK_PARK_LIST_JSON)
        elif "queue_times.json" in url:
            return Response(status_code=200, text=MOCK_PARK_DATA_JSON)
        else:
            return Response(status_code=404, text="{}")

@pytest.mark.asyncio
async def test_fetch_park_list():
    """Test fetching the park list"""
    # Setup
    http_client = MockHttpClient()
    settings_manager = MagicMock()
    service = ThemeParkService(http_client, settings_manager)
    
    # Execute
    park_list = await service.fetch_park_list()
    
    # Assert
    assert park_list is not None
    assert park_list.park_list is not None
    assert len(park_list.park_list) == 3
    assert park_list.park_list[0].name == "Disney Magic Kingdom"
    assert park_list.park_list[0].id == 6

@pytest.mark.asyncio
async def test_fetch_park_data():
    """Test fetching specific park data"""
    # Setup
    http_client = MockHttpClient()
    settings_manager = MagicMock()
    service = ThemeParkService(http_client, settings_manager)
    
    # Execute
    park_data = await service.fetch_park_data(6)  # Magic Kingdom ID
    
    # Assert
    assert park_data is not None
    assert "lands" in park_data
    assert len(park_data["lands"]) == 1
    assert len(park_data["lands"][0]["rides"]) == 3
    assert park_data["lands"][0]["rides"][0]["name"] == "Space Mountain"

@pytest.mark.asyncio
async def test_get_ride_wait_times():
    """Test getting ride wait times"""
    # Setup
    http_client = MockHttpClient()
    settings_manager = MagicMock()
    service = ThemeParkService(http_client, settings_manager)
    
    # First fetch the park list to populate the park_list attribute
    await service.fetch_park_list()
    
    # Execute - get all ride wait times
    wait_times = await service.get_ride_wait_times(park_id=6)
    
    # Assert
    assert wait_times is not None
    assert len(wait_times) == 4  # Total rides in mock data
    assert "Space Mountain" in wait_times
    assert wait_times["Space Mountain"]["wait_time"] == 45
    assert wait_times["Space Mountain"]["is_open"] is True
    
    # Execute - get specific ride wait time
    space_mountain = await service.get_ride_wait_times(park_id=6, ride_name="Space Mountain")
    
    # Assert
    assert space_mountain is not None
    assert space_mountain["name"] == "Space Mountain"
    assert space_mountain["wait_time"] == 45
    assert space_mountain["is_open"] is True

@pytest.mark.asyncio
async def test_search_parks():
    """Test searching for parks"""
    # Setup
    http_client = MockHttpClient()
    settings_manager = MagicMock()
    service = ThemeParkService(http_client, settings_manager)
    
    # First fetch the park list to populate the park_list attribute
    await service.fetch_park_list()
    
    # Execute - search for Disney parks
    disney_parks = await service.search_parks("Disney")
    
    # Assert
    assert disney_parks is not None
    assert len(disney_parks) == 2
    assert disney_parks[0]["name"] == "Disney Magic Kingdom"
    assert disney_parks[1]["name"] == "Disney's EPCOT"
    
    # Execute - search for Universal parks
    universal_parks = await service.search_parks("Universal")
    
    # Assert
    assert universal_parks is not None
    assert len(universal_parks) == 1
    assert universal_parks[0]["name"] == "Universal Studios Florida"