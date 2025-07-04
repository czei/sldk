"""
Display presets for common use cases.

This module provides pre-configured combinations of data sources,
styles, and board configurations for common display scenarios.

Example usage:
    # Use a theme park preset
    from cpyapp.apps import SimpleScrollApp
    app = SimpleScrollApp.from_preset("disney_world")
    app.run()
    
    # Use with customization
    app = SimpleScrollApp.from_preset("stock_tracker", 
                                     symbols=['AAPL', 'TSLA'],
                                     api_key="your_key")
    app.run()
    
    # List available presets
    from cpyapp.presets import list_presets
    for preset in list_presets():
        print(f"{preset['name']}: {preset['description']}")
"""

# Import main components
from .base import BasePreset, ConfigurablePreset
from .factory import (
    PresetFactory,
    create_preset,
    list_presets,
    list_categories,
    get_preset_config,
    validate_preset,
    add_from_preset_to_app
)

# Import specific preset categories
from .theme_parks import (
    ThemeParkPreset,
    DisneyWorldPreset,
    MagicKingdomPreset,
    EpcotPreset,
    HollywoodStudiosPreset,
    AnimalKingdomPreset,
    DisneylandPreset,
    DisneylandParkPreset,
    CaliforniaAdventurePreset,
    UniversalOrlandoPreset,
    UniversalStudiosPreset,
    IslandsOfAdventurePreset,
    UniversalHollywoodPreset,
    CedarPointPreset
)

from .displays import (
    StockTrackerPreset,
    CryptoTrackerPreset,
    WeatherStationPreset,
    NewsTickerPreset,
    SportsScoresPreset,
    TransitTrackerPreset
)

from .time import (
    DigitalClockPreset,
    WorldClockPreset,
    CountdownTimerPreset,
    CalendarDisplayPreset,
    PomodoroTimerPreset
)

from .entertainment import (
    MovieTimesPreset,
    ConcertTrackerPreset,
    EventCalendarPreset,
    TVSchedulePreset,
    GameScoresPreset,
    StreamingTrackerPreset
)

# Auto-register from_preset method
add_from_preset_to_app()

# Define public API
__all__ = [
    # Base classes
    'BasePreset',
    'ConfigurablePreset',
    
    # Factory and functions
    'PresetFactory',
    'create_preset',
    'list_presets',
    'list_categories',
    'get_preset_config',
    'validate_preset',
    
    # Theme park presets
    'ThemeParkPreset',
    'DisneyWorldPreset',
    'MagicKingdomPreset',
    'EpcotPreset',
    'HollywoodStudiosPreset',
    'AnimalKingdomPreset',
    'DisneylandPreset',
    'DisneylandParkPreset',
    'CaliforniaAdventurePreset',
    'UniversalOrlandoPreset',
    'UniversalStudiosPreset',
    'IslandsOfAdventurePreset',
    'UniversalHollywoodPreset',
    'CedarPointPreset',
    
    # Display presets
    'StockTrackerPreset',
    'CryptoTrackerPreset',
    'WeatherStationPreset',
    'NewsTickerPreset',
    'SportsScoresPreset',
    'TransitTrackerPreset',
    
    # Time presets
    'DigitalClockPreset',
    'WorldClockPreset',
    'CountdownTimerPreset',
    'CalendarDisplayPreset',
    'PomodoroTimerPreset',
    
    # Entertainment presets
    'MovieTimesPreset',
    'ConcertTrackerPreset',
    'EventCalendarPreset',
    'TVSchedulePreset',
    'GameScoresPreset',
    'StreamingTrackerPreset'
]