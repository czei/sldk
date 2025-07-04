#!/usr/bin/env python3
"""
Examples of using presets with SimpleScrollApp.

This file demonstrates various ways to use the preset system
to quickly create display applications.
"""
import sys
sys.path.insert(0, '../src')

# Note: These examples assume SimpleScrollApp is available.
# In CircuitPython, the from_preset method will be automatically added.

print("=== Preset Usage Examples ===\n")

print("1. Basic Theme Park Display:")
print("""
from cpyapp.apps import SimpleScrollApp

# Display all Disney World parks
app = SimpleScrollApp.from_preset("disney_world")
app.run()
""")

print("\n2. Theme Park with Custom Settings:")
print("""
# Only show rides with 30+ minute waits
app = SimpleScrollApp.from_preset("disney_world", 
                                 min_wait=30,
                                 update_interval=180)
app.run()
""")

print("\n3. Stock Tracker:")
print("""
# Track specific stocks (API key required)
app = SimpleScrollApp.from_preset("stock_tracker",
                                 api_key="YOUR_API_KEY",
                                 symbols=["AAPL", "TSLA", "GOOGL"],
                                 show_volume=True)
app.run()
""")

print("\n4. Weather Station:")
print("""
# Display local weather
app = SimpleScrollApp.from_preset("weather_station",
                                 location="Orlando, FL",
                                 api_key="YOUR_OPENWEATHERMAP_KEY",
                                 units="imperial")
app.run()
""")

print("\n5. Digital Clock:")
print("""
# Simple clock display
app = SimpleScrollApp.from_preset("digital_clock",
                                 format_12hr=True,
                                 show_seconds=True,
                                 show_date=True)
app.run()
""")

print("\n6. Crypto Tracker:")
print("""
# Track cryptocurrency prices
app = SimpleScrollApp.from_preset("crypto_tracker",
                                 currencies=["BTC", "ETH", "DOGE"],
                                 vs_currency="USD")
app.run()
""")

print("\n7. News Ticker:")
print("""
# Display news headlines
app = SimpleScrollApp.from_preset("news_ticker",
                                 feed_url="https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
                                 max_items=15)
app.run()
""")

print("\n8. Pomodoro Timer:")
print("""
# Productivity timer
app = SimpleScrollApp.from_preset("pomodoro_timer",
                                 work_minutes=25,
                                 break_minutes=5,
                                 long_break_minutes=15)
app.run()
""")

print("\n9. Custom Board with Preset:")
print("""
# Use preset with specific board
app = SimpleScrollApp.from_preset("universal_orlando",
                                 board="matrixportal_s3")
app.run()
""")

print("\n10. Override Style in Preset:")
print("""
# Use preset but change the style
from cpyapp.presets import get_preset_config

config = get_preset_config("disney_world")
config['style'] = 'rainbow'  # Override style

app = SimpleScrollApp(**config)
app.run()
""")

print("\n=== Listing Available Presets ===\n")

print("""
from cpyapp.presets import list_presets, list_categories

# Show all categories
for category in list_categories():
    print(f"{category['name']}: {category['description']}")

# List presets in a category
theme_park_presets = list_presets(category="theme_parks")
for preset in theme_park_presets:
    print(f"  - {preset['name']}")

# Search for presets
from cpyapp.presets import PresetFactory
results = PresetFactory.search_presets("disney")
""")

print("\n=== Creating Custom Presets ===\n")

print("""
from cpyapp.presets.base import ConfigurablePreset

class MyCustomPreset(ConfigurablePreset):
    def __init__(self):
        super().__init__("my_custom", category="custom")
        
        self._config.update({
            'data_source': {
                'type': 'url',
                'url': 'https://api.mysite.com/data.json',
                'parser': 'json_path',
                'parser_config': {
                    'path': 'message',
                    'format': '{text}'
                }
            },
            'style': {
                'name': 'custom_style',
                'scroll_speed': 0.05,
                'colors': {
                    'text': 'Cyan',
                    'background': 'Black'
                }
            }
        })

# Register and use custom preset
from cpyapp.presets.factory import PRESET_CATEGORIES
PRESET_CATEGORIES['custom'] = {
    'presets': {'my_custom': MyCustomPreset},
    'getter': lambda name: MyCustomPreset() if name == 'my_custom' else None,
    'description': 'Custom presets'
}

app = SimpleScrollApp.from_preset("my_custom")
app.run()
""")