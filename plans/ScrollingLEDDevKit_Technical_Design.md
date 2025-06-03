# Scrolling LED Dev Kit - Technical Design Document

## Overview

This document provides technical implementation details for refactoring the Theme Park Waits application into the Scrolling LED Dev Kit library. It includes specific code examples, interface definitions, and migration strategies.

## Core Interfaces

### Display System

```python
# led_devkit/display/interface.py
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Callable

class DisplayInterface(ABC):
    """Base interface for all display implementations."""
    
    @property
    @abstractmethod
    def width(self) -> int:
        """Display width in pixels."""
        pass
    
    @property
    @abstractmethod
    def height(self) -> int:
        """Display height in pixels."""
        pass
    
    @abstractmethod
    def set_pixel(self, x: int, y: int, color: int) -> None:
        """Set a single pixel color."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear the display."""
        pass
    
    @abstractmethod
    def show(self) -> None:
        """Update the physical display."""
        pass
    
    @abstractmethod
    async def show_text(self, text: str, **kwargs) -> None:
        """Display text with optional parameters."""
        pass
    
    @abstractmethod
    def set_brightness(self, brightness: float) -> None:
        """Set display brightness (0.0-1.0)."""
        pass

class ScrollingDisplay(DisplayInterface):
    """Display with scrolling text capabilities."""
    
    @abstractmethod
    async def scroll_text(self, text: str, speed: float = 0.05, **kwargs) -> None:
        """Scroll text across the display."""
        pass
    
    @abstractmethod
    def set_scroll_speed(self, speed: float) -> None:
        """Set default scroll speed."""
        pass
```

### Application Framework with Three Async Processes

```python
# led_devkit/app/base.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
import asyncio
from dataclasses import dataclass
import time

@dataclass
class AppState:
    """Shared application state between async processes."""
    running: bool = True
    display_content: Optional['DisplayContent'] = None
    config: Dict[str, Any] = None
    last_update: float = 0
    update_in_progress: bool = False
    
class LEDApplication(ABC):
    """Base class for LED applications with three separate async processes."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.display = None
        self.web_server = None
        self.state = AppState(config=self.config)
        self._tasks = []
        self._message_queue = asyncio.Queue()
        self._display_queue = asyncio.Queue()
    
    @abstractmethod
    async def setup(self) -> None:
        """Initialize application resources."""
        pass
    
    @abstractmethod
    async def update_data(self) -> None:
        """Update application data - called by data update process."""
        pass
    
    @abstractmethod
    async def prepare_display_content(self) -> DisplayContent:
        """Prepare content for display - called by display process."""
        pass
    
    async def cleanup(self) -> None:
        """Cleanup resources on shutdown."""
        pass
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Return JSON schema for configuration."""
        return {
            "type": "object",
            "properties": {
                "brightness": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.5
                },
                "update_interval": {
                    "type": "integer",
                    "minimum": 60,
                    "default": 300,
                    "description": "Data update interval in seconds"
                }
            }
        }
    
    def get_web_routes(self) -> List[Tuple[str, str, Callable]]:
        """Return list of (path, method, handler) tuples."""
        return []
    
    # Process 1: Display Process
    async def display_process(self) -> None:
        """Process 1: Handle display updates."""
        logger.info("Starting display process")
        
        while self.state.running:
            try:
                # Get content to display
                if self.state.display_content:
                    await self.state.display_content.render(self.display)
                else:
                    # No content, show default
                    content = await self.prepare_display_content()
                    if content:
                        await content.render(self.display)
                
                # Small delay to control frame rate
                await asyncio.sleep(0.02)  # ~50 FPS
                
            except Exception as e:
                logger.error(f"Display process error: {e}")
                await asyncio.sleep(1)
    
    # Process 2: Data Update Process  
    async def data_update_process(self) -> None:
        """Process 2: Handle data updates."""
        logger.info("Starting data update process")
        
        while self.state.running:
            try:
                # Check if update needed
                update_interval = self.config.get('update_interval', 300)
                if time.time() - self.state.last_update >= update_interval:
                    self.state.update_in_progress = True
                    
                    # Perform update
                    await self.update_data()
                    
                    self.state.last_update = time.time()
                    self.state.update_in_progress = False
                    
                    # Notify display process of new data
                    await self._message_queue.put({'type': 'data_updated'})
                
                # Check for config changes more frequently
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Data update process error: {e}")
                self.state.update_in_progress = False
                await asyncio.sleep(30)  # Back off on error
    
    # Process 3: Web Server Process
    async def web_server_process(self) -> None:
        """Process 3: Handle web interface."""
        logger.info("Starting web server process")
        
        if not self.web_server:
            from ..web.server import WebServer
            self.web_server = WebServer(self)
        
        try:
            await self.web_server.start()
            
            while self.state.running:
                # Process any web server tasks
                await self.web_server.process_requests()
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Web server process error: {e}")
        finally:
            await self.web_server.stop()
    
    async def run(self) -> None:
        """Run the application with three async processes."""
        try:
            self.state.running = True
            await self.setup()
            
            # Start all three processes
            tasks = [
                asyncio.create_task(self.display_process()),
                asyncio.create_task(self.data_update_process()),
                asyncio.create_task(self.web_server_process())
            ]
            self._tasks.extend(tasks)
            
            # Wait for any task to complete (should run forever)
            done, pending = await asyncio.wait(
                tasks,
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # If any task completes, something went wrong
            for task in done:
                if task.exception():
                    logger.error(f"Task failed: {task.exception()}")
                    
        finally:
            self.state.running = False
            await self.cleanup()
            
            # Cancel all tasks
            for task in self._tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
    
    # Inter-process communication
    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send message between processes."""
        await self._message_queue.put(message)
    
    async def update_config(self, config: Dict[str, Any]) -> None:
        """Update configuration from web interface."""
        self.config.update(config)
        self.state.config = self.config
        
        # Notify processes of config change
        await self.send_message({
            'type': 'config_updated',
            'config': config
        })
```

### Thread-Safe Content Queue

```python
# led_devkit/display/queue.py
import asyncio
from typing import List, Optional
from .content import DisplayContent

class ThreadSafeContentQueue:
    """Thread-safe content queue for display process."""
    
    def __init__(self):
        self._queue: List[DisplayContent] = []
        self._lock = asyncio.Lock()
        self._current_index = 0
        self._update_event = asyncio.Event()
    
    async def set_content(self, content_list: List[DisplayContent]) -> None:
        """Replace entire content list (called by data update process)."""
        async with self._lock:
            self._queue = content_list
            self._current_index = 0
        self._update_event.set()
    
    async def get_next(self) -> Optional[DisplayContent]:
        """Get next content to display (called by display process)."""
        async with self._lock:
            if not self._queue:
                return None
                
            content = self._queue[self._current_index]
            
            # Check if current content is complete
            if content.is_complete():
                self._current_index = (self._current_index + 1) % len(self._queue)
                content = self._queue[self._current_index]
                
            return content
    
    async def wait_for_update(self, timeout: Optional[float] = None) -> bool:
        """Wait for content update."""
        try:
            await asyncio.wait_for(self._update_event.wait(), timeout)
            self._update_event.clear()
            return True
        except asyncio.TimeoutError:
            return False
```

### Content and Animation System

```python
# led_devkit/display/content.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import asyncio

class DisplayContent(ABC):
    """Base class for displayable content."""
    
    def __init__(self, duration: Optional[float] = None):
        self.duration = duration
        self.start_time = None
    
    @abstractmethod
    async def render(self, display: DisplayInterface) -> None:
        """Render content to display."""
        pass
    
    def is_complete(self) -> bool:
        """Check if content display is complete."""
        if self.duration is None:
            return False
        if self.start_time is None:
            return False
        return (asyncio.get_event_loop().time() - self.start_time) >= self.duration

class ScrollingTextContent(DisplayContent):
    """Scrolling text content."""
    
    def __init__(self, text: str, color: int = 0xFFFFFF, speed: float = 0.05):
        super().__init__()
        self.text = text
        self.color = color
        self.speed = speed
        self.position = 0
    
    async def render(self, display: DisplayInterface) -> None:
        """Render scrolling text."""
        if self.start_time is None:
            self.start_time = asyncio.get_event_loop().time()
            
        await display.show_text(
            self.text,
            x=self.position,
            color=self.color
        )
        self.position -= 1
        
        # Reset when text scrolls off screen
        text_width = len(self.text) * 6  # Approximate
        if self.position < -text_width:
            self.position = display.width

class Animation(DisplayContent):
    """Base class for animations."""
    
    def __init__(self, duration: Optional[float] = None, fps: int = 30):
        super().__init__(duration)
        self.fps = fps
        self.frame = 0
        self.last_frame_time = 0
    
    @abstractmethod
    def update(self, display: DisplayInterface, frame: int) -> None:
        """Update animation for current frame."""
        pass
    
    async def render(self, display: DisplayInterface) -> None:
        """Render animation frame."""
        current_time = asyncio.get_event_loop().time()
        
        if self.start_time is None:
            self.start_time = current_time
            
        # Check if it's time for next frame
        frame_duration = 1.0 / self.fps
        if current_time - self.last_frame_time >= frame_duration:
            self.update(display, self.frame)
            self.frame += 1
            self.last_frame_time = current_time
```

### Configuration System

```python
# led_devkit/config/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
import os

class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, 
                 config_file: str = "settings.json",
                 schema: Optional[Dict[str, Any]] = None):
        self.config_file = config_file
        self.schema = schema or {}
        self._config = {}
        self._observers = []
        self.load()
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(self.config_file, 'r') as f:
                self._config = json.load(f)
        except (OSError, json.JSONDecodeError):
            self._config = self._get_defaults()
        return self._config
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
        except OSError as e:
            print(f"Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        old_value = self._config.get(key)
        self._config[key] = value
        
        # Notify observers
        for observer in self._observers:
            observer(key, old_value, value)
    
    def observe(self, callback: Callable[[str, Any, Any], None]) -> None:
        """Register configuration change observer."""
        self._observers.append(callback)
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default values from schema."""
        defaults = {}
        for key, spec in self.schema.get('properties', {}).items():
            if 'default' in spec:
                defaults[key] = spec['default']
        return defaults
```

### Web Framework

```python
# led_devkit/web/server.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, Optional, List, Tuple
import asyncio
import json

class WebHandler:
    """Base web request handler."""
    
    def __init__(self, app: 'LEDApplication'):
        self.app = app
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming request."""
        path = request.get('path', '/')
        method = request.get('method', 'GET')
        
        # Find matching route
        for route_path, route_method, handler in self.get_routes():
            if path == route_path and method == route_method:
                return await handler(request)
        
        # Default 404
        return {
            'status': 404,
            'body': 'Not Found',
            'headers': {'Content-Type': 'text/plain'}
        }
    
    def get_routes(self) -> List[Tuple[str, str, Callable]]:
        """Get all available routes."""
        routes = [
            ('/', 'GET', self.index),
            ('/api/config', 'GET', self.get_config),
            ('/api/config', 'POST', self.set_config),
            ('/api/status', 'GET', self.get_status),
        ]
        
        # Add application-specific routes
        if hasattr(self.app, 'get_web_routes'):
            routes.extend(self.app.get_web_routes())
            
        return routes
    
    async def index(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Serve index page."""
        return {
            'status': 200,
            'body': self.render_template('index.html'),
            'headers': {'Content-Type': 'text/html'}
        }
    
    async def get_config(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get current configuration."""
        return {
            'status': 200,
            'body': json.dumps(self.app.config),
            'headers': {'Content-Type': 'application/json'}
        }
    
    async def set_config(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Update configuration."""
        try:
            data = json.loads(request.get('body', '{}'))
            for key, value in data.items():
                self.app.config[key] = value
            
            # Save configuration
            if hasattr(self.app, 'config_manager'):
                self.app.config_manager.save()
                
            return {
                'status': 200,
                'body': json.dumps({'success': True}),
                'headers': {'Content-Type': 'application/json'}
            }
        except Exception as e:
            return {
                'status': 400,
                'body': json.dumps({'error': str(e)}),
                'headers': {'Content-Type': 'application/json'}
            }
```

## Migration Strategy

### Phase 1: Extract Display Interfaces

Current code:
```python
# src/ui/display_base.py
class Display:
    def __init__(self, config=None):
        self.settings_manager = config.get('settings_manager') if config else None
        # ... hardware specific setup ...
```

Refactored library code:
```python
# led_devkit/display/base.py
class BaseDisplay(DisplayInterface):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.width = self.config.get('width', 64)
        self.height = self.config.get('height', 32)
```

Application-specific code:
```python
# theme_park_waits/displays/ride_display.py
from led_devkit.display import BaseDisplay

class RideDisplay(BaseDisplay):
    async def show_ride_wait_time(self, wait_time: str):
        """Theme park specific method."""
        await self.show_text(
            wait_time,
            scale=2,
            color=self.config.get('wait_time_color', 0xFFFFFF)
        )
```

### Phase 2: Extract Message Queue

Current code:
```python
# src/ui/message_queue.py
class MessageQueue:
    async def add_rides(self, park_list):
        # Theme park specific logic
```

Refactored library code:
```python
# led_devkit/display/queue.py
class ContentQueue:
    """Generic content queue."""
    
    def __init__(self, display: DisplayInterface):
        self.display = display
        self.queue = []
        self.current_index = 0
    
    def add(self, content: DisplayContent) -> None:
        """Add content to queue."""
        self.queue.append(content)
    
    async def show_next(self) -> None:
        """Show next content in queue."""
        if not self.queue:
            return
            
        content = self.queue[self.current_index]
        await content.render(self.display)
        
        if content.is_complete():
            self.current_index = (self.current_index + 1) % len(self.queue)
```

Application-specific code:
```python
# theme_park_waits/displays/ride_queue.py
from led_devkit.display import ContentQueue, ScrollingTextContent

class RideQueue(ContentQueue):
    async def add_rides(self, park_list):
        """Add theme park rides to queue."""
        for park in park_list.selected_parks:
            for ride in park.rides:
                if ride.is_open():
                    content = RideWaitContent(ride)
                    self.add(content)
```

### Phase 3: Web Server Refactoring

Current code:
```python
# src/network/unified_web_server.py
async def handle_set_settings(self, query_params):
    # Direct theme park logic
```

Refactored library code:
```python
# led_devkit/web/handlers.py
class ConfigHandler:
    """Generic configuration handler."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
    
    async def handle_update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle configuration update."""
        errors = self.validate(data)
        if errors:
            return {'success': False, 'errors': errors}
            
        for key, value in data.items():
            self.config_manager.set(key, value)
            
        self.config_manager.save()
        return {'success': True}
```

Application-specific code:
```python
# theme_park_waits/web/handlers.py
from led_devkit.web import ConfigHandler

class ThemeParkConfigHandler(ConfigHandler):
    def validate(self, data: Dict[str, Any]) -> List[str]:
        """Validate theme park specific settings."""
        errors = super().validate(data)
        
        if 'park_ids' in data:
            # Validate park IDs
            valid_ids = self.get_valid_park_ids()
            for park_id in data['park_ids']:
                if park_id not in valid_ids:
                    errors.append(f"Invalid park ID: {park_id}")
                    
        return errors
```

## Memory Optimization for ESP32/CircuitPython

### ESP32 Constraints
- **RAM**: ~520KB total, ~200KB available to CircuitPython
- **Speed**: 240MHz dual-core, but CircuitPython uses single core
- **Flash**: 4-8MB typical, but .py files are loaded into RAM
- **No threading**: Only cooperative multitasking via asyncio

### Memory Optimization Strategies

#### 1. Minimal Core with Optional Features

```python
# led_devkit/__init__.py
# Absolute minimal imports - just what's needed to display
__version__ = "0.1.0"

# Core display only
def get_display():
    """Get display with minimal memory usage."""
    from .display.base import Display
    return Display()

# Optional features loaded on demand
_features = {
    'web': None,
    'ota': None,
    'animations': None
}

def enable_feature(name):
    """Enable optional feature on demand."""
    if name == 'web' and _features['web'] is None:
        from .web.minimal import MinimalWebServer
        _features['web'] = MinimalWebServer()
    elif name == 'ota' and _features['ota'] is None:
        from .ota.minimal import MinimalOTA
        _features['ota'] = MinimalOTA()
    return _features.get(name)
```

#### 2. Memory-Conscious Data Structures

```python
# led_devkit/display/queue.py
# Use arrays instead of lists where possible
import array

class MemoryEfficientQueue:
    """Queue optimized for low memory usage."""
    
    def __init__(self, max_items=20):
        # Pre-allocate fixed size to avoid fragmentation
        self.max_items = max_items
        self.items = [None] * max_items
        self.head = 0
        self.tail = 0
        self.count = 0
    
    def add(self, item):
        """Add item with minimal allocation."""
        if self.count >= self.max_items:
            # Overwrite oldest
            self.head = (self.head + 1) % self.max_items
            self.count -= 1
            
        self.items[self.tail] = item
        self.tail = (self.tail + 1) % self.max_items
        self.count += 1
        
    def get_next(self):
        """Get next item without allocation."""
        if self.count == 0:
            return None
            
        item = self.items[self.head]
        self.head = (self.head + 1) % self.max_items
        self.count -= 1
        return item
```

#### 3. Compile to .mpy Files

```makefile
# Makefile for creating .mpy files
MPY_CROSS = mpy-cross

# Compile only essential modules
CORE_MODULES = display/base.py display/text.py app/minimal.py utils/colors.py

compile-core:
	@for module in $(CORE_MODULES); do \
		$(MPY_CROSS) -march=xtensawin -o "src/led_devkit/$${module%.py}.mpy" "src/led_devkit/$$module"; \
	done

# Full compile for production
compile-all:
	find src/led_devkit -name "*.py" -not -path "*/examples/*" | while read f; do \
		$(MPY_CROSS) -march=xtensawin -o "$${f%.py}.mpy" "$$f"; \
		rm "$$f"; \
	done
```

#### 4. Simplified Three-Process Architecture for ESP32

```python
# led_devkit/app/minimal.py
# Simplified for ESP32 memory constraints
import gc
import asyncio
import time

class MinimalLEDApp:
    """Minimal app for ESP32 with reduced memory usage."""
    
    def __init__(self):
        self.running = True
        self.display = None
        self.last_update = 0
        self.update_interval = 300  # 5 minutes
        self.content = []
        self.content_index = 0
        
    async def run(self):
        """Run with memory-conscious task management."""
        # Start with garbage collection
        gc.collect()
        print(f"Free memory at start: {gc.mem_free()}")
        
        # Create minimal tasks
        display_task = asyncio.create_task(self._display_loop())
        update_task = asyncio.create_task(self._update_loop())
        
        # Optional web server only if enough memory
        web_task = None
        if gc.mem_free() > 50000:  # 50KB free
            try:
                web_task = asyncio.create_task(self._web_loop())
            except MemoryError:
                print("Not enough memory for web server")
        
        # Run until stopped
        tasks = [t for t in [display_task, update_task, web_task] if t]
        await asyncio.gather(*tasks)
    
    async def _display_loop(self):
        """Minimal display loop."""
        while self.running:
            if self.content:
                # Show current content
                item = self.content[self.content_index]
                await self.display.show_text(item)
                
                # Advance
                self.content_index = (self.content_index + 1) % len(self.content)
                
            await asyncio.sleep(0.05)  # 20 FPS for ESP32
            
            # Periodic GC during display
            if self.content_index == 0:
                gc.collect()
    
    async def _update_loop(self):
        """Minimal update loop."""
        while self.running:
            now = time.monotonic()
            if now - self.last_update >= self.update_interval:
                try:
                    await self.update_data()
                    self.last_update = now
                except Exception as e:
                    print(f"Update error: {e}")
                finally:
                    gc.collect()
                    
            await asyncio.sleep(10)  # Check every 10 seconds
    
    async def _web_loop(self):
        """Optional minimal web server."""
        if not hasattr(self, 'web_server'):
            return
            
        while self.running:
            try:
                await self.web_server.poll()
            except Exception:
                pass  # Ignore web errors
            await asyncio.sleep(0.5)  # Lower priority
```

#### 5. String and Buffer Reuse

```python
# led_devkit/utils/memory.py
# Reuse strings and buffers to reduce allocations

class StringPool:
    """Pool frequently used strings to save memory."""
    
    def __init__(self):
        # Pre-define common strings
        self._pool = {
            'loading': "Loading...",
            'error': "Error",
            'closed': "Closed",
            'updating': "Updating...",
            'connected': "Connected",
            'disconnected': "Disconnected"
        }
        
    def get(self, key, default=None):
        """Get pooled string or default."""
        return self._pool.get(key, default)
        
    def add(self, key, value):
        """Add string to pool if memory allows."""
        if gc.mem_free() > 10000:  # Only if 10KB+ free
            self._pool[key] = value

# Global string pool
strings = StringPool()

# Buffer reuse for display
class ReusableBuffer:
    """Reusable buffer for display operations."""
    
    def __init__(self, size=256):
        self.buffer = bytearray(size)
        self.size = size
        
    def clear(self):
        """Clear buffer efficiently."""
        for i in range(self.size):
            self.buffer[i] = 0
            
    def get_slice(self, length):
        """Get buffer slice without allocation."""
        return memoryview(self.buffer)[:length]
```

### 2. Compiled Modules

```makefile
# Makefile for creating .mpy files
MPY_CROSS = mpy-cross

compile:
	find src/led_devkit -name "*.py" -not -path "*/examples/*" | while read f; do \
		$(MPY_CROSS) -o "$${f%.py}.mpy" "$$f"; \
	done

clean-mpy:
	find src/led_devkit -name "*.mpy" -delete
```

### 3. Memory Pool Pattern

```python
# led_devkit/utils/memory.py
class ObjectPool:
    """Reusable object pool to reduce allocations."""
    
    def __init__(self, factory: Callable, size: int = 10):
        self.factory = factory
        self.pool = [factory() for _ in range(size)]
        self.available = list(range(size))
        self.in_use = set()
    
    def acquire(self):
        """Get object from pool."""
        if not self.available:
            # Pool exhausted, create new
            return self.factory()
            
        index = self.available.pop()
        self.in_use.add(index)
        return self.pool[index]
    
    def release(self, obj):
        """Return object to pool."""
        try:
            index = self.pool.index(obj)
            if index in self.in_use:
                self.in_use.remove(index)
                self.available.append(index)
        except ValueError:
            pass  # Object not from pool
```

## ESP32-First Unified Codebase

The library uses a single codebase that runs identically on both ESP32 hardware and desktop development environments. This is achieved through careful design that respects ESP32 constraints everywhere.

### Platform Detection and Adaptation

```python
# led_devkit/utils/platform.py
import sys
import gc

IS_CIRCUITPYTHON = hasattr(sys, 'implementation') and sys.implementation.name == 'circuitpython'

class Platform:
    """Platform utilities that work identically on ESP32 and desktop."""
    
    @staticmethod
    def get_free_memory() -> int:
        """Get available memory in bytes."""
        # Always use gc.mem_free() style - desktop simulator provides it
        try:
            return gc.mem_free()
        except AttributeError:
            # Fallback for desktop without simulator
            return 200_000  # Simulate ESP32 memory limit
    
    @staticmethod
    def collect_garbage() -> int:
        """Force garbage collection, return free memory."""
        gc.collect()
        return Platform.get_free_memory()
    
    @staticmethod
    def can_allocate(size: int) -> bool:
        """Check if we can safely allocate size bytes."""
        # Always enforce ESP32 limits
        return Platform.get_free_memory() > (size + 10_000)  # Keep 10KB buffer
```

### Memory-Safe Feature Loading

```python
# led_devkit/app/features.py
class FeatureManager:
    """Manage optional features based on available memory."""
    
    def __init__(self):
        self.features = {}
        self.memory_requirements = {
            'web_server': 30_000,  # 30KB
            'ota_updates': 20_000,  # 20KB  
            'animations': 15_000,   # 15KB
            'advanced_ui': 25_000   # 25KB
        }
    
    def enable(self, feature_name: str):
        """Enable feature if memory allows."""
        if feature_name in self.features:
            return self.features[feature_name]
            
        required = self.memory_requirements.get(feature_name, 0)
        if not Platform.can_allocate(required):
            print(f"Insufficient memory for {feature_name} (needs {required} bytes)")
            return None
            
        # Load feature
        if feature_name == 'web_server':
            from ..web.minimal import MinimalWebServer
            self.features[feature_name] = MinimalWebServer()
        # ... other features ...
        
        return self.features[feature_name]
```

## Testing Utilities

```python
# led_devkit/testing/helpers.py
from unittest.mock import MagicMock
from ..display.interface import DisplayInterface

class MockDisplay(DisplayInterface):
    """Mock display for testing."""
    
    def __init__(self, width: int = 64, height: int = 32):
        self._width = width
        self._height = height
        self.pixels = [[0 for _ in range(width)] for _ in range(height)]
        self.brightness = 1.0
        
    @property
    def width(self) -> int:
        return self._width
        
    @property
    def height(self) -> int:
        return self._height
        
    def set_pixel(self, x: int, y: int, color: int) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = color
            
    def clear(self) -> None:
        self.pixels = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
    def show(self) -> None:
        pass  # No-op for mock
        
    async def show_text(self, text: str, **kwargs) -> None:
        pass  # Mock implementation
        
    def set_brightness(self, brightness: float) -> None:
        self.brightness = max(0.0, min(1.0, brightness))

def create_test_app(app_class, config=None):
    """Create app instance for testing."""
    app = app_class(config or {})
    app.display = MockDisplay()
    return app
```

## Example: Migrated Theme Park App with Three Processes

```python
# theme_park_waits/app.py
from led_devkit import LEDApplication, ThreadSafeContentQueue
from led_devkit.display import ScrollingTextContent
from .models import ThemeParkList
from .api import ThemeParkService
from .displays import RideWaitContent
import asyncio

class ThemeParkApp(LEDApplication):
    """Theme Park Waits application with three async processes."""
    
    async def setup(self):
        """Initialize application resources."""
        # Initialize services
        self.park_service = ThemeParkService()
        self.park_list = ThemeParkList()
        self.content_queue = ThreadSafeContentQueue()
        
        # Load saved parks
        park_ids = self.config.get('park_ids', [])
        self.park_list.set_selected_parks(park_ids)
        
        # Set initial state
        self.state.display_content = await self.prepare_display_content()
    
    async def update_data(self):
        """Process 2: Update park data from API."""
        try:
            # Fetch latest data for each park
            updated_parks = []
            for park in self.park_list.selected_parks:
                data = await self.park_service.fetch_park_data(park.id)
                park.update_from_data(data)
                updated_parks.append(park)
            
            # Build new content list
            content_list = []
            for park in updated_parks:
                if park.is_open:
                    # Add park name
                    content_list.append(
                        ScrollingTextContent(f"{park.name} Wait Times")
                    )
                    
                    # Add rides based on settings
                    skip_closed = self.config.get('skip_closed', False)
                    skip_meet = self.config.get('skip_meet', False)
                    
                    for ride in park.rides:
                        if ride.is_open() or not skip_closed:
                            if 'Meet' not in ride.name or not skip_meet:
                                content_list.append(RideWaitContent(ride))
            
            # Update content queue (thread-safe)
            await self.content_queue.set_content(content_list)
            
            # Update app state
            self.state.display_content = await self.content_queue.get_next()
            
        except Exception as e:
            logger.error(f"Failed to update park data: {e}")
            # Don't clear existing content on error
    
    async def prepare_display_content(self):
        """Process 1: Get content for display."""
        # Get next content from queue
        content = await self.content_queue.get_next()
        
        if not content:
            # No content available, show loading message
            return ScrollingTextContent("Loading wait times...")
            
        return content
    
    def get_config_schema(self):
        """Define configuration schema for web UI."""
        schema = super().get_config_schema()
        schema['properties'].update({
            'park_ids': {
                'type': 'array',
                'items': {'type': 'integer'},
                'default': [],
                'description': 'Selected theme park IDs'
            },
            'skip_closed': {
                'type': 'boolean',
                'default': False,
                'description': 'Hide closed attractions'
            },
            'skip_meet': {
                'type': 'boolean', 
                'default': False,
                'description': 'Hide meet & greet attractions'
            },
            'update_interval': {
                'type': 'integer',
                'minimum': 60,
                'maximum': 3600,
                'default': 300,
                'description': 'Update interval in seconds'
            },
            'sort_mode': {
                'type': 'string',
                'enum': ['alphabetical', 'wait_time', 'location'],
                'default': 'alphabetical',
                'description': 'How to sort attractions'
            }
        })
        return schema
    
    def get_web_routes(self):
        """Define custom web routes for park selection."""
        from .web import handlers
        return [
            ('/api/parks', 'GET', handlers.get_available_parks),
            ('/api/parks/select', 'POST', handlers.select_parks),
            ('/api/vacation', 'GET', handlers.get_vacation),
            ('/api/vacation', 'POST', handlers.set_vacation),
        ]
    
    async def handle_config_change(self, key: str, old_value, new_value):
        """Handle configuration changes from web UI."""
        if key == 'park_ids':
            # Update selected parks
            self.park_list.set_selected_parks(new_value)
            # Trigger immediate data update
            self.state.last_update = 0
        
        elif key == 'update_interval':
            # New interval will be used on next check
            pass
            
        elif key in ['skip_closed', 'skip_meet', 'sort_mode']:
            # Rebuild display content with new filters
            await self.update_data()

# Entry point
def create_app(config=None):
    """Factory function to create app."""
    return ThemeParkApp(config)

if __name__ == "__main__":
    # Run the application
    import asyncio
    app = create_app()
    asyncio.run(app.run())
```

## Process Communication Example

```python
# led_devkit/app/messages.py
from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional

class MessageType(Enum):
    """Message types for inter-process communication."""
    CONFIG_UPDATED = "config_updated"
    DATA_UPDATED = "data_updated" 
    DISPLAY_REQUEST = "display_request"
    ERROR = "error"
    STATUS = "status"

@dataclass
class AppMessage:
    """Message for inter-process communication."""
    type: MessageType
    source: str  # 'display', 'data', 'web'
    data: Optional[Any] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            import time
            self.timestamp = time.time()

# Example usage in processes
async def example_data_process(app: LEDApplication):
    """Example of sending messages from data process."""
    # Send update notification
    await app.send_message(AppMessage(
        type=MessageType.DATA_UPDATED,
        source='data',
        data={'parks_updated': 3, 'rides_found': 47}
    ))
    
async def example_display_process(app: LEDApplication):
    """Example of receiving messages in display process."""
    try:
        # Check for messages with timeout
        message = await asyncio.wait_for(
            app._message_queue.get(),
            timeout=0.1
        )
        
        if message.type == MessageType.DATA_UPDATED:
            # Refresh display content
            app.state.display_content = await app.prepare_display_content()
            
    except asyncio.TimeoutError:
        # No messages, continue normal operation
        pass
```

## Architecture Decisions

Based on requirements, the following decisions have been made:

1. **Library Name**: SLDK (Scrolling LED Dev Kit)
2. **Application Model**: Inheritance-based (`class MyApp(LEDApplication)`)
3. **Web Framework**: Included by default, with easy opt-out
4. **Async Model**: Async/await throughout for consistency
5. **Deployment**: Built-in .mpy compilation support
6. **Implementation Order**: Display/animation system first

### Web Framework Opt-Out

```python
# Easy opt-out for web server
class MyApp(LEDApplication):
    def __init__(self):
        super().__init__(enable_web=False)  # No web server
        
# Or runtime disable
app = MyApp()
app.disable_feature('web_server')
```

### Built-in Deployment

```python
# sldk/deploy.py
import os
import subprocess

async def export_mpy(source_dir: str, output_dir: str, target: str = 'xtensawin'):
    """Export Python files as .mpy for deployment."""
    mpy_cross = 'mpy-cross'
    
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.py'):
                src = os.path.join(root, file)
                rel_path = os.path.relpath(src, source_dir)
                dst = os.path.join(output_dir, rel_path.replace('.py', '.mpy'))
                
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                
                cmd = [mpy_cross, '-march', target, '-o', dst, src]
                subprocess.run(cmd, check=True)
                print(f"Compiled: {rel_path}")
```

## Conclusion

This technical design provides a clear path for extracting reusable LED development functionality while maintaining clean separation from application-specific code. The interfaces are designed to be extensible, memory-efficient, and compatible with both CircuitPython hardware and desktop development environments.