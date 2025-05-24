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

### 2. Core Components

#### 2.1 LED Matrix Core (`led_matrix.py`)
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

### 4. Key Features to Implement

#### 4.1 Pixel-Perfect LED Simulation
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

### 8. Documentation Requirements

#### 8.1 API Documentation
- Complete docstrings for all public methods
- Type hints throughout
- Usage examples for each class
- Migration guide showing single codebase for hardware and simulator
- displayio API compatibility reference

#### 8.2 Tutorials
- Getting started guide
- Converting CircuitPython code
- Creating custom devices
- Advanced animation techniques

### 9. Packaging and Distribution

#### 9.1 Package Configuration
- setup.py with proper metadata
- Requirements: pygame>=2.0 (hard dependency), pillow>=8.0, numpy
- Python 3.7+ support
- Apache 2.0 License

#### 9.2 Distribution
- PyPI package (pip install pyledsimulator)
- GitHub releases with examples
- Docker image for easy testing
- Conda package for scientific users

### 10. Future Enhancements

#### 10.1 Additional Device Support
- Various Adafruit LED matrices
- RGB LED panels
- Custom LED arrangements
- E-paper display simulation

#### 10.2 Advanced Features
- Hardware-specific features (accelerometer, buttons)
- Color depth restrictions
- Dirty rectangle tracking for performance
- 3D visualization mode
- Network streaming for remote display
- Recording and playback of animations
- Integration with CircuitPython REPL

### 11. Implementation Timeline

#### Phase 1: Core Framework (Week 1-2)
- Set up project structure
- Implement LEDMatrix and PixelBuffer
- Basic pygame rendering
- Simple device implementation

#### Phase 2: displayio Implementation (Week 3-4)
- Implement all displayio classes
- Add font support
- Implement Label and text rendering
- Create unit tests

#### Phase 3: Device Support (Week 5)
- Complete MatrixPortal S3 implementation
- Add multi-display support
- Performance optimization
- Integration tests

#### Phase 4: Polish and Release (Week 6)
- Complete documentation
- Create examples
- Package for distribution
- Initial release

This plan provides a comprehensive roadmap for creating a professional, reusable LED matrix simulator library that can be used across different projects and hardware configurations.