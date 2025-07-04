# CircuitPython App Framework

> Build LED matrix applications with just 2 lines of code!

The CircuitPython App Framework makes it incredibly easy to create scrolling text displays, data dashboards, and interactive LED applications. Start simple, grow powerful.

## 🚀 Quick Start

```python
from cpyapp import SimpleScrollApp

app = SimpleScrollApp("Hello World!")
app.run()
```

That's it! Your LED matrix is now displaying scrolling text.

## 📦 Installation

### For CircuitPython Devices

1. Copy the `src/cpyapp` folder to your CIRCUITPY drive
2. Install required libraries:
   ```
   adafruit_display_text
   adafruit_matrixportal
   adafruit_requests
   ```

### For Development

```bash
git clone https://github.com/yourusername/circuitpython-app-framework.git
cd circuitpython-app-framework
pip install -r requirements-dev.txt
```

## 🌟 Features

- **Dead Simple**: Start with 2 lines of code
- **Progressive Complexity**: Grow from "Hello World" to full applications
- **Hardware Agnostic**: Works on MatrixPortal, LED Glasses, and custom boards
- **Built-in Presets**: Weather, clock, stocks, news - ready to use
- **Data Sources**: Fetch from URLs, files, or custom functions
- **Style System**: Colors, animations, brightness control
- **Web Interface**: Optional web configuration
- **Error Handling**: Robust error recovery
- **Plugin System**: Extend with your own features

## 📚 Examples

### Dynamic Clock
```python
import time
from cpyapp import SimpleScrollApp

app = SimpleScrollApp(
    text_source=lambda: time.strftime("%H:%M:%S"),
    update_interval=1
)
app.run()
```

### Weather Display
```python
from cpyapp import SimpleScrollApp
from cpyapp.presets import WeatherPreset

weather = WeatherPreset(
    api_key="your_key",
    city="Orlando"
)
app = SimpleScrollApp(preset=weather)
app.run()
```

### Styled Text
```python
from cpyapp import SimpleScrollApp

app = SimpleScrollApp(
    "ALERT!",
    styles={
        "text_color": (255, 0, 0),  # Red
        "scroll_speed": 0.02,  # Fast
        "brightness": 0.5
    }
)
app.run()
```

### URL Data Source
```python
from cpyapp import SimpleScrollApp
from cpyapp.data import URLDataSource

quote = URLDataSource(
    url="https://api.quotable.io/random",
    json_path="content"
)

app = SimpleScrollApp(
    text_source=lambda: quote.get(),
    update_interval=300  # New quote every 5 minutes
)
app.run()
```

## 🏗️ Architecture

The framework uses a simple three-component architecture:

```
┌─────────────┐     ┌──────────┐     ┌─────────┐
│ Data Source │ ──▶ │  Style   │ ──▶ │  Board  │
└─────────────┘     └──────────┘     └─────────┘
      │                   │                │
      ▼                   ▼                ▼
   Content           Appearance        Hardware
```

- **Data Source**: What to display (text, API data, sensor readings)
- **Style**: How it looks (colors, speed, brightness)
- **Board**: Where it displays (MatrixPortal, LED Glasses, etc.)

## 🎯 Progressive Learning Path

1. **Level 1**: Static text - [Hello World](examples/progression/level_1_hello_world.py)
2. **Level 2**: Dynamic functions - [Clock](examples/progression/level_2_dynamic_text.py)
3. **Level 3**: Styled displays - [Colors](examples/progression/level_3_styled_text.py)
4. **Level 4**: Internet data - [APIs](examples/progression/level_4_data_sources.py)
5. **Level 5**: Built-in apps - [Presets](examples/progression/level_5_presets.py)
6. **Level 6**: Custom hardware - [Boards](examples/progression/level_6_custom_boards.py)
7. **Level 7**: Advanced features - [Plugins](examples/progression/level_7_advanced_features.py)
8. **Level 8**: Full control - [BaseApplication](examples/progression/level_8_full_application.py)

## 🛠️ Supported Boards

- Adafruit MatrixPortal S3
- Adafruit MatrixPortal M4
- Adafruit LED Glasses
- Adafruit RGB Matrix FeatherWing
- Custom boards (see [board configuration](docs/BOARDS.md))

## 📖 Documentation

- [Getting Started Guide](docs/GETTING_STARTED.md) - Your first app
- [API Reference](docs/API_REFERENCE.md) - Complete API documentation
- [Architecture Overview](docs/ARCHITECTURE.md) - How it all works
- [Data Sources Guide](docs/DATA_SOURCES.md) - Working with data
- [Style System](docs/STYLES.md) - Colors and animations
- [Board Configuration](docs/BOARDS.md) - Hardware setup
- [Presets Guide](docs/PRESETS.md) - Built-in applications
- [Deployment Guide](docs/DEPLOYMENT.md) - Deploy to hardware

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on [Adafruit CircuitPython](https://circuitpython.org/)
- Inspired by the maker community
- Special thanks to all contributors

## 🚧 Project Status

This framework is actively maintained and used in production. We follow semantic versioning and maintain backwards compatibility.

## 💬 Support

- [GitHub Issues](https://github.com/yourusername/circuitpython-app-framework/issues)
- [Discord Community](https://discord.gg/circuitpython)
- [Adafruit Forums](https://forums.adafruit.com/)

---

Made with ❤️ for the CircuitPython community