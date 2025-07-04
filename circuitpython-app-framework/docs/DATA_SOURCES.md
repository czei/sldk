# Data Sources Guide

Learn how to fetch and display data from various sources in your LED matrix applications.

## Overview

Data sources provide a unified way to get content for your display:

- **Static text**: Simple strings
- **Dynamic functions**: Python functions that return text
- **URLs**: Fetch data from web APIs
- **Files**: Read from local storage
- **Sensors**: Read from hardware sensors
- **Custom sources**: Create your own

## Built-in Data Sources

### Static Text

The simplest data source - text that never changes:

```python
from cpyapp import SimpleScrollApp

# Direct string
app = SimpleScrollApp("Hello World!")

# Or using StaticDataSource explicitly
from cpyapp.data import StaticDataSource
source = StaticDataSource("Hello World!")
app = SimpleScrollApp(text_source=source)
```

### Function Data Source

Use any Python function that returns a string:

```python
import time

# Simple function
def get_time():
    return time.strftime("%H:%M:%S")

app = SimpleScrollApp(
    text_source=get_time,
    update_interval=1  # Call function every second
)

# Lambda function
app = SimpleScrollApp(
    text_source=lambda: f"Uptime: {time.monotonic():.0f}s",
    update_interval=1
)

# Class method
class SensorReader:
    def get_temperature(self):
        return f"Temp: {sensor.temperature}°C"

reader = SensorReader()
app = SimpleScrollApp(
    text_source=reader.get_temperature,
    update_interval=5
)
```

### URL Data Source

Fetch data from web APIs:

```python
from cpyapp.data import URLDataSource

# Basic usage
weather = URLDataSource(
    url="https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_KEY"
)

# Get the full response
data = weather.get()  # Returns parsed JSON

# Extract specific field
temperature = URLDataSource(
    url="https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_KEY",
    json_path="main.temp"  # Extract nested field
)

app = SimpleScrollApp(
    text_source=lambda: f"London: {temperature.get()}°C",
    update_interval=300  # Update every 5 minutes
)
```

#### Advanced URL Options

```python
# With headers
api_source = URLDataSource(
    url="https://api.example.com/data",
    headers={
        "Authorization": "Bearer YOUR_TOKEN",
        "Accept": "application/json"
    }
)

# With caching
cached_source = URLDataSource(
    url="https://api.example.com/expensive-call",
    cache_duration=3600,  # Cache for 1 hour
    fallback="No data"    # Show if request fails
)

# With timeout
fast_source = URLDataSource(
    url="https://api.example.com/data",
    timeout=5,  # 5 second timeout
    fallback="Timeout"
)
```

#### JSON Path Syntax

```python
# Example JSON response:
# {
#   "weather": [
#     {"description": "clear sky", "temp": 20}
#   ],
#   "main": {
#     "temp": 20,
#     "humidity": 65
#   }
# }

# Access nested fields
URLDataSource(url, json_path="main.temp")  # Returns: 20
URLDataSource(url, json_path="main.humidity")  # Returns: 65

# Access array elements
URLDataSource(url, json_path="weather.0.description")  # Returns: "clear sky"

# Access nested arrays
URLDataSource(url, json_path="weather.0.temp")  # Returns: 20
```

### File Data Source

Read data from local files:

```python
from cpyapp.data import FileDataSource

# Read text file
quote = FileDataSource(
    path="/quotes.txt",
    mode="text"  # Default
)

# Read JSON file
config = FileDataSource(
    path="/config.json",
    mode="json",
    json_path="display.message"  # Extract field
)

# Watch for changes
dynamic_config = FileDataSource(
    path="/message.txt",
    watch=True,  # Auto-reload when file changes
    check_interval=5  # Check every 5 seconds
)

app = SimpleScrollApp(
    text_source=lambda: dynamic_config.get(),
    update_interval=1
)
```

## Creating Custom Data Sources

### Basic Custom Source

```python
from cpyapp.data import DataSource

class RandomNumberSource(DataSource):
    def __init__(self, min_val=0, max_val=100, **kwargs):
        super().__init__(**kwargs)
        self.min_val = min_val
        self.max_val = max_val
    
    def fetch(self):
        """Called to get fresh data."""
        import random
        return random.randint(self.min_val, self.max_val)

# Use it
random_source = RandomNumberSource(
    min_val=1,
    max_val=100,
    cache_duration=5  # New number every 5 seconds
)

app = SimpleScrollApp(
    text_source=lambda: f"Random: {random_source.get()}",
    update_interval=1
)
```

### Sensor Data Source

```python
class TemperatureSensorSource(DataSource):
    def __init__(self, sensor, unit="C", **kwargs):
        super().__init__(**kwargs)
        self.sensor = sensor
        self.unit = unit
    
    def fetch(self):
        """Read from hardware sensor."""
        temp = self.sensor.temperature
        
        if self.unit == "F":
            temp = temp * 9/5 + 32
        
        return {
            "value": temp,
            "unit": self.unit,
            "formatted": f"{temp:.1f}°{self.unit}"
        }

# Initialize sensor
import board
import adafruit_ahtx0
i2c = board.I2C()
sensor = adafruit_ahtx0.AHTx0(i2c)

# Create source
temp_source = TemperatureSensorSource(
    sensor,
    unit="F",
    cache_duration=2  # Read every 2 seconds
)

app = SimpleScrollApp(
    text_source=lambda: temp_source.get()["formatted"]
)
```

### Composite Data Source

```python
class MultiDataSource(DataSource):
    """Combine multiple data sources."""
    
    def __init__(self, sources, separator=" | ", **kwargs):
        super().__init__(**kwargs)
        self.sources = sources
        self.separator = separator
    
    def fetch(self):
        """Fetch from all sources."""
        results = []
        for source in self.sources:
            try:
                data = source.get()
                if data:
                    results.append(str(data))
            except Exception:
                pass  # Skip failed sources
        
        return self.separator.join(results)

# Combine weather and time
multi = MultiDataSource([
    URLDataSource(weather_url, json_path="main.temp"),
    FunctionDataSource(lambda: time.strftime("%H:%M"))
])

app = SimpleScrollApp(text_source=multi.get)
```

## Advanced Patterns

### Fallback Chain

```python
class FallbackDataSource(DataSource):
    """Try sources in order until one works."""
    
    def __init__(self, sources, **kwargs):
        super().__init__(**kwargs)
        self.sources = sources
    
    def fetch(self):
        for source in self.sources:
            try:
                data = source.get()
                if data is not None:
                    return data
            except Exception:
                continue
        return "All sources failed"

# Try API, then cache, then static message
reliable = FallbackDataSource([
    URLDataSource("https://api.example.com/status"),
    FileDataSource("/cache/last_status.txt"),
    StaticDataSource("Status unavailable")
])
```

### Rate-Limited Source

```python
class RateLimitedSource(DataSource):
    """Limit how often a source is called."""
    
    def __init__(self, source, min_interval=60, **kwargs):
        super().__init__(**kwargs)
        self.source = source
        self.min_interval = min_interval
        self.last_call = 0
    
    def fetch(self):
        current = time.monotonic()
        if current - self.last_call < self.min_interval:
            # Return cached value
            return self._cache
        
        self.last_call = current
        return self.source.get()
```

### Transformed Data Source

```python
class TransformDataSource(DataSource):
    """Transform data from another source."""
    
    def __init__(self, source, transform_func, **kwargs):
        super().__init__(**kwargs)
        self.source = source
        self.transform = transform_func
    
    def fetch(self):
        data = self.source.get()
        return self.transform(data)

# Example: Convert temperature
celsius_source = URLDataSource(url, json_path="temp_c")
fahrenheit_source = TransformDataSource(
    celsius_source,
    transform_func=lambda c: c * 9/5 + 32
)

# Example: Format text
raw_source = URLDataSource(url, json_path="message")
formatted_source = TransformDataSource(
    raw_source,
    transform_func=lambda msg: msg.upper().replace("_", " ")
)
```

### Aggregating Data Source

```python
class AverageDataSource(DataSource):
    """Calculate average from multiple sources."""
    
    def __init__(self, sources, **kwargs):
        super().__init__(**kwargs)
        self.sources = sources
    
    def fetch(self):
        values = []
        for source in self.sources:
            try:
                value = float(source.get())
                values.append(value)
            except (ValueError, TypeError):
                pass
        
        if values:
            return sum(values) / len(values)
        return 0

# Average temperature from multiple sensors
avg_temp = AverageDataSource([
    SensorDataSource(sensor1),
    SensorDataSource(sensor2),
    SensorDataSource(sensor3)
])
```

## Best Practices

### 1. Error Handling

Always provide fallbacks:

```python
# Good
weather = URLDataSource(
    url="https://api.weather.com/data",
    fallback="Weather unavailable",
    cache_duration=300  # Use cache if API fails
)

# Better
class SafeWeatherSource(DataSource):
    def fetch(self):
        try:
            response = requests.get(self.url, timeout=5)
            response.raise_for_status()
            return response.json()["temp"]
        except requests.Timeout:
            return "Timeout"
        except requests.HTTPError as e:
            return f"Error: {e.response.status_code}"
        except Exception:
            return "Unknown error"
```

### 2. Caching Strategy

Balance freshness vs. performance:

```python
# Frequently changing data: short cache
stock_price = URLDataSource(
    url="https://api.stocks.com/AAPL",
    cache_duration=60  # 1 minute
)

# Slowly changing data: long cache
weather_forecast = URLDataSource(
    url="https://api.weather.com/forecast",
    cache_duration=3600  # 1 hour
)

# Critical data: no cache
alerts = URLDataSource(
    url="https://api.alerts.com/emergency",
    cache_duration=0  # Always fresh
)
```

### 3. Memory Management

Be mindful of memory on CircuitPython:

```python
# Bad: Keeps large response in memory
class BadSource(DataSource):
    def fetch(self):
        self.last_response = requests.get(url).json()  # Keeps reference
        return self.last_response["data"]

# Good: Extract only what's needed
class GoodSource(DataSource):
    def fetch(self):
        response = requests.get(url).json()
        return response["data"]  # Response gets garbage collected
```

### 4. Testing Data Sources

```python
# Create test-friendly sources
class WeatherSource(DataSource):
    def __init__(self, api_key=None, test_mode=False, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key or os.environ.get("WEATHER_API_KEY")
        self.test_mode = test_mode
    
    def fetch(self):
        if self.test_mode:
            return {"temp": 72, "condition": "sunny"}
        
        # Real API call
        return self._fetch_from_api()

# In tests
def test_weather_display():
    source = WeatherSource(test_mode=True)
    assert source.get()["temp"] == 72
```

## WiFi Setup

For URL data sources, you need WiFi:

```python
# Create secrets.py on CIRCUITPY drive
secrets = {
    "ssid": "Your_WiFi_Network",
    "password": "Your_Password"
}
```

The framework automatically connects using these credentials.

## Troubleshooting

### "No module named 'requests'"

Install adafruit_requests library on CircuitPython.

### "Failed to get data"

1. Check WiFi connection
2. Verify URL is correct
3. Test API in browser first
4. Check for required headers/auth
5. Increase timeout value

### Data not updating

1. Check update_interval
2. Verify cache_duration isn't too long
3. Add logging to fetch() method
4. Test data source independently

### Memory errors

1. Reduce cache_duration
2. Extract only needed fields with json_path
3. Avoid keeping large responses
4. Use simpler data structures

## Next Steps

- Learn about [Styles](STYLES.md) to make your data beautiful
- Explore [Presets](PRESETS.md) for ready-made data sources
- See [API Reference](API_REFERENCE.md) for all options