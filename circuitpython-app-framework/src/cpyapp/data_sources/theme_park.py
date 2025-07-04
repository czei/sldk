"""
Theme Park Data Source for queue-times.com API.

This module provides a data source for fetching theme park wait times
and park information from the queue-times.com API.
"""
import json
try:
    from typing import Dict, Any, Optional, List
except ImportError:
    # CircuitPython doesn't have typing
    pass

from .base import HttpDataSource
from ..utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")


class ThemeParkDataSource(HttpDataSource):
    """
    Data source for theme park wait times from queue-times.com.
    
    This class wraps the queue-times.com API and provides easy access
    to theme park wait times and park information.
    """
    
    # Base URL for queue-times.com API
    BASE_URL = "https://queue-times.com"
    
    # Popular park presets
    PRESETS = {
        # Disney World Parks
        'magic_kingdom': 6,
        'epcot': 5,
        'hollywood_studios': 7,
        'animal_kingdom': 8,
        'disney_world': [6, 5, 7, 8],  # All Disney World parks
        
        # Disneyland Parks
        'disneyland': 16,
        'california_adventure': 17,
        'disneyland_resort': [16, 17],  # Both Disneyland parks
        
        # Universal Orlando
        'universal_studios': 10,
        'islands_of_adventure': 9,
        'universal_orlando': [10, 9],  # Both Universal Orlando parks
        
        # Universal Hollywood
        'universal_hollywood': 13,
        
        # Other popular parks
        'cedar_point': 50,
        'six_flags_magic_mountain': 32,
        'knotts_berry_farm': 30,
        'busch_gardens_tampa': 52,
        'seaworld_orlando': 53,
    }
    
    def __init__(self, park_id=None, preset=None, **kwargs):
        """
        Initialize theme park data source.
        
        Args:
            park_id: Specific park ID or list of park IDs
            preset: Preset name (e.g., 'disney_world', 'magic_kingdom')
            **kwargs: Additional arguments passed to HttpDataSource
        """
        # Use preset if provided
        if preset and preset in self.PRESETS:
            park_id = self.PRESETS[preset]
            
        # Default to Magic Kingdom if nothing specified
        if park_id is None:
            park_id = self.PRESETS['magic_kingdom']
            logger.info("No park specified, defaulting to Magic Kingdom")
            
        # Store park configuration
        self.park_id = park_id
        self.park_list = None
        self.current_park_data = None
        
        # Set appropriate URL based on configuration
        if isinstance(park_id, list):
            # Multiple parks - we'll need to fetch each
            url = None  # Will be set per request
        else:
            # Single park
            url = f"{self.BASE_URL}/parks/{park_id}/queue_times.json"
            
        super().__init__("ThemePark", url=url, **kwargs)
        
    async def _fetch_data(self):
        """Fetch theme park data."""
        if isinstance(self.park_id, list):
            # Fetch data for multiple parks
            return await self._fetch_multiple_parks()
        else:
            # Fetch data for single park
            return await self._fetch_single_park(self.park_id)
            
    async def _fetch_single_park(self, park_id):
        """Fetch data for a single park."""
        self.url = f"{self.BASE_URL}/parks/{park_id}/queue_times.json"
        park_data = await super()._fetch_data()
        
        # Store for later use
        self.current_park_data = park_data
        
        return park_data
        
    async def _fetch_multiple_parks(self):
        """Fetch data for multiple parks."""
        all_parks_data = []
        
        for park_id in self.park_id:
            try:
                park_data = await self._fetch_single_park(park_id)
                if park_data:
                    all_parks_data.append(park_data)
            except Exception as e:
                logger.error(e, f"Failed to fetch data for park {park_id}")
                
        return all_parks_data
        
    async def get_park_list(self):
        """
        Get list of all available parks.
        
        Returns:
            List of park dictionaries with id, name, latitude, longitude
        """
        if self.park_list is None:
            try:
                # Temporarily change URL to fetch park list
                original_url = self.url
                self.url = f"{self.BASE_URL}/parks.json"
                
                parks_data = await super()._fetch_data()
                self.park_list = parks_data
                
                # Restore original URL
                self.url = original_url
                
            except Exception as e:
                logger.error(e, "Failed to fetch park list")
                self.park_list = []
                
        return self.park_list
        
    def parse_data(self, raw_data):
        """Parse theme park data into standard format."""
        if isinstance(raw_data, list):
            # Multiple parks
            parsed_parks = []
            for park_data in raw_data:
                parsed = self._parse_single_park(park_data)
                if parsed:
                    parsed_parks.append(parsed)
            return parsed_parks
        else:
            # Single park
            return self._parse_single_park(raw_data)
            
    def _parse_single_park(self, park_data):
        """Parse single park data."""
        if not park_data:
            return None
            
        parsed = {
            'name': park_data.get('name', 'Unknown Park'),
            'is_open': park_data.get('is_open', False),
            'rides': [],
            'total_rides': 0,
            'rides_open': 0,
            'average_wait': 0
        }
        
        # Process lands and rides
        total_wait = 0
        rides_with_wait = 0
        
        for land in park_data.get('lands', []):
            for ride in land.get('rides', []):
                ride_info = {
                    'name': ride.get('name', 'Unknown'),
                    'wait_time': ride.get('wait_time', 0),
                    'is_open': ride.get('is_open', False),
                    'land': land.get('name', 'Unknown')
                }
                
                parsed['rides'].append(ride_info)
                parsed['total_rides'] += 1
                
                if ride_info['is_open']:
                    parsed['rides_open'] += 1
                    if ride_info['wait_time'] > 0:
                        total_wait += ride_info['wait_time']
                        rides_with_wait += 1
                        
        # Calculate average wait time
        if rides_with_wait > 0:
            parsed['average_wait'] = total_wait // rides_with_wait
            
        # Sort rides by wait time (highest first)
        parsed['rides'].sort(key=lambda x: x['wait_time'], reverse=True)
        
        return parsed
        
    def format_for_display(self, data):
        """Format theme park data for display."""
        messages = []
        
        if not data:
            return [{
                'type': 'scroll',
                'text': 'No park data available',
                'delay': 2
            }]
            
        if isinstance(data, list):
            # Multiple parks - show summary
            for park in data:
                if park:
                    messages.extend(self._format_park_summary(park))
        else:
            # Single park - show detailed info
            messages.extend(self._format_park_details(data))
            
        return messages
        
    def _format_park_summary(self, park):
        """Format park summary for multiple parks display."""
        messages = []
        
        # Park name and status
        status = "OPEN" if park['is_open'] else "CLOSED"
        messages.append({
            'type': 'scroll',
            'text': f"{park['name']} - {status}",
            'delay': 2
        })
        
        if park['is_open'] and park['rides_open'] > 0:
            # Show statistics
            messages.append({
                'type': 'scroll',
                'text': f"Rides: {park['rides_open']}/{park['total_rides']} | Avg Wait: {park['average_wait']}min",
                'delay': 2
            })
            
            # Show top 3 wait times
            top_rides = [r for r in park['rides'] if r['is_open'] and r['wait_time'] > 0][:3]
            for ride in top_rides:
                messages.append({
                    'type': 'scroll',
                    'text': f"{ride['name']}: {ride['wait_time']}min",
                    'delay': 1.5
                })
                
        return messages
        
    def _format_park_details(self, park):
        """Format detailed park information for single park display."""
        messages = []
        
        # Park header
        status = "OPEN" if park['is_open'] else "CLOSED"
        messages.append({
            'type': 'scroll',
            'text': f"=== {park['name']} - {status} ===",
            'delay': 3
        })
        
        if not park['is_open']:
            return messages
            
        # Park statistics
        messages.append({
            'type': 'scroll',
            'text': f"Open Rides: {park['rides_open']}/{park['total_rides']}",
            'delay': 2
        })
        
        if park['average_wait'] > 0:
            messages.append({
                'type': 'scroll',
                'text': f"Average Wait: {park['average_wait']} minutes",
                'delay': 2
            })
            
        # Show rides by wait time
        open_rides = [r for r in park['rides'] if r['is_open']]
        
        if open_rides:
            # Longest waits
            long_waits = [r for r in open_rides if r['wait_time'] >= 60]
            if long_waits:
                messages.append({
                    'type': 'scroll',
                    'text': "--- LONG WAITS (60+ min) ---",
                    'delay': 2
                })
                for ride in long_waits[:5]:  # Top 5
                    messages.append({
                        'type': 'scroll',
                        'text': f"{ride['name']}: {ride['wait_time']}min",
                        'delay': 1.5
                    })
                    
            # Moderate waits
            moderate_waits = [r for r in open_rides if 30 <= r['wait_time'] < 60]
            if moderate_waits:
                messages.append({
                    'type': 'scroll',
                    'text': "--- MODERATE WAITS (30-59 min) ---",
                    'delay': 2
                })
                for ride in moderate_waits[:5]:  # Top 5
                    messages.append({
                        'type': 'scroll',
                        'text': f"{ride['name']}: {ride['wait_time']}min",
                        'delay': 1.5
                    })
                    
            # Short waits
            short_waits = [r for r in open_rides if 0 < r['wait_time'] < 30]
            if short_waits:
                messages.append({
                    'type': 'scroll',
                    'text': "--- SHORT WAITS (<30 min) ---",
                    'delay': 2
                })
                for ride in short_waits[:5]:  # Top 5
                    messages.append({
                        'type': 'scroll',
                        'text': f"{ride['name']}: {ride['wait_time']}min",
                        'delay': 1.5
                    })
                    
            # Walk-ons
            walk_ons = [r for r in open_rides if r['wait_time'] == 0]
            if walk_ons:
                messages.append({
                    'type': 'scroll',
                    'text': f"--- WALK-ON RIDES ({len(walk_ons)}) ---",
                    'delay': 2
                })
                # Show first few walk-ons
                for ride in walk_ons[:3]:
                    messages.append({
                        'type': 'scroll',
                        'text': f"{ride['name']}",
                        'delay': 1
                    })
                if len(walk_ons) > 3:
                    messages.append({
                        'type': 'scroll',
                        'text': f"... and {len(walk_ons) - 3} more",
                        'delay': 1
                    })
                    
        return messages
        
    def get_ride_wait_time(self, ride_name):
        """
        Get wait time for a specific ride.
        
        Args:
            ride_name: Name of the ride
            
        Returns:
            Wait time in minutes, or None if not found
        """
        if not self.current_park_data:
            return None
            
        parsed = self.parse_data(self.current_park_data)
        if not parsed:
            return None
            
        # Handle multiple parks
        parks = parsed if isinstance(parsed, list) else [parsed]
        
        for park in parks:
            for ride in park.get('rides', []):
                if ride_name.lower() in ride['name'].lower():
                    return ride['wait_time']
                    
        return None