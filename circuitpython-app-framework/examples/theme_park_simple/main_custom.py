"""
Custom Theme Park Configuration Example.

Shows how to customize the theme park display with different styles and options.
"""
from cpyapp.apps.simple import SimpleScrollApp

# Example 1: Disney World with custom style
disney_app = SimpleScrollApp.from_preset(
    'disney_world',
    min_wait=30,  # Only show rides with 30+ minute waits
    update_interval=600  # Update every 10 minutes
)

# Example 2: Universal Orlando with rainbow style  
universal_app = SimpleScrollApp(
    data_source={'type': 'theme_park', 'park_ids': [9, 10]},
    style='rainbow',
    board='matrixportal_s3'
)

# Example 3: Using the convenience data source directly
magic_kingdom = SimpleScrollApp(
    data_source={'type': 'theme_park', 'preset': 'magic_kingdom'},
    style={'scroll_speed': 0.05, 'colors': {'primary': 'Purple'}}
)

# Run whichever one you want
disney_app.run()
# universal_app.run()
# magic_kingdom.run()