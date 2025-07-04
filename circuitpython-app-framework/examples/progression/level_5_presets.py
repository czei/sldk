"""Level 5: Using Presets - Built-in Application Templates

This example shows how to use the framework's built-in presets
for common display patterns.

What you'll learn:
- Available preset applications
- How to customize presets
- Creating your own preset patterns
- Combining multiple presets
"""

from cpyapp import SimpleScrollApp
from cpyapp.presets import (
    ClockPreset,
    WeatherPreset,
    StockTickerPreset,
    NewsTickerPreset,
    CountdownPreset,
    SystemMonitorPreset
)

# Example 1: Simple Clock
# The most basic preset - just shows time
clock = ClockPreset(
    format_24h=False,  # Use 12-hour format
    show_seconds=True,  # Include seconds
    show_date=False  # Just time, no date
)
clock_app = SimpleScrollApp(preset=clock)

# Example 2: Weather Display with Configuration
weather = WeatherPreset(
    api_key="your_openweather_api_key",
    city="Orlando",
    units="imperial",  # or "metric"
    show_forecast=False  # Just current weather
)
weather_app = SimpleScrollApp(preset=weather)

# Example 3: Stock Ticker
stocks = StockTickerPreset(
    symbols=["DIS", "AAPL", "GOOGL"],
    api_key="your_api_key",
    show_change=True,  # Show price change
    show_percent=True  # Show percent change
)
stock_app = SimpleScrollApp(preset=stocks)

# Example 4: News Headlines
news = NewsTickerPreset(
    source="bbc-news",  # News source
    api_key="your_newsapi_key",
    category="technology",  # Filter by category
    max_headlines=5  # Number of headlines to cycle
)
news_app = SimpleScrollApp(preset=news)

# Example 5: Countdown Timer
# Great for events or deadlines
import time

# Countdown to New Year
countdown = CountdownPreset(
    target_date="2024-01-01 00:00:00",
    label="New Year",
    show_days=True,
    show_hours=True,
    show_minutes=True,
    show_seconds=True
)
countdown_app = SimpleScrollApp(preset=countdown)

# Example 6: System Monitor
# Shows device statistics
monitor = SystemMonitorPreset(
    show_memory=True,
    show_temperature=True,
    show_voltage=True,
    show_frequency=True
)
monitor_app = SimpleScrollApp(preset=monitor)

# Example 7: Combining Multiple Presets
# Create a rotating display with multiple data sources
from cpyapp.presets import MultiPreset

multi = MultiPreset(
    presets=[
        ClockPreset(show_date=True),
        WeatherPreset(city="Orlando"),
        SystemMonitorPreset()
    ],
    rotation_interval=10  # Switch every 10 seconds
)
multi_app = SimpleScrollApp(preset=multi)

# Example 8: Customizing Preset Styles
# You can override the default styling of any preset
stylish_clock = SimpleScrollApp(
    preset=ClockPreset(),
    styles={
        "text_color": (0, 255, 255),  # Cyan
        "brightness": 0.5,
        "scroll_speed": 0  # Don't scroll (static display)
    }
)

# Example 9: Creating Your Own Preset
class CustomPreset:
    """Example of creating a custom preset."""
    
    def __init__(self, name="User"):
        self.name = name
        self.start_time = time.monotonic()
    
    def get_text(self):
        """Return the text to display."""
        uptime = int(time.monotonic() - self.start_time)
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        seconds = uptime % 60
        return f"Hello {self.name}! Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def get_update_interval(self):
        """How often to update."""
        return 1  # Update every second
    
    def get_styles(self):
        """Optional: Return custom styles."""
        # Rainbow effect based on time
        hue = (time.monotonic() * 30) % 360
        # Simple HSV to RGB conversion
        r = int(255 * (1 + math.sin(math.radians(hue))) / 2)
        g = int(255 * (1 + math.sin(math.radians(hue + 120))) / 2)
        b = int(255 * (1 + math.sin(math.radians(hue + 240))) / 2)
        
        return {
            "text_color": (r, g, b),
            "brightness": 0.3
        }

custom = CustomPreset(name="Developer")
custom_app = SimpleScrollApp(preset=custom)

# Run the multi-preset app
multi_app.run()