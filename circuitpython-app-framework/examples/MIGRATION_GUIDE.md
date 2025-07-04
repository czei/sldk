# Migration Guide: Legacy to Simplified Architecture

This guide helps you migrate from the legacy BaseApplication approach to the new simplified architecture.

## Quick Migration

### Legacy (85+ lines)
```python
# Complex setup with multiple imports and classes
from cpyapp.core.application import BaseApplication
# ... 10+ imports ...

class ThemeParkApplication(BaseApplication):
    def __init__(self, display, http_client, settings_manager):
        # ... initialization code ...
    
    async def initialize_app(self):
        # ... setup code ...
        
    async def update_data(self):
        # ... data fetching ...
        
    def create_display_content(self, data):
        # ... display logic ...

# ... main() function with complex setup ...
```

### Simplified (3 lines)
```python
from cpyapp.apps.simple import SimpleScrollApp

app = SimpleScrollApp.from_preset('magic_kingdom')
app.run()
```

## Migration Steps

### Step 1: Identify Your Use Case

Most applications fall into these categories:

#### A. Standard Display with Preset
If you're displaying:
- Theme park wait times
- Stock prices
- Weather information
- News feeds
- Time/clocks

**Migration**: Use the appropriate preset
```python
app = SimpleScrollApp.from_preset('preset_name')
app.run()
```

#### B. Custom URL/API Display
If you're fetching from a custom API:

**Legacy**:
```python
class MyApp(BaseApplication):
    async def update_data(self):
        data = await self.http_client.fetch_json(url)
        return self.process_data(data)
```

**Simplified**:
```python
app = SimpleScrollApp(
    data_source={
        'type': 'url',
        'url': 'https://api.example.com/data',
        'parser': 'json_path',
        'path': 'data.value'
    }
)
app.run()
```

#### C. Complex Custom Logic
If you have complex processing:

**Use Progressive Enhancement**:
```python
# Start simple
app = SimpleScrollApp(data_source=my_source)

# Add custom plugin for complex logic
class MyPlugin(DisplayPlugin):
    async def get_messages(self, app):
        # Your custom logic here
        return messages

app.register_plugin(MyPlugin())
app.run()
```

### Step 2: Map Your Components

| Legacy Component | Simplified Equivalent |
|-----------------|----------------------|
| Custom Application Class | Not needed - use SimpleScrollApp |
| API Client Class | Use data_source configuration |
| Display Plugin | Use built-in or create minimal plugin |
| Settings Manager | Handled automatically |
| Error Handler | Built-in with better defaults |
| WiFi Manager | Automatic with board detection |

### Step 3: Migrate Settings

**Legacy** (settings.json):
```json
{
    "park_ids": [6, 5],
    "update_interval": 300,
    "brightness": 0.5,
    "scroll_speed": "medium"
}
```

**Simplified** (in code):
```python
app = SimpleScrollApp.from_preset(
    'disney_world',
    update_interval=300,
    brightness=0.5
)
```

Or use settings.json with the same format - it's automatically loaded!

### Step 4: Migrate Data Processing

**Legacy**:
```python
async def update_data(self):
    raw_data = await self.api_client.fetch()
    processed = self.process_rides(raw_data)
    return self.format_for_display(processed)
```

**Simplified**:
```python
# Built into data source
data_source = {
    'type': 'theme_park',
    'park_ids': [6, 5],
    'min_wait': 30  # Filtering built-in
}
```

### Step 5: Migrate Display Logic

**Legacy**:
```python
def create_display_content(self, data):
    messages = []
    for ride in data['rides']:
        messages.append({
            'text': f"{ride['name']}: {ride['wait']}min",
            'color': self.get_color(ride['wait'])
        })
    return messages
```

**Simplified**:
```python
# Handled automatically by data source
# Or customize with style configuration:
style = {
    'colors': {
        'low_wait': 'Green',
        'high_wait': 'Red'
    }
}
```

## Common Migration Patterns

### Pattern 1: Simple API Display

**Before**:
```python
class WeatherApp(BaseApplication):
    def __init__(self, ...):
        self.weather_api = WeatherAPI(api_key)
        # ... setup ...
    
    async def update_data(self):
        return await self.weather_api.get_weather(city)
```

**After**:
```python
app = SimpleScrollApp.from_preset('weather', city='Seattle')
app.run()
```

### Pattern 2: Multiple Data Sources

**Before**:
```python
class MultiApp(BaseApplication):
    async def update_data(self):
        weather = await self.get_weather()
        stocks = await self.get_stocks()
        return self.combine_data(weather, stocks)
```

**After**:
```python
# Use plugins for multiple sources
app = SimpleScrollApp(data_source=weather_source)
app.register_plugin(StockPlugin(symbols=['AAPL']))
app.run()
```

### Pattern 3: Custom Formatting

**Before**:
```python
def create_display_content(self, data):
    # Complex formatting logic
    return custom_messages
```

**After**:
```python
# Option 1: Use data source formatters
data_source = {
    'type': 'url',
    'url': '...',
    'formatter': lambda data: f"Custom: {data['value']}"
}

# Option 2: Use a simple plugin
class FormatPlugin(DisplayPlugin):
    async def get_messages(self, app):
        # Your formatting logic
        return messages
```

## Testing Your Migration

1. **Start Simple**: Get basic functionality working first
2. **Add Features**: Progressively add customization
3. **Compare Output**: Ensure display matches legacy version
4. **Test on Hardware**: Verify on actual CircuitPython device

## Benefits After Migration

- ✅ 90%+ less code to maintain
- ✅ Easier to understand and modify
- ✅ Better error handling built-in
- ✅ Automatic updates and improvements
- ✅ Access to preset ecosystem
- ✅ Progressive enhancement path

## Getting Help

1. Check the [examples](theme_park_simple/) for working code
2. Use `list_presets()` to see available options
3. Start with a preset and customize from there
4. The legacy code still works if needed!

## FAQ

**Q: Will my legacy code still work?**
A: Yes! The BaseApplication class is still available for complex use cases.

**Q: Can I mix old and new approaches?**
A: Yes, you can use SimpleScrollApp with custom plugins that use your legacy logic.

**Q: What about performance?**
A: The simplified version is actually faster due to optimized defaults.

**Q: How do I debug?**
A: The simplified version has better error messages and logging by default.

**Q: Can I contribute my configuration as a preset?**
A: Yes! Presets are designed to be community-contributed.