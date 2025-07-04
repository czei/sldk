"""
Theme Park presets for popular theme parks and attractions.

This module provides presets for displaying wait times from various
theme parks using the queue-times.com API.
"""
from .base import BasePreset, ConfigurablePreset
from ..utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")


class ThemeParkPreset(ConfigurablePreset):
    """Base class for theme park presets."""
    
    def __init__(self, name, park_ids, description=""):
        """
        Initialize theme park preset.
        
        Args:
            name: Preset name
            park_ids: Single park ID or list of park IDs
            description: Preset description
        """
        super().__init__(name, category="theme_parks")
        
        # Convert single ID to list
        if isinstance(park_ids, int):
            park_ids = [park_ids]
            
        self.park_ids = park_ids
        
        # Update configuration
        self._config.update({
            'data_source': {
                'type': 'theme_park',
                'park_ids': park_ids,
                'min_wait': 0,  # Show all attractions
                'cache_ttl': 300  # 5 minute cache
            },
            'style': {
                'name': 'theme_park',
                'scroll_speed': 0.04,
                'colors': {
                    'low_wait': 'Green',      # 0-15 min
                    'medium_wait': 'Yellow',  # 16-45 min
                    'high_wait': 'Orange',    # 46-90 min
                    'very_high_wait': 'Red'   # 90+ min
                }
            },
            'board': 'auto',
            'metadata': {
                'name': name,
                'category': 'theme_parks',
                'description': description,
                'tags': ['theme_park', 'wait_times', 'attractions']
            }
        })
        
        # Parameters for customization
        self.parameters = {
            'min_wait': {
                'type': 'int',
                'default': 0,
                'description': 'Minimum wait time to display (minutes)'
            },
            'update_interval': {
                'type': 'int', 
                'default': 300,
                'description': 'How often to update data (seconds)'
            },
            'show_closed': {
                'type': 'bool',
                'default': False,
                'description': 'Show closed attractions'
            }
        }
        
    def apply_parameters(self, config):
        """Apply parameter values to configuration."""
        # Apply min_wait parameter
        min_wait = self.get_parameter('min_wait', 0)
        config['data_source']['min_wait'] = min_wait
        
        # Apply update interval
        update_interval = self.get_parameter('update_interval', 300)
        config['data_source']['cache_ttl'] = update_interval
        
        # Apply show_closed
        show_closed = self.get_parameter('show_closed', False)
        config['data_source']['show_closed'] = show_closed
        
        return config


# Disney World Presets
class DisneyWorldPreset(ThemeParkPreset):
    """All Disney World parks combined."""
    
    def __init__(self):
        super().__init__(
            name="disney_world",
            park_ids=[6, 5, 7, 8],  # MK, EPCOT, HS, AK
            description="All Walt Disney World parks - Magic Kingdom, EPCOT, Hollywood Studios, Animal Kingdom"
        )
        
        # Disney-specific styling
        self._config['style'].update({
            'theme': 'disney',
            'colors': {
                'primary': 'Blue',
                'secondary': 'Yellow',
                'accent': 'Red'
            }
        })


class MagicKingdomPreset(ThemeParkPreset):
    """Magic Kingdom park."""
    
    def __init__(self):
        super().__init__(
            name="magic_kingdom",
            park_ids=6,
            description="Magic Kingdom at Walt Disney World"
        )


class EpcotPreset(ThemeParkPreset):
    """EPCOT park."""
    
    def __init__(self):
        super().__init__(
            name="epcot",
            park_ids=5,
            description="EPCOT at Walt Disney World"
        )


class HollywoodStudiosPreset(ThemeParkPreset):
    """Hollywood Studios park."""
    
    def __init__(self):
        super().__init__(
            name="hollywood_studios", 
            park_ids=7,
            description="Disney's Hollywood Studios at Walt Disney World"
        )


class AnimalKingdomPreset(ThemeParkPreset):
    """Animal Kingdom park."""
    
    def __init__(self):
        super().__init__(
            name="animal_kingdom",
            park_ids=8,
            description="Disney's Animal Kingdom at Walt Disney World"
        )


# Disneyland Presets
class DisneylandPreset(ThemeParkPreset):
    """Both Disneyland Resort parks."""
    
    def __init__(self):
        super().__init__(
            name="disneyland_resort",
            park_ids=[16, 17],  # DL, DCA
            description="Disneyland and Disney California Adventure"
        )
        
        self._config['style'].update({
            'theme': 'disney_classic',
            'colors': {
                'primary': 'Pink',
                'secondary': 'Purple', 
                'accent': 'Gold'
            }
        })


class DisneylandParkPreset(ThemeParkPreset):
    """Disneyland park only."""
    
    def __init__(self):
        super().__init__(
            name="disneyland",
            park_ids=16,
            description="Disneyland Park in Anaheim, California"
        )


class CaliforniaAdventurePreset(ThemeParkPreset):
    """Disney California Adventure."""
    
    def __init__(self):
        super().__init__(
            name="california_adventure",
            park_ids=17,
            description="Disney California Adventure Park"
        )


# Universal Presets
class UniversalOrlandoPreset(ThemeParkPreset):
    """Both Universal Orlando parks."""
    
    def __init__(self):
        super().__init__(
            name="universal_orlando",
            park_ids=[9, 10],  # IoA, Studios
            description="Universal Studios Florida and Islands of Adventure"
        )
        
        self._config['style'].update({
            'theme': 'universal',
            'colors': {
                'primary': 'DarkBlue',
                'secondary': 'Orange',
                'accent': 'White'
            }
        })


class UniversalStudiosPreset(ThemeParkPreset):
    """Universal Studios Florida."""
    
    def __init__(self):
        super().__init__(
            name="universal_studios",
            park_ids=10,
            description="Universal Studios Florida"
        )


class IslandsOfAdventurePreset(ThemeParkPreset):
    """Islands of Adventure."""
    
    def __init__(self):
        super().__init__(
            name="islands_of_adventure",
            park_ids=9,
            description="Universal's Islands of Adventure"
        )


class UniversalHollywoodPreset(ThemeParkPreset):
    """Universal Studios Hollywood."""
    
    def __init__(self):
        super().__init__(
            name="universal_hollywood",
            park_ids=13,
            description="Universal Studios Hollywood"
        )


# Six Flags Presets
class SixFlagsPreset(ConfigurablePreset):
    """Base class for Six Flags parks."""
    
    def __init__(self, name, park_id, park_name):
        super().__init__(name, category="theme_parks")
        
        self._config.update({
            'data_source': {
                'type': 'theme_park',
                'park_ids': [park_id],
                'min_wait': 0,
                'cache_ttl': 300
            },
            'style': {
                'name': 'six_flags',
                'theme': 'thrill',
                'colors': {
                    'primary': 'Red',
                    'secondary': 'Blue',
                    'accent': 'White'
                },
                'scroll_speed': 0.03  # Faster for thrill seekers
            },
            'metadata': {
                'name': name,
                'description': f"Six Flags {park_name}",
                'tags': ['six_flags', 'thrill_rides', 'coasters']
            }
        })


class SixFlagsMagicMountainPreset(SixFlagsPreset):
    """Six Flags Magic Mountain."""
    
    def __init__(self):
        super().__init__(
            name="six_flags_magic_mountain",
            park_id=32,
            park_name="Magic Mountain - Thrill Capital of the World"
        )


class SixFlagsGreatAdventurePreset(SixFlagsPreset):
    """Six Flags Great Adventure."""
    
    def __init__(self):
        super().__init__(
            name="six_flags_great_adventure",
            park_id=33,
            park_name="Great Adventure - New Jersey"
        )


# Cedar Fair Parks
class CedarPointPreset(ThemeParkPreset):
    """Cedar Point - America's Roller Coast."""
    
    def __init__(self):
        super().__init__(
            name="cedar_point",
            park_ids=50,
            description="Cedar Point - The Roller Coaster Capital of the World"
        )
        
        self._config['style'].update({
            'theme': 'coaster',
            'colors': {
                'primary': 'Blue',
                'secondary': 'Red',
                'accent': 'Yellow',
                'background': 'DarkBlue'
            },
            'scroll_speed': 0.025  # Even faster for coaster enthusiasts
        })


class KingsIslandPreset(ThemeParkPreset):
    """Kings Island."""
    
    def __init__(self):
        super().__init__(
            name="kings_island",
            park_ids=51,
            description="Kings Island - Cincinnati, Ohio"
        )


# International Parks
class TokyoDisneylandPreset(ThemeParkPreset):
    """Tokyo Disney Resort."""
    
    def __init__(self):
        super().__init__(
            name="tokyo_disney",
            park_ids=[179, 180],  # TDL, TDS
            description="Tokyo Disneyland and Tokyo DisneySea"
        )
        
        self._config['style'].update({
            'theme': 'tokyo_disney',
            'colors': {
                'primary': 'Pink',
                'secondary': 'Blue',
                'accent': 'Gold'
            }
        })


class DisneylandParisPreset(ThemeParkPreset):
    """Disneyland Paris Resort."""
    
    def __init__(self):
        super().__init__(
            name="disneyland_paris",
            park_ids=[4, 3],  # DLP, Walt Disney Studios
            description="Disneyland Paris and Walt Disney Studios Park"
        )


# Registry of all theme park presets
THEME_PARK_PRESETS = {
    # Disney World
    'disney_world': DisneyWorldPreset,
    'magic_kingdom': MagicKingdomPreset,
    'epcot': EpcotPreset,
    'hollywood_studios': HollywoodStudiosPreset,
    'animal_kingdom': AnimalKingdomPreset,
    
    # Disneyland
    'disneyland': DisneylandParkPreset,
    'disneyland_resort': DisneylandPreset,
    'california_adventure': CaliforniaAdventurePreset,
    
    # Universal
    'universal_orlando': UniversalOrlandoPreset,
    'universal_studios': UniversalStudiosPreset,
    'islands_of_adventure': IslandsOfAdventurePreset,
    'universal_hollywood': UniversalHollywoodPreset,
    
    # Six Flags
    'six_flags_magic_mountain': SixFlagsMagicMountainPreset,
    'six_flags_great_adventure': SixFlagsGreatAdventurePreset,
    
    # Cedar Fair
    'cedar_point': CedarPointPreset,
    'kings_island': KingsIslandPreset,
    
    # International
    'tokyo_disney': TokyoDisneylandPreset,
    'disneyland_paris': DisneylandParisPreset
}


def get_theme_park_preset(name):
    """
    Get a theme park preset by name.
    
    Args:
        name: Preset name
        
    Returns:
        Preset instance or None
    """
    preset_class = THEME_PARK_PRESETS.get(name)
    if preset_class:
        return preset_class()
    return None