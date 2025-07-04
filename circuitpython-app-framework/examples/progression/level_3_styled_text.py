"""Level 3: Styled Text - Adding Colors and Effects

This example shows how to add visual style to your text.
We'll create a temperature display with color-coded warnings.

What you'll learn:
- Using the styles parameter
- Color values and how to use them
- Conditional styling based on data
- Built-in style presets
"""

import random
from cpyapp import SimpleScrollApp

# Define colors (RGB tuples)
COLD_BLUE = (0, 0, 255)
NORMAL_GREEN = (0, 255, 0)
WARN_YELLOW = (255, 255, 0)
HOT_RED = (255, 0, 0)

def get_temperature():
    """Simulate temperature reading."""
    # In real app, read from sensor
    temp = random.randint(60, 90)
    return f"Temp: {temp}°F"

def get_temp_color():
    """Return color based on temperature."""
    # Get just the number from the string
    temp_str = get_temperature()
    temp = int(temp_str.split()[1].replace("°F", ""))
    
    if temp < 65:
        return COLD_BLUE
    elif temp < 75:
        return NORMAL_GREEN
    elif temp < 85:
        return WARN_YELLOW
    else:
        return HOT_RED

# Create app with dynamic color styling
app = SimpleScrollApp(
    text_source=get_temperature,
    styles={
        "text_color": get_temp_color,  # Dynamic color function
        "brightness": 0.3,  # 30% brightness
        "scroll_speed": 0.05  # Slower scroll
    },
    update_interval=2  # Update every 2 seconds
)

app.run()

# The display will show temperature with color coding:
# - Blue for cold (< 65°F)
# - Green for normal (65-74°F)
# - Yellow for warm (75-84°F)
# - Red for hot (85°F+)

# Example 2: Using built-in style presets
from cpyapp.styles import STYLE_PRESETS

# Available presets:
# - "default": White text, normal speed
# - "alert": Red text, fast scroll
# - "success": Green text
# - "warning": Yellow text
# - "info": Blue text
# - "stealth": Dim white text

alert_app = SimpleScrollApp(
    "SYSTEM ALERT!",
    styles=STYLE_PRESETS["alert"]
)

# Example 3: Combining preset with overrides
custom_app = SimpleScrollApp(
    "Custom Style",
    styles={
        **STYLE_PRESETS["info"],  # Start with info preset
        "brightness": 0.5,  # Override brightness
        "scroll_speed": 0.02  # Override speed
    }
)