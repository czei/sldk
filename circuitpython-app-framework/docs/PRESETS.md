# Presets Guide

Ready-to-use application templates for common LED matrix displays.

## Overview

Presets are pre-configured applications that handle:
- Data fetching
- Formatting
- Styling
- Update intervals
- Error handling

Just add your API keys and run!

## Built-in Presets

### Clock Preset

Display current time with various formats.

```python
from cpyapp import SimpleScrollApp
from cpyapp.presets import ClockPreset

# Simple clock
clock = ClockPreset()
app = SimpleScrollApp(preset=clock)
app.run()

# Customized clock
clock = ClockPreset(
    format_24h=True,        # 24-hour format
    show_seconds=True,      # Include seconds
    show_date=False,        # Don't show date
    timezone="US/Eastern",  # Specific timezone
    date_format="%m/%d"     # MM/DD format
)

# With custom styling
app = SimpleScrollApp(
    preset=clock,
    styles={
        "text_color": (0, 255, 255),  # Cyan
        "brightness": 0.5
    }
)
```

**Options:**
- `format_24h`: Use 24-hour format (default: False)
- `show_seconds`: Display seconds (default: True)
- `show_date`: Include date (default: False)
- `timezone`: Timezone name or None for local (default: None)
- `date_format`: strftime format for date (default: "%Y-%m-%d")

### Weather Preset

Display weather conditions from OpenWeatherMap.

```python
from cpyapp.presets import WeatherPreset

# Basic weather
weather = WeatherPreset(
    api_key="your_openweathermap_api_key",
    city="New York",
    units="imperial"  # or "metric"
)
app = SimpleScrollApp(preset=weather)
app.run()

# Multiple cities
weather = WeatherPreset(
    api_key="your_api_key",
    cities=["New York", "London", "Tokyo"],
    units="metric",
    show_forecast=True,     # Include forecast
    forecast_days=3,        # 3-day forecast
    update_interval=600     # Update every 10 minutes
)

# Detailed format
weather = WeatherPreset(
    api_key="your_api_key",
    city="Orlando",
    format="{city}: {temp}°{unit} {description} H:{high}° L:{low}° Humidity:{humidity}%"
)
```

**Options:**
- `api_key`: OpenWeatherMap API key (required)
- `city` or `cities`: Single city or list of cities
- `units`: "imperial" (F) or "metric" (C)
- `show_forecast`: Include forecast data
- `forecast_days`: Number of forecast days (1-5)
- `format`: Custom format string
- `update_interval`: Seconds between updates

### Stock Ticker Preset

Display stock prices and changes.

```python
from cpyapp.presets import StockTickerPreset

# Single stock
stock = StockTickerPreset(
    api_key="your_alphavantage_api_key",
    symbol="AAPL"
)

# Multiple stocks
stocks = StockTickerPreset(
    api_key="your_api_key",
    symbols=["AAPL", "GOOGL", "MSFT", "AMZN"],
    show_change=True,       # Show price change
    show_percent=True,      # Show percent change
    show_volume=False,      # Don't show volume
    update_interval=60      # Update every minute
)

# Custom format
stocks = StockTickerPreset(
    api_key="your_api_key",
    symbols=["DIS", "NFLX"],
    format="{symbol}: ${price} ({change_percent}%)",
    positive_color=(0, 255, 0),   # Green for gains
    negative_color=(255, 0, 0),   # Red for losses
    unchanged_color=(255, 255, 255)  # White for unchanged
)
```

**Options:**
- `api_key`: API key for stock data service
- `symbol` or `symbols`: Stock ticker(s) to display
- `show_change`: Display price change
- `show_percent`: Display percent change
- `show_volume`: Display trading volume
- `format`: Custom format string
- `positive_color`: Color for gains
- `negative_color`: Color for losses

### News Ticker Preset

Display news headlines from various sources.

```python
from cpyapp.presets import NewsTickerPreset

# Basic news
news = NewsTickerPreset(
    api_key="your_newsapi_key",
    source="bbc-news"
)

# Category-based news
news = NewsTickerPreset(
    api_key="your_api_key",
    category="technology",   # Category filter
    country="us",           # Country code
    max_headlines=10,       # Number of headlines
    include_source=True     # Show source name
)

# Multiple sources
news = NewsTickerPreset(
    api_key="your_api_key",
    sources=["cnn", "bbc-news", "reuters"],
    shuffle=True,           # Randomize order
    update_interval=1800    # Update every 30 minutes
)
```

**Options:**
- `api_key`: NewsAPI key (required)
- `source` or `sources`: News source(s)
- `category`: Filter by category
- `country`: Country code for local news
- `max_headlines`: Maximum headlines to show
- `include_source`: Show source in display
- `shuffle`: Randomize headline order

### Countdown Preset

Count down to important dates and events.

```python
from cpyapp.presets import CountdownPreset

# Countdown to specific date
countdown = CountdownPreset(
    target_date="2024-12-25 00:00:00",
    label="Christmas",
    show_days=True,
    show_hours=True,
    show_minutes=True,
    show_seconds=True
)

# Multiple events
from datetime import datetime, timedelta

events = [
    {
        "date": "2024-07-04 00:00:00",
        "label": "Independence Day"
    },
    {
        "date": datetime.now() + timedelta(days=30),
        "label": "30 Days From Now"
    }
]

countdown = CountdownPreset(
    events=events,
    format="{label}: {days}d {hours}h {minutes}m",
    completed_message="{label} is here!"
)
```

**Options:**
- `target_date`: Target datetime string or datetime object
- `label`: Event name
- `events`: List of events to cycle through
- `show_days/hours/minutes/seconds`: Which units to display
- `format`: Custom format string
- `completed_message`: Message when countdown reaches zero

### System Monitor Preset

Display device statistics and health.

```python
from cpyapp.presets import SystemMonitorPreset

# Basic monitoring
monitor = SystemMonitorPreset()

# Detailed monitoring
monitor = SystemMonitorPreset(
    show_memory=True,        # RAM usage
    show_temperature=True,   # CPU temperature
    show_voltage=True,       # Power info
    show_frequency=True,     # CPU frequency
    show_uptime=True,       # System uptime
    show_wifi=True,         # WiFi status
    show_ip=True,           # IP address
    rotate_stats=True,      # Cycle through stats
    rotation_interval=5     # 5 seconds per stat
)

# Custom format
monitor = SystemMonitorPreset(
    format="RAM: {memory_percent}% | CPU: {temperature}°C | Up: {uptime}",
    alert_temperature=70,    # Alert if temp > 70°C
    alert_memory=80         # Alert if RAM > 80%
)
```

**Options:**
- `show_*`: Which statistics to display
- `rotate_stats`: Cycle through different stats
- `rotation_interval`: Seconds per statistic
- `alert_temperature`: Temperature warning threshold
- `alert_memory`: Memory warning threshold

### Transit Tracker Preset

Display public transportation arrival times.

```python
from cpyapp.presets import TransitTrackerPreset

# Bus/train arrivals
transit = TransitTrackerPreset(
    api_key="your_transit_api_key",
    stop_id="12345",
    route_filter=["Red Line", "Blue Line"],
    max_arrivals=3,
    show_destination=True
)

# Multiple stops
transit = TransitTrackerPreset(
    api_key="your_api_key",
    stops=[
        {"id": "12345", "name": "Main St"},
        {"id": "67890", "name": "Park Ave"}
    ],
    format="{stop}: {route} in {minutes}min"
)
```

## Creating Custom Presets

### Basic Custom Preset

```python
class MyPreset:
    """Custom preset for my application."""
    
    def __init__(self, param1="default", param2=None):
        self.param1 = param1
        self.param2 = param2 or "fallback"
        self.update_count = 0
    
    def get_text(self):
        """Return the text to display."""
        self.update_count += 1
        return f"{self.param1} - {self.param2} (Update #{self.update_count})"
    
    def get_update_interval(self):
        """How often to update in seconds."""
        return 5
    
    def get_styles(self):
        """Optional: Return custom styles."""
        return {
            "text_color": (255, 255, 0),  # Yellow
            "scroll_speed": 0.03
        }

# Use it
my_preset = MyPreset(param1="Hello", param2="World")
app = SimpleScrollApp(preset=my_preset)
app.run()
```

### Advanced Preset with Data Source

```python
from cpyapp.data import URLDataSource
import time

class CryptoTickerPreset:
    """Display cryptocurrency prices."""
    
    def __init__(self, coins=["bitcoin", "ethereum"], currency="usd"):
        self.coins = coins
        self.currency = currency
        self.data_source = URLDataSource(
            url=f"https://api.coingecko.com/api/v3/simple/price"
                f"?ids={','.join(coins)}&vs_currencies={currency}",
            cache_duration=60
        )
        self.last_prices = {}
    
    def get_text(self):
        """Format crypto prices."""
        data = self.data_source.get()
        if not data:
            return "Loading crypto prices..."
        
        messages = []
        for coin in self.coins:
            if coin in data:
                price = data[coin][self.currency]
                symbol = coin[:3].upper()
                messages.append(f"{symbol}: ${price:,.2f}")
        
        return " | ".join(messages)
    
    def get_styles(self):
        """Dynamic styling based on price changes."""
        data = self.data_source.get()
        if not data:
            return {"text_color": (255, 255, 255)}
        
        # Simple logic: green if any price increased
        for coin in self.coins:
            if coin in data:
                current = data[coin][self.currency]
                last = self.last_prices.get(coin, current)
                if current > last:
                    self.last_prices[coin] = current
                    return {"text_color": (0, 255, 0)}  # Green
                elif current < last:
                    self.last_prices[coin] = current
                    return {"text_color": (255, 0, 0)}  # Red
        
        return {"text_color": (255, 255, 255)}  # White
    
    def get_update_interval(self):
        return 30  # Update every 30 seconds

# Use it
crypto = CryptoTickerPreset(
    coins=["bitcoin", "ethereum", "dogecoin"],
    currency="usd"
)
app = SimpleScrollApp(preset=crypto)
```

### Preset with Multiple Modes

```python
class MultiModePreset:
    """Preset that cycles through different display modes."""
    
    def __init__(self):
        self.modes = [
            self.show_time,
            self.show_date,
            self.show_weather,
            self.show_message
        ]
        self.current_mode = 0
        self.last_switch = time.monotonic()
        self.mode_duration = 5  # 5 seconds per mode
    
    def get_text(self):
        # Switch modes periodically
        if time.monotonic() - self.last_switch > self.mode_duration:
            self.current_mode = (self.current_mode + 1) % len(self.modes)
            self.last_switch = time.monotonic()
        
        # Call current mode function
        return self.modes[self.current_mode]()
    
    def show_time(self):
        return time.strftime("%H:%M:%S")
    
    def show_date(self):
        return time.strftime("%Y-%m-%d")
    
    def show_weather(self):
        # Simplified - would normally fetch real data
        return "Weather: 72°F Sunny"
    
    def show_message(self):
        return "Hello CircuitPython!"
    
    def get_update_interval(self):
        return 1  # Update every second for clock
```

## Combining Presets

### Rotating Multiple Presets

```python
from cpyapp.presets import MultiPreset, ClockPreset, WeatherPreset

# Rotate between different presets
multi = MultiPreset(
    presets=[
        ClockPreset(show_date=True),
        WeatherPreset(api_key="key", city="NYC"),
        SystemMonitorPreset()
    ],
    rotation_interval=10,  # 10 seconds each
    transition="fade"      # Fade between presets
)

app = SimpleScrollApp(preset=multi)
```

### Conditional Presets

```python
class ConditionalPreset:
    """Show different presets based on conditions."""
    
    def __init__(self):
        self.clock = ClockPreset()
        self.alert = AlertPreset()
        self.weather = WeatherPreset(api_key="key")
    
    def get_active_preset(self):
        """Choose preset based on conditions."""
        hour = time.localtime().tm_hour
        
        # Show alerts if any exist
        if self.has_alerts():
            return self.alert
        
        # Show weather in morning (6-9 AM)
        elif 6 <= hour < 9:
            return self.weather
        
        # Otherwise show clock
        else:
            return self.clock
    
    def get_text(self):
        preset = self.get_active_preset()
        return preset.get_text()
    
    def get_styles(self):
        preset = self.get_active_preset()
        return preset.get_styles() if hasattr(preset, 'get_styles') else {}
```

## Preset Configuration

### Loading from File

```python
import json

class ConfigurablePreset:
    """Preset that loads settings from file."""
    
    def __init__(self, config_file="preset_config.json"):
        self.load_config(config_file)
    
    def load_config(self, filename):
        try:
            with open(filename, 'r') as f:
                self.config = json.load(f)
        except:
            self.config = self.get_default_config()
    
    def get_default_config(self):
        return {
            "message": "Default Message",
            "color": [255, 255, 255],
            "speed": 0.04,
            "update_interval": 60
        }
    
    def get_text(self):
        return self.config.get("message", "No message")
    
    def get_styles(self):
        return {
            "text_color": tuple(self.config.get("color", [255, 255, 255])),
            "scroll_speed": self.config.get("speed", 0.04)
        }
```

### Environment-Based Configuration

```python
import os

class EnvironmentPreset:
    """Preset configured via environment variables."""
    
    def __init__(self):
        self.api_key = os.environ.get("WEATHER_API_KEY")
        self.city = os.environ.get("WEATHER_CITY", "London")
        self.units = os.environ.get("WEATHER_UNITS", "metric")
    
    def get_text(self):
        if not self.api_key:
            return "Set WEATHER_API_KEY environment variable"
        
        # Fetch and format weather...
        return f"Weather for {self.city}"
```

## Best Practices

### 1. Handle Missing Configuration

```python
class RobustPreset:
    def __init__(self, required_param=None):
        if not required_param:
            raise ValueError("required_param is required")
        
        self.param = required_param
        self.optional = os.environ.get("OPTIONAL_PARAM", "default")
```

### 2. Provide Sensible Defaults

```python
class DefaultsPreset:
    def __init__(self, 
                 update_interval=60,
                 cache_duration=300,
                 retry_count=3,
                 timeout=10):
        self.update_interval = update_interval
        self.cache_duration = cache_duration
        self.retry_count = retry_count
        self.timeout = timeout
```

### 3. Document Configuration

```python
class DocumentedPreset:
    """
    Display weather information.
    
    Required configuration:
    - api_key: OpenWeatherMap API key
    - city: City name (e.g., "New York")
    
    Optional configuration:
    - units: "imperial" or "metric" (default: "metric")
    - format: Display format string (default: "{city}: {temp}°{unit}")
    - update_interval: Seconds between updates (default: 600)
    
    Example:
        preset = DocumentedPreset(
            api_key="your_key",
            city="London",
            units="metric"
        )
    """
```

## Troubleshooting Presets

### API Key Issues

```python
# Store API keys in secrets.py
try:
    from secrets import secrets
    api_key = secrets.get("weather_api_key")
except ImportError:
    print("Create secrets.py with your API keys")
    api_key = None

if not api_key:
    # Use demo mode
    preset = WeatherPreset(demo_mode=True)
```

### Data Fetching Failures

```python
class FallbackPreset:
    def get_text(self):
        try:
            return self.fetch_live_data()
        except NetworkError:
            return self.get_cached_data()
        except Exception:
            return "Data temporarily unavailable"
```

### Update Timing

```python
class SmartUpdatePreset:
    def get_update_interval(self):
        """Adjust update frequency based on time of day."""
        hour = time.localtime().tm_hour
        
        if 0 <= hour < 6:  # Night
            return 3600  # Update hourly
        elif 6 <= hour < 22:  # Day
            return 300   # Update every 5 minutes
        else:  # Evening
            return 600   # Update every 10 minutes
```

## Next Steps

- Browse [example presets](../examples/presets/) for more ideas
- Learn about [creating data sources](DATA_SOURCES.md)
- Explore [styling options](STYLES.md) to customize preset appearance
- See [API Reference](API_REFERENCE.md#presets) for all preset options