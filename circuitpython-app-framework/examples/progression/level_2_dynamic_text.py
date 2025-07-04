"""Level 2: Dynamic Text - Functions for Dynamic Content

This example shows how to display dynamic content that updates.
We'll create a simple clock that shows the current time.

What you'll learn:
- Using functions to generate dynamic text
- The update_interval parameter
- How the framework calls your function periodically
"""

import time
from cpyapp import SimpleScrollApp

# Define a function that returns the current text to display
def get_current_time():
    """Return the current time as a string."""
    # In CircuitPython, we use time.localtime()
    current = time.localtime()
    return f"Time: {current.tm_hour:02d}:{current.tm_min:02d}:{current.tm_sec:02d}"

# Create app with a function instead of static text
# update_interval=1 means update every second
app = SimpleScrollApp(
    text_source=get_current_time,  # Pass the function (no parentheses!)
    update_interval=1  # Update every second
)

app.run()

# The display will show:
# ┌─────────────────────────────────┐
# │ Time: 14:32:05                  │
# └─────────────────────────────────┘
# (Time updates every second)

# Alternative: You can also use lambda functions for simple cases
app2 = SimpleScrollApp(
    text_source=lambda: f"Uptime: {time.monotonic():.0f}s",
    update_interval=1
)

# Pro tip: update_interval can be:
# - 1: Update every second
# - 0.5: Update twice per second
# - 60: Update every minute
# - None: Never update (for static text)