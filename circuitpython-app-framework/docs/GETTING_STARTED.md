# Getting Started with CircuitPython App Framework

Welcome! This guide will walk you through creating your first LED matrix application in minutes.

## Prerequisites

### Hardware
- An LED matrix display (64x32 recommended)
- A compatible board:
  - Adafruit MatrixPortal S3 (recommended)
  - Adafruit MatrixPortal M4
  - Any CircuitPython board with RGB matrix support

### Software
- [CircuitPython 8.x or 9.x](https://circuitpython.org/downloads)
- A text editor (VS Code, Mu, or any editor)
- (Optional) Python 3.8+ for desktop development

## Installation

### Step 1: Install CircuitPython

1. Download CircuitPython for your board from [circuitpython.org](https://circuitpython.org/downloads)
2. Connect your board via USB
3. Double-press the reset button to enter bootloader mode
4. Copy the CircuitPython UF2 file to the bootloader drive
5. Your board will restart with CircuitPython installed

### Step 2: Install the Framework

1. Download the framework:
   ```bash
   git clone https://github.com/yourusername/circuitpython-app-framework.git
   ```

2. Copy to your CIRCUITPY drive:
   ```bash
   cp -r circuitpython-app-framework/src/cpyapp /Volumes/CIRCUITPY/
   ```

### Step 3: Install Required Libraries

Download these from the [CircuitPython Library Bundle](https://circuitpython.org/libraries):

- `adafruit_matrixportal`
- `adafruit_display_text`
- `adafruit_requests`

Copy them to `/Volumes/CIRCUITPY/lib/`

## Your First App

### Hello World

Create a file called `code.py` on your CIRCUITPY drive:

```python
from cpyapp import SimpleScrollApp

app = SimpleScrollApp("Hello World!")
app.run()
```

Save the file and your LED matrix will start scrolling "Hello World!"

### Understanding What Happened

1. `SimpleScrollApp` is a convenience class that handles all the setup
2. It automatically:
   - Detects your board type
   - Initializes the display
   - Creates a scrolling text renderer
   - Manages the display loop

## Next Steps

### 1. Dynamic Content

Show the current time:

```python
import time
from cpyapp import SimpleScrollApp

app = SimpleScrollApp(
    text_source=lambda: time.strftime("%H:%M:%S"),
    update_interval=1
)
app.run()
```

### 2. Add Color

Make it colorful:

```python
from cpyapp import SimpleScrollApp

app = SimpleScrollApp(
    "Rainbow Text!",
    styles={
        "text_color": (255, 0, 255),  # Purple
        "brightness": 0.5
    }
)
app.run()
```

### 3. Internet Data

Show a random quote:

```python
from cpyapp import SimpleScrollApp
from cpyapp.data import URLDataSource

# First, set up WiFi in secrets.py:
# secrets = {
#     "ssid": "YourWiFiName",
#     "password": "YourWiFiPassword"
# }

quote_source = URLDataSource(
    url="https://api.quotable.io/random",
    json_path="content"
)

app = SimpleScrollApp(
    text_source=lambda: f"Quote: {quote_source.get()}",
    update_interval=300  # New quote every 5 minutes
)
app.run()
```

## Common Patterns

### Temperature Display with Color

```python
from cpyapp import SimpleScrollApp
import random  # Simulated temperature

def get_temp():
    return random.randint(60, 90)

def get_temp_text():
    temp = get_temp()
    return f"Temp: {temp}°F"

def get_temp_color():
    temp = get_temp()
    if temp < 70:
        return (0, 0, 255)  # Blue for cold
    elif temp < 80:
        return (0, 255, 0)  # Green for nice
    else:
        return (255, 0, 0)  # Red for hot

app = SimpleScrollApp(
    text_source=get_temp_text,
    styles={
        "text_color": get_temp_color,
        "brightness": 0.3
    },
    update_interval=5
)
app.run()
```

### Multiple Messages

```python
from cpyapp import SimpleScrollApp
import time

class MessageRotator:
    def __init__(self):
        self.messages = [
            "Welcome!",
            "Time: {time}",
            "Have a great day!"
        ]
        self.index = 0
    
    def get_message(self):
        msg = self.messages[self.index]
        if "{time}" in msg:
            msg = msg.format(time=time.strftime("%H:%M"))
        
        self.index = (self.index + 1) % len(self.messages)
        return msg

rotator = MessageRotator()
app = SimpleScrollApp(
    text_source=rotator.get_message,
    update_interval=5  # Change message every 5 seconds
)
app.run()
```

## Troubleshooting

### Display Not Working

1. Check connections - ensure matrix is properly connected
2. Verify power - LED matrices need external 5V power
3. Check board type - some boards need explicit configuration:
   ```python
   app = SimpleScrollApp("Test", board="matrixportal_s3")
   ```

### WiFi Issues

1. Create `secrets.py` with your credentials:
   ```python
   secrets = {
       "ssid": "Your_Network_Name",
       "password": "Your_Password"
   }
   ```

2. Check signal strength - move closer to router
3. Verify 2.4GHz network (5GHz not supported)

### Memory Errors

1. Reduce update frequency:
   ```python
   app = SimpleScrollApp("Text", update_interval=10)  # Update less often
   ```

2. Simplify your code - remove unused imports
3. Use `.mpy` compiled libraries when available

### Import Errors

If you get "No module named 'cpyapp'":
1. Verify the framework is in the right location: `/CIRCUITPY/cpyapp/`
2. Check that `__init__.py` exists in the cpyapp folder
3. Try importing directly: `from cpyapp.simple import SimpleScrollApp`

## Desktop Development

You can develop without hardware using the simulator:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run your app
python code.py
```

The simulator will open a window showing your LED matrix.

## What's Next?

- Read about [Data Sources](DATA_SOURCES.md) to fetch data from APIs
- Learn the [Style System](STYLES.md) for animations and effects
- Explore [Built-in Presets](PRESETS.md) for ready-made apps
- See [Architecture](ARCHITECTURE.md) to understand how it works
- Check [API Reference](API_REFERENCE.md) for all options

## Getting Help

- Check the [examples folder](../examples/) for more code
- Visit the [CircuitPython Discord](https://adafru.it/discord)
- Post issues on [GitHub](https://github.com/yourusername/circuitpython-app-framework/issues)
- Read the [Adafruit Learn Guides](https://learn.adafruit.com/)

Happy making! 🎉