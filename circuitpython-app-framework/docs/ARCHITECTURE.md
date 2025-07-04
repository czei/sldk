# Framework Architecture

Understanding how the CircuitPython App Framework is designed and how its components work together.

## Design Philosophy

The framework follows these core principles:

1. **Progressive Complexity**: Start simple, add features as needed
2. **Hardware Abstraction**: Write once, run on any supported board
3. **Batteries Included**: Common patterns built-in, but replaceable
4. **CircuitPython First**: Designed for constrained environments
5. **Developer Friendly**: Clear APIs and helpful error messages

## High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                      User Code                      │
│                                                     │
│  SimpleScrollApp / BaseApplication / Custom App    │
└───────────────┬─────────────────────┬───────────────┘
                 │                     │
┌───────────────┴───────────────┐     │
│       Framework Core          │     │
│                               │     │
│  ┌─────────────────────────┐ │     │
│  │     Data Sources        │ │     │
│  │  URL / File / Function  │ │     │
│  └─────────┬──────────────┘ │     │
│             │                 │     │
│  ┌─────────┴──────────────┐ │     │  ┌──────────────┐
│  │    Style Engine        │ │     │  │   Plugins    │
│  │  Colors / Animation    │ │     │  │  Extensions  │
│  └─────────┬──────────────┘ │     │  └──────┬──────┘
│             │                 │     │         │
│  ┌─────────┴──────────────┐ │     │         │
│  │   Display Manager      │ │     │         │
│  │  Rendering / Queue     │ │     │         │
│  └────────────────────────┘ │     │         │
└───────────────┬───────────────┘     └─────────┴─────────┘
                 │                                   │
┌───────────────┴───────────────┐     ┌─────────┴─────────┐
│   Hardware Abstraction        │     │    Utilities          │
│                               │     │                       │
│  ┌─────────────────────────┐ │     │  Error Handler        │
│  │    Board Detection      │ │     │  Config Manager       │
│  │    Pin Mapping          │ │     │  State Manager        │
│  └─────────┬──────────────┘ │     │  Network Manager      │
│             │                 │     └─────────────────────┘
│  ┌─────────┴──────────────┐ │
│  │   Display Hardware      │ │
│  │   Matrix / Simulator    │ │
│  └────────────────────────┘ │
└───────────────────────────────┘
```

## Core Components

### SimpleScrollApp

The high-level API that makes simple things simple:

```python
class SimpleScrollApp:
    def __init__(self, text_source=None, **options):
        # Auto-detect board
        self.board = BoardDetector.detect()
        
        # Initialize display
        self.display = DisplayManager(self.board)
        
        # Set up data source
        if callable(text_source):
            self.data_source = FunctionDataSource(text_source)
        elif isinstance(text_source, str):
            self.data_source = StaticDataSource(text_source)
        else:
            self.data_source = text_source
        
        # Apply styles
        self.style_engine = StyleEngine(options.get('styles', {}))
```

### BaseApplication

The foundation for complex applications:

```python
class BaseApplication:
    """Base class providing all framework features."""
    
    async def initialize(self):
        """Set up hardware and network."""
        await self.setup_hardware()
        await self.setup_network()
        await self.load_configuration()
    
    async def run(self):
        """Main application loop."""
        await self.initialize()
        
        while True:
            try:
                # Update data
                data = await self.update_data()
                
                # Create display content
                messages = self.create_display_content(data)
                
                # Update display
                self.display_queue.set_messages(messages)
                
                # Process plugins
                await self.plugin_manager.update_all()
                
                # Handle web requests
                if self.web_server:
                    await self.web_server.process_requests()
                
            except Exception as e:
                self.error_handler.handle(e)
            
            await asyncio.sleep(0.1)
```

### Data Source Architecture

Data sources provide a uniform interface for getting data:

```python
class DataSource:
    """Abstract base for all data sources."""
    
    def __init__(self, cache_duration=None, fallback=None):
        self.cache_duration = cache_duration
        self.fallback = fallback
        self._cache = None
        self._last_fetch = 0
    
    def get(self):
        """Get data with caching."""
        if self._should_update():
            try:
                self._cache = self.fetch()
                self._last_fetch = time.monotonic()
            except Exception:
                return self.fallback
        return self._cache
    
    def fetch(self):
        """Override to implement data fetching."""
        raise NotImplementedError
```

### Style Engine

The style engine handles all visual aspects:

```python
class StyleEngine:
    """Manages visual styling and effects."""
    
    def __init__(self, styles):
        self.styles = self._merge_with_defaults(styles)
        self.effect_processors = self._create_processors()
    
    def apply(self, text, frame_count):
        """Apply all styles and effects."""
        # Basic styling
        color = self._get_color(frame_count)
        brightness = self._get_brightness()
        
        # Effects
        for processor in self.effect_processors:
            text, color = processor.process(text, color, frame_count)
        
        return RenderedText(text, color, brightness)
```

### Display Manager

Handles the complexity of different display types:

```python
class DisplayManager:
    """Manages display hardware and rendering."""
    
    def __init__(self, board_config):
        self.config = board_config
        self.display = self._create_display()
        self.renderer = self._create_renderer()
        self.queue = MessageQueue()
    
    def update(self):
        """Update display with current content."""
        message = self.queue.get_current()
        if message:
            rendered = self.renderer.render(message)
            self.display.show(rendered)
```

## Design Patterns

### 1. Progressive Enhancement

Start simple and add complexity:

```python
# Level 1: Simplest
app = SimpleScrollApp("Hello")

# Level 2: Add dynamics
app = SimpleScrollApp(lambda: get_time())

# Level 3: Add styling
app = SimpleScrollApp(get_time, styles={...})

# Level 4: Full control
class MyApp(BaseApplication):
    # Override everything
```

### 2. Composition Over Inheritance

Components are composable:

```python
# Combine data sources
data = CombinedDataSource([
    URLDataSource("http://api1.com"),
    FileDataSource("/backup.json")
])

# Stack effects
styles = {
    "effects": [RainbowEffect(), BlinkEffect(), FadeEffect()]
}
```

### 3. Dependency Injection

Components can be swapped:

```python
app = SimpleScrollApp(
    data_source=CustomDataSource(),
    display=CustomDisplay(),
    style_engine=CustomStyleEngine()
)
```

### 4. Event-Driven Plugins

Plugins react to application events:

```python
class MyPlugin(Plugin):
    async def on_data_update(self, data):
        # React to new data
        pass
    
    async def on_display_update(self, message):
        # Modify display content
        pass
    
    async def on_error(self, error):
        # Handle errors
        pass
```

## Memory Management

CircuitPython has limited memory, so the framework:

### 1. Lazy Loading

```python
class Component:
    def __init__(self):
        self._heavy_resource = None
    
    @property
    def heavy_resource(self):
        if self._heavy_resource is None:
            self._heavy_resource = self._load_resource()
        return self._heavy_resource
```

### 2. Object Pooling

```python
class MessagePool:
    def __init__(self, size=10):
        self.pool = [DisplayMessage() for _ in range(size)]
        self.available = list(self.pool)
    
    def acquire(self):
        if self.available:
            return self.available.pop()
        return DisplayMessage()  # Create if needed
    
    def release(self, message):
        message.reset()
        if len(self.available) < len(self.pool):
            self.available.append(message)
```

### 3. Streaming Processing

```python
def process_large_data(data_source):
    """Process data in chunks to save memory."""
    for chunk in data_source.iter_chunks(size=100):
        processed = process_chunk(chunk)
        yield processed
        gc.collect()  # Force garbage collection
```

## Network Architecture

### Async HTTP Client

```python
class HTTPClient:
    """Unified HTTP client for CircuitPython and desktop."""
    
    def __init__(self):
        if CIRCUITPYTHON:
            import adafruit_requests
            self.backend = adafruit_requests
        else:
            import aiohttp
            self.backend = AiohttpWrapper()
    
    async def get(self, url, **kwargs):
        # Unified interface regardless of backend
        return await self.backend.get(url, **kwargs)
```

### Connection Management

```python
class NetworkManager:
    """Manages WiFi connection and recovery."""
    
    async def maintain_connection(self):
        """Background task to keep WiFi connected."""
        while True:
            if not self.is_connected():
                try:
                    await self.connect()
                except Exception:
                    await asyncio.sleep(30)  # Retry delay
            await asyncio.sleep(60)  # Check interval
```

## Error Handling Strategy

### Graceful Degradation

```python
class ResilientApp(BaseApplication):
    async def update_data(self):
        try:
            # Try primary source
            return await self.fetch_from_api()
        except NetworkError:
            # Fall back to cache
            return self.load_from_cache()
        except Exception:
            # Last resort: static message
            return {"message": "Data temporarily unavailable"}
```

### Error Recovery

```python
class ErrorHandler:
    def __init__(self):
        self.error_counts = {}
        self.recovery_strategies = {
            NetworkError: self.recover_network,
            MemoryError: self.recover_memory,
            DisplayError: self.recover_display
        }
    
    async def handle(self, error):
        error_type = type(error)
        
        # Track frequency
        self.error_counts[error_type] = \
            self.error_counts.get(error_type, 0) + 1
        
        # Apply recovery strategy
        if error_type in self.recovery_strategies:
            await self.recovery_strategies[error_type]()
```

## Performance Considerations

### 1. Minimize Allocations

```python
# Bad: Creates new string each frame
def update():
    text = "Time: " + str(time.time())
    display.show(text)

# Good: Reuse buffer
text_buffer = bytearray(50)
def update():
    # Format into existing buffer
    text_buffer[:] = b"Time: %d" % time.time()
    display.show(text_buffer)
```

### 2. Batch Operations

```python
class BatchProcessor:
    def __init__(self, batch_size=10):
        self.batch = []
        self.batch_size = batch_size
    
    def add(self, item):
        self.batch.append(item)
        if len(self.batch) >= self.batch_size:
            self.process_batch()
    
    def process_batch(self):
        # Process all items at once
        results = batch_operation(self.batch)
        self.batch.clear()
        return results
```

### 3. Async Cooperation

```python
async def long_operation():
    """Long operation that yields control."""
    for i in range(1000):
        # Do work
        process_item(i)
        
        # Yield control every 10 items
        if i % 10 == 0:
            await asyncio.sleep(0)
```

## Testing Architecture

### Hardware Abstraction for Testing

```python
class MockDisplay:
    """Mock display for testing."""
    def __init__(self, width=64, height=32):
        self.width = width
        self.height = height
        self.buffer = [[0] * width for _ in range(height)]
    
    def show(self, pixels):
        # Capture display state for assertions
        self.last_frame = pixels
```

### Test Fixtures

```python
@pytest.fixture
def test_app():
    """Create app with mock hardware."""
    with patch('cpyapp.hardware.detect_board', return_value=MockBoard()):
        app = SimpleScrollApp("Test")
        app.display = MockDisplay()
        yield app
```

## Future Extensibility

The architecture supports future additions:

### 1. New Display Types

```python
class OLEDDisplay(BaseDisplay):
    """Support for OLED displays."""
    def __init__(self, i2c, width=128, height=64):
        super().__init__(width, height)
        self.oled = adafruit_ssd1306.SSD1306_I2C(width, height, i2c)
```

### 2. New Data Sources

```python
class MQTTDataSource(DataSource):
    """Real-time data from MQTT broker."""
    def __init__(self, broker, topic):
        super().__init__()
        self.client = self.connect_mqtt(broker)
        self.client.subscribe(topic)
```

### 3. New Effects

```python
class ScrollingRainbowEffect(Effect):
    """Rainbow that scrolls across text."""
    def process(self, text, color, frame):
        colors = []
        for i, char in enumerate(text):
            hue = (frame + i * 10) % 360
            colors.append(hsv_to_rgb(hue, 1.0, 1.0))
        return text, colors
```

## Conclusion

The CircuitPython App Framework architecture prioritizes:

- **Simplicity**: Easy things are easy
- **Flexibility**: Hard things are possible
- **Performance**: Efficient on constrained hardware
- **Reliability**: Graceful error handling
- **Extensibility**: Easy to add new features

The layered architecture allows users to engage at their comfort level while providing power users full control over every aspect of their LED applications.