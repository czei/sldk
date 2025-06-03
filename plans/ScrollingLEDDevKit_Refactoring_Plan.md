# Scrolling LED Dev Kit - Refactoring Plan

## Executive Summary

This document outlines the plan to refactor the Theme Park Waits application to extract generic LED development functionality into a reusable library called "Scrolling LED Dev Kit" (working title). The library will provide a complete development environment for creating CircuitPython-based scrolling LED applications with modern development tools, debugging capabilities, and deployment features.

## Project Goals

1. **Create a reusable library** for developing scrolling LED applications
2. **Maintain compatibility** with both CircuitPython hardware and desktop development
3. **Optimize for ESP32 constraints** - ~200KB available RAM, single-core performance
4. **Provide modern development tools** including debugging, simulation, and hot-reload
5. **Enable easy deployment** with OTA updates and web-based configuration
6. **Support extensibility** through clean interfaces and plugin architecture

## ESP32-First Design Philosophy

The library follows an "ESP32-first" design approach - if it runs well on the constrained ESP32 hardware, it will run excellently in the development environment. This ensures that code written and tested on desktop will work reliably when deployed to hardware.

### ESP32/CircuitPython Constraints

The library must work within severe hardware limitations:
- **Memory**: Only ~200KB RAM available after CircuitPython loads
- **Performance**: Single-threaded, 240MHz, but Python overhead is significant  
- **Storage**: .py files loaded into RAM, so code size directly impacts available memory
- **No true multithreading**: Only cooperative async via asyncio
- **Slow I/O**: Network operations can block for seconds

### Design Benefits

By designing for the most constrained environment first:
- **Guaranteed Compatibility**: Desktop-tested code always fits on hardware
- **Optimal Performance**: Efficient code on ESP32 is blazing fast on desktop
- **Simplified Testing**: One codebase, no platform-specific optimizations needed
- **Better Architecture**: Constraints force clean, modular design

## Library Name: SLDK (Scrolling LED Dev Kit)

The library will be named **SLDK** - a concise, memorable name that clearly indicates its purpose.\n\n## Hardware Support Strategy\n\nSLDK is designed to support any CircuitPython-compatible LED matrix display through a flexible two-tier approach:\n\n### Tier 1: Application-Specific Hardware\n\nFor custom setups, users can override the `create_display()` method in their application:\n\n```python\nclass MyApp(SLDKApp):\n    async def create_display(self):\n        return MyCustomDisplay()  # User's hardware implementation\n```\n\n**Benefits:**\n- Quick implementation for one-off projects\n- Full control over hardware specifics\n- No need to modify SLDK library\n- Perfect for prototyping and custom hardware\n\n### Tier 2: Library Contributions\n\nFor widely-used hardware, device drivers are contributed to SLDK:\n\n```python\n# sldk/display/devices/new_device.py\nclass NewDeviceDisplay(DisplayInterface):\n    # Hardware-specific implementation\n```\n\n**Benefits:**\n- Community-driven hardware support\n- Auto-detection and plug-and-play operation\n- Shared maintenance and optimization\n- Comprehensive testing and documentation\n\n### Supported Hardware Ecosystem\n\n| Hardware Category | Examples | Implementation |\n|-------------------|----------|----------------|\n| **Matrix Controllers** | HUB75, WS2812, APA102 | Direct GPIO/SPI control |\n| **Display Modules** | SSD1306, ST7735, ILI9341 | I2C/SPI communication |\n| **Development Boards** | MatrixPortal, ESP32, Pi | Board-specific drivers |\n| **Custom Hardware** | User designs | Application override |\n\nThis approach ensures SLDK can work with virtually any LED display hardware while maintaining clean abstractions and optimal performance."

## Architecture Overview

### Three-Process Architecture

The library implements a three-process async architecture for optimal performance and separation of concerns:

1. **Display Process** - Handles all display rendering at consistent frame rate
   - Runs at 50+ FPS for smooth animations
   - Never blocked by network operations
   - Consumes content from thread-safe queue
   - Manages display hardware/simulator

2. **Data Update Process** - Manages data fetching and updates in the background
   - Fetches data on configurable intervals
   - Updates content queue atomically
   - Handles API failures gracefully
   - Sends notifications to other processes

3. **Web Server Process** - Provides web UI for configuration and monitoring
   - Non-blocking web interface
   - Real-time configuration updates
   - Status monitoring and debugging
   - WebSocket support for live updates

#### Benefits of Three-Process Design

- **Responsive Display**: Network delays never affect animation smoothness
- **Reliable Updates**: Data fetching failures don't crash the display
- **Interactive Config**: Web UI remains responsive during updates
- **Scalability**: Each process can be optimized independently
- **Debugging**: Easier to isolate issues to specific processes
- **Memory Safety**: Clear boundaries prevent race conditions

#### ESP32 Adaptations

On ESP32, the three-process architecture adapts to available memory:

1. **Always Running**: Display process (minimal memory)
2. **Usually Running**: Data update process (moderate memory)
3. **Optional**: Web server (only if >50KB free RAM)

The system gracefully degrades based on available resources, ensuring the display always works even in low-memory conditions.

### Core Library Components

```
scrolling-led-devkit/
├── pyproject.toml
├── README.md
├── LICENSE
├── docs/
├── examples/
│   ├── hello_world/
│   ├── scrolling_text/
│   ├── animations/
│   └── web_config/
└── src/
    └── led_devkit/
        ├── __init__.py
        ├── display/
        │   ├── __init__.py
        │   ├── interface.py      # DisplayInterface ABC
        │   ├── base.py           # Base display implementation
        │   ├── unified.py        # Unified hardware/simulator display
        │   ├── text.py           # Text rendering utilities
        │   ├── content.py        # DisplayContent base classes
        │   ├── queue.py          # Thread-safe content queue
        │   └── animations/
        │       ├── __init__.py
        │       ├── base.py       # Animation base class
        │       ├── scroll.py     # Scrolling animations
        │       └── effects.py    # Built-in effects
        ├── simulator/
        │   └── (existing led_simulator code)
        ├── web/
        │   ├── __init__.py
        │   ├── server.py         # Async web server
        │   ├── handlers.py       # Request handlers
        │   ├── static/           # Base CSS/JS
        │   └── templates/        # Base HTML templates
        ├── network/
        │   ├── __init__.py
        │   ├── wifi.py           # WiFi management
        │   ├── http.py           # HTTP client
        │   └── mdns.py           # mDNS support
        ├── ota/
        │   ├── __init__.py
        │   ├── updater.py        # OTA update logic
        │   └── github.py         # GitHub release integration
        ├── config/
        │   ├── __init__.py
        │   ├── settings.py       # Settings framework
        │   └── schema.py         # Configuration schema
        ├── utils/
        │   ├── __init__.py
        │   ├── colors.py         # Color utilities
        │   ├── fonts.py          # Font management
        │   ├── errors.py         # Error handling
        │   └── platform.py       # Platform detection
        └── app/
            ├── __init__.py
            ├── base.py           # LEDApplication base class
            ├── state.py          # Shared state management
            ├── messages.py       # Inter-process messaging
            └── runner.py         # Application runner
```

### Application Structure (Theme Park Waits)

```
theme-park-waits/
├── pyproject.toml
├── README.md
├── boot.py              # CircuitPython boot
├── code.py              # CircuitPython entry
└── src/
    ├── main.py          # Application entry
    ├── app.py           # ThemeParkApp(LEDApplication)
    ├── models/          # Theme park specific models
    ├── api/             # Queue-times API
    ├── displays/        # Theme park specific displays
    ├── web/             # Theme park web extensions
    └── config/          # Theme park configuration
```

## Key Abstractions

### 1. Application Base Class

```python
from abc import ABC, abstractmethod

class LEDApplication(ABC):
    """Base class for LED applications."""
    
    @abstractmethod
    def setup(self):
        """Initialize the application."""
        pass
    
    @abstractmethod
    def loop(self):
        """Main application loop."""
        pass
    
    @abstractmethod
    def get_config_schema(self):
        """Return configuration schema."""
        pass
    
    @abstractmethod
    def get_web_routes(self):
        """Return custom web routes."""
        pass
```

### 2. Display Application Interface

```python
class DisplayContent(ABC):
    """Base class for displayable content."""
    
    @abstractmethod
    async def render(self, display):
        """Render content to display."""
        pass

class MessageQueue:
    """Generic message queue for display content."""
    
    def add_content(self, content: DisplayContent):
        """Add content to queue."""
        pass
```

### 3. Configuration Provider

```python
class ConfigProvider(ABC):
    """Base configuration provider."""
    
    @abstractmethod
    def get_defaults(self):
        """Return default configuration."""
        pass
    
    @abstractmethod
    def validate(self, config):
        """Validate configuration."""
        pass
```

## Refactoring Steps

### Phase 1: Library Structure Setup ✅ COMPLETED

1. **Create new library repository** ✅
   - Initialize `sldk` project structure
   - Set up proper Python packaging with pyproject.toml
   - Create comprehensive README and documentation
   - Add LICENSE and contributing guidelines

2. **Extract display interfaces** ✅
   - Define DisplayInterface ABC with async methods
   - Create display content classes (ScrollingText, StaticText)
   - Implement ContentQueue for automatic content cycling
   - Add comprehensive docstrings and type hints

3. **Extract unified display logic** ✅
   - Move unified display implementation
   - Add hardware auto-detection system
   - Create device driver structure in sldk/display/devices/
   - Support for both hardware and simulator platforms

4. **Application framework** ✅
   - Create SLDKApp base class with three-process architecture
   - Implement memory-aware process spawning
   - Add create_display() override capability for custom hardware
   - Full async/await support for ESP32 compatibility

### Phase 2: Hardware Abstraction ✅ COMPLETED

5. **Multi-hardware support** ✅
   - Device driver architecture with auto-detection
   - MatrixPortal S3 device driver implementation
   - Generic displayio device driver for any CircuitPython board
   - Application-specific hardware override support

6. **Hardware contribution framework** ✅
   - Hardware developer guide and documentation
   - Device registration and detection system
   - Custom hardware examples and templates
   - Clear contribution guidelines for new devices

### Phase 3: Web Framework (Planned)

1. **Extract web framework**
   - Create generic web server base with async support
   - Define handler interface for custom endpoints
   - Move static assets framework and templates
   - Add configuration UI components

2. **Settings and configuration**
   - Create settings management abstraction
   - Web-based configuration interface
   - Real-time settings updates via WebSocket
   - Configuration validation and persistence

3. **Web UI enhancements**
   - Live display preview in browser
   - Animation controls and tuning
   - Hardware status and diagnostics
   - Mobile-responsive design

### Phase 4: OTA Updates and Deployment (Planned)

1. **Extract OTA system**
   - Generic OTA updater for any Git repository
   - Version management and rollback capabilities
   - Progress tracking and error handling
   - Integration with web UI

2. **Deployment tools**
   - .mpy compilation and optimization
   - Dependency management for CircuitPython
   - File size optimization and bundling
   - Remote deployment via web interface

3. **Development tools**
   - Hot-reload for rapid development
   - Remote debugging capabilities
   - Performance profiling and memory monitoring
   - Automated testing framework

### Phase 5: Advanced Features (Planned)

1. **Animation framework**
   - Advanced transition effects and easing
   - Animation composition and sequencing
   - Performance-optimized rendering pipeline
   - Custom animation plugins

2. **Plugin system**
   - Plugin discovery and loading mechanism
   - Configuration plugin interface
   - Content source plugins (RSS, APIs, sensors)
   - Display effect plugins

### Phase 6: Package Distribution (Planned)

1. **PyPI distribution**
   - Prepare package for PyPI upload
   - Add comprehensive package metadata
   - Create installation documentation
   - Set up automated releases

2. **CircuitPython Bundle**
   - Integrate with Adafruit CircuitPython Bundle
   - Optimize for memory usage on microcontrollers
   - Create bundle-specific documentation
   - Test on various CircuitPython boards

3. **Community and ecosystem**
   - Create community contribution guidelines
   - Set up issue and feature request templates
   - Build example gallery and showcase
   - Establish roadmap and versioning strategy

## Current Status Update

### ✅ Completed (Phases 1-2)

**Core Infrastructure:**
- SLDK library structure with modern Python packaging
- Display abstraction layer with async support
- Three-process architecture (display, data, web)
- Memory-aware process spawning for ESP32
- Content framework (ScrollingText, StaticText, ContentQueue)
- Application framework with SLDKApp base class

**Hardware Support:**
- Two-tier hardware support (application-specific + library contributions)
- Hardware auto-detection system
- MatrixPortal S3 device driver
- Generic displayio device support
- Custom hardware override capability
- Comprehensive hardware developer documentation

**Examples and Testing:**
- Hello World example application
- Animation demo with custom content
- Custom hardware implementation example
- Basic library tests (151 unit tests still passing)
- Hardware developer guide and contribution framework

### 🚧 Next Priority (Phase 3)

**Web Framework** - Extract and modernize the web interface system for settings, configuration, and live display preview.

## Theme Park App Migration (Final Phase)

1. **Refactor theme park app**
   - Create ThemeParkApp(SLDKApp)
   - Move models to app-specific directory
   - Extract theme park web routes
   - Isolate API service

2. **Update imports and dependencies**
   - Update all imports to use SLDK library
   - Remove duplicated code
   - Update requirements and deployment
   - Test on hardware

3. **Create migration guide**
   - Document breaking changes
   - Provide migration scripts
   - Update all documentation
   - Create upgrade path

## Technical Considerations

### 1. Backward Compatibility

- Maintain CircuitPython 8.x/9.x compatibility
- Support existing MatrixPortal S3 hardware
- Preserve OTA update capability
- Keep memory footprint minimal

### 2. Extensibility Points

- **Display Providers**: Custom display implementations
- **Web Handlers**: Application-specific endpoints
- **Animations**: Custom animation classes
- **Config Schemas**: Application settings
- **Update Sources**: Alternative update mechanisms

### 3. Development Experience

- **Hot Reload**: Automatic reload on file changes (desktop only)
- **Debug Mode**: Enhanced logging and diagnostics (when memory allows)
- **Simulator**: Accurate hardware simulation (desktop development)
- **Web UI**: Live configuration and testing (optional on ESP32)
- **CLI Tools**: Project scaffolding and deployment

### 4. Memory Optimization for ESP32

#### Core Principles
- **Pay for what you use**: Features are optional and loaded on-demand
- **Pre-allocate**: Fixed-size buffers to avoid fragmentation
- **Reuse everything**: String pools, buffer reuse, object recycling
- **Compile to .mpy**: Reduces memory by ~50% and speeds loading
- **Minimal dependencies**: Core functionality with zero external deps

#### Memory Budget (Target)
- CircuitPython core: ~300KB
- LED Dev Kit core: <50KB
- Application code: <50KB  
- Runtime data: ~100KB
- **Total**: <500KB (fits in ESP32-S3's 520KB)

#### Techniques
```python
# Bad - Creates new strings constantly
def update_display(temp):
    return f"Temperature: {temp}°F"

# Good - Reuses format string
TEMP_FORMAT = "Temperature: {}°F"
def update_display(temp):
    return TEMP_FORMAT.format(temp)

# Better - Pre-allocated buffer
class TempDisplay:
    def __init__(self):
        self.buffer = bytearray(30)
        self.format = "Temperature: {}°F"
    
    def update(self, temp):
        # Reuse buffer, no allocation
        self.buffer[:] = self.format.format(temp).encode()
        return self.buffer
```

## API Examples

### Creating a Simple Application

```python
from led_devkit import LEDApplication, ScrollingText
from led_devkit.colors import RED, BLUE

class HelloWorldApp(LEDApplication):
    def setup(self):
        self.message = ScrollingText("Hello, World!", color=RED)
    
    def loop(self):
        self.display.show(self.message)
        self.wait(0.1)

# Run the application
if __name__ == "__main__":
    app = HelloWorldApp()
    app.run()
```

### Adding Web Configuration

```python
from led_devkit import LEDApplication, ConfigSchema
from led_devkit.web import route

class ConfigurableApp(LEDApplication):
    def get_config_schema(self):
        return ConfigSchema({
            'message': {'type': 'string', 'default': 'Hello'},
            'color': {'type': 'color', 'default': '#FF0000'},
            'speed': {'type': 'number', 'default': 0.05}
        })
    
    @route('/custom')
    def custom_page(self, request):
        return self.render_template('custom.html')
```

### Custom Animation

```python
from led_devkit.animations import Animation

class RainbowWave(Animation):
    def setup(self):
        self.offset = 0
    
    def update(self, display):
        for x in range(display.width):
            hue = (x + self.offset) / display.width
            display.set_pixel(x, 0, hsv_to_rgb(hue, 1, 1))
        self.offset += 1
```

## Testing Strategy

### 1. Unit Tests
- Test each component in isolation
- Mock hardware dependencies
- Achieve >90% coverage

### 2. Integration Tests
- Test library integration points
- Verify platform compatibility
- Test with example applications

### 3. Hardware Tests
- Test on actual MatrixPortal S3
- Verify memory usage
- Test OTA updates
- Measure performance

### 4. Example Applications
- Create 5-10 example applications
- Cover different use cases
- Include in CI/CD pipeline

## Documentation Plan

### 1. Getting Started Guide
- Installation instructions
- First application tutorial
- Hardware setup guide
- Development environment setup

### 2. API Reference
- Auto-generated from docstrings
- Complete parameter documentation
- Usage examples for each class

### 3. Cookbook
- Common patterns and recipes
- Animation examples
- Web UI customization
- Deployment strategies

### 4. Architecture Guide
- Design decisions
- Extension points
- Performance considerations
- Memory optimization

## Release Plan

### Version 0.1.0 (MVP)
- Core display functionality
- Basic simulator
- Simple web server
- Text scrolling

### Version 0.2.0
- OTA updates
- WiFi configuration
- Enhanced simulator
- More animations

### Version 0.3.0
- Plugin system
- Advanced web UI
- Performance tools
- More examples

### Version 1.0.0
- Stable API
- Comprehensive docs
- Production ready
- Community tools

## Success Metrics

1. **Adoption**: 100+ GitHub stars in 6 months
2. **Usage**: 50+ projects using the library
3. **Community**: 10+ contributors
4. **Quality**: >90% test coverage
5. **Performance**: <500KB memory footprint

## Risks and Mitigation

### Technical Risks
1. **Memory constraints**: Mitigate with lazy loading and optimization
2. **Platform differences**: Extensive testing on both platforms
3. **API stability**: Careful design and beta testing

### Adoption Risks
1. **Documentation**: Invest heavily in docs and examples
2. **Migration effort**: Provide tools and guides
3. **Learning curve**: Video tutorials and workshops

## Implementation Status

### Current Phase: Display/Animation System (Phase 1)
See [SLDK_Phase1_Display_Implementation.md](SLDK_Phase1_Display_Implementation.md) for detailed progress.

### Completed Decisions
- ✅ Library name: SLDK (Scrolling LED Dev Kit)
- ✅ Architecture: Inheritance model with `LEDApplication` base class
- ✅ Web framework: Included with easy opt-out
- ✅ Async model: Full async/await throughout
- ✅ Deployment: Built-in .mpy export functionality

### Next Steps

1. **Create SLDK library structure** (In Progress)
2. **Extract display interfaces and base implementation**
3. **Build animation framework**
4. **Test on ESP32 hardware**
5. **Continue with remaining phases**

## Outstanding Questions

1. Should we support other LED hardware beyond MatrixPortal S3?
2. What license should the library use? (Suggesting MIT for maximum adoption)
3. Should we create a companion VS Code extension?
4. What additional examples beyond Hello World are most important?

## Conclusion

This refactoring will transform the Theme Park Waits codebase into a powerful, reusable library for LED development while maintaining all existing functionality. The clean separation of concerns will enable faster development, easier testing, and broader adoption of LED matrix projects in the CircuitPython community.