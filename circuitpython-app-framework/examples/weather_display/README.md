# Weather Display Example

A simple weather display application that shows current weather conditions on your LED matrix display. This example demonstrates how to use the SimpleScrollApp framework to create a weather monitoring display with just a few lines of code.

## Features

- 🌡️ Real-time weather data from OpenWeatherMap
- 🌍 Support for any location worldwide
- 🎨 Customizable display styling
- 📍 Preset locations for popular destinations
- 🔄 Automatic updates every 10 minutes
- 📴 Mock data fallback when offline

## Quick Start

### Simple Version

The simplest weather display in just 3 lines:

```python
from cpyapp.apps.simple import SimpleScrollApp

app = SimpleScrollApp(preset='weather_station', location='orlando')
app.run()
```

### Setup

1. **Get an API Key**
   - Sign up for a free account at [OpenWeatherMap](https://openweathermap.org/api)
   - Copy your API key from the dashboard

2. **Configure Secrets**
   ```bash
   cp secrets_template.py secrets.py
   ```
   Edit `secrets.py` and add:
   - Your WiFi credentials
   - Your OpenWeatherMap API key
   - Your preferred location

3. **Deploy to CircuitPython**
   ```bash
   # Copy all files to your CIRCUITPY drive
   cp -r * /Volumes/CIRCUITPY/
   ```

## Configuration Options

### Location Settings

You can specify location in multiple ways:

```python
# Method 1: City name
app = SimpleScrollApp(preset='weather_station', location='New York, NY')

# Method 2: Coordinates
app = SimpleScrollApp(preset='weather_station', location={'lat': 40.7128, 'lon': -74.0060})

# Method 3: Preset location
app = SimpleScrollApp(preset='weather_station', location={'preset': 'disney_world'})
```

### Available Preset Locations

- Major Cities: `new_york`, `los_angeles`, `chicago`, `miami`, `seattle`, `orlando`
- Theme Parks: `disney_world`, `disneyland`, `universal_orlando`
- International: `london`, `paris`, `tokyo`

### Temperature Units

```python
# Fahrenheit (default)
app = SimpleScrollApp(preset='weather_station', units='imperial')

# Celsius
app = SimpleScrollApp(preset='weather_station', units='metric')
```

## Customization

### Custom Styling

```python
custom_config = {
    'style': {
        'scroll_speed': 0.04,
        'colors': {
            'sunny': (255, 255, 0),    # Yellow
            'cloudy': (128, 128, 128), # Gray
            'rainy': (0, 0, 255),      # Blue
            'temperature': (255, 165, 0) # Orange
        },
        'show_icons': True
    }
}

app = SimpleScrollApp(preset='weather_station', **custom_config)
```

### Custom Message Formatting

See `main_custom.py` for an advanced example with:
- Color-coded temperatures
- Wind speed warnings
- Theme park weather ratings
- Custom emoji indicators

## Display Information

The weather display shows:
- Current temperature and "feels like" temperature
- Weather condition with emoji icons
- Humidity percentage
- Wind speed and direction
- Atmospheric pressure
- Visibility (when available)

### Weather Icons

- ☀️ Clear sky
- ⛅ Partly cloudy
- ☁️ Cloudy
- 🌧️ Rain
- ⛈️ Thunderstorm
- ❄️ Snow
- 🌫️ Fog/Mist

## Settings File

The `settings.json` file contains all configurable options:

```json
{
    "weather_display": {
        "location": "Orlando, FL",
        "units": "imperial",
        "update_interval": 600,
        "show_forecast": true
    }
}
```

## Troubleshooting

### No Weather Data
- Check your API key is correct in `secrets.py`
- Verify WiFi connection
- Ensure location format is correct

### Mock Data Mode
If no API key is provided, the app will display mock weather data for testing.

### API Rate Limits
Free OpenWeatherMap accounts allow:
- 60 calls/minute
- 1,000,000 calls/month

The default 10-minute update interval stays well within these limits.

## Advanced Features

### Multiple Locations

Create a rotating display of multiple locations:

```python
locations = ['New York', 'Los Angeles', 'Chicago']
for location in locations:
    app = SimpleScrollApp(preset='weather_station', location=location)
    # Display for 30 seconds
    app.run(duration=30)
```

### Weather Alerts

Enable weather alerts in settings:

```json
{
    "alerts": {
        "enabled": true,
        "types": ["severe", "warning"],
        "flash_on_alert": true
    }
}
```

### Forecast Display

Show 5-day forecast (requires additional API configuration):

```python
app = SimpleScrollApp(
    preset='weather_station',
    show_forecast=True
)
```

## API Documentation

- [OpenWeatherMap API](https://openweathermap.org/api)
- [Weather Icons](https://openweathermap.org/weather-conditions)
- [API Response Format](https://openweathermap.org/current)

## License

This example is part of the CircuitPython App Framework and follows the same license terms.