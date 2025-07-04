"""
Simple Weather Display Example

This example shows how to create a weather display using the SimpleScrollApp.
Just a few lines of code to get current weather conditions on your display!
"""
from cpyapp.apps.simple import SimpleScrollApp

# Create weather display app with Orlando, FL as default location
# Perfect for theme park visitors!
app = SimpleScrollApp(preset='weather_station', location='orlando')

# Run the app
app.run()