#!/usr/bin/env python3
"""
Data Sources Demo - Examples of using built-in data sources with SimpleScrollApp.

This script demonstrates various ways to use the new data source system.
"""

# Add the framework to Python path
import sys
sys.path.insert(0, 'src')

from cpyapp.apps.simple import SimpleScrollApp, scroll_text, scroll_url, scroll_function
import asyncio


def demo_simple_text():
    """Simplest example - just text."""
    print("\n=== Simple Text Demo ===")
    app = SimpleScrollApp("Hello from Data Sources!")
    # In real usage, you'd call app.run()
    print("Created app with text: 'Hello from Data Sources!'")


def demo_theme_park_preset():
    """Theme park data using preset."""
    print("\n=== Theme Park Preset Demo ===")
    app = SimpleScrollApp("magic_kingdom")  # Uses preset
    print("Created app with Magic Kingdom preset")
    
    # Or with explicit configuration
    app2 = SimpleScrollApp({
        'type': 'theme_park',
        'preset': 'disney_world'  # All Disney World parks
    })
    print("Created app with Disney World preset (all parks)")


def demo_stock_ticker():
    """Stock ticker using preset."""
    print("\n=== Stock Ticker Demo ===")
    app = SimpleScrollApp("tech_stocks")  # Uses preset
    print("Created app with tech stocks preset")
    
    # Or with custom symbols
    app2 = SimpleScrollApp({
        'type': 'stock',
        'symbols': ['AAPL', 'TSLA', 'AMZN']
    })
    print("Created app with custom stock symbols")


def demo_weather():
    """Weather data source."""
    print("\n=== Weather Demo ===")
    app = SimpleScrollApp("weather_orlando")  # Uses preset
    print("Created app with Orlando weather preset")
    
    # Or with custom location
    app2 = SimpleScrollApp({
        'type': 'weather',
        'location': {'lat': 28.5383, 'lon': -81.3792},  # Orlando coordinates
        'units': 'imperial'
    })
    print("Created app with custom weather location")


def demo_url_source():
    """Generic URL data source."""
    print("\n=== URL Source Demo ===")
    
    # Simple JSON API
    app = SimpleScrollApp({
        'type': 'url',
        'url': 'https://api.example.com/status.json'
    })
    print("Created app with JSON URL")
    
    # With JSON path extraction
    app2 = SimpleScrollApp({
        'type': 'url',
        'url': 'https://api.example.com/data.json',
        'parser': 'json_path',
        'parser_config': {
            'path': 'status.message'  # Extract specific field
        }
    })
    print("Created app with JSON path extraction")
    
    # With custom formatting
    app3 = SimpleScrollApp({
        'type': 'url',
        'url': 'https://api.example.com/data.json',
        'parser_config': {
            'format': '{name}: {value} ({status})'  # Format template
        }
    })
    print("Created app with custom formatting")


def demo_function_source():
    """Function data source examples."""
    print("\n=== Function Source Demo ===")
    
    # Built-in time function
    app = SimpleScrollApp({
        'type': 'function',
        'function': 'time',
        'format': '%H:%M:%S'
    })
    print("Created app with time function")
    
    # Custom function
    def get_system_info():
        import platform
        return f"Python {platform.python_version()} on {platform.system()}"
    
    app2 = SimpleScrollApp(get_system_info)  # Direct function
    print("Created app with custom function")
    
    # Counter function
    app3 = SimpleScrollApp({
        'type': 'function',
        'function': 'counter',
        'start': 100,
        'step': -1,
        'prefix': 'Countdown: '
    })
    print("Created app with countdown function")


def demo_text_variations():
    """Various text data source options."""
    print("\n=== Text Variations Demo ===")
    
    # Multiple messages
    app = SimpleScrollApp([
        "First message",
        "Second message",
        "Third message"
    ])
    print("Created app with message list")
    
    # Pre-formatted messages
    app2 = SimpleScrollApp([
        {'text': 'Alert!', 'type': 'scroll', 'delay': 3},
        {'text': 'Warning!', 'type': 'scroll', 'delay': 2},
        {'text': 'All Clear', 'type': 'scroll', 'delay': 5}
    ])
    print("Created app with formatted messages")
    
    # With styling
    app3 = SimpleScrollApp("Rainbow Text!", style="rainbow")
    print("Created app with rainbow style")


def demo_advanced_parsing():
    """Advanced parsing examples."""
    print("\n=== Advanced Parsing Demo ===")
    
    # Multiple JSON paths
    from cpyapp.data_sources import create_data_source
    
    config = {
        'type': 'url',
        'url': 'https://api.example.com/complex.json',
        'parser': lambda data, cfg: [
            f"User: {data.get('user', {}).get('name', 'Unknown')}",
            f"Score: {data.get('stats', {}).get('score', 0)}",
            f"Level: {data.get('stats', {}).get('level', 1)}"
        ]
    }
    
    source = create_data_source(config)
    print("Created data source with custom parser function")


def demo_combining_sources():
    """Example of switching between multiple data sources."""
    print("\n=== Combining Sources Demo ===")
    
    # This would require a custom plugin, but shows the concept
    print("To combine multiple data sources, create a custom plugin that")
    print("cycles through different sources or combines their output.")
    
    # Example configuration structure
    multi_config = {
        'sources': [
            {'type': 'text', 'text': 'Welcome!'},
            {'type': 'function', 'function': 'time'},
            {'type': 'weather', 'preset': 'orlando'},
            {'type': 'theme_park', 'preset': 'magic_kingdom'}
        ],
        'cycle_time': 30  # Seconds per source
    }
    print("Example multi-source configuration:", multi_config)


def main():
    """Run all demos."""
    print("=== CircuitPython App Framework - Data Sources Demo ===")
    print("This demonstrates the new data source system")
    
    demo_simple_text()
    demo_theme_park_preset()
    demo_stock_ticker()
    demo_weather()
    demo_url_source()
    demo_function_source()
    demo_text_variations()
    demo_advanced_parsing()
    demo_combining_sources()
    
    print("\n=== Available Presets ===")
    from cpyapp.data_sources import DataSourceFactory
    presets = DataSourceFactory.list_presets()
    for preset in sorted(presets):
        info = DataSourceFactory.get_preset_info(preset)
        print(f"  {preset}: {info}")
    
    print("\n=== Usage Examples ===")
    print("# Simple text:")
    print("app = SimpleScrollApp('Hello World!')")
    print("")
    print("# Theme park preset:")
    print("app = SimpleScrollApp('disney_world')")
    print("")
    print("# Stock ticker:")
    print("app = SimpleScrollApp({'type': 'stock', 'symbols': ['AAPL', 'GOOGL']})")
    print("")
    print("# Weather:")
    print("app = SimpleScrollApp({'type': 'weather', 'location': 'New York'})")
    print("")
    print("# URL with parsing:")
    print("app = SimpleScrollApp({")
    print("    'type': 'url',")
    print("    'url': 'https://api.example.com/data.json',")
    print("    'parser': 'json_path',")
    print("    'parser_config': {'path': 'message.text'}")
    print("})")
    print("")
    print("# Then run the app:")
    print("app.run()")


if __name__ == '__main__':
    main()