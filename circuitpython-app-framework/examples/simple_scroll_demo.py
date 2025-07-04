"""
Simple Scroll App Demo - Shows the progressive API in action.

This demonstrates how easy it is to create LED matrix applications
with the SimpleScrollApp class.
"""
import sys
import os

# Add framework to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cpyapp.apps import SimpleScrollApp, scroll_text, scroll_url, scroll_function


def demo_minimal():
    """Minimal example - just text."""
    print("Demo 1: Minimal - Just text")
    app = SimpleScrollApp("Hello World!")
    # app.run()  # Uncomment to run


def demo_with_style():
    """Example with built-in style."""
    print("Demo 2: With style")
    app = SimpleScrollApp("Breaking News!", style="alert")
    # app.run()  # Uncomment to run


def demo_custom_style():
    """Example with custom style."""
    print("Demo 3: Custom style")
    custom_style = {
        'scroll_speed': 0.02,  # Very fast
        'text_color': (255, 128, 0),  # Orange
        'background_color': (0, 0, 64),  # Dark blue
    }
    app = SimpleScrollApp("Custom styled text", style=custom_style)
    # app.run()  # Uncomment to run


def demo_function_source():
    """Example with function data source."""
    print("Demo 4: Function data source")
    
    import time
    def get_current_time():
        return f"Time: {time.strftime('%H:%M:%S')}"
    
    app = SimpleScrollApp(get_current_time, style="info")
    app.settings_manager.set('update_interval', 1)  # Update every second
    # app.run()  # Uncomment to run


def demo_url_source():
    """Example with URL data source."""
    print("Demo 5: URL data source")
    
    # Example: Fetch a message from an API
    app = SimpleScrollApp(
        data_source={
            'url': 'https://api.example.com/message.json',
            'parser': 'json_path',
            'json_path': 'data.message'
        },
        style="default"
    )
    # app.run()  # Uncomment to run


def demo_theme_park_parser():
    """Example with theme park wait times parser."""
    print("Demo 6: Theme park wait times")
    
    app = SimpleScrollApp(
        data_source={
            'url': 'https://queue-times.com/parks/16/queue_times.json',
            'parser': 'theme_park_waits'
        },
        style="info"
    )
    # app.run()  # Uncomment to run


def demo_stock_ticker():
    """Example with stock ticker parser."""
    print("Demo 7: Stock ticker")
    
    # Mock stock data source
    def get_mock_stocks():
        return {
            'AAPL': {'price': 185.92, 'change': 2.15},
            'GOOGL': {'price': 142.83, 'change': -1.27},
            'MSFT': {'price': 378.91, 'change': 3.82}
        }
    
    app = SimpleScrollApp(
        data_source=get_mock_stocks,
        style="default"
    )
    app.settings_manager.set('update_interval', 60)  # Update every minute
    # app.run()  # Uncomment to run


def demo_weather():
    """Example with weather parser."""
    print("Demo 8: Weather display")
    
    # OpenWeatherMap API example (requires API key)
    app = SimpleScrollApp(
        data_source={
            'url': 'https://api.openweathermap.org/data/2.5/weather?q=Orlando&appid=YOUR_API_KEY&units=imperial',
            'parser': 'weather'
        },
        style="info"
    )
    # app.run()  # Uncomment to run


def demo_convenience_functions():
    """Demonstrate convenience functions."""
    print("Demo 9: Convenience functions")
    
    # Simple text scroll
    # scroll_text("Hello from convenience function!")
    
    # Scroll from URL
    # scroll_url("https://api.example.com/message", parser="json_path", json_path="text")
    
    # Scroll from function
    def get_counter():
        if not hasattr(get_counter, 'count'):
            get_counter.count = 0
        get_counter.count += 1
        return f"Count: {get_counter.count}"
    
    # scroll_function(get_counter, style="success", update_interval=2)


def demo_progressive_complexity():
    """Show how the API grows with user needs."""
    print("Demo 10: Progressive complexity")
    
    # Level 1: Absolute beginner
    app1 = SimpleScrollApp("My first LED app!")
    
    # Level 2: Beginner who discovered styles
    app2 = SimpleScrollApp("Rainbow text!", style="rainbow")
    
    # Level 3: Intermediate - using functions
    def my_message():
        return "Dynamic message!"
    app3 = SimpleScrollApp(my_message, style="info")
    
    # Level 4: Advanced - full configuration
    app4 = SimpleScrollApp(
        data_source={
            'url': 'https://api.example.com/data',
            'parser': 'json_path',
            'json_path': 'items',
            'parser_config': {
                'format': '{name}: {value}',
                'field': 'display_text'
            }
        },
        style={
            'scroll_speed': 0.04,
            'text_color': (0, 255, 128),
            'background_color': (16, 0, 32),
            'message_delay': 3
        },
        board={
            'type': 'matrixportal_s3',
            'width': 64,
            'height': 32
        }
    )
    
    print("All apps created successfully!")


if __name__ == "__main__":
    print("SimpleScrollApp Demo Suite")
    print("=" * 50)
    
    # Run all demos (display creation commented out)
    demo_minimal()
    demo_with_style()
    demo_custom_style()
    demo_function_source()
    demo_url_source()
    demo_theme_park_parser()
    demo_stock_ticker()
    demo_weather()
    demo_convenience_functions()
    demo_progressive_complexity()
    
    print("\nDemo complete! Uncomment app.run() lines to actually run the apps.")