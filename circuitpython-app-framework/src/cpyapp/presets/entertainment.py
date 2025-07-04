"""
Entertainment presets for movies, concerts, events, and gaming.

This module provides presets for displaying entertainment-related
information like movie times, concerts, TV schedules, and game scores.
"""
from .base import ConfigurablePreset
from ..utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")


class MovieTimesPreset(ConfigurablePreset):
    """Display local movie showtimes."""
    
    def __init__(self):
        super().__init__("movie_times", category="entertainment")
        
        self._config.update({
            'data_source': {
                'type': 'url',
                'url': None,  # Would need a movie API
                'parser': 'json',
                'parser_config': {
                    'format': '{title} @ {times}'
                },
                'cache_ttl': 3600  # 1 hour cache
            },
            'style': {
                'name': 'cinema',
                'theme': 'movie_theater',
                'colors': {
                    'title': 'Yellow',
                    'times': 'White',
                    'rating': 'Orange',
                    'sold_out': 'Red',
                    'background': 'DarkRed'
                },
                'scroll_speed': 0.045,
                'show_ratings': True,
                'separator': ' • '
            },
            'metadata': {
                'name': 'movie_times',
                'description': 'Local movie theater showtimes',
                'tags': ['movies', 'cinema', 'showtimes', 'entertainment']
            }
        })
        
        self.parameters = {
            'location': {
                'type': 'str',
                'required': True,
                'description': 'Zip code or city'
            },
            'theaters': {
                'type': 'list',
                'default': [],
                'description': 'Specific theaters (empty for all)'
            },
            'api_key': {
                'type': 'str',
                'description': 'Movie API key if required'
            },
            'show_only_today': {
                'type': 'bool',
                'default': True,
                'description': 'Only show today\'s showtimes'
            }
        }
        
    def get_requirements(self):
        """Get requirements for this preset."""
        return {
            'location': 'Location required for local theaters',
            'api_key': 'May require movie database API key',
            'network': 'Internet connection required'
        }


class ConcertTrackerPreset(ConfigurablePreset):
    """Track upcoming concerts and music events."""
    
    def __init__(self):
        super().__init__("concert_tracker", category="entertainment")
        
        self._config.update({
            'data_source': {
                'type': 'url',
                'url': None,  # Would use Songkick, Bandsintown, etc.
                'parser': 'json',
                'parser_config': {
                    'format': '{artist} @ {venue} - {date}'
                },
                'cache_ttl': 7200  # 2 hour cache
            },
            'style': {
                'name': 'concert',
                'theme': 'music_venue',
                'colors': {
                    'artist': 'Purple',
                    'venue': 'Cyan',
                    'date': 'Yellow',
                    'on_sale': 'Green',
                    'sold_out': 'Red',
                    'background': 'Black'
                },
                'scroll_speed': 0.04,
                'pulse_on_sale': True
            },
            'metadata': {
                'name': 'concert_tracker',
                'description': 'Upcoming concerts and live music events',
                'tags': ['concerts', 'music', 'live', 'events']
            }
        })
        
        self.parameters = {
            'location': {
                'type': 'str',
                'required': True,
                'description': 'City or metro area'
            },
            'artists': {
                'type': 'list',
                'default': [],
                'description': 'Specific artists to track'
            },
            'venues': {
                'type': 'list',
                'default': [],
                'description': 'Specific venues to monitor'
            },
            'radius_miles': {
                'type': 'int',
                'default': 50,
                'description': 'Search radius from location'
            }
        }


class EventCalendarPreset(ConfigurablePreset):
    """Display local events and activities."""
    
    def __init__(self):
        super().__init__("event_calendar", category="entertainment")
        
        self._config.update({
            'data_source': {
                'type': 'url',
                'url': None,  # Would use Eventbrite, Meetup, etc.
                'parser': 'json',
                'parser_config': {
                    'format': '{name} - {date} @ {location}'
                },
                'cache_ttl': 3600  # 1 hour cache
            },
            'style': {
                'name': 'events',
                'theme': 'community',
                'colors': {
                    'today': 'Yellow',
                    'this_week': 'Orange',
                    'free': 'Green',
                    'ticketed': 'Cyan',
                    'location': 'White',
                    'background': 'DarkBlue'
                },
                'scroll_speed': 0.045,
                'group_by_date': True
            },
            'metadata': {
                'name': 'event_calendar',
                'description': 'Local events and activities',
                'tags': ['events', 'activities', 'local', 'community']
            }
        })
        
        self.parameters = {
            'location': {
                'type': 'str',
                'required': True,
                'description': 'City or zip code'
            },
            'categories': {
                'type': 'list',
                'default': ['music', 'arts', 'food', 'family'],
                'description': 'Event categories to include'
            },
            'days_ahead': {
                'type': 'int',
                'default': 7,
                'description': 'Days to look ahead'
            },
            'free_only': {
                'type': 'bool',
                'default': False,
                'description': 'Only show free events'
            }
        }


class TVSchedulePreset(ConfigurablePreset):
    """Display TV show schedules and premieres."""
    
    def __init__(self):
        super().__init__("tv_schedule", category="entertainment")
        
        self._config.update({
            'data_source': {
                'type': 'url',
                'url': None,  # Would use TV guide API
                'parser': 'json',
                'parser_config': {
                    'format': '{time} {channel}: {show}'
                },
                'cache_ttl': 1800  # 30 minute cache
            },
            'style': {
                'name': 'tv_guide',
                'theme': 'television',
                'colors': {
                    'prime_time': 'Yellow',
                    'new_episode': 'Green',
                    'season_finale': 'Red',
                    'rerun': 'Gray',
                    'channel': 'Cyan',
                    'background': 'Black'
                },
                'scroll_speed': 0.05,
                'highlight_new': True
            },
            'metadata': {
                'name': 'tv_schedule',
                'description': 'TV show schedules and premieres',
                'tags': ['tv', 'television', 'shows', 'schedule']
            }
        })
        
        self.parameters = {
            'provider': {
                'type': 'str',
                'description': 'Cable/streaming provider'
            },
            'channels': {
                'type': 'list',
                'default': [],
                'description': 'Specific channels to show'
            },
            'shows': {
                'type': 'list',
                'default': [],
                'description': 'Specific shows to track'
            },
            'time_range': {
                'type': 'str',
                'default': 'tonight',
                'choices': ['now', 'tonight', 'tomorrow', 'week'],
                'description': 'Time range to display'
            }
        }


class GameScoresPreset(ConfigurablePreset):
    """Display gaming and esports scores."""
    
    def __init__(self):
        super().__init__("game_scores", category="entertainment")
        
        self._config.update({
            'data_source': {
                'type': 'url',
                'url': None,  # Would use esports APIs
                'parser': 'json',
                'parser_config': {
                    'format': '{game}: {team1} {score1} - {score2} {team2}'
                },
                'cache_ttl': 60  # 1 minute for live games
            },
            'style': {
                'name': 'esports',
                'theme': 'gaming',
                'colors': {
                    'team1': 'Blue',
                    'team2': 'Red',
                    'score': 'Yellow',
                    'live': 'Green',
                    'game_name': 'Purple',
                    'background': 'Black'
                },
                'scroll_speed': 0.04,
                'flash_on_score': True,
                'show_tournament': True
            },
            'metadata': {
                'name': 'game_scores',
                'description': 'Esports and gaming tournament scores',
                'tags': ['gaming', 'esports', 'scores', 'tournaments']
            }
        })
        
        self.parameters = {
            'games': {
                'type': 'list',
                'default': ['LoL', 'CS:GO', 'Valorant', 'Dota2'],
                'description': 'Games to track'
            },
            'teams': {
                'type': 'list',
                'default': [],
                'description': 'Specific teams to follow'
            },
            'tournaments': {
                'type': 'list',
                'default': [],
                'description': 'Specific tournaments'
            },
            'region': {
                'type': 'str',
                'default': 'NA',
                'choices': ['NA', 'EU', 'KR', 'CN', 'ALL'],
                'description': 'Region to focus on'
            }
        }


class StreamingTrackerPreset(ConfigurablePreset):
    """Track live streams and content creators."""
    
    def __init__(self):
        super().__init__("streaming_tracker", category="entertainment")
        
        self._config.update({
            'data_source': {
                'type': 'url',
                'url': None,  # Would use Twitch/YouTube APIs
                'parser': 'json',
                'parser_config': {
                    'format': '{streamer}: {game} - {viewers} viewers'
                },
                'cache_ttl': 120  # 2 minute cache
            },
            'style': {
                'name': 'streaming',
                'theme': 'twitch',
                'colors': {
                    'live': 'Red',
                    'streamer': 'Purple',
                    'game': 'White',
                    'viewers': 'Green',
                    'offline': 'Gray',
                    'background': 'Black'
                },
                'scroll_speed': 0.04,
                'pulse_when_live': True
            },
            'metadata': {
                'name': 'streaming_tracker',
                'description': 'Live stream status for content creators',
                'tags': ['streaming', 'twitch', 'youtube', 'live']
            }
        })
        
        self.parameters = {
            'platform': {
                'type': 'str',
                'default': 'twitch',
                'choices': ['twitch', 'youtube', 'both'],
                'description': 'Streaming platform'
            },
            'streamers': {
                'type': 'list',
                'required': True,
                'description': 'Streamers to track'
            },
            'notify_when_live': {
                'type': 'bool',
                'default': True,
                'description': 'Special alert when going live'
            }
        }


# Registry of all entertainment presets
ENTERTAINMENT_PRESETS = {
    'movie_times': MovieTimesPreset,
    'concert_tracker': ConcertTrackerPreset,
    'event_calendar': EventCalendarPreset,
    'tv_schedule': TVSchedulePreset,
    'game_scores': GameScoresPreset,
    'streaming_tracker': StreamingTrackerPreset
}


def get_entertainment_preset(name):
    """
    Get an entertainment preset by name.
    
    Args:
        name: Preset name
        
    Returns:
        Preset instance or None
    """
    preset_class = ENTERTAINMENT_PRESETS.get(name)
    if preset_class:
        return preset_class()
    return None