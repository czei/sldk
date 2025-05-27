# PyLEDSimulator Implementation Plan

## Project Overview
Create a standalone, reusable Python library for simulating LED matrix displays used with CircuitPython boards. The library will provide a visual representation of LED hardware using Pygame, allowing developers to test their code on desktop platforms before deploying to actual hardware.

## Architecture Design

### 1. Project Structure
```
PyLEDSimulator/
├── README.md
├── setup.py
├── requirements.txt
├── LICENSE (Apache 2.0)
├── fonts/
│   ├── tom-thumb.bdf              # Default small font
│   ├── 5x8.bdf                    # Standard 5x8 font
│   └── ter-u12n.bdf               # Medium size font
├── examples/
│   ├── matrixportal_s3_example.py
│   ├── scrolling_text_example.py
│   ├── dual_zone_example.py
│   ├── multi_display_example.py
│   ├── rainbow_text.py            # Port of common CircuitPython example
│   └── pixel_dust.py              # Port of common CircuitPython example
├── pyledsimulator/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── led_matrix.py          # Core LED matrix simulation
│   │   ├── pixel_buffer.py        # Pixel management
│   │   ├── display_manager.py     # Multi-display coordination
│   │   └── color_utils.py         # Color manipulation utilities
│   ├── displayio/
│   │   ├── __init__.py
│   │   ├── display.py             # Display class
│   │   ├── group.py               # Group class
│   │   ├── bitmap.py              # Bitmap class
│   │   ├── palette.py             # Palette class
│   │   ├── tilegrid.py            # TileGrid class
│   │   ├── ondiskbitmap.py        # OnDiskBitmap class
│   │   └── fourwire.py            # FourWire interface
│   ├── terminalio/
│   │   └── __init__.py            # Provides FONT constant with default font
│   ├── adafruit_display_text/
│   │   ├── __init__.py
│   │   ├── label.py               # Label implementation
│   │   ├── bitmap_label.py        # BitmapLabel implementation
│   │   └── scrolling_label.py     # ScrollingLabel implementation
│   ├── adafruit_bitmap_font/
│   │   ├── __init__.py
│   │   ├── bitmap_font.py         # BDF font loader
│   │   └── glyph_cache.py         # Glyph caching
│   ├── devices/
│   │   ├── __init__.py
│   │   ├── base_device.py         # Abstract base for devices
│   │   ├── matrixportal_s3.py     # MatrixPortal S3 implementation
│   │   └── generic_matrix.py      # Generic matrix device
│   └── utils/
│       ├── __init__.py
│       ├── font_loader.py         # Font loading utilities
│       ├── image_utils.py         # Image manipulation
│       └── timing.py              # Timing utilities
└── tests/
    ├── __init__.py
    ├── test_displayio/
    │   ├── test_display.py
    │   ├── test_group.py
    │   ├── test_bitmap.py
    │   ├── test_palette.py
    │   └── test_tilegrid.py
    ├── test_adafruit_display_text/
    │   ├── test_label.py
    │   └── test_scrolling_label.py
    ├── test_core/
    │   ├── test_led_matrix.py
    │   ├── test_pixel_buffer.py
    │   └── test_display_manager.py
    └── test_devices/
        └── test_matrixportal_s3.py
```

### 2. Implementation Philosophy and Constraints

#### 2.1 API Compatibility Approach
The simulator aims for "sufficient API compatibility" rather than 100% byte-for-byte behavioral matching with CircuitPython's displayio. This pragmatic approach acknowledges that:

- CircuitPython's displayio is implemented in highly optimized C/C++
- Perfect behavioral replication in pure Python/Pygame would be extremely challenging
- The primary goal is visual testing and development, not hardware emulation

##### Known Limitations (to be documented):
- Rendering order nuances may differ slightly
- Memory management will follow Python's model, not CircuitPython's
- Some advanced features (rotation, scaling transforms) may have behavioral differences
- Transparency and clipping edge cases may not match exactly

##### Compatibility Priority (implement in this order):
1. Basic display operations (show, refresh)
2. Common displayio classes (Group, Bitmap, TileGrid, Label)
3. Font rendering with terminalio.FONT
4. Palette and color operations
5. Advanced features as needed by real-world usage

#### 2.2 Font Rendering Compatibility

##### Known Font Rendering Challenges:
1. **BDF Font Parsing**: CircuitPython's font rendering differs from standard implementations
2. **Glyph Metrics**: Baseline, ascent, and descent calculations may vary
3. **Anti-aliasing**: CircuitPython uses 1-bit rendering, no anti-aliasing
4. **Character Spacing**: Kerning and advance width handling differences

##### Compatibility Testing Requirements:
- Create visual comparison tests with CircuitPython screenshots
- Test all bundled fonts with various character sets
- Verify special character rendering (accents, symbols)
- Test edge cases: empty strings, missing glyphs, oversized text

#### 2.3 Pygame Event Loop Integration

##### Non-Blocking Architecture Requirements:
The simulator must integrate seamlessly with existing Pygame applications without taking over the main event loop. This requires:

1. **Event Loop Patterns**:
   ```python
   # Pattern 1: User-controlled loop
   device = MatrixPortalS3()
   while running:
       # User's game logic
       device.update()  # Non-blocking update
       
   # Pattern 2: Callback-based updates
   device = MatrixPortalS3()
   device.on_frame_update = my_callback
   device.start_async()  # Runs in background
   ```

2. **Integration Challenges**:
   - Cannot assume control of pygame.init() or display creation
   - Must handle cases where user already has a Pygame window
   - Need to support both standalone and embedded usage
   - Event handling must not interfere with user's event processing

3. **Solution Approach**:
   - Provide multiple integration modes (standalone, embedded, headless)
   - Use pygame.Surface for rendering instead of direct display access
   - Optional automatic event loop with escape hatch for manual control
   - Clear documentation on integration patterns

#### 2.4 Board Module Simulation Strategy

##### Minimal Initial Implementation:
The `board` module simulation will start with a minimal approach, adding features only as needed by real usage:

```python
# board/__init__.py - Minimal initial implementation
class Board:
    """Minimal board module for simulator compatibility"""
    
    def __init__(self):
        self.DISPLAY = None  # Set by device initialization
        # Add other attributes as needed based on actual usage
        
# Future additions based on need:
# - Pin definitions (board.D13, board.A0, etc.)
# - I2C/SPI interfaces
# - Built-in sensors (accelerometer, etc.)
# - Board-specific features
```

This approach avoids over-engineering and ensures we only implement what's actually used.

#### 2.5 Memory Management Simulation

##### Simplified GC Simulation:
Rather than attempting to replicate CircuitPython's exact GC behavior, use a simplified model:

```python
class SimplifiedGC:
    """Simplified garbage collection simulation"""
    
    def __init__(self, memory_limit_kb=256):
        self.memory_limit = memory_limit_kb * 1024
        self.allocated = 0
        self.gc_threshold = 0.8  # Trigger at 80% usage
        
    def allocate(self, size):
        """Simulate memory allocation"""
        if self.allocated + size > self.memory_limit:
            self.collect()  # Try GC first
            if self.allocated + size > self.memory_limit:
                raise MemoryError("Unable to allocate memory")
        self.allocated += size
        
    def collect(self):
        """Simulate garbage collection"""
        # Simple model: recover 30-50% of allocated memory
        recovered = random.uniform(0.3, 0.5) * self.allocated
        self.allocated -= recovered
        # Add realistic delay
        time.sleep(0.01 + (self.allocated / self.memory_limit) * 0.05)
```

This provides memory pressure simulation without the complexity of tracking individual allocations.

### 3. Core Components

#### 3.1 LED Matrix Core (`led_matrix.py`)
```python
class LEDMatrix:
    """Core LED matrix simulation with pixel-level control"""
    
    def __init__(self, width, height, pitch=2.5, led_size=None):
        self.width = width              # Matrix width in pixels
        self.height = height            # Matrix height in pixels
        self.pitch = pitch              # LED pitch in mm (2.5, 3, 4, 5, or 6)
        
        # Calculate LED size and spacing based on pitch
        # For a given pitch, LED size is typically 80% of pitch
        if led_size is None:
            self.led_size = int(pitch * 0.8 * 4)  # Scale factor for visual display
        else:
            self.led_size = led_size
        self.spacing = int(pitch * 0.2 * 4)  # 20% of pitch is dark space
        
        self.pixel_buffer = PixelBuffer(width, height)
        self.pygame_surface = None
        self.scale_factor = 1.0
        self.brightness = 1.0
        
    def set_pixel(self, x, y, color):
        """Set a single pixel color"""
        
    def get_pixel(self, x, y):
        """Get a single pixel color"""
        
    def clear(self):
        """Clear all pixels"""
        
    def render(self):
        """Render the matrix to pygame surface"""
        
    def update_display(self):
        """Update the pygame display"""
```

#### 2.2 Display Manager (`display_manager.py`)
```python
class DisplayManager:
    """Manages multiple LED matrix displays"""
    
    def __init__(self):
        self.displays = []
        self.layout = None  # Grid layout for multiple displays
        self.window = None
        
    def add_display(self, display, position=(0, 0)):
        """Add a display at specified position"""
        
    def create_window(self, title="LED Simulator"):
        """Create pygame window for all displays"""
        
    def update(self):
        """Update all displays"""
        
    def handle_events(self):
        """Handle pygame events"""
```

#### 2.3 displayio Implementation

The displayio module will be implemented with sufficient API compatibility to allow a single codebase to work on both hardware and simulator. This includes all commonly used classes and methods from CircuitPython's displayio module.

##### Display (`displayio/display.py`)
```python
class Display:
    """CircuitPython displayio.Display equivalent"""
    
    def __init__(self, display_bus, *, width, height, rotation=0, 
                 color_depth=16, auto_refresh=True):
        self.width = width
        self.height = height
        self.rotation = rotation
        self.root_group = None
        self.auto_refresh = auto_refresh
        self._brightness = 1.0
        
    @property
    def brightness(self):
        return self._brightness
        
    @brightness.setter
    def brightness(self, value):
        self._brightness = max(0.0, min(1.0, value))
        
    def refresh(self):
        """Manually refresh the display"""
        
    def show(self, group_or_tilegrid):
        """Show a Group or TileGrid"""
```

##### Group (`displayio/group.py`)
```python
class Group:
    """CircuitPython displayio.Group equivalent"""
    
    def __init__(self, *, scale=1, x=0, y=0):
        self.scale = scale
        self.x = x
        self.y = y
        self.hidden = False
        self._items = []
        
    def append(self, item):
        """Add an item to the group"""
        
    def remove(self, item):
        """Remove an item from the group"""
        
    def __len__(self):
        return len(self._items)
        
    def __getitem__(self, index):
        return self._items[index]
```

##### Bitmap (`displayio/bitmap.py`)
```python
class Bitmap:
    """CircuitPython displayio.Bitmap equivalent"""
    
    def __init__(self, width, height, value_count):
        self.width = width
        self.height = height
        self.value_count = value_count
        self._buffer = [[0 for _ in range(width)] for _ in range(height)]
        
    def __setitem__(self, index, value):
        """Set pixel value"""
        x, y = index
        self._buffer[y][x] = value
        
    def __getitem__(self, index):
        """Get pixel value"""
        x, y = index
        return self._buffer[y][x]
```

#### 2.4 terminalio Implementation

##### terminalio Module (`terminalio/__init__.py`)
```python
from pyledsimulator.adafruit_bitmap_font import bitmap_font

# Load default font matching CircuitPython's terminalio.FONT
# This will be the bundled tom-thumb.bdf font
FONT = bitmap_font.load_font("fonts/tom-thumb.bdf")
```

### 3. Device Implementations

#### 3.1 Base Device (`devices/base_device.py`)
```python
class BaseDevice:
    """Abstract base class for LED matrix devices"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.display = None
        self.matrix = None
        
    def initialize(self):
        """Initialize the device"""
        raise NotImplementedError
        
    def set_brightness(self, brightness):
        """Set display brightness"""
        
    def clear(self):
        """Clear the display"""
```

#### 3.2 MatrixPortal S3 (`devices/matrixportal_s3.py`)
```python
class MatrixPortalS3(BaseDevice):
    """Simulated MatrixPortal S3 device"""
    
    def __init__(self, pitch=4.0):
        super().__init__(64, 32)  # Standard 64x32 display
        self.pitch = pitch  # Common pitches: 2.5, 3, 4, 5, 6mm
        
    def initialize(self):
        """Initialize MatrixPortal S3 specific features"""
        self.matrix = LEDMatrix(self.width, self.height, pitch=self.pitch)
        self.display = Display(None, width=self.width, height=self.height)
```

### 4. CircuitPython Source Code Reference

#### 4.1 Accessing CircuitPython Source
The complete CircuitPython source code is available at: https://github.com/adafruit/circuitpython

Key directories for displayio implementation reference:
- **shared-module/displayio/**: Core displayio implementation in C
- **shared-bindings/displayio/**: Python API bindings
- **tests/**: Unit tests for various modules
- **examples/**: Example code demonstrating displayio usage

##### Important Source Files to Study:
1. **Display Implementation**:
   - `shared-module/displayio/Display.c` - Core display logic
   - `shared-bindings/displayio/Display.c` - Python API

2. **Group Implementation**:
   - `shared-module/displayio/Group.c` - Group rendering logic
   - `shared-bindings/displayio/Group.c` - Python API

3. **Bitmap and Palette**:
   - `shared-module/displayio/Bitmap.c`
   - `shared-module/displayio/Palette.c`

4. **TileGrid**:
   - `shared-module/displayio/TileGrid.c` - Sprite rendering

##### Function Lists to Implement:
Extract complete function lists by examining the Python binding files:
```bash
# Clone CircuitPython repository
git clone https://github.com/adafruit/circuitpython.git
cd circuitpython

# Find all displayio Python API functions
grep -h "STATIC mp_obj_t" shared-bindings/displayio/*.c | grep -o "displayio_[^(]*"

# Find all display_text functions
grep -h "STATIC mp_obj_t" shared-bindings/adafruit_display_text/*.c | grep -o "display_text_[^(]*"
```

#### 4.2 Utilizing CircuitPython Tests

##### Test Integration Strategy:
1. **Copy Relevant Tests**:
   - Copy tests from `circuitpython/tests/circuitpython/` that test displayio functionality
   - Adapt tests to run against the simulator implementation
   - Use these as acceptance tests to verify API compatibility

2. **Test Categories to Import**:
   - `test_displayio_*.py` - Core displayio tests
   - `test_bitmap_*.py` - Bitmap manipulation tests
   - `test_group_*.py` - Group hierarchy tests
   - Any display_text related tests

3. **Test Adaptation Process**:
   ```python
   # Original CircuitPython test
   import displayio
   display = board.DISPLAY
   
   # Adapted for simulator
   from pyledsimulator import displayio
   from pyledsimulator.devices import MatrixPortalS3
   device = MatrixPortalS3()
   display = device.display
   ```

##### Running CircuitPython Tests:
```bash
# Clone CircuitPython if not already done
git clone https://github.com/adafruit/circuitpython.git

# Copy relevant tests to PyLEDSimulator
mkdir -p tests/circuitpython_compat
cp circuitpython/tests/circuitpython/test_displayio*.py tests/circuitpython_compat/

# Create test adapter to run CircuitPython tests
# See tests/circuitpython_compat/adapter.py for implementation
```

##### Test Adapter Example (`tests/circuitpython_compat/adapter.py`):
```python
"""Adapter to run CircuitPython tests against PyLEDSimulator"""
import sys
import pytest

# Mock CircuitPython specific modules
class MockBoard:
    DISPLAY = None

sys.modules['board'] = MockBoard()

# Import simulator modules as CircuitPython modules
import pyledsimulator.displayio as displayio
import pyledsimulator.terminalio as terminalio
import pyledsimulator.adafruit_display_text as adafruit_display_text

sys.modules['displayio'] = displayio
sys.modules['terminalio'] = terminalio
sys.modules['adafruit_display_text'] = adafruit_display_text

# Setup default display for tests
from pyledsimulator.devices import MatrixPortalS3
device = MatrixPortalS3()
device.initialize()
MockBoard.DISPLAY = device.display
```

#### 4.3 Code Examples from CircuitPython

Study these key examples from the CircuitPython repository:
1. **examples/displayio_simpletest.py** - Basic displayio usage
2. **examples/display_text_simpletest.py** - Text rendering
3. **examples/bitmap_font_simpletest.py** - Font loading
4. **examples/display_shapes_simpletest.py** - Shape drawing
5. **examples/matrixportal_simpletest.py** - MatrixPortal specific features

These examples should be:
- Copied to PyLEDSimulator's examples directory
- Modified minimally to work with the simulator
- Used as integration tests to verify compatibility
- Referenced in documentation as "works identically to hardware"

#### 4.4 License Attribution for Adapted Code
Since CircuitPython is MIT licensed and PyLEDSimulator will be Apache 2.0:
- Create an `ATTRIBUTION.md` file listing all adapted CircuitPython code
- Add MIT license headers to any files containing adapted code
- Include original CircuitPython copyright notices where applicable
- Example attribution format:
```
# Portions adapted from CircuitPython
# Copyright (c) 2016-2024 Adafruit Industries
# Licensed under MIT License
# Original source: https://github.com/adafruit/circuitpython/blob/main/tests/...
```

### 5. Key Features to Implement

#### 5.1 Pixel-Perfect LED Simulation
- Each LED is rendered as a rounded rectangle with configurable pitch (2.5, 3, 4, 5, 6mm)
- Dark gaps between LEDs to simulate real hardware appearance
- LED size calculated as 80% of pitch, with 20% dark space
- Realistic brightness simulation with color blending
- Anti-aliasing for smooth LED appearance

#### 4.2 Font Support
- Bundled default BDF fonts (tom-thumb.bdf, 5x8.bdf, ter-u12n.bdf)
- BDF font file loading and rendering
- terminalio.FONT provides default font matching CircuitPython
- Glyph caching for performance
- Proper scaling for LED matrix resolution

#### 4.3 Text Rendering
- Label implementation with proper positioning
- Scrolling text with configurable speed
- Multi-line text support
- Text anchoring (left, center, right)

#### 4.4 Animation Support
- Frame-based animation system
- Sprite support with TileGrid
- Smooth scrolling for text and graphics
- Transition effects

#### 4.5 Multi-Display Support
- Tile multiple displays together (up to 4x4 grid = 256x128 pixels)
- Synchronized updates across displays
- Different layout configurations (horizontal, vertical, grid)
- Independent control of each display

### 5. Testing Strategy

#### 5.1 Unit Tests
- Test each displayio class method
- Verify pixel operations
- Test color conversions
- Validate font rendering
- Test group hierarchies

#### 5.2 Integration Tests
- Test complete display scenarios
- Verify multi-display coordination
- Test animation sequences
- Validate memory management

#### 5.3 Visual Tests
- Screenshot comparison tests with configurable tolerance
- Rendering accuracy tests allowing for minor pixel differences
- Performance benchmarks

### 6. Example Implementations

#### 6.1 Basic Text Display
```python
from pyledsimulator.devices import MatrixPortalS3
from pyledsimulator.displayio import Group
from pyledsimulator.adafruit_display_text import Label

# Create device
device = MatrixPortalS3()
device.initialize()

# Create text label
text_group = Group()
label = Label(font=device.default_font, text="Hello LED!")
label.x = 0
label.y = 15
text_group.append(label)

# Show on display
device.display.show(text_group)
```

#### 6.2 Scrolling Text
```python
from pyledsimulator.adafruit_display_text import ScrollingLabel

scroll_label = ScrollingLabel(
    font=device.default_font,
    text="This is a long scrolling message...",
    max_characters=10
)
scroll_label.animate()
```

### 7. Performance Considerations

#### 7.1 Optimization Strategies
- Pixel buffer caching
- Efficient color space conversions
- Frame rate limiting
- Hardware acceleration via pygame
- Note: Dirty rectangle tracking deferred to future enhancement

#### 7.2 Memory Management
- Lazy loading of resources
- Glyph cache limits
- Bitmap pooling
- Group flattening for rendering

### 8. Hardware Performance Simulation (Simplified Approach)

#### 8.1 Performance Simulation Philosophy
The simulator will provide a simplified, high-level approximation of hardware performance rather than attempting to exactly emulate CircuitPython's execution characteristics. This pragmatic approach acknowledges:

- Exact CPU instruction timing simulation would add significant overhead
- Python's GC differs fundamentally from MicroPython's GC
- The primary goal is to approximate timing, not exact hardware emulation

#### 8.2 Simplified Performance System

##### Core Performance Manager (`core/performance_manager.py`)
```python
class PerformanceManager:
    """Manages hardware performance simulation"""
    
    def __init__(self, hardware_profile="SAMD51"):
        self.hardware_profile = hardware_profile
        self.profiles = {
            "SAMD51": {
                "cpu_mhz": 120,
                "base_delay_ms": 0.1,
                "memory_kb": 256,
                "gc_overhead": 0.15,  # 15% overhead for garbage collection
                "io_delay_ms": 0.5
            },
            "RP2040": {
                "cpu_mhz": 125,
                "base_delay_ms": 0.08,
                "memory_kb": 264,
                "gc_overhead": 0.12,
                "io_delay_ms": 0.3
            },
            "ESP32-S3": {
                "cpu_mhz": 240,
                "base_delay_ms": 0.05,
                "memory_kb": 512,
                "gc_overhead": 0.10,
                "io_delay_ms": 0.2
            }
        }
        self.enabled = True
        self.speed_multiplier = 1.0
        self._last_gc_time = 0
        
    def simulate_instruction_delay(self, instruction_count=1):
        """Add delay based on instruction complexity"""
        
    def simulate_memory_constraint(self, allocation_size):
        """Simulate memory allocation delays and failures"""
        
    def simulate_gc_pause(self):
        """Simulate garbage collection pauses"""
        
    def simulate_io_operation(self, operation_type="read"):
        """Simulate I/O operation delays"""
```

#### 8.2 Hardware Simulation Features

##### 8.2.1 CPU Speed Simulation
- Configurable CPU clock speeds matching real hardware (SAMD51: 120MHz, RP2040: 125MHz, ESP32-S3: 240MHz)
- Instruction-level delays based on operation complexity
- Python interpreter overhead simulation
- Adjustable speed multiplier for testing (0.1x to 10x real speed)

##### 8.2.2 Memory Constraints
- Simulated memory limits matching hardware (256KB for SAMD51, 264KB for RP2040, etc.)
- Memory allocation delays
- Out-of-memory exception simulation
- Garbage collection pause simulation with realistic timing
- Memory fragmentation effects

##### 8.2.3 I/O Operation Delays
- Display update delays (SPI communication simulation)
- File system access delays
- Network operation delays (for WiFi-enabled boards)
- Hardware bus communication delays

##### 8.2.4 CircuitPython-Specific Behaviors
- Cooperative multitasking simulation (no true threading)
- Import statement delays
- Module memory overhead
- Watchdog timer simulation
- Auto-reload delays when code changes

#### 8.3 Integration with Display Operations

##### Modified LED Matrix (`core/led_matrix.py`)
```python
class LEDMatrix:
    def __init__(self, width, height, pitch=2.5, led_size=None, 
                 performance_manager=None):
        # ... existing init code ...
        self.performance_manager = performance_manager or PerformanceManager()
        
    def set_pixel(self, x, y, color):
        """Set a single pixel color with performance simulation"""
        if self.performance_manager.enabled:
            # Simulate pixel write delay
            self.performance_manager.simulate_instruction_delay(3)
        # ... existing pixel setting code ...
        
    def render(self):
        """Render the matrix to pygame surface with realistic delays"""
        if self.performance_manager.enabled:
            # Simulate display refresh delay
            self.performance_manager.simulate_io_operation("display_refresh")
            # Simulate potential GC pause during rendering
            self.performance_manager.simulate_gc_pause()
        # ... existing render code ...
```

#### 8.4 Configuration and Control

##### Performance Configuration (`config/performance_config.py`)
```python
class PerformanceConfig:
    """Configuration for hardware performance simulation"""
    
    def __init__(self):
        self.simulation_enabled = True
        self.hardware_profile = "SAMD51"
        self.speed_multiplier = 1.0
        self.gc_simulation = True
        self.memory_constraints = True
        self.io_delays = True
        self.profile_overrides = {}
        
    def load_from_file(self, config_path):
        """Load performance settings from JSON config"""
        
    def create_custom_profile(self, name, settings):
        """Create custom hardware profile"""
```

#### 8.5 Profiling and Metrics

##### Performance Monitor (`utils/performance_monitor.py`)
```python
class PerformanceMonitor:
    """Monitor and report performance metrics"""
    
    def __init__(self, performance_manager):
        self.performance_manager = performance_manager
        self.metrics = {
            "frame_times": [],
            "gc_pauses": [],
            "memory_usage": [],
            "cpu_utilization": []
        }
        
    def start_frame(self):
        """Mark the start of a frame"""
        
    def end_frame(self):
        """Mark the end of a frame and calculate metrics"""
        
    def generate_report(self):
        """Generate performance report comparing simulated vs actual"""
        
    def export_metrics(self, filename):
        """Export metrics for analysis"""
```

#### 8.6 Example Usage

```python
from pyledsimulator.devices import MatrixPortalS3
from pyledsimulator.core import PerformanceManager
from pyledsimulator.config import PerformanceConfig

# Create performance configuration
perf_config = PerformanceConfig()
perf_config.hardware_profile = "SAMD51"
perf_config.speed_multiplier = 1.0  # Real-time simulation

# Create performance manager
perf_manager = PerformanceManager(perf_config.hardware_profile)

# Create device with performance simulation
device = MatrixPortalS3(performance_manager=perf_manager)
device.initialize()

# Code will now run with realistic hardware delays
# Scrolling text will move at actual hardware speed
# Memory constraints will be enforced
```

#### 8.7 Testing with Performance Simulation

##### Performance Test Suite (`tests/test_performance/`)
- Test timing accuracy against real hardware measurements
- Verify memory constraint enforcement
- Test GC pause simulation
- Validate I/O operation delays
- Benchmark different hardware profiles

#### 8.8 User Interface for Performance Control

##### Performance Control Panel
- Real-time speed adjustment slider
- Hardware profile selector
- Memory usage visualization
- Frame rate display
- GC pause indicator
- Toggle for enabling/disabling simulation
- Save/load performance profiles

### 9. Documentation Requirements

#### 9.1 API Documentation
- Complete docstrings for all public methods
- Type hints throughout
- Usage examples for each class
- Migration guide showing single codebase for hardware and simulator
- displayio API compatibility reference

#### 9.2 Tutorials
- Getting started guide
- Converting CircuitPython code
- Creating custom devices
- Advanced animation techniques

### 10. Packaging and Distribution

#### 10.1 Package Configuration
- setup.py with proper metadata
- Requirements: pygame>=2.0 (hard dependency), pillow>=8.0, numpy
- Python 3.7+ support
- Apache 2.0 License

#### 10.2 Distribution
- PyPI package (pip install pyledsimulator)
- GitHub releases with examples
- Docker image for easy testing
- Conda package for scientific users

### 11. Future Enhancements

#### 11.1 Additional Device Support
- Various Adafruit LED matrices
- RGB LED panels
- Custom LED arrangements
- E-paper display simulation

#### 11.2 Advanced Features
- Hardware-specific features (accelerometer, buttons)
- Color depth restrictions
- Dirty rectangle tracking for performance
- 3D visualization mode
- Network streaming for remote display
- Recording and playback of animations
- Integration with CircuitPython REPL

### 12. Summary of Key Design Decisions Based on Feedback

#### 12.1 Pragmatic Implementation Philosophy
- Acknowledge that perfect CircuitPython emulation is not the goal
- Focus on "sufficient API compatibility" for practical development use
- Document known limitations clearly to set appropriate expectations

#### 12.2 Simplified Approaches
- **Performance Simulation**: High-level timing approximation rather than CPU instruction emulation
- **Memory Management**: Simple allocation tracking with percentage-based GC recovery
- **Board Module**: Minimal initial implementation, expanding based on actual usage needs
- **Font Rendering**: Accept minor visual differences, focus on functional compatibility

#### 12.3 Integration Flexibility
- Multiple Pygame integration patterns to avoid taking over the event loop
- Support both standalone window and embedded surface rendering
- Clear separation between simulator core and UI presentation

#### 12.4 Testing Strategy
- Leverage CircuitPython's existing test suite for API compatibility validation
- Visual comparison tests with configurable tolerance for rendering differences
- Performance benchmarks comparing simulated vs actual hardware timing

### 13. Implementation Timeline

#### Phase 1: Core Framework (Week 1-2)
- Set up project structure
- Implement LEDMatrix and PixelBuffer
- Basic pygame rendering
- Simple device implementation
- Initial PerformanceManager implementation

#### Phase 2: displayio Implementation (Week 3-4)
- Implement all displayio classes
- Add font support
- Implement Label and text rendering
- Create unit tests
- Integrate performance simulation with display operations

#### Phase 3: Hardware Performance Simulation (Week 5)
- Complete PerformanceManager with all hardware profiles
- Implement memory constraint simulation
- Add GC pause simulation
- Create performance monitoring tools
- Performance simulation unit tests

#### Phase 4: Device Support (Week 6)
- Complete MatrixPortal S3 implementation
- Add multi-display support
- Performance optimization
- Integration tests with performance simulation

#### Phase 5: Polish and Release (Week 7)
- Complete documentation including performance simulation guide
- Create examples demonstrating performance simulation
- Package for distribution
- Initial release

This plan provides a comprehensive roadmap for creating a professional, reusable LED matrix simulator library that can be used across different projects and hardware configurations.