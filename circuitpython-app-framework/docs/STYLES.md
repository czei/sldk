# Style System Guide

Learn how to make your LED matrix displays beautiful with colors, animations, and effects.

## Overview

The style system controls how your content looks:

- **Colors**: Text and background colors
- **Brightness**: Display intensity
- **Animation**: Scrolling, blinking, fading
- **Effects**: Rainbow, gradient, sparkle
- **Layout**: Font size, spacing, alignment

## Basic Styling

### Setting Colors

```python
from cpyapp import SimpleScrollApp

# Single color
app = SimpleScrollApp(
    "Hello World!",
    styles={"text_color": (255, 0, 0)}  # Red
)

# Common colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
WHITE = (255, 255, 255)
ORANGE = (255, 128, 0)
PURPLE = (128, 0, 255)
```

### Brightness Control

```python
# Brightness from 0.0 (off) to 1.0 (full)
app = SimpleScrollApp(
    "Bright Text",
    styles={
        "text_color": (255, 255, 255),
        "brightness": 0.5  # 50% brightness
    }
)

# Dim for night time
night_app = SimpleScrollApp(
    "Night Mode",
    styles={
        "text_color": (255, 0, 0),
        "brightness": 0.1  # Very dim
    }
)
```

### Scroll Speed

```python
# Speed in pixels per frame
app = SimpleScrollApp(
    "Slow and steady",
    styles={"scroll_speed": 0.02}  # Slow
)

fast_app = SimpleScrollApp(
    "URGENT MESSAGE!",
    styles={
        "scroll_speed": 0.08,  # Fast
        "text_color": (255, 0, 0)
    }
)

# Static (no scroll)
static_app = SimpleScrollApp(
    "STOP",
    styles={"scroll_speed": 0}  # No scrolling
)
```

## Style Presets

```python
from cpyapp.styles import STYLE_PRESETS

# Built-in presets
app = SimpleScrollApp("Alert!", styles=STYLE_PRESETS["alert"])

# Available presets:
# - "default": White text, normal speed
# - "alert": Red, fast, bright
# - "success": Green, normal speed
# - "warning": Yellow/orange
# - "info": Blue
# - "stealth": Dim white (low brightness)
# - "rainbow": Animated rainbow colors
# - "matrix": Green with fade effect
# - "fire": Red/orange with flicker
# - "ocean": Blue/cyan with wave effect
```

### Customizing Presets

```python
# Start with preset, override specific values
custom_alert = {
    **STYLE_PRESETS["alert"],
    "brightness": 0.3,  # Less bright than default alert
    "scroll_speed": 0.05  # Slightly slower
}

app = SimpleScrollApp("Custom Alert", styles=custom_alert)
```

## Dynamic Styles

### Color Based on Data

```python
import random

def get_temperature():
    return random.randint(60, 90)

def get_temp_color():
    temp = get_temperature()
    if temp < 70:
        return (0, 0, 255)  # Blue for cold
    elif temp < 80:
        return (0, 255, 0)  # Green for nice
    else:
        return (255, 0, 0)  # Red for hot

app = SimpleScrollApp(
    text_source=lambda: f"Temp: {get_temperature()}°F",
    styles={"text_color": get_temp_color},
    update_interval=2
)
```

### Time-Based Styles

```python
import time

def get_time_based_brightness():
    hour = time.localtime().tm_hour
    if 6 <= hour < 18:  # Daytime
        return 0.5
    else:  # Nighttime
        return 0.1

app = SimpleScrollApp(
    "Hello",
    styles={"brightness": get_time_based_brightness}
)
```

### Rainbow Effect

```python
import math

def rainbow_color():
    # Create color that changes over time
    hue = (time.monotonic() * 30) % 360
    
    # Simple HSV to RGB
    c = 1.0
    x = c * (1 - abs((hue / 60) % 2 - 1))
    
    if hue < 60:
        r, g, b = c, x, 0
    elif hue < 120:
        r, g, b = x, c, 0
    elif hue < 180:
        r, g, b = 0, c, x
    elif hue < 240:
        r, g, b = 0, x, c
    elif hue < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    return (int(r * 255), int(g * 255), int(b * 255))

app = SimpleScrollApp(
    "Rainbow Text!",
    styles={"text_color": rainbow_color}
)
```

## Animation Effects

### Blinking

```python
app = SimpleScrollApp(
    "ALERT",
    styles={
        "text_color": (255, 0, 0),
        "blink": True,
        "blink_rate": 0.5  # Seconds
    }
)
```

### Fade In/Out

```python
app = SimpleScrollApp(
    "Smooth",
    styles={
        "fade_in": True,
        "fade_out": True,
        "fade_duration": 1.0  # Seconds
    }
)
```

### Pulsing Brightness

```python
def pulsing_brightness():
    # Sine wave for smooth pulsing
    return 0.3 + 0.2 * math.sin(time.monotonic() * 2)

app = SimpleScrollApp(
    "Pulse",
    styles={
        "brightness": pulsing_brightness,
        "text_color": (255, 255, 255)
    }
)
```

## Advanced Effects

### Gradient Text

```python
class GradientStyle:
    def __init__(self, color1, color2):
        self.color1 = color1
        self.color2 = color2
    
    def get_color(self, position, total):
        # Linear interpolation between colors
        ratio = position / total
        r = int(self.color1[0] * (1 - ratio) + self.color2[0] * ratio)
        g = int(self.color1[1] * (1 - ratio) + self.color2[1] * ratio)
        b = int(self.color1[2] * (1 - ratio) + self.color2[2] * ratio)
        return (r, g, b)

gradient = GradientStyle((255, 0, 0), (0, 0, 255))  # Red to blue
```

### Fire Effect

```python
import random

def fire_color():
    # Flicker between red and orange
    flicker = random.random()
    if flicker > 0.5:
        return (255, random.randint(100, 200), 0)
    else:
        return (255, random.randint(50, 150), 0)

app = SimpleScrollApp(
    "FIRE!",
    styles={
        "text_color": fire_color,
        "brightness": lambda: 0.3 + random.random() * 0.2
    }
)
```

### Matrix Rain Effect

```python
def matrix_color():
    # Green with random brightness
    brightness = random.randint(100, 255)
    return (0, brightness, 0)

app = SimpleScrollApp(
    "MATRIX",
    styles={
        "text_color": matrix_color,
        "background_color": (0, 20, 0),  # Dark green background
        "font": "matrix"  # If available
    }
)
```

## Font and Layout

### Font Size

```python
# Different font sizes
small_app = SimpleScrollApp(
    "tiny text",
    styles={"font_size": 8}
)

normal_app = SimpleScrollApp(
    "Normal Text",
    styles={"font_size": 12}  # Default
)

large_app = SimpleScrollApp(
    "BIG",
    styles={"font_size": 16}
)
```

### Letter Spacing

```python
# Adjust space between letters
tight_app = SimpleScrollApp(
    "TIGHT",
    styles={"spacing": 0}  # No extra space
)

spaced_app = SimpleScrollApp(
    "S P A C E D",
    styles={"spacing": 2}  # 2 pixels between letters
)
```

## Creating Custom Styles

### Style Class

```python
class CustomStyle:
    """Encapsulate complex styling logic."""
    
    def __init__(self):
        self.start_time = time.monotonic()
    
    def get_styles(self):
        elapsed = time.monotonic() - self.start_time
        
        return {
            "text_color": self.get_color(elapsed),
            "brightness": self.get_brightness(elapsed),
            "scroll_speed": self.get_speed(elapsed)
        }
    
    def get_color(self, elapsed):
        # Change color over time
        if elapsed < 5:
            return (255, 0, 0)  # Red for first 5 seconds
        elif elapsed < 10:
            return (255, 255, 0)  # Yellow
        else:
            return (0, 255, 0)  # Green
    
    def get_brightness(self, elapsed):
        # Fade in
        if elapsed < 2:
            return elapsed / 2
        return 1.0
    
    def get_speed(self, elapsed):
        # Speed up over time
        return min(0.02 + elapsed * 0.001, 0.1)

custom = CustomStyle()
app = SimpleScrollApp(
    "Custom!",
    styles=custom.get_styles
)
```

### Reactive Styles

```python
class ReactiveStyle:
    """Style that reacts to external events."""
    
    def __init__(self):
        self.alert_mode = False
        self.last_update = 0
    
    def check_conditions(self):
        # Check some condition
        if sensor.temperature > 80:
            self.alert_mode = True
        else:
            self.alert_mode = False
    
    def get_color(self):
        if self.alert_mode:
            # Flash red/white in alert mode
            if int(time.monotonic() * 2) % 2:
                return (255, 0, 0)
            else:
                return (255, 255, 255)
        else:
            return (0, 255, 0)  # Green when normal

reactive = ReactiveStyle()
app = SimpleScrollApp(
    "Status",
    styles={"text_color": reactive.get_color}
)
```

## Performance Tips

### 1. Cache Computed Values

```python
# Bad: Computes every frame
def bad_color():
    # Complex calculation every time
    return complex_color_calculation()

# Good: Cache and update periodically
class CachedColor:
    def __init__(self):
        self.color = (255, 255, 255)
        self.last_update = 0
    
    def get_color(self):
        now = time.monotonic()
        if now - self.last_update > 0.5:  # Update every 0.5s
            self.color = self.calculate_color()
            self.last_update = now
        return self.color
```

### 2. Simple Effects

```python
# Simple effects are more efficient

# Good: Simple color
styles = {"text_color": (255, 0, 0)}

# OK: Simple function
styles = {"text_color": lambda: (255, random.randint(0, 100), 0)}

# Expensive: Complex calculation every frame
styles = {"text_color": lambda: complex_rainbow_with_perlin_noise()}
```

### 3. Avoid Allocations

```python
# Bad: Creates new tuple every call
def bad_color():
    return tuple([random.randint(0, 255) for _ in range(3)])

# Good: Reuse color values
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
def good_color():
    return COLORS[int(time.monotonic()) % 3]
```

## Style Combinations

### Weather Dashboard Style

```python
def weather_styles(temp, condition):
    # Base styles
    styles = {
        "scroll_speed": 0.03,
        "font_size": 12
    }
    
    # Color based on temperature
    if temp < 32:
        styles["text_color"] = (100, 100, 255)  # Ice blue
    elif temp < 60:
        styles["text_color"] = (0, 200, 255)  # Cool blue
    elif temp < 80:
        styles["text_color"] = (0, 255, 0)  # Green
    else:
        styles["text_color"] = (255, 100, 0)  # Orange
    
    # Effects based on condition
    if "storm" in condition.lower():
        styles["blink"] = True
        styles["blink_rate"] = 0.2
    elif "rain" in condition.lower():
        styles["brightness"] = 0.2  # Dim for rain
    elif "sun" in condition.lower():
        styles["brightness"] = 0.5  # Bright for sun
    
    return styles
```

### Stock Ticker Style

```python
def stock_styles(price_change):
    if price_change > 0:
        return {
            "text_color": (0, 255, 0),  # Green for up
            "scroll_speed": 0.04
        }
    elif price_change < 0:
        return {
            "text_color": (255, 0, 0),  # Red for down
            "scroll_speed": 0.04
        }
    else:
        return {
            "text_color": (255, 255, 255),  # White for unchanged
            "scroll_speed": 0.04
        }
```

## Debugging Styles

### Style Tester

```python
class StyleTester:
    """Cycle through different styles for testing."""
    
    def __init__(self):
        self.styles = [
            {"text_color": (255, 0, 0), "name": "Red"},
            {"text_color": (0, 255, 0), "name": "Green"},
            {"text_color": (0, 0, 255), "name": "Blue"},
            {"text_color": (255, 255, 255), "brightness": 0.1, "name": "Dim"},
            {"text_color": (255, 255, 255), "brightness": 1.0, "name": "Bright"},
            {"scroll_speed": 0.01, "name": "Slow"},
            {"scroll_speed": 0.1, "name": "Fast"}
        ]
        self.current = 0
    
    def next_style(self):
        self.current = (self.current + 1) % len(self.styles)
        return self.styles[self.current]
    
    def get_text(self):
        style = self.styles[self.current]
        return f"Style: {style['name']}"

tester = StyleTester()
app = SimpleScrollApp(
    text_source=tester.get_text,
    styles=tester.next_style,
    update_interval=3  # Change every 3 seconds
)
```

## Next Steps

- Explore [Presets](PRESETS.md) with pre-made style combinations
- Learn about [Board Configuration](BOARDS.md) for hardware-specific styling
- See [API Reference](API_REFERENCE.md#styles) for all style options