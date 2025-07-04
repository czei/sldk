# SimpleScrollApp - Easy LED Matrix Applications

The SimpleScrollApp class provides a beginner-friendly way to create scrolling text applications on LED matrices while maintaining all the power of the full CircuitPython App Framework.

## Quick Start

### Minimal Example
```python
from cpyapp.apps import SimpleScrollApp

app = SimpleScrollApp("Hello World!")
app.run()
```

That's it! This creates a scrolling "Hello World!" message with default white text.

### With Style
```python
# Built-in styles: default, rainbow, fast, slow, alert, success, info
app = SimpleScrollApp("Breaking News!", style="alert")
app.run()
```

### Custom Style
```python
custom_style = {
    'scroll_speed': 0.02,      # Faster scrolling
    'text_color': (255, 128, 0),  # Orange
    'background_color': (0, 0, 64),  # Dark blue
}
app = SimpleScrollApp("Custom styled text", style=custom_style)
app.run()
```

## Data Sources

### Static Text
```python
app = SimpleScrollApp("Static message")
```

### Function
```python
import time

def get_time():
    return f"Time: {time.strftime('%H:%M:%S')}"

app = SimpleScrollApp(get_time)
app.settings_manager.set('update_interval', 1)  # Update every second
app.run()
```

### URL with JSON
```python
app = SimpleScrollApp("https://api.example.com/message.json")
app.run()
```

### Advanced URL Configuration
```python
app = SimpleScrollApp({
    'url': 'https://api.example.com/data.json',
    'parser': 'json_path',
    'json_path': 'data.message'
})
app.run()
```

## Built-in Parsers

### Theme Park Wait Times
```python
app = SimpleScrollApp({
    'url': 'https://queue-times.com/parks/16/queue_times.json',
    'parser': 'theme_park_waits'
})
app.run()
```

### Stock Ticker
```python
app = SimpleScrollApp({
    'url': 'https://api.example.com/stocks.json',
    'parser': 'stock_ticker'
})
app.run()
```

### Weather
```python
app = SimpleScrollApp({
    'url': 'https://api.openweathermap.org/data/2.5/weather?q=Orlando&appid=KEY',
    'parser': 'weather'
})
app.run()
```

## Convenience Functions

For even simpler usage:

```python
from cpyapp.apps import scroll_text, scroll_url, scroll_function

# Simple text
scroll_text("Hello World!")

# From URL
scroll_url("https://api.example.com/message", parser="json_path", json_path="text")

# From function
def counter():
    counter.n = getattr(counter, 'n', 0) + 1
    return f"Count: {counter.n}"

scroll_function(counter, update_interval=2)
```

## Progressive API Design

The SimpleScrollApp grows with your needs:

1. **Beginner**: Just pass text
   ```python
   SimpleScrollApp("Hello!")
   ```

2. **Learning**: Discover styles
   ```python
   SimpleScrollApp("Alert!", style="alert")
   ```

3. **Intermediate**: Use functions and URLs
   ```python
   SimpleScrollApp(my_function, style="custom")
   ```

4. **Advanced**: Full configuration
   ```python
   SimpleScrollApp(
       data_source={'url': '...', 'parser': '...'},
       style={'text_color': (255, 0, 0)},
       board={'type': 'matrixportal_s3'}
   )
   ```

## Board Configuration

By default, the board is auto-detected. You can specify:

```python
# Auto-detect (default)
app = SimpleScrollApp("Text", board="auto")

# Specific board
app = SimpleScrollApp("Text", board="matrixportal_s3")

# Custom configuration
app = SimpleScrollApp("Text", board={
    'type': 'matrixportal_s3',
    'width': 64,
    'height': 32
})
```

## Under the Hood

SimpleScrollApp uses the full CircuitPython App Framework internally:
- BaseApplication for the core loop
- Display factory for hardware/simulator support
- HTTP client for fetching URLs
- Settings manager for configuration
- Plugin system for data parsing

This means you get all the power of the framework (OTA updates, WiFi management, error handling) with a simple interface!