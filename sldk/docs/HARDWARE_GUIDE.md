# SLDK Hardware Developer Guide

This guide explains how to add support for new LED matrix hardware in SLDK.

## Overview

SLDK supports hardware through the `DisplayInterface` abstraction layer. There are two ways to add hardware support:

1. **Application-specific implementation** - Quick custom hardware support for your specific project
2. **Library contribution** - Add device support to SLDK for the community

## Method 1: Application-Specific Hardware

For custom or one-off hardware setups, override the `create_display()` method in your application:

```python
from sldk import SLDKApp
from sldk.display import DisplayInterface

class MyCustomDisplay(DisplayInterface):
    def __init__(self, **kwargs):
        # Your hardware initialization
        pass
        
    # Implement required methods...

class MyApp(SLDKApp):
    async def create_display(self):
        return MyCustomDisplay()
```

### Advantages
- Quick to implement
- No need to modify SLDK library
- Full control over hardware specifics
- Can use proprietary or experimental hardware

### When to use
- Prototyping with custom hardware
- Using proprietary display controllers
- One-off projects or research
- Hardware not suitable for general use

## Method 2: Contributing to SLDK

For widely-used hardware, contribute a device driver to the SLDK library:

### Step 1: Create Device Driver

Create `sldk/src/sldk/display/devices/your_device.py`:

```python
from ..interface import DisplayInterface

class YourDeviceDisplay(DisplayInterface):
    """Display driver for Your Device Name."""
    
    def __init__(self, width=64, height=32, **kwargs):
        self._width = width
        self._height = height
        # Device-specific parameters
        
    @property
    def width(self):
        return self._width
        
    @property
    def height(self):
        return self._height
    
    async def initialize(self):
        """Initialize your hardware."""
        # Hardware setup code
        pass
        
    async def clear(self):
        """Clear the display."""
        # Clear implementation
        pass
        
    async def show(self):
        """Update the physical display."""
        # Display update code
        return True
        
    async def set_pixel(self, x, y, color):
        """Set a single pixel color."""
        # Pixel setting code
        pass
        
    async def set_brightness(self, brightness):
        """Set display brightness."""
        # Brightness control code
        pass
```

### Step 2: Register Device

Add detection logic to `sldk/src/sldk/display/devices/__init__.py`:

```python
# Import your device
try:
    from .your_device import YourDeviceDisplay
    __all__.append("YourDeviceDisplay")
except ImportError:
    YourDeviceDisplay = None

def detect_hardware(**kwargs):
    """Auto-detect available hardware."""
    
    # Add detection for your device
    if YourDeviceDisplay:
        try:
            # Device-specific detection logic
            # Check for specific chips, I2C addresses, etc.
            return YourDeviceDisplay(**kwargs)
        except Exception:
            pass
    
    # Existing detection logic...
```

### Step 3: Test and Document

1. Test with SLDK examples
2. Add device-specific examples
3. Update documentation
4. Submit pull request

## DisplayInterface Requirements

All hardware implementations must provide these methods:

### Required Properties

```python
@property
def width(self) -> int:
    """Display width in pixels."""
    
@property
def height(self) -> int:
    """Display height in pixels."""
```

### Required Methods

```python
async def initialize(self):
    """Initialize the display hardware.
    
    Called once at startup. Set up SPI, I2C, GPIO, etc.
    """
    
async def clear(self):
    """Clear the display.
    
    Set all pixels to black or hide all content.
    """
    
async def show(self):
    """Update the physical display.
    
    Push any buffered changes to the hardware.
    
    Returns:
        bool: True if successful, False to stop app
    """
    
async def set_pixel(self, x: int, y: int, color: int):
    """Set a single pixel color.
    
    Args:
        x: X coordinate (0 to width-1)
        y: Y coordinate (0 to height-1)
        color: 24-bit RGB color (0xRRGGBB)
    """
    
async def set_brightness(self, brightness: float):
    """Set display brightness.
    
    Args:
        brightness: 0.0 (off) to 1.0 (full brightness)
    """
```

### Optional Methods

```python
async def fill(self, color: int):
    """Fill entire display with color.
    
    Default implementation uses set_pixel() but you can
    provide a more efficient hardware-specific version.
    """
    
async def draw_text(self, text: str, x: int = 0, y: int = 0, 
                    color: int = 0xFFFFFF, font=None):
    """Draw text on display.
    
    Default implementation is basic. Override for better
    text rendering with your hardware's capabilities.
    """
```

## Hardware Categories

### LED Matrix Controllers

**Examples:** HUB75, WS2812, APA102, SK9822

**Key considerations:**
- Frame rate and timing requirements
- Color depth and gamma correction
- Power management
- Chaining multiple panels

**Implementation tips:**
- Use DMA for high frame rates
- Implement double buffering
- Handle color format conversion
- Optimize for memory usage

### SPI/I2C Displays

**Examples:** SSD1306, ST7735, ILI9341, SH1106

**Key considerations:**
- Display controller commands
- Pixel format and endianness
- Display orientation and mirroring
- Partial update support

**Implementation tips:**
- Cache command sequences
- Use hardware scrolling when available
- Implement dirty rectangle updates
- Handle orientation changes efficiently

### Parallel/GPIO Displays

**Examples:** Direct-driven LED arrays, custom hardware

**Key considerations:**
- GPIO pin management
- Timing and refresh rates
- Power consumption
- Electrical drive capabilities

**Implementation tips:**
- Use GPIO expanders for large displays
- Implement multiplexing for rows/columns
- Consider using timers for refresh
- Add current limiting and protection

## CircuitPython Compatibility

Ensure your driver works on CircuitPython:

### Memory Management
```python
# Minimize memory allocation in hot paths
# Reuse objects when possible
# Use memoryview for large data

# Good
self._buffer = bytearray(width * height * 3)

# Avoid
for pixel in pixels:
    self.send_pixel(pixel)  # Creates temporary objects
```

### Async Best Practices
```python
# Use cooperative yielding
async def update_display(self):
    for row in range(self.height):
        self._update_row(row)
        await asyncio.sleep(0)  # Yield to other tasks
```

### Hardware Access
```python
# Use CircuitPython's hardware APIs
import board
import busio
import digitalio

# SPI setup
spi = busio.SPI(board.SCK, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)
```

## Testing Your Hardware Driver

### 1. Basic Functionality
```bash
# Test with hello world
python examples/hello_world.py

# Test with animations
python examples/animation_demo.py
```

### 2. Memory Usage
```python
# Monitor memory in your driver
import gc

async def show(self):
    gc.collect()
    print(f"Free memory: {gc.mem_free()}")
    # Your display update code
```

### 3. Performance Testing
```python
# Measure frame rate
import time

start_time = time.monotonic()
frames = 0

while frames < 100:
    await self.show()
    frames += 1
    
fps = frames / (time.monotonic() - start_time)
print(f"Frame rate: {fps:.1f} FPS")
```

## Example: Complete Driver Implementation

See `examples/custom_hardware.py` for a complete example of implementing custom hardware support.

## Submitting Your Driver

When contributing to SLDK:

1. **Follow naming conventions**: `DeviceNameDisplay`
2. **Add comprehensive docstrings**: Document all parameters and behavior
3. **Include examples**: Show how to use your device
4. **Test thoroughly**: Verify on actual hardware
5. **Update documentation**: Add to hardware compatibility list
6. **Handle errors gracefully**: Provide helpful error messages

## Hardware Compatibility List

| Device | Status | Driver | Notes |
|--------|--------|--------|---------|
| Adafruit MatrixPortal S3 | ✅ Built-in | `MatrixPortalS3Display` | ESP32-S3 with HUB75 |
| Adafruit Matrix Portal | 🚧 Planned | `MatrixPortalDisplay` | Original ESP32 |
| Generic displayio | ✅ Built-in | `GenericDisplayIODevice` | Any displayio device |
| WS2812 Strips | 📋 Planned | `WS2812Display` | NeoPixel strips |
| SSD1306 OLED | 📋 Planned | `SSD1306Display` | I2C/SPI OLED |
| Your Device | 🔌 [Contribute!](../README.md#contributing-hardware) | | |

## Getting Help

If you need help implementing hardware support:

1. Check existing drivers for examples
2. Review the `DisplayInterface` documentation
3. Test with the simulator first
4. Ask questions in GitHub issues

We welcome all hardware contributions to make SLDK work with as many devices as possible!