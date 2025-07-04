#!/usr/bin/env python3
"""
Test the simplified theme park application.

This demonstrates the dramatic simplification - just 3 lines for a fully
functional theme park wait times display!
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the simple theme park app
from cpyapp.apps.simple import SimpleScrollApp

# Method 1: Ultra-simple with preset
print("Starting Magic Kingdom wait times display...")
print("This would normally run on an LED matrix!")
print("-" * 50)

app = SimpleScrollApp.from_preset('magic_kingdom')
app.run()

# Note: To test other parks, just change the preset:
# app = SimpleScrollApp.from_preset('disney_world')  # All 4 parks
# app = SimpleScrollApp.from_preset('universal_orlando')  # Universal
# app = SimpleScrollApp.from_preset('disneyland')  # Disneyland