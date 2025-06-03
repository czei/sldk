# SLDK Migration Guide

## Migrating Theme Park Waits to SLDK

This guide explains how to migrate the Theme Park Waits application to use the SLDK framework.

### Overview

SLDK (Scrolling LED Dev Kit) extracts the generic LED display functionality from Theme Park Waits into a reusable framework. This allows:

1. Development and debugging on desktop before deploying to CircuitPython
2. Reusable components for other LED projects
3. Cleaner separation of concerns
4. Better memory management on ESP32

### Architecture Changes

#### Before (Theme Park Waits)
```python
# Direct hardware/simulator management
if IS_CIRCUITPYTHON:
    from adafruit_matrixportal.matrix import Matrix
else:
    from led_simulator.devices.matrixportal_s3 import MatrixPortalS3

# Mixed application and display logic
class UnifiedDisplay:
    # Theme park specific groups
    self.wait_time_name_group = None
    self.wait_time_group = None
    # ...
```

#### After (SLDK)
```python
from sldk import SLDKApp, ScrollingText, StaticText

class ThemeParkApp(SLDKApp):
    async def setup(self):
        # Application-specific setup
        pass
        
    async def update_data(self):
        # Fetch theme park data
        pass
```

### Step-by-Step Migration

#### 1. Install SLDK

```bash
# For development (includes simulator)
pip install -e ./sldk[simulator,web]

# For production (CircuitPython)
# Copy sldk/src/sldk to CIRCUITPY/lib/
```

#### 2. Create New App Structure

Create `src/theme_park_app.py`:

```python
from sldk import SLDKApp, ScrollingText, StaticText
from src.api.theme_park_service import ThemeParkService
from src.config.settings_manager import SettingsManager

class ThemeParkApp(SLDKApp):
    def __init__(self):
        super().__init__(enable_web=True, update_interval=300)
        self.theme_park_service = None
        self.settings_manager = None
        self.current_park_index = 0
        
    async def setup(self):
        """Initialize theme park services."""
        # Initialize settings
        self.settings_manager = SettingsManager()
        self.settings_manager.read_settings()
        
        # Initialize API service
        self.theme_park_service = ThemeParkService(
            self.settings_manager.get_setting("api_url"),
            self.settings_manager.get_setting("api_key")
        )
        
        # Show splash screen
        await self._show_splash()
        
    async def update_data(self):
        """Update theme park wait times."""
        # Show updating message
        self.content_queue.clear()
        self.content_queue.add(ScrollingText(
            "Updating wait times from queue-times.com...",
            color=0xFFFF00
        ))
        
        # Fetch data
        parks = self.theme_park_service.get_wait_times()
        
        # Update content queue with wait times
        self._populate_wait_times(parks)
        
    def _populate_wait_times(self, parks):
        """Populate content queue with wait times."""
        self.content_queue.clear()
        
        for park in parks:
            for ride in park.rides:
                # Add ride name
                self.content_queue.add(StaticText(
                    ride.name,
                    x=0, y=7,
                    color=0x0080FF,
                    duration=1
                ))
                
                # Add wait time or closed
                if ride.is_open:
                    self.content_queue.add(StaticText(
                        f"{ride.wait_time} min",
                        x=10, y=20,
                        color=0xFFFFFF,
                        duration=3
                    ))
                else:
                    self.content_queue.add(StaticText(
                        "Closed",
                        x=14, y=20,
                        color=0xFF0000,
                        duration=2
                    ))
```

#### 3. Update Main Entry Point

Update `src/main.py`:

```python
import asyncio
from src.theme_park_app import ThemeParkApp

async def main():
    app = ThemeParkApp()
    await app.run()

if __name__ == "__main__":
    asyncio.run(main())
```

#### 4. Migrate Display Content

##### Custom Animations

Convert existing animations to SLDK DisplayContent:

```python
from sldk.display import DisplayContent

class RollerCoasterAnimation(DisplayContent):
    def __init__(self):
        super().__init__(duration=10)
        self.frame = 0
        
    async def render(self, display):
        # Your existing roller coaster rendering code
        # Use display.set_pixel(x, y, color)
        pass
```

##### Splash Screens

```python
class RevealSplash(DisplayContent):
    def __init__(self):
        super().__init__(duration=8)
        self.progress = 0
        
    async def render(self, display):
        # Your reveal animation logic
        pass
```

#### 5. Migrate Web Server

The web server architecture changes to support SLDK's three-process model:

```python
from sldk.web import WebHandler

class ThemeParkWebHandler(WebHandler):
    async def handle_settings_update(self, request):
        # Update settings
        # Signal main app to refresh
        pass
```

### Memory Optimization

SLDK automatically handles memory constraints:

1. **Display Process**: Always runs (minimal memory)
2. **Data Update Process**: Runs if >30KB free
3. **Web Server Process**: Runs if >50KB free

### Testing Migration

1. **Desktop Testing**:
```bash
cd /path/to/theme-park-api
python src/main.py
```

2. **CircuitPython Testing**:
```bash
make copy_to_circuitpy
```

### Common Issues

#### Import Errors
- Ensure SLDK is in the Python path
- For CircuitPython, copy to `/lib/sldk/`

#### Memory Issues  
- SLDK will automatically disable features if memory is low
- Check serial output for memory reports

#### Display Differences
- SLDK uses baseline text positioning
- Adjust Y coordinates if needed

### Benefits After Migration

1. **Cleaner Code**: Application logic separated from display logic
2. **Reusability**: Display components can be used in other projects  
3. **Better Testing**: Can develop on desktop with simulator
4. **Memory Safety**: Automatic feature degradation on low memory
5. **Async Throughout**: Better performance on ESP32

### Next Steps

1. Complete data update process migration
2. Migrate web server endpoints
3. Add OTA update support
4. Create custom animations
5. Package for distribution