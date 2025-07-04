"""
Test Weather Display

Simple test script to verify weather display functionality.
Run this on your computer to test before deploying to CircuitPython.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from cpyapp.data_sources.weather import WeatherDataSource
import asyncio


async def test_weather_display():
    """Test basic weather functionality."""
    print("Weather Display Test\n" + "="*50)
    
    # Test 1: Mock data (no API key)
    print("\n1. Testing with mock data:")
    weather = WeatherDataSource(location='Orlando, FL')
    
    # Fetch and parse data
    data = await weather.fetch()
    parsed = weather.parse_data(data)
    
    if parsed:
        print(f"Location: {parsed['location']}")
        print(f"Temperature: {parsed['temperature']}{parsed['temperature_unit']}")
        print(f"Condition: {parsed['condition']} {parsed['icon']}")
        print(f"Description: {parsed['description']}")
        print(f"Humidity: {parsed['humidity']}%")
        print("✓ Mock data test passed")
    else:
        print("✗ Mock data test failed")
    
    # Test 2: Preset locations
    print("\n2. Testing preset locations:")
    presets_to_test = ['disney_world', 'new_york', 'london']
    
    for preset in presets_to_test:
        weather = WeatherDataSource(preset=preset)
        data = await weather.fetch()
        parsed = weather.parse_data(data)
        
        if parsed:
            print(f"✓ {preset}: {parsed['location']} - {parsed['temperature']}{parsed['temperature_unit']}")
        else:
            print(f"✗ {preset}: Failed to get data")
    
    # Test 3: Display formatting
    print("\n3. Testing display formatting:")
    weather = WeatherDataSource(location='Orlando, FL')
    data = await weather.fetch()
    parsed = weather.parse_data(data)
    messages = weather.format_for_display(parsed)
    
    print("Display messages:")
    for msg in messages:
        print(f"  - {msg['text']} (delay: {msg['delay']}s)")
    
    # Test 4: Different units
    print("\n4. Testing temperature units:")
    for units in ['imperial', 'metric']:
        weather = WeatherDataSource(location='Orlando, FL', units=units)
        data = await weather.fetch()
        parsed = weather.parse_data(data)
        
        if parsed:
            print(f"✓ {units}: {parsed['temperature']}{parsed['temperature_unit']}")
        else:
            print(f"✗ {units}: Failed")
    
    print("\n" + "="*50)
    print("Weather display tests complete!")


async def test_weather_api_key():
    """Test with real API key if available."""
    try:
        from secrets import secrets
        api_key = secrets.get('openweather_key')
        
        if api_key:
            print("\n5. Testing with real API key:")
            weather = WeatherDataSource(
                location='Orlando, FL',
                api_key=api_key
            )
            
            data = await weather.fetch()
            parsed = weather.parse_data(data)
            
            if parsed:
                print(f"✓ Real data received:")
                print(f"  Location: {parsed['location']}")
                print(f"  Temperature: {parsed['temperature']}{parsed['temperature_unit']}")
                print(f"  Live conditions: {parsed['description']}")
            else:
                print("✗ Failed to get real data")
    except ImportError:
        print("\n5. No secrets.py found - skipping API key test")


# Run tests
if __name__ == "__main__":
    print("Starting weather display tests...")
    
    # Run async tests
    asyncio.run(test_weather_display())
    asyncio.run(test_weather_api_key())
    
    print("\nTo deploy to CircuitPython:")
    print("1. Copy secrets_template.py to secrets.py")
    print("2. Add your OpenWeatherMap API key")
    print("3. Copy all files to CIRCUITPY drive")
    print("4. The display will start automatically!"