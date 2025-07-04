# Board Configuration Guide

Learn how to configure the CircuitPython App Framework for different LED matrix hardware.

## Supported Boards

### Adafruit MatrixPortal S3

The recommended board with built-in WiFi and plenty of memory.

```python
from cpyapp import SimpleScrollApp

# Auto-detected by default
app = SimpleScrollApp("Hello MatrixPortal S3!")

# Or explicitly specify
app = SimpleScrollApp(
    "Hello",
    board="matrixportal_s3"
)
```

**Specifications:**
- ESP32-S3 processor
- 8MB Flash, 2MB PSRAM
- Built-in WiFi
- Designed for 64x32 RGB matrices
- STEMMA QT connector

### Adafruit MatrixPortal M4

The original MatrixPortal with SAMD51.

```python
app = SimpleScrollApp(
    "Hello M4!",
    board="matrixportal_m4"
)
```

**Specifications:**
- ATSAMD51J19 processor
- 512KB Flash, 192KB RAM
- External ESP32 for WiFi
- 64x32 RGB matrix support

### Adafruit LED Glasses

Wearable LED matrix glasses.

```python
app = SimpleScrollApp(
    "Cool!",
    board="led_glasses",
    styles={
        "font_size": 5,  # Tiny font for small display
        "scroll_speed": 0.02  # Slower for readability
    }
)
```

**Specifications:**
- nRF52840 processor
- 18x5 LED matrix per eye
- Bluetooth capable
- Battery powered

### RGB Matrix FeatherWing

For Feather boards with RGB matrix shield.

```python
app = SimpleScrollApp(
    "Feather",
    board="rgb_matrix_featherwing"
)
```

## Custom Board Configuration

### Basic Custom Board

```python
from cpyapp.boards import BoardConfig

custom_board = BoardConfig(
    name="my_custom_board",
    width=64,
    height=32,
    bit_depth=5  # Color depth (1-6)
)

app = SimpleScrollApp("Custom!", board=custom_board)
```

### Full Pin Mapping

```python
custom_board = BoardConfig(
    name="custom_rgb_matrix",
    width=64,
    height=32,
    rgb_pins={
        # Upper half pins
        "r1": "GP2",   # Red 1
        "g1": "GP3",   # Green 1
        "b1": "GP4",   # Blue 1
        # Lower half pins
        "r2": "GP5",   # Red 2
        "g2": "GP8",   # Green 2
        "b2": "GP9",   # Blue 2
        # Address pins
        "a": "GP10",   # Address A
        "b": "GP16",   # Address B
        "c": "GP18",   # Address C
        "d": "GP20",   # Address D (32+ pixel high)
        "e": "GP22",   # Address E (64+ pixel high)
        # Control pins
        "clk": "GP11", # Clock
        "lat": "GP12", # Latch
        "oe": "GP13"   # Output Enable
    }
)
```

### Board Features

```python
feature_board = BoardConfig(
    name="advanced_board",
    width=64,
    height=32,
    # Hardware features
    has_wifi=True,
    has_bluetooth=True,
    has_battery_monitor=True,
    # Memory info
    heap_size=192 * 1024,  # 192KB
    stack_size=8 * 1024,   # 8KB
    # Special features
    features=[
        "STEMMA_QT",      # I2C connector
        "NEOPIXEL_STATUS", # Status LED
        "SD_CARD",         # SD card slot
        "ACCELEROMETER"    # Motion sensor
    ]
)
```

## Display Configurations

### Different Matrix Sizes

```python
# 32x16 display
small_matrix = BoardConfig(
    name="small_display",
    width=32,
    height=16,
    bit_depth=4  # Lower bit depth for performance
)

# 64x64 display
large_matrix = BoardConfig(
    name="large_display",
    width=64,
    height=64,
    rgb_pins={
        # ... includes d and e pins for 64 height
    }
)

# 128x32 (two panels chained)
wide_matrix = BoardConfig(
    name="chained_display",
    width=128,
    height=32,
    chain_length=2,  # Two 64x32 panels
    parallel_chains=1
)
```

### Tiled Displays

```python
# 2x2 tile of 64x32 displays
tiled_display = BoardConfig(
    name="tiled_matrix",
    width=128,
    height=64,
    tile_rows=2,
    tile_columns=2,
    chain_length=4,  # Total panels
    serpentine=True  # Zigzag wiring
)
```

## Board-Specific Features

### WiFi Configuration

```python
class WiFiBoardConfig(BoardConfig):
    def __init__(self):
        super().__init__(
            name="wifi_board",
            has_wifi=True
        )
    
    def setup_wifi(self):
        """Board-specific WiFi setup."""
        import wifi
        import socketpool
        
        # Custom WiFi configuration
        wifi.radio.mac_address = b"custom_mac"
        wifi.radio.tx_power = 20  # dBm
        
        return socketpool.SocketPool(wifi.radio)
```

### Sensor Integration

```python
class SensorBoardConfig(BoardConfig):
    def __init__(self):
        super().__init__(
            name="sensor_board",
            features=["TEMPERATURE_SENSOR", "LIGHT_SENSOR"]
        )
        self.setup_sensors()
    
    def setup_sensors(self):
        import board
        import adafruit_ahtx0
        import analogio
        
        # Temperature/humidity sensor
        i2c = board.I2C()
        self.temp_sensor = adafruit_ahtx0.AHTx0(i2c)
        
        # Light sensor
        self.light_sensor = analogio.AnalogIn(board.A0)
    
    def get_sensor_data(self):
        return {
            "temperature": self.temp_sensor.temperature,
            "humidity": self.temp_sensor.humidity,
            "light": self.light_sensor.value
        }
```

### Battery Monitoring

```python
class BatteryBoardConfig(BoardConfig):
    def __init__(self):
        super().__init__(
            name="battery_board",
            has_battery_monitor=True
        )
        self.setup_battery_monitor()
    
    def setup_battery_monitor(self):
        import board
        import analogio
        
        # Battery voltage divider on A6
        self.battery = analogio.AnalogIn(board.BATTERY)
    
    def get_battery_voltage(self):
        # Convert ADC to voltage (assuming 2:1 divider)
        return (self.battery.value * 3.3 / 65536) * 2
    
    def get_battery_percent(self):
        voltage = self.get_battery_voltage()
        # LiPo battery: 4.2V = 100%, 3.0V = 0%
        percent = (voltage - 3.0) / (4.2 - 3.0) * 100
        return max(0, min(100, percent))
```

## Memory Optimization

### Low Memory Boards

```python
class LowMemoryBoardConfig(BoardConfig):
    def __init__(self):
        super().__init__(
            name="tiny_board",
            heap_size=64 * 1024  # Only 64KB
        )
    
    def get_optimized_settings(self):
        """Settings optimized for low memory."""
        return {
            "display_buffer_size": 512,  # Smaller buffer
            "message_queue_size": 5,     # Fewer messages
            "cache_size": 3,             # Minimal cache
            "font_size": 8,              # Smaller font
            "bit_depth": 3               # Lower color depth
        }
```

### Memory Usage by Board

```python
# Memory recommendations by board type
MEMORY_PROFILES = {
    "high_memory": {  # 256KB+ RAM
        "buffer_size": 4096,
        "cache_entries": 20,
        "history_size": 100,
        "concurrent_tasks": 5
    },
    "medium_memory": {  # 128-256KB RAM
        "buffer_size": 2048,
        "cache_entries": 10,
        "history_size": 50,
        "concurrent_tasks": 3
    },
    "low_memory": {  # <128KB RAM
        "buffer_size": 512,
        "cache_entries": 5,
        "history_size": 10,
        "concurrent_tasks": 1
    }
}

def get_memory_profile(board_config):
    if board_config.heap_size >= 256 * 1024:
        return MEMORY_PROFILES["high_memory"]
    elif board_config.heap_size >= 128 * 1024:
        return MEMORY_PROFILES["medium_memory"]
    else:
        return MEMORY_PROFILES["low_memory"]
```

## Board Detection

### Automatic Detection

```python
from cpyapp.boards import detect_board

# Detect current board
board_type = detect_board()
print(f"Detected: {board_type}")

# The framework does this automatically
app = SimpleScrollApp("Auto-detected!")
```

### Manual Override

```python
# Force specific board even if different detected
import os
os.environ["CPYAPP_BOARD"] = "matrixportal_s3"

app = SimpleScrollApp("Forced board type")
```

## Hardware Setup

### Wiring Guide

```
RGB Matrix Panel         MatrixPortal
-----------------       -------------
R1  ----------------->  R0
G1  ----------------->  G0
B1  ----------------->  B0
R2  ----------------->  R1
G2  ----------------->  G1
B2  ----------------->  B1
A   ----------------->  A
B   ----------------->  B
C   ----------------->  C
D   ----------------->  D
CLK ----------------->  CLK
LAT ----------------->  LAT
OE  ----------------->  OE
GND ----------------->  GND
```

### Power Requirements

```python
def calculate_power_requirements(board_config):
    """Calculate power needs for LED matrix."""
    pixels = board_config.width * board_config.height
    
    # Assume 60mA per pixel at full white
    max_current_ma = pixels * 60
    
    # Typical usage is ~20% of max
    typical_current_ma = max_current_ma * 0.2
    
    # Add board overhead
    board_current_ma = 200  # ESP32 + peripherals
    
    return {
        "max_current_ma": max_current_ma + board_current_ma,
        "typical_current_ma": typical_current_ma + board_current_ma,
        "recommended_supply": "5V " + 
            f"{(max_current_ma + board_current_ma) / 1000:.1f}A"
    }

# Example for 64x32 matrix
power = calculate_power_requirements(BoardConfig(width=64, height=32))
print(f"Recommended PSU: {power['recommended_supply']}")
# Output: "Recommended PSU: 5V 123.2A"
```

## Testing Custom Boards

### Board Test Suite

```python
class BoardTester:
    """Test custom board configurations."""
    
    def __init__(self, board_config):
        self.board = board_config
    
    def test_display(self):
        """Test basic display functionality."""
        print("Testing display...")
        
        # Test each color
        for color_name, color in [
            ("Red", (255, 0, 0)),
            ("Green", (0, 255, 0)),
            ("Blue", (0, 0, 255)),
            ("White", (255, 255, 255))
        ]:
            app = SimpleScrollApp(
                f"Testing {color_name}",
                board=self.board,
                styles={"text_color": color}
            )
            # Run for a few seconds
            # app.run_for(seconds=3)
    
    def test_memory(self):
        """Test memory limits."""
        import gc
        
        gc.collect()
        before = gc.mem_free()
        
        # Create app
        app = SimpleScrollApp("Memory Test", board=self.board)
        
        gc.collect()
        after = gc.mem_free()
        
        print(f"App uses {before - after} bytes")
    
    def test_features(self):
        """Test board-specific features."""
        if self.board.has_wifi:
            print("Testing WiFi...")
            # WiFi tests
        
        if "TEMPERATURE_SENSOR" in self.board.features:
            print("Testing temperature sensor...")
            # Sensor tests

# Run tests
tester = BoardTester(custom_board)
tester.test_display()
tester.test_memory()
tester.test_features()
```

## Troubleshooting

### Display Issues

1. **Nothing displays**
   - Check power to matrix (needs 5V supply)
   - Verify pin connections
   - Try lower bit_depth (3 or 4)

2. **Wrong colors**
   - RGB pins may be swapped
   - Check color channel mapping

3. **Flickering**
   - Increase bit_depth
   - Check OE pin connection
   - Ensure adequate power supply

### Board Not Detected

```python
# Debug board detection
import board
import os

print(f"Board ID: {os.uname().machine}")
print(f"Board module: {board.board_id}")

# List all pins
for pin in dir(board):
    if not pin.startswith("_"):
        print(f"  {pin}")
```

### Memory Issues

```python
# Check available memory
import gc

gc.collect()
print(f"Free memory: {gc.mem_free()} bytes")

# For low memory boards
if gc.mem_free() < 50000:  # Less than 50KB
    # Use minimal configuration
    app = SimpleScrollApp(
        "Low Mem",
        board=BoardConfig(
            name="minimal",
            width=32,
            height=16,
            bit_depth=3
        )
    )
```

## Next Steps

- See [Examples](../examples/) for board-specific demos
- Read [Deployment Guide](DEPLOYMENT.md) for installation
- Check [API Reference](API_REFERENCE.md#board-configuration) for all options