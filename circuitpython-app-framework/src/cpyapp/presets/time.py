"""
Time and Clock presets for various time-based displays.

This module provides presets for displaying clocks, timers,
calendars, and other time-related information.
"""
import time
try:
    from typing import Dict, Any, List
except ImportError:
    # CircuitPython doesn't have typing
    pass

from .base import ConfigurablePreset
from ..utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")


class DigitalClockPreset(ConfigurablePreset):
    """Standard digital clock display."""
    
    def __init__(self):
        super().__init__("digital_clock", category="time")
        
        self._config.update({
            'data_source': {
                'type': 'function',
                'function': self._get_time,
                'cache_ttl': 0  # No caching
            },
            'style': {
                'name': 'clock',
                'theme': 'digital',
                'colors': {
                    'time': 'Cyan',
                    'date': 'White',
                    'seconds': 'Gray',
                    'background': 'Black'
                },
                'scroll_speed': 0.1,  # Slower scroll for time
                'font_scale': 2,      # Larger font for time
                'format': '{time}'
            },
            'board': 'auto',
            'metadata': {
                'name': 'digital_clock',
                'description': 'Simple digital clock display',
                'tags': ['clock', 'time', 'digital']
            }
        })
        
        self.parameters = {
            'format_12hr': {
                'type': 'bool',
                'default': True,
                'description': '12-hour format (vs 24-hour)'
            },
            'show_seconds': {
                'type': 'bool',
                'default': True,
                'description': 'Display seconds'
            },
            'show_date': {
                'type': 'bool',
                'default': False,
                'description': 'Show date with time'
            },
            'timezone': {
                'type': 'str',
                'default': 'local',
                'description': 'Timezone (local or UTC offset)'
            }
        }
        
    def _get_time(self):
        """Get current time formatted."""
        format_12hr = self.get_parameter('format_12hr', True)
        show_seconds = self.get_parameter('show_seconds', True)
        show_date = self.get_parameter('show_date', False)
        
        if format_12hr:
            time_fmt = "%I:%M"
            if show_seconds:
                time_fmt += ":%S"
            time_fmt += " %p"
        else:
            time_fmt = "%H:%M"
            if show_seconds:
                time_fmt += ":%S"
                
        current_time = time.strftime(time_fmt)
        
        if show_date:
            date_str = time.strftime("%b %d")
            return f"{current_time} | {date_str}"
            
        return current_time


class WorldClockPreset(ConfigurablePreset):
    """Multiple timezone clock display."""
    
    def __init__(self):
        super().__init__("world_clock", category="time")
        
        self._config.update({
            'data_source': {
                'type': 'function',
                'function': self._get_world_times,
                'cache_ttl': 0
            },
            'style': {
                'name': 'world_clock',
                'theme': 'international',
                'colors': {
                    'city': 'Yellow',
                    'time': 'White',
                    'am': 'Cyan',
                    'pm': 'Orange',
                    'background': 'DarkBlue'
                },
                'scroll_speed': 0.05,
                'separator': ' | '
            },
            'metadata': {
                'name': 'world_clock',
                'description': 'Clock showing multiple time zones',
                'tags': ['clock', 'time', 'timezone', 'world']
            }
        })
        
        self.parameters = {
            'cities': {
                'type': 'dict',
                'default': {
                    'New York': -5,
                    'London': 0,
                    'Tokyo': 9,
                    'Sydney': 11
                },
                'description': 'Cities and their UTC offsets'
            },
            'format_12hr': {
                'type': 'bool',
                'default': True,
                'description': '12-hour format'
            }
        }
        
    def _get_world_times(self):
        """Get times for multiple cities."""
        cities = self.get_parameter('cities', {})
        format_12hr = self.get_parameter('format_12hr', True)
        
        times = []
        current_utc = time.time()
        
        for city, offset in cities.items():
            # Simple timezone calculation (doesn't handle DST)
            city_time = current_utc + (offset * 3600)
            
            if format_12hr:
                time_str = time.strftime("%I:%M %p", time.gmtime(city_time))
            else:
                time_str = time.strftime("%H:%M", time.gmtime(city_time))
                
            times.append(f"{city}: {time_str}")
            
        return " | ".join(times)


class CountdownTimerPreset(ConfigurablePreset):
    """Countdown timer to a specific event."""
    
    def __init__(self):
        super().__init__("countdown_timer", category="time")
        
        self._config.update({
            'data_source': {
                'type': 'function',
                'function': self._get_countdown,
                'cache_ttl': 0
            },
            'style': {
                'name': 'countdown',
                'theme': 'timer',
                'colors': {
                    'days': 'Red',
                    'hours': 'Orange',
                    'minutes': 'Yellow',
                    'seconds': 'Green',
                    'event': 'White',
                    'background': 'Black'
                },
                'scroll_speed': 0.06,
                'blink_when_close': True
            },
            'metadata': {
                'name': 'countdown_timer',
                'description': 'Countdown to an event or deadline',
                'tags': ['timer', 'countdown', 'event']
            }
        })
        
        self.parameters = {
            'event_name': {
                'type': 'str',
                'default': 'Event',
                'description': 'Name of the event'
            },
            'target_time': {
                'type': 'str',
                'required': True,
                'description': 'Target time (ISO format or timestamp)'
            },
            'show_seconds': {
                'type': 'bool',
                'default': True,
                'description': 'Show seconds in countdown'
            }
        }
        
    def _get_countdown(self):
        """Calculate countdown to target."""
        event_name = self.get_parameter('event_name', 'Event')
        target_str = self.get_parameter('target_time', '')
        show_seconds = self.get_parameter('show_seconds', True)
        
        if not target_str:
            return f"{event_name}: No target set"
            
        try:
            # Parse target time (simplified - would need better parsing)
            if target_str.isdigit():
                target_time = int(target_str)
            else:
                # Basic ISO format parsing
                # In real implementation, would use proper date parsing
                target_time = time.time() + 86400  # Default to 24 hours from now
                
            current_time = time.time()
            remaining = int(target_time - current_time)
            
            if remaining < 0:
                return f"{event_name}: Complete!"
                
            days = remaining // 86400
            hours = (remaining % 86400) // 3600
            minutes = (remaining % 3600) // 60
            seconds = remaining % 60
            
            parts = []
            if days > 0:
                parts.append(f"{days}d")
            if hours > 0 or days > 0:
                parts.append(f"{hours}h")
            if minutes > 0 or hours > 0 or days > 0:
                parts.append(f"{minutes}m")
            if show_seconds and (seconds > 0 or not parts):
                parts.append(f"{seconds}s")
                
            return f"{event_name}: {' '.join(parts)}"
            
        except Exception as e:
            logger.error(e, "Error calculating countdown")
            return f"{event_name}: Error"


class CalendarDisplayPreset(ConfigurablePreset):
    """Display calendar events and appointments."""
    
    def __init__(self):
        super().__init__("calendar_display", category="time")
        
        self._config.update({
            'data_source': {
                'type': 'function',
                'function': self._get_calendar_events,
                'cache_ttl': 300  # 5 minute cache
            },
            'style': {
                'name': 'calendar',
                'theme': 'schedule',
                'colors': {
                    'today': 'Yellow',
                    'tomorrow': 'Orange',
                    'event': 'White',
                    'time': 'Cyan',
                    'background': 'DarkBlue'
                },
                'scroll_speed': 0.045,
                'separator': ' • '
            },
            'metadata': {
                'name': 'calendar_display',
                'description': 'Upcoming calendar events',
                'tags': ['calendar', 'events', 'schedule']
            }
        })
        
        self.parameters = {
            'calendar_url': {
                'type': 'str',
                'description': 'iCal URL or calendar feed'
            },
            'days_ahead': {
                'type': 'int',
                'default': 7,
                'description': 'Days to look ahead'
            },
            'max_events': {
                'type': 'int',
                'default': 5,
                'description': 'Maximum events to show'
            }
        }
        
    def _get_calendar_events(self):
        """Get calendar events (placeholder)."""
        # In real implementation, would parse iCal feed
        # For now, return sample events
        return "Today 2pm: Team Meeting • Tomorrow 10am: Project Review • Thu: Deadline"


class PomodoroTimerPreset(ConfigurablePreset):
    """Pomodoro work/break timer."""
    
    def __init__(self):
        super().__init__("pomodoro_timer", category="productivity")
        
        # Track timer state
        self._timer_state = {
            'mode': 'work',  # work or break
            'start_time': None,
            'session_count': 0
        }
        
        self._config.update({
            'data_source': {
                'type': 'function',
                'function': self._get_pomodoro_status,
                'cache_ttl': 0
            },
            'style': {
                'name': 'pomodoro',
                'theme': 'productivity',
                'colors': {
                    'work': 'Red',
                    'break': 'Green',
                    'long_break': 'Blue',
                    'complete': 'Yellow',
                    'background': 'Black'
                },
                'scroll_speed': 0.08,
                'pulse_on_complete': True
            },
            'metadata': {
                'name': 'pomodoro_timer',
                'description': 'Pomodoro technique work/break timer',
                'tags': ['timer', 'productivity', 'pomodoro', 'work']
            }
        })
        
        self.parameters = {
            'work_minutes': {
                'type': 'int',
                'default': 25,
                'description': 'Work period duration'
            },
            'break_minutes': {
                'type': 'int',
                'default': 5,
                'description': 'Short break duration'
            },
            'long_break_minutes': {
                'type': 'int',
                'default': 15,
                'description': 'Long break duration'
            },
            'sessions_before_long': {
                'type': 'int',
                'default': 4,
                'description': 'Sessions before long break'
            }
        }
        
    def _get_pomodoro_status(self):
        """Get current pomodoro status."""
        work_min = self.get_parameter('work_minutes', 25)
        break_min = self.get_parameter('break_minutes', 5)
        long_break_min = self.get_parameter('long_break_minutes', 15)
        sessions_before_long = self.get_parameter('sessions_before_long', 4)
        
        # Initialize timer if needed
        if self._timer_state['start_time'] is None:
            self._timer_state['start_time'] = time.time()
            
        current_time = time.time()
        elapsed = int(current_time - self._timer_state['start_time'])
        
        mode = self._timer_state['mode']
        
        if mode == 'work':
            duration = work_min * 60
            remaining = duration - elapsed
            
            if remaining <= 0:
                # Work session complete
                self._timer_state['session_count'] += 1
                self._timer_state['mode'] = 'break'
                self._timer_state['start_time'] = current_time
                return "Work Complete! Take a break."
                
            minutes = remaining // 60
            seconds = remaining % 60
            return f"Work: {minutes}:{seconds:02d}"
            
        else:  # break mode
            # Determine break duration
            if self._timer_state['session_count'] % sessions_before_long == 0:
                duration = long_break_min * 60
                break_type = "Long Break"
            else:
                duration = break_min * 60
                break_type = "Break"
                
            remaining = duration - elapsed
            
            if remaining <= 0:
                # Break complete
                self._timer_state['mode'] = 'work'
                self._timer_state['start_time'] = current_time
                return "Break Over! Back to work."
                
            minutes = remaining // 60
            seconds = remaining % 60
            return f"{break_type}: {minutes}:{seconds:02d}"


# Registry of all time presets
TIME_PRESETS = {
    'digital_clock': DigitalClockPreset,
    'world_clock': WorldClockPreset,
    'countdown_timer': CountdownTimerPreset,
    'calendar_display': CalendarDisplayPreset,
    'pomodoro_timer': PomodoroTimerPreset
}


def get_time_preset(name):
    """
    Get a time preset by name.
    
    Args:
        name: Preset name
        
    Returns:
        Preset instance or None
    """
    preset_class = TIME_PRESETS.get(name)
    if preset_class:
        return preset_class()
    return None