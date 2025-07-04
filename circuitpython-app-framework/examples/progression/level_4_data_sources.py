"""Level 4: Data Sources - Using URLs and APIs

This example shows how to fetch and display data from the internet.
We'll create a weather display that shows real weather data.

What you'll learn:
- Using URL data sources
- JSON parsing and data extraction
- Error handling for network requests
- Caching to reduce API calls
"""

from cpyapp import SimpleScrollApp
from cpyapp.data import URLDataSource

# Example 1: Simple weather display
# Using OpenWeatherMap API (you need an API key)
API_KEY = "your_api_key_here"
CITY = "Orlando"
WEATHER_URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=imperial"

# Create a data source that fetches weather data
weather_source = URLDataSource(
    url=WEATHER_URL,
    json_path="main.temp",  # Extract temperature from JSON
    cache_duration=300,  # Cache for 5 minutes
    fallback="--"  # Show this if fetch fails
)

# Create app using the data source
weather_app = SimpleScrollApp(
    text_source=lambda: f"{CITY}: {weather_source.get()}°F",
    update_interval=60  # Check for updates every minute
)

# Example 2: Multiple data points from same API
class WeatherDisplay:
    """More complex weather display with multiple data points."""
    
    def __init__(self):
        self.weather = URLDataSource(
            url=WEATHER_URL,
            cache_duration=300
        )
    
    def get_display_text(self):
        """Format weather data for display."""
        data = self.weather.get()
        
        if not data:
            return "Weather unavailable"
        
        temp = data.get("main", {}).get("temp", "--")
        feels_like = data.get("main", {}).get("feels_like", "--")
        description = data.get("weather", [{}])[0].get("description", "")
        
        return f"{CITY}: {temp}°F (feels {feels_like}°F) - {description}"

weather_display = WeatherDisplay()
advanced_weather_app = SimpleScrollApp(
    text_source=weather_display.get_display_text,
    update_interval=60
)

# Example 3: Using the data source directly for other APIs
# This could be any JSON API
quote_source = URLDataSource(
    url="https://api.quotable.io/random",
    json_path="content",  # Extract the quote content
    cache_duration=3600,  # Cache for 1 hour
    fallback="No quote available"
)

quote_app = SimpleScrollApp(
    text_source=lambda: f"Quote: {quote_source.get()}",
    update_interval=300  # New quote every 5 minutes
)

# Example 4: Custom data processing
def process_weather_data():
    """Process weather data with custom logic."""
    data = weather_source.get_raw()  # Get full JSON
    
    if not data:
        return "No data"
    
    temp = data.get("main", {}).get("temp", 0)
    
    # Add emoji based on temperature
    if temp < 32:
        emoji = "❄"  # Snowflake
    elif temp < 60:
        emoji = "🌥"  # Cloud
    elif temp < 80:
        emoji = "☀"  # Sun
    else:
        emoji = "🔥"  # Fire
    
    return f"{emoji} {CITY}: {temp}°F"

emoji_weather_app = SimpleScrollApp(
    text_source=process_weather_data,
    update_interval=60
)

# Run the app
weather_app.run()