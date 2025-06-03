# SLDK Phase 1: Display/Animation System Implementation

## Overview

This document tracks the implementation of the display and animation system for SLDK (Scrolling LED Dev Kit). This is the first phase of extracting reusable LED development functionality from the Theme Park Waits application.

## Goals

1. Extract core display interfaces and implementations
2. Create a unified display system that works on both ESP32 and desktop
3. Build a flexible animation framework
4. Maintain ESP32 memory constraints (<50KB for core display system)
5. Ensure all code is async/await compatible

## Current Status

- [ ] Create SLDK library structure
- [ ] Extract display interfaces
- [ ] Migrate unified display implementation
- [ ] Create animation framework
- [ ] Build text rendering system
- [ ] Test on ESP32 hardware
- [ ] Document API

## Implementation Plan

### Step 1: Create Library Structure

```bash
sldk/
├── pyproject.toml
├── README.md
├── LICENSE (MIT)
├── src/
│   └── sldk/
│       ├── __init__.py
│       ├── __version__.py
│       ├── display/
│       │   ├── __init__.py
│       │   ├── interface.py
│       │   ├── base.py
│       │   ├── unified.py
│       │   └── content.py
│       └── utils/
│           ├── __init__.py
│           ├── colors.py
│           └── platform.py
└── tests/
    └── test_display.py
```

### Step 2: Display Interface Definition

```python
# sldk/display/interface.py
from abc import ABC, abstractmethod
from typing import Optional, Tuple

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
    async def clear(self) -> None:
        """Clear the display."""
        pass
    
    @abstractmethod
    async def show(self) -> None:
        """Update the physical display."""
        pass
    
    @abstractmethod
    async def set_pixel(self, x: int, y: int, color: int) -> None:
        """Set a single pixel color."""
        pass
    
    @abstractmethod
    async def set_brightness(self, brightness: float) -> None:
        """Set display brightness (0.0-1.0)."""
        pass
```

### Step 3: Base Display Implementation

Extract from `src/ui/display_base.py`:
- Remove theme park specific methods
- Keep only generic display functionality
- Make all methods async
- Add memory-efficient text rendering

### Step 4: Unified Display

Extract from `src/ui/unified_display.py`:
- Platform detection logic
- Hardware/simulator abstraction
- Remove theme park specific groups
- Simplify for generic use

### Step 5: Display Content System

```python
# sldk/display/content.py
from abc import ABC, abstractmethod
from typing import Optional
import asyncio

class DisplayContent(ABC):
    """Base class for displayable content."""
    
    def __init__(self, duration: Optional[float] = None):
        self.duration = duration
        self._start_time = None
    
    @abstractmethod
    async def render(self, display: DisplayInterface) -> None:
        """Render content to display."""
        pass
    
    @property
    def elapsed(self) -> float:
        """Time elapsed since content started displaying."""
        if self._start_time is None:
            return 0.0
        return asyncio.get_event_loop().time() - self._start_time
    
    @property
    def is_complete(self) -> bool:
        """Check if content display is complete."""
        if self.duration is None:
            return False
        return self.elapsed >= self.duration
    
    async def start(self) -> None:
        """Called when content starts displaying."""
        self._start_time = asyncio.get_event_loop().time()
    
    async def stop(self) -> None:
        """Called when content stops displaying."""
        pass
```

## Files to Extract From

### Display System Files
1. `/src/ui/display_interface.py` - Base interface
2. `/src/ui/display_base.py` - Base implementation 
3. `/src/ui/unified_display.py` - Platform abstraction
4. `/src/utils/color_utils.py` - Color utilities

### Remove Theme Park Dependencies
- `show_ride_wait_time()` 
- `show_ride_name()`
- `show_ride_closed()`
- Theme park specific display groups
- Queue-times attribution

### Keep Generic Features
- `show_text()`
- `scroll_text()`
- `show_splash()`
- `set_brightness()`
- `clear()`
- Basic display groups

## Memory Optimization Checklist

- [ ] Use `__slots__` on frequently created classes
- [ ] Pre-allocate text buffers
- [ ] Reuse display groups
- [ ] Compile color constants
- [ ] Minimize import dependencies
- [ ] Test memory usage on ESP32

## Testing Plan

### Unit Tests
- [ ] Test display interface compliance
- [ ] Test platform detection
- [ ] Test content lifecycle
- [ ] Test memory usage

### Integration Tests  
- [ ] Test on desktop with simulator
- [ ] Test on ESP32 hardware
- [ ] Verify async operation
- [ ] Measure frame rates

### Example Application
```python
# examples/hello_world.py
from sldk import SLDKApp, ScrollingText

class HelloWorld(SLDKApp):
    async def setup(self):
        self.content = ScrollingText("Hello SLDK!", color=0xFF0000)
    
    async def update_data(self):
        pass  # No data updates needed
    
    async def prepare_display_content(self):
        return self.content

if __name__ == "__main__":
    import asyncio
    app = HelloWorld(enable_web=False)
    asyncio.run(app.run())
```

## Progress Tracking

### Completed
- [x] Planning documents created
- [x] Architecture decisions made
- [x] Memory optimization strategies defined

### In Progress
- [ ] Creating library structure
- [ ] Extracting display interfaces

### Next Steps
1. Create sldk repository/directory structure
2. Set up pyproject.toml for modern Python packaging
3. Extract DisplayInterface and create base implementation
4. Test basic functionality
5. Continue with remaining display components

## Notes

- Keep imports minimal to reduce memory overhead
- All methods must be async for consistency
- Test memory usage after each component addition
- Document ESP32-specific considerations
- Maintain compatibility with existing LED simulator