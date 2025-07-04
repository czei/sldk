# API Reference

Complete API documentation for the CircuitPython App Framework.

## Table of Contents

- [SimpleScrollApp](#simplescrollapp)
- [BaseApplication](#baseapplication)
- [Data Sources](#data-sources)
- [Styles](#styles)
- [Board Configuration](#board-configuration)
- [Presets](#presets)
- [Plugins](#plugins)
- [Utilities](#utilities)

## SimpleScrollApp

The easiest way to create a scrolling text display.

### Constructor

```python
SimpleScrollApp(
    text_source=None,
    *,
    preset=None,
    styles=None,
    board=None,
    update_interval=None,
    plugins=None
)
```

#### Parameters

- **text_source** (str | callable | None): The text to display
  - `str`: Static text that never changes
  - `callable`: Function that returns text (called periodically)
  - `None`: Use a preset instead

- **preset** (Preset | None): A preset application configuration
  - Takes precedence over text_source if both provided
  - See [Presets](#presets) section

- **styles** (dict | None): Visual styling options
  - `text_color`: RGB tuple like (255, 0, 0) for red
  - `brightness`: Float 0.0-1.0, default 0.3
  - `scroll_speed`: Float, pixels per second, default 0.04
  - `font_size`: Int, height in pixels, default 12
  - See [Styles](#styles) section for all options

- **board** (str | BoardConfig | None): Hardware configuration
  - `str`: Board name like "matrixportal_s3"
  - `BoardConfig`: Custom board configuration
  - `None`: Auto-detect board

- **update_interval** (float | None): How often to update text in seconds
  - Only used when text_source is a callable
  - `None` means never update (static text)
  - Default depends on preset or 60 seconds

- **plugins** (list[Plugin] | None): Optional plugins to extend functionality

### Methods

#### run()

Start the application main loop.

```python
app = SimpleScrollApp("Hello")
app.run()  # Blocks forever
```

### Examples

```python
# Static text
app = SimpleScrollApp("Hello World!")

# Dynamic text
app = SimpleScrollApp(
    text_source=lambda: time.strftime("%H:%M:%S"),
    update_interval=1
)

# With styling
app = SimpleScrollApp(
    "Alert!",
    styles={"text_color": (255, 0, 0), "brightness": 0.5}
)

# Using preset
from cpyapp.presets import ClockPreset
app = SimpleScrollApp(preset=ClockPreset())
```

## BaseApplication

Base class for creating custom applications with full control.

### Constructor

```python
BaseApplication(config_file="config.json")
```

### Methods to Override

#### async initialize()

Called once at startup. Initialize your components here.

```python
async def initialize(self):
    await super().initialize()
    self.my_data = await self.load_data()
```

#### async update_data()

Called periodically to fetch new data.

```python
async def update_data(self):
    response = await self.http_client.get("https://api.example.com/data")
    return response.json()
```

#### create_display_content(data)

Convert data into display messages.

```python
def create_display_content(self, data):
    messages = []
    for item in data:
        messages.append(DisplayMessage(
            text=item["name"],
            color=(255, 255, 255),
            duration=5
        ))
    return messages
```

#### async run()

Main application loop.

```python
async def run(self):
    await self.initialize()
    
    while True:
        data = await self.update_data()
        messages = self.create_display_content(data)
        self.display_queue.set_messages(messages)
        await asyncio.sleep(60)
```

### Properties

- **config**: Configuration manager
- **display**: Display hardware interface
- **network**: Network manager
- **http_client**: HTTP client for API calls
- **error_handler**: Centralized error handling

## Data Sources

Classes for fetching data from various sources.

### URLDataSource

Fetch data from HTTP endpoints.

```python
from cpyapp.data import URLDataSource

source = URLDataSource(
    url="https://api.example.com/data",
    json_path="results.0.value",  # Optional: extract nested JSON
    cache_duration=300,  # Cache for 5 minutes
    headers={"Authorization": "Bearer token"},  # Optional
    fallback="No data"  # Shown on error
)

# Get data synchronously
value = source.get()

# Get data asynchronously
value = await source.get_async()

# Get full response
data = source.get_raw()
```

### FileDataSource

Read data from local files.

```python
from cpyapp.data import FileDataSource

source = FileDataSource(
    path="/data.json",
    json_path="config.setting",
    watch=True,  # Auto-reload on change
    fallback={}
)
```

### FunctionDataSource

Wrap a function as a data source.

```python
from cpyapp.data import FunctionDataSource

def get_sensor_data():
    return sensor.temperature

source = FunctionDataSource(
    function=get_sensor_data,
    cache_duration=10,
    fallback=0
)
```

### Custom Data Sources

Create your own by inheriting from DataSource:

```python
from cpyapp.data import DataSource

class SensorDataSource(DataSource):
    def __init__(self, sensor, **kwargs):
        super().__init__(**kwargs)
        self.sensor = sensor
    
    def fetch(self):
        return {
            "temperature": self.sensor.temperature,
            "humidity": self.sensor.humidity
        }
```

## Styles

Visual styling system for displays.

### Style Options

```python
styles = {
    # Text appearance
    "text_color": (255, 255, 255),  # RGB tuple
    "background_color": (0, 0, 0),  # RGB tuple
    "brightness": 0.3,  # 0.0 to 1.0
    
    # Text rendering
    "font_size": 12,  # Height in pixels
    "font": "default",  # Font name
    "spacing": 1,  # Letter spacing
    
    # Animation
    "scroll_speed": 0.04,  # Pixels per frame
    "scroll_delay": 0,  # Pause before scrolling
    "wrap": False,  # Wrap text instead of scroll
    
    # Effects
    "blink": False,  # Blinking text
    "blink_rate": 0.5,  # Seconds
    "fade_in": False,  # Fade in effect
    "fade_out": False,  # Fade out effect
    "rainbow": False,  # Rainbow color effect
}
```

### Style Presets

```python
from cpyapp.styles import STYLE_PRESETS

# Available presets
STYLE_PRESETS["default"]  # White text, normal speed
STYLE_PRESETS["alert"]    # Red, fast, bright
STYLE_PRESETS["success"]  # Green
STYLE_PRESETS["warning"]  # Yellow
STYLE_PRESETS["info"]     # Blue
STYLE_PRESETS["stealth"]  # Dim white
```

### Dynamic Styles

Styles can be functions for dynamic effects:

```python
def dynamic_color():
    # Change color based on time
    hour = time.localtime().tm_hour
    if hour < 12:
        return (255, 255, 0)  # Yellow morning
    else:
        return (0, 0, 255)  # Blue afternoon

styles = {
    "text_color": dynamic_color,
    "brightness": lambda: 0.8 if is_day() else 0.2
}
```

## Board Configuration

### Built-in Boards

```python
from cpyapp.boards import BOARD_PRESETS

# Available boards
BOARD_PRESETS["matrixportal_s3"]     # Adafruit MatrixPortal S3
BOARD_PRESETS["matrixportal_m4"]     # Adafruit MatrixPortal M4  
BOARD_PRESETS["led_glasses"]         # Adafruit LED Glasses
BOARD_PRESETS["rgb_matrix_featherwing"]  # FeatherWing
```

### Custom Board

```python
from cpyapp.boards import BoardConfig

custom = BoardConfig(
    name="my_board",
    width=64,
    height=32,
    bit_depth=5,
    rgb_pins={
        "r1": "GP2", "g1": "GP3", "b1": "GP4",
        "r2": "GP5", "g2": "GP8", "b2": "GP9",
        "a": "GP10", "b": "GP16", "c": "GP18",
        "d": "GP20", "e": "GP22",
        "clk": "GP11", "lat": "GP12", "oe": "GP13"
    },
    has_wifi=True,
    has_bluetooth=False
)

app = SimpleScrollApp("Custom!", board=custom)
```

## Presets

Ready-to-use application templates.

### ClockPreset

```python
from cpyapp.presets import ClockPreset

clock = ClockPreset(
    format_24h=True,    # 24-hour format
    show_seconds=True,  # Include seconds  
    show_date=False,    # Include date
    timezone=None       # Local time
)
```

### WeatherPreset

```python
from cpyapp.presets import WeatherPreset

weather = WeatherPreset(
    api_key="your_key",
    city="Orlando",
    units="imperial",   # or "metric"
    show_forecast=False,
    update_interval=300
)
```

### StockTickerPreset

```python
from cpyapp.presets import StockTickerPreset

stocks = StockTickerPreset(
    symbols=["AAPL", "GOOGL", "MSFT"],
    api_key="your_key",
    show_change=True,
    show_percent=True,
    update_interval=60
)
```

### Custom Preset

```python
class MyPreset:
    def __init__(self, param="default"):
        self.param = param
    
    def get_text(self):
        return f"Custom: {self.param}"
    
    def get_update_interval(self):
        return 30
    
    def get_styles(self):
        return {"text_color": (0, 255, 0)}
```

## Plugins

Extend functionality with plugins.

### Creating a Plugin

```python
from cpyapp.plugins import Plugin

class TemperatureAlertPlugin(Plugin):
    def __init__(self, threshold=80):
        super().__init__("temp_alert")
        self.threshold = threshold
    
    async def initialize(self, app):
        self.app = app
        self.sensor = app.get_sensor()
    
    async def update(self):
        temp = self.sensor.temperature
        if temp > self.threshold:
            await self.show_alert(f"High temp: {temp}!")
    
    async def show_alert(self, message):
        # Override display temporarily
        self.app.display_override(message, duration=5)
```

### Using Plugins

```python
app = SimpleScrollApp(
    "Normal display",
    plugins=[
        TemperatureAlertPlugin(threshold=85),
        MemoryMonitorPlugin(),
        WebServerPlugin(port=80)
    ]
)
```

## Utilities

### ErrorHandler

```python
from cpyapp.utils import ErrorHandler

handler = ErrorHandler(
    log_to_file=True,
    log_file="/errors.log",
    max_retries=3,
    backoff_factor=2.0
)

try:
    risky_operation()
except Exception as e:
    handler.log(f"Operation failed: {e}")
    handler.handle_error(e)
```

### ConfigManager

```python
from cpyapp.utils import ConfigManager

config = ConfigManager("settings.json")

# Get with default
value = config.get("key", default="default")

# Set value
config.set("key", "value")

# Save to file
config.save()

# Validate types
config.get_int("port", default=80)
config.get_float("brightness", default=0.3)
config.get_bool("enabled", default=True)
```

### StateManager

```python
from cpyapp.utils import StateManager

state = StateManager(
    "state.json",
    auto_save=True,
    save_interval=60
)

# Track state
state.set("last_run", time.time())
state.increment("run_count")

# Get state
count = state.get("run_count", 0)
```

## Display Components

### DisplayMessage

```python
from cpyapp.display import DisplayMessage

msg = DisplayMessage(
    text="Hello",
    color=(255, 0, 0),
    brightness=0.5,
    duration=5,  # Seconds to display
    scroll_speed=0.04,
    priority=0  # Higher = more important
)
```

### ScrollingText

```python
from cpyapp.display import ScrollingText

scroller = ScrollingText(
    display=matrix_display,
    text="Long text that scrolls",
    color=(255, 255, 255),
    speed=0.04
)

while True:
    scroller.update()
    time.sleep(0.01)
```

## Network Components

### NetworkManager

```python
from cpyapp.network import NetworkManager

network = NetworkManager()

# Connect to WiFi
await network.connect(ssid="MyWiFi", password="password")

# Check status
if network.is_connected():
    ip = network.ip_address
    signal = network.signal_strength

# Disconnect
await network.disconnect()
```

### HTTPClient

```python
from cpyapp.network import HTTPClient

client = HTTPClient()

# GET request
response = await client.get(
    "https://api.example.com/data",
    headers={"Accept": "application/json"}
)
data = response.json()

# POST request
response = await client.post(
    "https://api.example.com/submit",
    json={"key": "value"},
    timeout=10
)
```

## Constants

```python
from cpyapp import constants

# Version info
constants.VERSION  # Framework version
constants.MIN_CIRCUITPYTHON  # Minimum CP version

# Display defaults
constants.DEFAULT_BRIGHTNESS  # 0.3
constants.DEFAULT_SCROLL_SPEED  # 0.04
constants.DEFAULT_FONT_SIZE  # 12

# Network timeouts
constants.HTTP_TIMEOUT  # 10 seconds
constants.WIFI_TIMEOUT  # 30 seconds

# Update intervals
constants.MIN_UPDATE_INTERVAL  # 0.1 seconds
constants.DEFAULT_UPDATE_INTERVAL  # 60 seconds
```