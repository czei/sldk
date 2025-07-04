# Data Sources for CircuitPython App Framework

This module provides built-in data sources for common use cases, making it easy to fetch and display data from various sources on LED matrix displays.

## Overview

Data sources handle:
- Fetching data from APIs, functions, or static content
- Parsing and transforming data
- Formatting data for display
- Caching and rate limiting
- Error handling

## Built-in Data Sources

### Theme Park Data Source
Fetches wait times from queue-times.com API.

**Presets:**
- `magic_kingdom`, `epcot`, `hollywood_studios`, `animal_kingdom`
- `disney_world` (all Disney World parks)
- `disneyland`, `california_adventure`, `disneyland_resort`
- `universal_studios`, `islands_of_adventure`, `universal_orlando`
- And many more!

**Example:**
```python
# Using preset
app = SimpleScrollApp("magic_kingdom")

# Custom configuration
app = SimpleScrollApp({
    'type': 'theme_park',
    'park_id': 6,  # Magic Kingdom
    'cache_ttl': 300  # 5 minutes
})
```

### Stock Data Source
Fetches stock prices from Alpha Vantage or mock data.

**Presets:**
- `tech_stocks` (AAPL, GOOGL, MSFT, AMZN, META)
- `faang_stocks` (Facebook, Apple, Amazon, Netflix, Google)
- `dow`, `crypto`, `meme`, `ev`, `finance`

**Example:**
```python
# Using preset
app = SimpleScrollApp("tech_stocks")

# Custom symbols
app = SimpleScrollApp({
    'type': 'stock',
    'symbols': ['AAPL', 'TSLA'],
    'api_key': 'your_key'  # Or set in secrets.py
})
```

### Weather Data Source
Fetches weather from OpenWeatherMap API.

**Presets:**
- Major cities: `weather_nyc`, `weather_la`, `weather_orlando`
- Theme parks: `weather_disney_world`, `weather_disneyland`

**Example:**
```python
# Using preset
app = SimpleScrollApp("weather_orlando")

# Custom location
app = SimpleScrollApp({
    'type': 'weather',
    'location': {'lat': 28.5383, 'lon': -81.3792},
    'units': 'imperial',  # or 'metric'
    'api_key': 'your_key'  # Or set in secrets.py
})
```

### URL Data Source
Fetches data from any HTTP endpoint.

**Features:**
- Auto-detect JSON/text
- JSON path extraction
- Custom parsers
- Template formatting

**Example:**
```python
# Simple JSON API
app = SimpleScrollApp({
    'type': 'url',
    'url': 'https://api.example.com/message.json'
})

# Extract specific field
app = SimpleScrollApp({
    'type': 'url',
    'url': 'https://api.example.com/data.json',
    'parser': 'json_path',
    'parser_config': {
        'path': 'status.message'
    }
})

# Custom formatting
app = SimpleScrollApp({
    'type': 'url',
    'url': 'https://api.example.com/data.json',
    'parser_config': {
        'format': 'Status: {status} ({timestamp})'
    }
})
```

### Function Data Source
Executes functions to generate dynamic content.

**Built-in functions:**
- `time` - Display current time
- `counter` - Incrementing/decrementing counter
- `random` - Random choices

**Example:**
```python
# Built-in time function
app = SimpleScrollApp({
    'type': 'function',
    'function': 'time',
    'format': '%H:%M:%S'
})

# Custom function
def get_sensor_data():
    return f"Temp: {read_temp()}°F"

app = SimpleScrollApp(get_sensor_data)

# Counter
app = SimpleScrollApp({
    'type': 'function',
    'function': 'counter',
    'start': 100,
    'step': -1,
    'prefix': 'Countdown: '
})
```

### Text Data Source
Static text or pre-formatted messages.

**Example:**
```python
# Simple text
app = SimpleScrollApp("Hello World!")

# Multiple messages
app = SimpleScrollApp([
    "First message",
    "Second message",
    "Third message"
])

# Formatted messages
app = SimpleScrollApp([
    {'text': 'Alert!', 'delay': 3},
    {'text': 'Warning!', 'delay': 2}
])
```

## Parser Utilities

### JSON Path Extraction
```python
from cpyapp.data_sources import extract_json_path

data = {'user': {'profile': {'name': 'John'}}}
name = extract_json_path(data, 'user.profile.name')  # 'John'

# Array access
data = {'items': [{'id': 1}, {'id': 2}]}
second_id = extract_json_path(data, 'items[1].id')  # 2
```

### Formatting Utilities
```python
from cpyapp.data_sources import format_number, format_currency, format_percentage

format_number(1234.56, decimals=2)  # "1,234.56"
format_currency(99.99)              # "$99.99"
format_percentage(0.85)             # "85.0%"
```

### Custom Parsers
```python
from cpyapp.data_sources import parser_registry

def my_parser(data, config):
    # Custom parsing logic
    return parsed_data

parser_registry.register('my_parser', my_parser)

# Use in data source
app = SimpleScrollApp({
    'type': 'url',
    'url': 'https://example.com/data',
    'parser': 'my_parser'
})
```

## Creating Custom Data Sources

```python
from cpyapp.data_sources import DataSource

class MyDataSource(DataSource):
    def __init__(self, **kwargs):
        super().__init__("MySource", **kwargs)
        
    async def _fetch_data(self):
        # Fetch your data
        return data
        
    def format_for_display(self, data):
        # Format for LED display
        return [{
            'type': 'scroll',
            'text': str(data),
            'delay': 2
        }]
```

## Configuration Options

### Common Options
- `cache_ttl`: Cache time-to-live in seconds (default: 300)
- `rate_limit`: Minimum seconds between requests (default: 1.0)

### HTTP Data Sources
- `url`: The URL to fetch from
- `headers`: Optional HTTP headers
- `parser`: Parser type ('auto', 'json', 'text', 'json_path', or callable)
- `parser_config`: Configuration for the parser

## Error Handling

All data sources include:
- Automatic retry on failure
- Cache fallback when API is down
- Rate limiting to prevent API abuse
- Detailed error logging

## API Keys

Some data sources require API keys:
1. Create `secrets.py` in your project root
2. Add your keys:
```python
secrets = {
    'alpha_vantage_key': 'your_key_here',
    'openweather_key': 'your_key_here'
}
```

## Tips

1. **Use presets** for quick setup: `SimpleScrollApp("disney_world")`
2. **Cache data** to reduce API calls and improve performance
3. **Handle errors** gracefully - data sources return cached data when APIs fail
4. **Rate limit** to avoid hitting API quotas
5. **Test locally** with mock data before deploying to hardware