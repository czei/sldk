"""Level 6: Custom Board Configurations

This example shows how to configure the framework for different
hardware setups and create custom board definitions.

What you'll learn:
- Configuring for specific boards
- Custom pin mappings
- Different display types
- Hardware-specific features
"""

from cpyapp import SimpleScrollApp
from cpyapp.boards import BoardConfig, BOARD_PRESETS

# Example 1: Using a predefined board configuration
# The framework auto-detects common boards, but you can be explicit
app = SimpleScrollApp(
    "Hello MatrixPortal!",
    board="matrixportal_s3"  # Explicitly specify board
)

# Available board presets:
# - "matrixportal_s3": Adafruit MatrixPortal S3
# - "matrixportal_m4": Adafruit MatrixPortal M4
# - "led_glasses": Adafruit LED Glasses
# - "led_matrix_featherwing": Adafruit RGB Matrix FeatherWing
# - "metro_m4_matrix": Metro M4 with RGB Matrix Shield

# Example 2: Custom pin configuration
# For boards not in the presets
custom_board = BoardConfig(
    name="my_custom_board",
    # Display size
    width=64,
    height=32,
    # Pin mappings for RGB Matrix
    rgb_pins={
        "r1": "GP2", "g1": "GP3", "b1": "GP4",
        "r2": "GP5", "g2": "GP8", "b2": "GP9",
        "a": "GP10", "b": "GP16", "c": "GP18",
        "d": "GP20", "e": "GP22",  # For 64x64 displays
        "clk": "GP11", "lat": "GP12", "oe": "GP13"
    },
    # Board features
    has_wifi=True,
    has_bluetooth=False,
    has_battery_monitor=True,
    # Memory constraints
    heap_size=192 * 1024,  # 192KB heap
    # Special features
    features=["STEMMA_QT", "NEOPIXEL_STATUS"]
)

app_custom = SimpleScrollApp(
    "Custom Board!",
    board=custom_board
)

# Example 3: Different display types
# 16x32 display configuration
small_display = BoardConfig(
    name="small_matrix",
    width=32,
    height=16,
    bit_depth=4,  # Lower bit depth for smaller displays
    rgb_pins=BOARD_PRESETS["matrixportal_s3"].rgb_pins  # Reuse pins
)

small_app = SimpleScrollApp(
    "Tiny!",
    board=small_display,
    styles={
        "font_size": 8,  # Smaller font for small display
        "scroll_speed": 0.03  # Slower for readability
    }
)

# Example 4: Board with special hardware
# E.g., board with temperature sensor and buttons
class SensorBoard(BoardConfig):
    """Board with integrated sensors."""
    
    def __init__(self):
        super().__init__(
            name="sensor_board",
            width=64,
            height=32,
            has_wifi=True,
            features=["TEMPERATURE_SENSOR", "BUTTONS"]
        )
        
        # Initialize hardware
        import board
        import digitalio
        import adafruit_ahtx0
        
        # Temperature sensor on I2C
        i2c = board.I2C()
        self.sensor = adafruit_ahtx0.AHTx0(i2c)
        
        # Buttons
        self.button_a = digitalio.DigitalInOut(board.BUTTON_A)
        self.button_a.switch_to_input(pull=digitalio.Pull.UP)
        
    def get_temperature(self):
        """Read temperature from sensor."""
        return self.sensor.temperature * 9/5 + 32  # Convert to F
    
    def is_button_pressed(self):
        """Check if button A is pressed."""
        return not self.button_a.value

# Use the sensor board
sensor_board = SensorBoard()

def show_sensor_data():
    """Display temperature and button state."""
    temp = sensor_board.get_temperature()
    button = "Pressed" if sensor_board.is_button_pressed() else "Released"
    return f"Temp: {temp:.1f}°F Button: {button}"

sensor_app = SimpleScrollApp(
    text_source=show_sensor_data,
    board=sensor_board,
    update_interval=0.5
)

# Example 5: Board-specific optimizations
# Different boards have different capabilities
if BoardConfig.current_board_has_feature("WIFI"):
    # Use network features
    from cpyapp.data import URLDataSource
    data_source = URLDataSource("https://api.example.com/data")
else:
    # Fall back to local data
    from cpyapp.data import FileDataSource
    data_source = FileDataSource("/data.json")

# Example 6: Memory-constrained boards
# Adjust behavior based on available memory
import gc

low_memory_board = BoardConfig(
    name="tiny_board",
    width=32,
    height=16,
    heap_size=64 * 1024  # Only 64KB
)

if low_memory_board.heap_size < 128 * 1024:
    # Use memory-efficient settings
    app_config = {
        "buffer_size": 512,  # Smaller buffer
        "cache_size": 5,  # Less caching
        "update_interval": 2  # Less frequent updates
    }
else:
    # Use normal settings
    app_config = {
        "buffer_size": 2048,
        "cache_size": 20,
        "update_interval": 1
    }

# Example 7: Display chain configuration
# For multiple chained displays
chained_display = BoardConfig(
    name="chained_matrix",
    width=128,  # Two 64x32 displays side by side
    height=32,
    chain_length=2,
    parallel_chains=1,
    tile_rows=1,
    tile_columns=2
)

wide_app = SimpleScrollApp(
    "This is a very wide display that spans across two matrices!",
    board=chained_display
)

# Run the app
app.run()