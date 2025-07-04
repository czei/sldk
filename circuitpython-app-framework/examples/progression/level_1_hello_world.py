"""Level 1: Hello World - The Simplest Possible App

This is the absolute simplest CircuitPython App Framework example.
It displays static text on your LED matrix display.

What you'll learn:
- How to create a basic app in just 2 lines
- The SimpleScrollApp convenience class
- Basic text display
"""

from cpyapp import SimpleScrollApp

# That's it! This creates and runs a simple scrolling text app
app = SimpleScrollApp("Hello World!")
app.run()

# The display will show:
# ┌─────────────────────────────────┐
# │ Hello World!                    │
# └─────────────────────────────────┘
# (Text scrolls continuously from right to left)

# Behind the scenes, SimpleScrollApp:
# - Detects your board automatically
# - Sets up the display
# - Creates a scrolling text renderer
# - Handles the main loop
# - Manages memory efficiently