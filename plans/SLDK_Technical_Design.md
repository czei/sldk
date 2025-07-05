# Scrolling LED Dev Kit (SLDK) - Technical Design & Implementation

## Overview

This document provides comprehensive technical implementation details for the Scrolling LED Dev Kit library, including architecture, interfaces, memory optimization strategies, and migration guidance.

## Core Architecture

### Three-Process Async Architecture

The library implements a three-process async architecture for optimal performance and separation of concerns:

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
```

## Core Interfaces

### Display Interface

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
```

#### 3. Simplified Three-Process Architecture for ESP32

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
```

#### 4. String and Buffer Reuse

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
```

## Platform Detection and Adaptation

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
    def can_allocate(size: int) -> bool:
        """Check if we can safely allocate size bytes."""
        # Always enforce ESP32 limits
        return Platform.get_free_memory() > (size + 10_000)  # Keep 10KB buffer
```

## Memory-Safe Feature Loading

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

## Example: Migrated Theme Park App

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
            
        except Exception as e:
            logger.error(f"Failed to update park data: {e}")
```

## Key Design Decisions

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