# Theme Park Wait Times Display - Legacy/Advanced Version

⚠️ **Note**: This is the legacy implementation showing the full BaseApplication approach. For most users, we recommend using the [simplified version](../theme_park_simple/) which achieves the same functionality in just 3 lines of code!

A real-time theme park wait times display application built with the CircuitPython Application Framework.

## Features

- 🎢 **Real-time Wait Times**: Displays current wait times for theme park rides
- 🏰 **Multiple Parks**: Support for Disney, Universal, SeaWorld and more
- 🎯 **Customizable Filtering**: Skip closed rides or meet & greet attractions
- 📊 **Multiple Sort Options**: Alphabetical, longest wait, or shortest wait
- 🎨 **Color Coding**: Different colors for ride names, wait times, and closed rides
- 🔄 **Auto Updates**: Refreshes data every 5 minutes
- 📱 **Web Interface**: Configure parks and settings via built-in web server

## Hardware Setup

1. **MatrixPortal S3** with CircuitPython 8.x or 9.x
2. **64x32 RGB LED Matrix** (or compatible size)
3. **WiFi Network** for data updates

## Configuration

### WiFi Setup
Create a `secrets.py` file:
```python
secrets = {
    "ssid": "Your_WiFi_SSID",
    "password": "Your_WiFi_Password"
}
```

### Theme Park Settings
Edit `settings.json` to configure your display:
```json
{
  "park_ids": [6, 5],
  "skip_closed": true,
  "skip_meet": false,
  "sort_mode": "alphabetical",
  "group_by_park": false,
  "brightness_scale": "0.5",
  "scroll_speed": "Medium"
}
```

### Available Parks
- **6**: Disney Magic Kingdom
- **5**: Disney EPCOT  
- **8**: Disney's Hollywood Studios
- **7**: Disney's Animal Kingdom
- **3**: Universal Studios Florida
- **4**: Islands of Adventure
- **14**: SeaWorld Orlando

## Web Interface

Access the web interface by connecting to your device's IP address:
- View current wait times
- Select which parks to display
- Configure display settings
- Set vacation countdown

## Data Source

Wait times are provided by [queue-times.com](https://queue-times.com) API.

## Example Display Output

```
Disney Magic Kingdom wait times...
Space Mountain: 45 min
Haunted Mansion: 30 min
Pirates of the Caribbean: 20 min
It's a Small World: Closed
```

## Development

Run in development mode with the LED simulator:
```bash
python code.py --dev
```

## Installation

1. Copy the framework files to your CIRCUITPY drive
2. Copy this example to the root of your device
3. Configure WiFi credentials and park preferences
4. The display will automatically start showing wait times

## Customization

This example demonstrates how to:
- Extend the BaseApplication class
- Create custom display plugins
- Handle API data parsing
- Implement settings management
- Build complex message queues

## Purpose

This example is preserved to demonstrate:
1. The full power and flexibility of the BaseApplication class
2. How to build complex applications with custom plugins
3. The contrast with the new simplified architecture
4. Advanced patterns for those who need maximum control

## When to Use This Approach

Use the legacy/advanced approach when you need:
- Complete control over the application lifecycle
- Custom data processing pipelines
- Complex plugin interactions
- Integration with legacy systems
- Educational understanding of the framework internals

## Comparison with Simplified Version

| Feature | Legacy (This) | Simplified |
|---------|--------------|------------|
| Lines of code | 85+ | 3 |
| Complexity | High | Low |
| Learning curve | Steep | Gentle |
| Customization | Maximum | Progressive |
| Use case | Advanced/Educational | Most users |

## Why We Moved to Simplified Architecture

While this approach offers maximum flexibility, we found that:
1. 90% of use cases don't need this complexity
2. The boilerplate code obscures the actual functionality
3. Beginners were overwhelmed by the setup
4. Maintenance was more difficult

The new architecture provides the same power through progressive disclosure - start simple and add complexity only when needed.

## See Also

- [Simplified Theme Park Example](../theme_park_simple/) - Recommended for most users
- [Framework Architecture Guide](../../docs/architecture.md)
- [Plugin Development Guide](../../docs/plugins.md)