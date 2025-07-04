# Display Presets

Presets combine data sources, styles, and board configurations into easy-to-use packages for common display scenarios.

## Quick Start

```python
from cpyapp.apps import SimpleScrollApp

# Use a preset
app = SimpleScrollApp.from_preset("disney_world")
app.run()

# Customize preset parameters
app = SimpleScrollApp.from_preset("stock_tracker", 
                                 api_key="YOUR_KEY",
                                 symbols=["AAPL", "TSLA"])
app.run()
```

## Available Presets

### Theme Parks
- **disney_world** - All Walt Disney World parks
- **magic_kingdom** - Magic Kingdom only
- **epcot** - EPCOT only
- **hollywood_studios** - Hollywood Studios only
- **animal_kingdom** - Animal Kingdom only
- **disneyland** - Disneyland Park
- **disneyland_resort** - Both Disneyland parks
- **california_adventure** - Disney California Adventure
- **universal_orlando** - Both Universal Orlando parks
- **universal_studios** - Universal Studios Florida
- **islands_of_adventure** - Islands of Adventure
- **universal_hollywood** - Universal Studios Hollywood
- **cedar_point** - Cedar Point roller coasters
- **six_flags_magic_mountain** - Six Flags Magic Mountain
- **tokyo_disney** - Tokyo Disney Resort
- **disneyland_paris** - Disneyland Paris

### Financial & Data
- **stock_tracker** - Real-time stock prices
- **crypto_tracker** - Cryptocurrency prices
- **weather_station** - Local weather conditions
- **news_ticker** - RSS news headlines
- **sports_scores** - Live sports scores
- **transit_tracker** - Public transit arrivals

### Time & Clocks
- **digital_clock** - Simple digital clock
- **world_clock** - Multiple time zones
- **countdown_timer** - Event countdown
- **calendar_display** - Upcoming events
- **pomodoro_timer** - Work/break timer

### Entertainment
- **movie_times** - Local movie showtimes
- **concert_tracker** - Upcoming concerts
- **event_calendar** - Local events
- **tv_schedule** - TV show schedules
- **game_scores** - Esports scores
- **streaming_tracker** - Live stream status

## Listing Presets

```python
from cpyapp.presets import list_presets, list_categories

# List all presets
for preset in list_presets():
    print(f"{preset['name']}: {preset['description']}")

# List by category
for preset in list_presets(category="theme_parks"):
    print(preset['name'])

# List categories
for category in list_categories():
    print(f"{category['name']}: {category['description']}")
```

## Creating Custom Presets

Extend `BasePreset` or `ConfigurablePreset`:

```python
from cpyapp.presets.base import ConfigurablePreset

class MyCustomPreset(ConfigurablePreset):
    def __init__(self):
        super().__init__("my_custom", category="custom")
        
        self._config.update({
            'data_source': {
                'type': 'url',
                'url': 'https://api.example.com/data'
            },
            'style': {
                'name': 'custom',
                'scroll_speed': 0.05
            }
        })
        
        self.parameters = {
            'api_key': {
                'type': 'str',
                'required': True,
                'description': 'API key'
            }
        }
```

## Preset Configuration

Each preset can be customized with parameters:

```python
# Get preset config
from cpyapp.presets import get_preset_config

config = get_preset_config("disney_world", {
    'min_wait': 30,
    'show_closed': False
})

# Validate preset
from cpyapp.presets import validate_preset

is_valid, error = validate_preset("stock_tracker", {
    'api_key': 'YOUR_KEY'
})
```

## Requirements

Some presets have specific requirements:

```python
from cpyapp.presets import create_preset

preset = create_preset("weather_station")
print(preset.get_requirements())
# Output: {'api_key': 'OpenWeatherMap API key required', ...}
```

## Configuration Files

Preset configurations can also be stored as JSON files in the `configs/` directory. These files define the complete preset configuration including data source, style, parameters, and documentation.

See `configs/disney_world.json` and `configs/stock_tracker.json` for examples.