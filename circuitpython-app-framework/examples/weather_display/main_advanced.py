"""
Advanced Weather Display Example

This example shows advanced features including:
- Weather alerts monitoring
- Multiple location rotation
- Custom API extensions
- Plugin integration
"""
from cpyapp.apps.simple import SimpleScrollApp
from src.api.weather import ExtendedWeatherAPI, THEME_PARK_WEATHER_CONFIGS
from src.plugins.weather_alerts import WeatherAlertsPlugin, WeatherRadarPlugin
import time

# Configuration for advanced weather display
class AdvancedWeatherDisplay:
    """Advanced weather display with multiple locations and alerts."""
    
    def __init__(self):
        """Initialize advanced weather display."""
        # Load API key from secrets
        try:
            from secrets import secrets
            self.api_key = secrets.get('openweather_key')
        except ImportError:
            self.api_key = None
            print("No API key found - using mock data")
            
        # Configure locations to rotate through
        self.locations = [
            # Theme parks with extended info
            {
                'name': 'Disney World',
                'config': THEME_PARK_WEATHER_CONFIGS['disney_world']
            },
            {
                'name': 'Disneyland', 
                'config': THEME_PARK_WEATHER_CONFIGS['disneyland']
            },
            # Major cities
            {
                'name': 'New York',
                'location': 'New York, NY',
                'theme_park_mode': False
            },
            {
                'name': 'Los Angeles',
                'location': 'Los Angeles, CA',
                'theme_park_mode': False
            }
        ]
        
        self.current_location_index = 0
        self.location_display_time = 30  # Seconds per location
        self.apps = []
        
    def create_app_for_location(self, location_config):
        """Create weather app for specific location."""
        # Use extended API for theme parks
        if location_config.get('config', {}).get('theme_park_mode', False):
            # Create app with extended theme park features
            app = SimpleScrollApp(
                preset='weather_station',
                data_source_class=ExtendedWeatherAPI,
                api_key=self.api_key,
                **location_config['config']
            )
        else:
            # Standard weather display
            app = SimpleScrollApp(
                preset='weather_station',
                location=location_config.get('location'),
                api_key=self.api_key
            )
            
        # Add plugins
        self._add_plugins(app)
        
        return app
        
    def _add_plugins(self, app):
        """Add weather plugins to app."""
        # Add weather alerts plugin
        alerts_plugin = WeatherAlertsPlugin(app)
        app.register_plugin(alerts_plugin)
        
        # Add radar plugin for visual weather
        radar_plugin = WeatherRadarPlugin(app)
        app.register_plugin(radar_plugin)
        
    def run(self):
        """Run the advanced weather display."""
        print("Starting Advanced Weather Display")
        print(f"Rotating through {len(self.locations)} locations")
        
        while True:
            # Get current location
            location = self.locations[self.current_location_index]
            print(f"\nDisplaying weather for: {location['name']}")
            
            # Create and run app for this location
            app = self.create_app_for_location(location)
            
            # Run for specified duration
            start_time = time.monotonic()
            while time.monotonic() - start_time < self.location_display_time:
                app.update()
                time.sleep(0.1)
                
            # Clean up
            app.stop()
            
            # Move to next location
            self.current_location_index = (self.current_location_index + 1) % len(self.locations)
            
            # Brief pause between locations
            time.sleep(1)


# Example of custom formatting for different locations
class LocationAwareFormatter:
    """Format weather data based on location type."""
    
    @staticmethod
    def format_theme_park_weather(data):
        """Special formatting for theme park weather."""
        messages = []
        
        # Park name with special icon
        messages.append({
            'text': f"🎢 {data['location']} 🎢",
            'color': 'rainbow',  # Special rainbow effect
            'delay': 3
        })
        
        # Temperature with rating
        rating = data.get('theme_park_rating', {})
        stars = rating.get('stars', 0)
        color = 'green' if stars >= 4 else 'yellow' if stars >= 3 else 'red'
        
        messages.append({
            'text': f"{data['temperature']}°F {'⭐' * stars}",
            'color': color,
            'delay': 2.5
        })
        
        # Park recommendations
        for rec in data.get('recommendations', [])[:2]:
            messages.append({
                'text': rec,
                'color': 'white',
                'delay': 2
            })
            
        return messages
        
    @staticmethod
    def format_city_weather(data):
        """Standard city weather formatting."""
        messages = []
        
        # City name
        messages.append({
            'text': f"📍 {data['location']}",
            'color': 'white',
            'delay': 2
        })
        
        # Temperature and condition
        messages.append({
            'text': f"{data['icon']} {data['temperature']}°F {data['condition']}",
            'color': 'white',
            'delay': 3
        })
        
        # Additional info
        messages.append({
            'text': f"💧{data['humidity']}% 💨{data['wind_speed']}mph",
            'color': 'cyan',
            'delay': 2
        })
        
        return messages


# Run the advanced display
if __name__ == "__main__":
    display = AdvancedWeatherDisplay()
    display.run()