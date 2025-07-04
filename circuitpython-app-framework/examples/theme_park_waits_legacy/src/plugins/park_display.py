"""
Display plugin for theme park wait times.
"""
import asyncio
from cpyapp.core.plugin import DisplayPlugin
from cpyapp.utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")

# Constants
REQUIRED_MESSAGE = "queue-times.com"


class ThemeParkDisplayPlugin(DisplayPlugin):
    """Plugin for displaying theme park wait times."""
    
    def __init__(self):
        super().__init__("ThemeParkDisplay")
        
    def get_messages(self, park_list):
        """
        Get display messages from theme park data.
        
        Args:
            park_list: ThemeParkList object with park data
            
        Returns:
            List of message dictionaries
        """
        messages = []
        
        if not park_list or not hasattr(park_list, 'selected_parks'):
            return messages
            
        # Get parks to display
        parks_to_display = []
        if hasattr(park_list, 'selected_parks') and park_list.selected_parks:
            parks_to_display = park_list.selected_parks
        elif park_list.current_park and park_list.current_park.is_valid():
            parks_to_display = [park_list.current_park]
            
        if not parks_to_display:
            messages.append({
                'type': 'scroll',
                'text': 'No parks selected',
                'delay': 3
            })
            return messages
            
        # Add vacation messages if configured
        if hasattr(park_list, 'vacation') and park_list.vacation:
            vacation_messages = self._get_vacation_messages(park_list.vacation)
            messages.extend(vacation_messages)
            
        # Get display settings
        group_by_park = getattr(park_list, 'group_by_park', False)
        sort_mode = getattr(park_list, 'sort_mode', 'alphabetical')
        skip_meet = getattr(park_list, 'skip_meet', False)
        skip_closed = getattr(park_list, 'skip_closed', False)
        
        if group_by_park:
            # Process each park separately
            for park in parks_to_display:
                if not park.is_open:
                    messages.append({
                        'type': 'scroll',
                        'text': f"{park.name} is closed",
                        'delay': 3
                    })
                else:
                    park_messages = self._get_park_messages(
                        park, skip_meet, skip_closed, sort_mode
                    )
                    messages.extend(park_messages)
        else:
            # Combine all rides from all parks
            all_rides = []
            for park in parks_to_display:
                if park.is_open:
                    for ride in park.rides:
                        if "Meet" in ride.name and skip_meet:
                            continue
                        if not ride.is_open() and skip_closed:
                            continue
                        all_rides.append((ride, park))
                        
            # Sort combined rides
            sorted_rides = self._sort_rides(all_rides, sort_mode)
            
            # Add ride messages
            for ride, park in sorted_rides:
                ride_messages = self._get_ride_messages(ride, park)
                messages.extend(ride_messages)
                
        # Add attribution message
        if parks_to_display:
            park_names = ", ".join([park.name for park in parks_to_display])
            messages.append({
                'type': 'scroll',
                'text': f"Wait times for {park_names} provided by {REQUIRED_MESSAGE}",
                'delay': 4
            })
            
        return messages
        
    def _get_vacation_messages(self, vacation):
        """Get vacation countdown messages."""
        messages = []
        
        if vacation.is_set():
            days_until = vacation.get_days_until()
            if days_until > 1:
                text = f"Vacation to {vacation.name} in: {days_until} days"
            elif days_until == 1:
                text = f"Your vacation to {vacation.name} is tomorrow!!!"
            elif days_until == 0:
                text = f"Your vacation to {vacation.name} is TODAY!!!!!!!!!!!!!"
            else:
                return messages  # Past vacation
                
            messages.append({
                'type': 'scroll',
                'text': text,
                'delay': 0
            })
            
        return messages
        
    def _get_park_messages(self, park, skip_meet, skip_closed, sort_mode):
        """Get messages for a single park."""
        messages = []
        
        # Park header
        messages.append({
            'type': 'scroll',
            'text': f"{park.name} wait times...",
            'delay': 2
        })
        
        # Get and sort rides
        rides_to_show = []
        for ride in park.rides:
            if "Meet" in ride.name and skip_meet:
                continue
            if not ride.is_open() and skip_closed:
                continue
            rides_to_show.append((ride, park))
            
        sorted_rides = self._sort_rides(rides_to_show, sort_mode)
        
        # Add ride messages
        for ride, _ in sorted_rides:
            ride_messages = self._get_ride_messages(ride, park)
            messages.extend(ride_messages)
            
        return messages
        
    def _get_ride_messages(self, ride, park):
        """Get messages for a single ride."""
        messages = []
        
        # Wait time or closed status
        if ride.open_flag:
            messages.append({
                'type': 'static',
                'text': f"{ride.wait_time} min",
                'duration': 2
            })
        else:
            messages.append({
                'type': 'static',
                'text': "Closed",
                'duration': 2
            })
            
        # Ride name
        messages.append({
            'type': 'scroll',
            'text': ride.name,
            'delay': 1
        })
        
        return messages
        
    def _sort_rides(self, rides_with_parks, sort_mode):
        """Sort rides based on mode."""
        if sort_mode == "alphabetical":
            return sorted(rides_with_parks, key=lambda x: x[0].name.lower())
        elif sort_mode == "max_wait":
            return sorted(rides_with_parks, 
                         key=lambda x: x[0].wait_time if x[0].open_flag else 0, 
                         reverse=True)
        elif sort_mode == "min_wait":
            return sorted(rides_with_parks, 
                         key=lambda x: x[0].wait_time if x[0].open_flag else 0)
        else:
            return sorted(rides_with_parks, key=lambda x: x[0].name.lower())
            
    def get_colors(self):
        """Get theme park color scheme."""
        return {
            'ride_name': (0, 150, 255),      # Blue
            'wait_time': (245, 245, 220),    # Old Lace 
            'closed': (255, 0, 0),           # Red
            'park_name': (255, 255, 0),      # Yellow
        }