"""
Custom Weather Display Example

This example shows how to customize the weather display with different
locations, styling, and display options.
"""
from cpyapp.apps.simple import SimpleScrollApp
from cpyapp.styles.colors import RAINBOW_COLORS

# Custom weather display configuration
custom_config = {
    # Use a preset location (Disney World!)
    'location': {'preset': 'disney_world'},
    
    # Or use coordinates
    # 'location': {'lat': 28.3852, 'lon': -81.5639, 'name': 'Disney World'},
    
    # Or use city name
    # 'location': 'Orlando, FL',
    
    # Temperature units
    'units': 'imperial',  # 'imperial' for °F, 'metric' for °C
    
    # Custom styling
    'style': {
        'scroll_speed': 0.04,
        'colors': {
            'sunny': RAINBOW_COLORS['yellow'],
            'cloudy': RAINBOW_COLORS['gray'],
            'rainy': RAINBOW_COLORS['blue'],
            'temperature': RAINBOW_COLORS['orange'],
            'background': (0, 0, 32)  # Dark blue background
        },
        'show_icons': True,
        'format': '{icon} {temp}°F {condition} | Humidity: {humidity}%'
    },
    
    # Update interval (in seconds)
    'update_interval': 600,  # Update every 10 minutes
    
    # Show additional information
    'show_forecast': True,
    'show_wind': True,
    'show_visibility': True
}

# Create customized weather app
app = SimpleScrollApp(preset='weather_station', **custom_config)

# Optional: Add custom message formatting
def format_weather_message(data):
    """Custom weather message formatting."""
    messages = []
    
    # Main weather info with emoji
    messages.append({
        'text': f"{data['icon']} {data['location']}",
        'color': 'white',
        'delay': 3
    })
    
    # Temperature with color coding
    temp = data['temperature']
    if temp >= 85:
        color = 'red'
    elif temp >= 70:
        color = 'orange'
    elif temp >= 50:
        color = 'yellow'
    else:
        color = 'cyan'
        
    messages.append({
        'text': f"{temp}°F (Feels like {data['feels_like']}°F)",
        'color': color,
        'delay': 2.5
    })
    
    # Weather condition
    messages.append({
        'text': data['description'].title(),
        'color': 'white',
        'delay': 2
    })
    
    # Wind information
    if data['wind_speed'] > 0:
        wind_color = 'red' if data['wind_speed'] > 20 else 'yellow' if data['wind_speed'] > 10 else 'green'
        messages.append({
            'text': f"Wind: {data['wind_speed']} mph {data['wind_direction']}",
            'color': wind_color,
            'delay': 2
        })
    
    # Park day rating
    if temp >= 70 and temp <= 85 and data['humidity'] < 70:
        messages.append({
            'text': "Perfect theme park weather! 🎢",
            'color': 'green',
            'delay': 3
        })
    elif data['condition'] == 'Rain':
        messages.append({
            'text': "Indoor attractions recommended ☔",
            'color': 'yellow',
            'delay': 3
        })
    
    return messages

# Set custom formatter
app.set_message_formatter(format_weather_message)

# Run the app
app.run()