# Board Configuration System

The board configuration system provides a unified interface for hardware abstraction across different CircuitPython boards and development environments.

## Features

- **Automatic Board Detection**: Automatically detects the current hardware platform
- **Built-in Configurations**: Pre-configured support for popular boards
- **Custom Board Support**: Easy creation of custom board configurations
- **Hardware Abstraction**: Unified interface for displays, networking, power, etc.
- **Settings Management**: Board-specific settings with persistence
- **Development Mode**: Seamless switching between hardware and simulator

## Quick Start

```python
from cpyapp.boards import create_board

# Auto-detect the current board
board = create_board('auto')

# Or specify a board explicitly
board = create_board('matrixportal_s3')

# Set up hardware components
display = board.setup_display()
network = board.setup_network()

# Check capabilities
if board.has_capability(BoardCapabilities.HAS_WIFI):
    print(f"{board.display_name} has WiFi support")
```

## Built-in Boards

### MatrixPortal S3
- 64x32 RGB LED Matrix
- Native ESP32-S3 WiFi
- Accelerometer and NeoPixel
- QSPI Flash storage

### MatrixPortal M4
- 64x32 RGB LED Matrix  
- ESP32 WiFi co-processor
- Accelerometer and NeoPixel
- QSPI Flash storage

### Raspberry Pi
- Support for RGB LED HATs/Bonnets
- Native WiFi and Ethernet
- SD card storage
- Full Linux capabilities

### Simulator
- Development environment
- Virtual 64x32 display
- Simulated network and sensors
- Perfect for testing

## Creating Custom Boards

### Method 1: JSON Configuration

Create a `my_board.json` file:

```json
{
  "name": "my_custom_board",
  "display_name": "My Custom Board",
  "manufacturer": "My Company",
  "capabilities": [
    "HAS_RGB_MATRIX",
    "HAS_WIFI"
  ],
  "display": {
    "type": "rgb_matrix",
    "width": 64,
    "height": 32,
    "bit_depth": 4
  },
  "network": {
    "type": "wifi",
    "module": "native"
  },
  "pins": {
    "button_1": "D5",
    "button_2": "D6"
  }
}
```

Use it:
```python
board = create_board('my_board.json')
```

### Method 2: Python Class

```python
from cpyapp.boards import BoardBase, BoardCapabilities

class MyCustomBoard(BoardBase):
    def __init__(self):
        super().__init__()
        self._capabilities.add(BoardCapabilities.HAS_RGB_MATRIX)
        # ... configure your board
    
    @property
    def name(self):
        return "my_custom_board"
    
    # ... implement required methods

# Register the board
BoardFactory.register_board('my_board', MyCustomBoard)
```

## Board Detection

Get a hardware report:

```python
from cpyapp.boards import get_hardware_report

report = get_hardware_report()
print(f"Board: {report['board']}")
print(f"Display: {report['display']}")
print(f"Network: {report['network']}")
```

## Settings Management

Board-specific settings with persistence:

```python
from cpyapp.boards import BoardSettingsManager

settings_mgr = BoardSettingsManager()
board_settings = settings_mgr.get_board_settings('matrixportal_s3')

# Get settings
brightness = board_settings.get('display.brightness', 0.5)

# Set settings
board_settings.set('display.brightness', 0.7)
board_settings.save()
```

## Integration with SimpleScrollApp

The board system integrates seamlessly with SimpleScrollApp:

```python
from cpyapp.apps import SimpleScrollApp
from cpyapp.boards import create_board

# Create app with specific board
app = SimpleScrollApp(
    board='matrixportal_s3',
    data_source='url:https://api.example.com/data',
    style='classic'
)

# Or with auto-detection
app = SimpleScrollApp(
    board='auto',
    data_source='text:Hello World',
    style='modern'
)
```

## Hardware Capabilities

Check what your board supports:

```python
from cpyapp.boards import BoardCapabilities

# All available capabilities
print(dir(BoardCapabilities))

# Check specific capability
if board.has_capability(BoardCapabilities.HAS_BATTERY):
    level = board.get_battery_level()
    print(f"Battery: {level * 100}%")
```

## Environment Variables

Configure boards via environment variables:

```bash
export CPYAPP_MATRIXPORTAL_S3_DISPLAY_BRIGHTNESS=0.8
export CPYAPP_MATRIXPORTAL_S3_NETWORK_WIFI_TIMEOUT=45
```

## Validation and Testing

Validate board configurations:

```python
from cpyapp.boards import BoardFactory

is_valid, board, errors = BoardFactory.validate_board('my_board.json')
if not is_valid:
    print("Validation errors:", errors)
```

Test custom boards:

```python
from cpyapp.boards import CustomBoardValidator

results = CustomBoardValidator.test_board('my_board.json')
print(f"Config valid: {results['config_valid']}")
print(f"Display OK: {results['display_initialized']}")
```

## Best Practices

1. **Use Auto-Detection**: Let the system detect your board when possible
2. **Override Sparingly**: Only override settings that need to change
3. **Test Configurations**: Validate custom boards before deployment
4. **Document Custom Boards**: Use `create_custom_board_docs()` to generate documentation
5. **Handle Capabilities**: Always check capabilities before using hardware features

## Troubleshooting

### Board Not Detected
- Check CircuitPython version (8.x or 9.x required)
- Verify board.board_id is available
- Try explicit board specification

### Custom Board Issues
- Validate JSON syntax
- Check capability names match BoardCapabilities constants
- Ensure pin names are correct for your hardware

### Settings Not Persisting
- Check write permissions on settings directory
- Verify settings path is correct
- Use absolute paths for custom locations