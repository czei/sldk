"""
Weather Display Secrets Template

Copy this file to secrets.py and fill in your API key and WiFi credentials.
IMPORTANT: Never commit secrets.py to version control!
"""

# WiFi credentials
secrets = {
    # WiFi settings
    'ssid': 'YOUR_WIFI_SSID',
    'password': 'YOUR_WIFI_PASSWORD',
    
    # OpenWeatherMap API key
    # Get your free API key at: https://openweathermap.org/api
    'openweather_key': 'YOUR_OPENWEATHERMAP_API_KEY',
    
    # Optional: Alternative weather providers
    # 'weatherapi_key': 'YOUR_WEATHERAPI_KEY',  # weatherapi.com
    # 'darksky_key': 'YOUR_DARKSKY_KEY',        # darksky.net (deprecated)
    # 'accuweather_key': 'YOUR_ACCUWEATHER_KEY' # accuweather.com
}

# Optional: Location settings
location_settings = {
    # Use one of the following methods:
    
    # Method 1: City name
    'city': 'Orlando, FL',
    
    # Method 2: Coordinates
    # 'lat': 28.5383,
    # 'lon': -81.3792,
    
    # Method 3: Preset location
    # 'preset': 'disney_world'  # See weather.py for available presets
}

# Display preferences
display_settings = {
    'units': 'imperial',     # 'imperial' for °F, 'metric' for °C
    'language': 'en',        # Language code for weather descriptions
    'update_interval': 600,  # Update interval in seconds (10 minutes)
    'show_forecast': True,   # Show 5-day forecast
    'show_alerts': True      # Show weather alerts
}