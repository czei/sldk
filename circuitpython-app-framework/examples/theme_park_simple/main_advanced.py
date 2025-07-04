"""
Advanced Theme Park Display Example.

Shows the progression from simple preset usage to more complex customization.
This demonstrates that you can still access all the power of the framework
when needed, while starting simple.
"""
import asyncio
from cpyapp.apps.simple import SimpleScrollApp
from cpyapp.presets import create_preset
from cpyapp.data_sources import create_data_source
from cpyapp.styles import create_style

# Method 1: Simple preset with parameter overrides
def simple_with_params():
    """Simplest customization - just override preset parameters."""
    app = SimpleScrollApp.from_preset(
        'disney_world',
        min_wait=45,  # Only show 45+ minute waits
        show_closed=False,
        update_interval=300
    )
    app.run()

# Method 2: Custom data source configuration
def custom_data_source():
    """More control over data source configuration."""
    # Create custom theme park data source
    data_config = {
        'type': 'theme_park',
        'park_ids': [6, 5],  # Just Magic Kingdom and EPCOT
        'min_wait': 30,
        'cache_ttl': 600,
        'format_options': {
            'show_land': True,
            'abbreviate_names': True
        }
    }
    
    app = SimpleScrollApp(
        data_source=data_config,
        style='theme_park',  # Use the theme park style
        board='matrixportal_s3'
    )
    app.run()

# Method 3: Custom style with theme park data
def custom_style():
    """Custom styling for theme park display."""
    # Create custom style for wait times
    wait_time_style = {
        'name': 'custom_wait_times',
        'scroll_speed': 0.03,  # Faster scrolling
        'colors': {
            'low_wait': 'Green',      # 0-30 min
            'medium_wait': 'Yellow',   # 31-60 min
            'high_wait': 'Orange',     # 61-90 min  
            'very_high_wait': 'Red',   # 90+ min
            'closed': 'DarkGray'
        },
        'effects': {
            'flash_high_waits': True,  # Flash rides over 90 minutes
            'rainbow_on_low': True     # Rainbow effect for walk-ons
        }
    }
    
    app = SimpleScrollApp(
        data_source={'type': 'theme_park', 'preset': 'magic_kingdom'},
        style=wait_time_style
    )
    app.run()

# Method 4: Multiple parks with rotation
def rotating_parks():
    """Rotate between different parks throughout the day."""
    import time
    
    # Define schedule (hour -> park preset)
    schedule = {
        9: 'magic_kingdom',      # Morning at MK
        12: 'epcot',            # Lunch at EPCOT
        15: 'hollywood_studios', # Afternoon at HS
        18: 'animal_kingdom',    # Evening at AK
        21: 'disney_world'       # Night - all parks
    }
    
    # Get current hour
    current_hour = time.localtime().tm_hour
    
    # Find appropriate park
    park = 'disney_world'  # Default
    for hour, preset in sorted(schedule.items()):
        if current_hour >= hour:
            park = preset
    
    app = SimpleScrollApp.from_preset(park)
    app.run()

# Method 5: Async control for advanced users
async def async_example():
    """Advanced async example with multiple data updates."""
    app = SimpleScrollApp.from_preset('universal_orlando')
    
    # Run the app asynchronously
    await app.run_async()

# Method 6: Direct component access
def component_access():
    """Access underlying components for maximum control."""
    # Create app
    app = SimpleScrollApp.from_preset('magic_kingdom')
    
    # Access the data source directly
    theme_park_source = app.data_plugin.data_source
    
    # You can now use data source methods directly if needed
    # For example, get specific ride wait times
    
    # Access the display
    display = app.display
    
    # Access settings
    settings = app.settings_manager
    settings.set('display.brightness', 0.8)
    
    # Run with modifications
    app.run()

# Method 7: Custom plugin integration
def with_custom_plugin():
    """Add custom functionality via plugins."""
    from cpyapp.core.plugin import DisplayPlugin
    
    class WaitTimeAlertPlugin(DisplayPlugin):
        """Alert when specific rides have low wait times."""
        
        def __init__(self, watch_rides):
            super().__init__("WaitTimeAlert")
            self.watch_rides = watch_rides
            self.alerted = set()
        
        async def get_messages(self, app):
            # Check if any watched rides have low waits
            messages = []
            
            # Get current data from the data source plugin
            if hasattr(app, 'data_plugin') and app.data_plugin.cached_data:
                data = app.data_plugin.cached_data
                
                # Check for low wait times
                for park in (data if isinstance(data, list) else [data]):
                    for ride in park.get('rides', []):
                        if ride['name'] in self.watch_rides:
                            if ride['is_open'] and ride['wait_time'] < 30:
                                if ride['name'] not in self.alerted:
                                    messages.append({
                                        'type': 'alert',
                                        'text': f"LOW WAIT: {ride['name']} - {ride['wait_time']}min!",
                                        'priority': 10,
                                        'style': {'color': 'Green', 'flash': True}
                                    })
                                    self.alerted.add(ride['name'])
            
            return messages
    
    # Create app
    app = SimpleScrollApp.from_preset('magic_kingdom')
    
    # Add alert plugin for popular rides
    alert_plugin = WaitTimeAlertPlugin([
        "Seven Dwarfs Mine Train",
        "Space Mountain",
        "Splash Mountain"
    ])
    app.register_plugin(alert_plugin)
    
    app.run()

# Run the example you want
if __name__ == "__main__":
    # Uncomment the example you want to run:
    
    simple_with_params()
    # custom_data_source()
    # custom_style()
    # rotating_parks()
    # asyncio.run(async_example())
    # component_access()
    # with_custom_plugin()