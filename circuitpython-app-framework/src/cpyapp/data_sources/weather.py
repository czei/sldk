"""
Weather Data Source for weather information.

This module provides a data source for fetching weather data
from various weather APIs including OpenWeatherMap.
"""
import json
try:
    from typing import Dict, Any, Optional, List
except ImportError:
    # CircuitPython doesn't have typing
    pass

from .base import HttpDataSource
from ..utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")


class WeatherDataSource(HttpDataSource):
    """
    Data source for weather information.
    
    This class provides access to current weather conditions and
    forecasts from various weather APIs.
    """
    
    # Temperature conversion functions
    @staticmethod
    def kelvin_to_fahrenheit(kelvin):
        """Convert Kelvin to Fahrenheit."""
        return (kelvin - 273.15) * 9/5 + 32
        
    @staticmethod
    def kelvin_to_celsius(kelvin):
        """Convert Kelvin to Celsius."""
        return kelvin - 273.15
        
    @staticmethod
    def celsius_to_fahrenheit(celsius):
        """Convert Celsius to Fahrenheit."""
        return celsius * 9/5 + 32
        
    # Weather icon to emoji mapping
    WEATHER_ICONS = {
        # Clear
        '01d': '☀️', '01n': '🌙',
        # Few clouds
        '02d': '⛅', '02n': '☁️',
        # Scattered clouds
        '03d': '☁️', '03n': '☁️',
        # Broken clouds
        '04d': '☁️', '04n': '☁️',
        # Shower rain
        '09d': '🌦️', '09n': '🌦️',
        # Rain
        '10d': '🌧️', '10n': '🌧️',
        # Thunderstorm
        '11d': '⛈️', '11n': '⛈️',
        # Snow
        '13d': '❄️', '13n': '❄️',
        # Mist
        '50d': '🌫️', '50n': '🌫️',
    }
    
    # Location presets
    PRESETS = {
        # Major US Cities
        'new_york': {'lat': 40.7128, 'lon': -74.0060, 'name': 'New York'},
        'los_angeles': {'lat': 34.0522, 'lon': -118.2437, 'name': 'Los Angeles'},
        'chicago': {'lat': 41.8781, 'lon': -87.6298, 'name': 'Chicago'},
        'houston': {'lat': 29.7604, 'lon': -95.3698, 'name': 'Houston'},
        'miami': {'lat': 25.7617, 'lon': -80.1918, 'name': 'Miami'},
        'seattle': {'lat': 47.6062, 'lon': -122.3321, 'name': 'Seattle'},
        'san_francisco': {'lat': 37.7749, 'lon': -122.4194, 'name': 'San Francisco'},
        'boston': {'lat': 42.3601, 'lon': -71.0589, 'name': 'Boston'},
        'denver': {'lat': 39.7392, 'lon': -104.9903, 'name': 'Denver'},
        'orlando': {'lat': 28.5383, 'lon': -81.3792, 'name': 'Orlando'},
        
        # Theme Parks
        'disney_world': {'lat': 28.3852, 'lon': -81.5639, 'name': 'Disney World'},
        'disneyland': {'lat': 33.8121, 'lon': -117.9190, 'name': 'Disneyland'},
        'universal_orlando': {'lat': 28.4752, 'lon': -81.4685, 'name': 'Universal Orlando'},
        
        # International
        'london': {'lat': 51.5074, 'lon': -0.1278, 'name': 'London'},
        'paris': {'lat': 48.8566, 'lon': 2.3522, 'name': 'Paris'},
        'tokyo': {'lat': 35.6762, 'lon': 139.6503, 'name': 'Tokyo'},
    }
    
    def __init__(self, location=None, preset=None, units='imperial', api_key=None, provider='openweathermap', **kwargs):
        """
        Initialize weather data source.
        
        Args:
            location: Dictionary with 'lat' and 'lon' keys, or city name string
            preset: Preset location name (e.g., 'new_york', 'disney_world')
            units: Temperature units ('imperial' for F, 'metric' for C)
            api_key: API key for the weather service
            provider: Weather API provider (currently only 'openweathermap')
            **kwargs: Additional arguments passed to HttpDataSource
        """
        # Use preset if provided
        if preset and preset in self.PRESETS:
            location = self.PRESETS[preset]
            
        # Default to New York if nothing specified
        if location is None:
            location = self.PRESETS['new_york']
            logger.info("No location specified, defaulting to New York")
            
        # Store configuration
        self.location = location
        self.units = units
        self.provider = provider
        self.api_key = api_key
        
        # Check for API key
        if not api_key:
            # Try to load from secrets
            try:
                from ..utils.url_utils import load_credentials
                credentials = load_credentials()
                self.api_key = credentials.get('openweather_key', '')
            except Exception:
                logger.warning("No weather API key provided, will use mock data")
                
        # Build URL based on location type
        if self.api_key and provider == 'openweathermap':
            if isinstance(location, dict) and 'lat' in location and 'lon' in location:
                # Coordinates provided
                url = f"https://api.openweathermap.org/data/2.5/weather?lat={location['lat']}&lon={location['lon']}&appid={self.api_key}"
            elif isinstance(location, str):
                # City name provided
                url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={self.api_key}"
            else:
                url = None
        else:
            url = None
            
        super().__init__("Weather", url=url, **kwargs)
        
    async def _fetch_data(self):
        """Fetch weather data."""
        if not self.api_key or not self.url:
            # Return mock data
            return self._get_mock_data()
            
        # Fetch real data
        return await super()._fetch_data()
        
    def _get_mock_data(self):
        """Generate mock weather data for testing."""
        import random
        
        # Generate realistic weather conditions
        conditions = [
            {'main': 'Clear', 'description': 'clear sky', 'icon': '01d'},
            {'main': 'Clouds', 'description': 'few clouds', 'icon': '02d'},
            {'main': 'Clouds', 'description': 'scattered clouds', 'icon': '03d'},
            {'main': 'Rain', 'description': 'light rain', 'icon': '10d'},
            {'main': 'Rain', 'description': 'moderate rain', 'icon': '10d'},
            {'main': 'Thunderstorm', 'description': 'thunderstorm', 'icon': '11d'},
        ]
        
        condition = random.choice(conditions)
        temp_f = random.uniform(30, 95)
        temp_c = (temp_f - 32) * 5/9
        
        location_name = self.location.get('name', 'Unknown') if isinstance(self.location, dict) else str(self.location)
        
        return {
            'name': location_name,
            'weather': [condition],
            'main': {
                'temp': temp_c + 273.15 if self.units == 'metric' else temp_f,  # Kelvin
                'feels_like': temp_c + 273.15 + random.uniform(-3, 3) if self.units == 'metric' else temp_f + random.uniform(-5, 5),
                'temp_min': temp_c + 273.15 - 5 if self.units == 'metric' else temp_f - 10,
                'temp_max': temp_c + 273.15 + 5 if self.units == 'metric' else temp_f + 10,
                'pressure': random.randint(1000, 1030),
                'humidity': random.randint(30, 90)
            },
            'wind': {
                'speed': random.uniform(0, 25),
                'deg': random.randint(0, 360)
            },
            'clouds': {
                'all': random.randint(0, 100)
            },
            'visibility': random.randint(5000, 10000),
            'sys': {
                'sunrise': 1234567890,
                'sunset': 1234567890
            }
        }
        
    def parse_data(self, raw_data):
        """Parse weather data into standard format."""
        if not raw_data:
            return None
            
        # Extract key information
        weather = raw_data.get('weather', [{}])[0]
        main = raw_data.get('main', {})
        wind = raw_data.get('wind', {})
        clouds = raw_data.get('clouds', {})
        
        # Convert temperature based on units
        temp_kelvin = main.get('temp', 0)
        if self.units == 'imperial':
            temp = self.kelvin_to_fahrenheit(temp_kelvin)
            temp_unit = '°F'
            wind_unit = 'mph'
        else:
            temp = self.kelvin_to_celsius(temp_kelvin)
            temp_unit = '°C'
            wind_unit = 'm/s'
            
        # Get weather icon/emoji
        icon_code = weather.get('icon', '01d')
        weather_emoji = self.WEATHER_ICONS.get(icon_code, '🌡️')
        
        return {
            'location': raw_data.get('name', 'Unknown'),
            'temperature': round(temp, 1),
            'temperature_unit': temp_unit,
            'feels_like': round(self.kelvin_to_fahrenheit(main.get('feels_like', temp_kelvin)) if self.units == 'imperial' else self.kelvin_to_celsius(main.get('feels_like', temp_kelvin)), 1),
            'condition': weather.get('main', 'Unknown'),
            'description': weather.get('description', 'Unknown'),
            'icon': weather_emoji,
            'humidity': main.get('humidity', 0),
            'pressure': main.get('pressure', 0),
            'wind_speed': wind.get('speed', 0),
            'wind_unit': wind_unit,
            'wind_direction': self._degrees_to_compass(wind.get('deg', 0)),
            'cloudiness': clouds.get('all', 0),
            'visibility': raw_data.get('visibility', 0) / 1000 if 'visibility' in raw_data else None  # Convert to km
        }
        
    def _degrees_to_compass(self, degrees):
        """Convert wind direction degrees to compass direction."""
        directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                     'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        index = round(degrees / 22.5) % 16
        return directions[index]
        
    def format_for_display(self, data):
        """Format weather data for display."""
        messages = []
        
        if not data:
            return [{
                'type': 'scroll',
                'text': 'Weather data unavailable',
                'delay': 2
            }]
            
        # Location and main condition
        messages.append({
            'type': 'scroll',
            'text': f"{data['icon']} {data['location']}: {data['condition']}",
            'delay': 3
        })
        
        # Temperature
        messages.append({
            'type': 'scroll',
            'text': f"Temp: {data['temperature']}{data['temperature_unit']} (Feels: {data['feels_like']}{data['temperature_unit']})",
            'delay': 2.5
        })
        
        # Description
        messages.append({
            'type': 'scroll',
            'text': data['description'].title(),
            'delay': 2
        })
        
        # Wind
        if data['wind_speed'] > 0:
            messages.append({
                'type': 'scroll',
                'text': f"Wind: {data['wind_speed']} {data['wind_unit']} {data['wind_direction']}",
                'delay': 2
            })
            
        # Humidity and pressure
        messages.append({
            'type': 'scroll',
            'text': f"Humidity: {data['humidity']}% | Pressure: {data['pressure']} hPa",
            'delay': 2
        })
        
        # Visibility if available
        if data['visibility']:
            messages.append({
                'type': 'scroll',
                'text': f"Visibility: {data['visibility']:.1f} km",
                'delay': 1.5
            })
            
        return messages
        
    async def get_forecast(self, days=5):
        """
        Get weather forecast for the next few days.
        
        Args:
            days: Number of days to forecast (max 5 for free API)
            
        Returns:
            List of daily forecasts
        """
        if not self.api_key or self.provider != 'openweathermap':
            logger.warning("Forecast requires OpenWeatherMap API key")
            return []
            
        # Build forecast URL
        if isinstance(self.location, dict) and 'lat' in self.location and 'lon' in self.location:
            url = f"https://api.openweathermap.org/data/2.5/forecast?lat={self.location['lat']}&lon={self.location['lon']}&appid={self.api_key}"
        elif isinstance(self.location, str):
            url = f"https://api.openweathermap.org/data/2.5/forecast?q={self.location}&appid={self.api_key}"
        else:
            return []
            
        # Temporarily change URL
        original_url = self.url
        self.url = url
        
        try:
            forecast_data = await super()._fetch_data()
            
            # Process forecast data
            # Note: This is simplified - real implementation would aggregate by day
            forecasts = []
            if forecast_data and 'list' in forecast_data:
                for item in forecast_data['list'][:days]:
                    parsed = self.parse_data(item)
                    if parsed:
                        forecasts.append(parsed)
                        
            return forecasts
            
        finally:
            # Restore original URL
            self.url = original_url