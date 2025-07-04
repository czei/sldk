"""
Weather Display Main Application

This file creates and configures the weather display application
for CircuitPython deployment.
"""
import sys
# Add lib path for CircuitPython
sys.path.insert(0, '/src/lib')

from cpyapp.apps.simple import SimpleScrollApp

# Try to load secrets for API key
try:
    from secrets import secrets, location_settings, display_settings
    api_key = secrets.get('openweather_key')
    
    # Get location from settings
    if 'preset' in location_settings:
        location = {'preset': location_settings['preset']}
    elif 'lat' in location_settings and 'lon' in location_settings:
        location = {
            'lat': location_settings['lat'],
            'lon': location_settings['lon'],
            'name': location_settings.get('name', 'Custom Location')
        }
    else:
        location = location_settings.get('city', 'Orlando, FL')
        
    # Get display preferences
    units = display_settings.get('units', 'imperial')
    update_interval = display_settings.get('update_interval', 600)
    
except ImportError:
    print("No secrets.py found - using defaults with mock data")
    api_key = None
    location = 'Orlando, FL'
    units = 'imperial'
    update_interval = 600

# Create weather display app
app = SimpleScrollApp(
    preset='weather_station',
    location=location,
    api_key=api_key,
    units=units,
    update_interval=update_interval
)

# Optional: Add weather-specific formatting
def format_for_matrix(data):
    """Format weather data for LED matrix display."""
    if not data:
        return [{'text': 'Weather unavailable', 'delay': 3}]
        
    messages = []
    
    # Location with icon
    messages.append({
        'text': f"{data.get('icon', '🌡️')} {data.get('location', 'Unknown')}",
        'delay': 3
    })
    
    # Temperature
    temp = data.get('temperature', 0)
    temp_unit = data.get('temperature_unit', '°F')
    messages.append({
        'text': f"{temp}{temp_unit}",
        'delay': 2
    })
    
    # Condition
    messages.append({
        'text': data.get('description', 'Unknown').title(),
        'delay': 2
    })
    
    # Humidity and wind
    humidity = data.get('humidity', 0)
    wind_speed = data.get('wind_speed', 0)
    wind_unit = data.get('wind_unit', 'mph')
    
    if wind_speed > 0:
        messages.append({
            'text': f"💨 {wind_speed} {wind_unit}",
            'delay': 1.5
        })
        
    messages.append({
        'text': f"💧 {humidity}%",
        'delay': 1.5
    })
    
    return messages

# Set the formatter
app.set_message_formatter(format_for_matrix)

# Export for code.py
__all__ = ['app']