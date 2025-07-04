"""
Ultra-simple Theme Park Wait Times Display.

This demonstrates the dramatic simplification possible with the new architecture.
Just 3 lines to create a fully functional theme park wait times display!
"""
from cpyapp.apps.simple import SimpleScrollApp

# Create and run Magic Kingdom wait times display
app = SimpleScrollApp.from_preset('magic_kingdom')
app.run()