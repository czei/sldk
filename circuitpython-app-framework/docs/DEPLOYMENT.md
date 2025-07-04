# Deployment Guide

Learn how to deploy your CircuitPython App Framework applications to hardware.

## Prerequisites

### Hardware Requirements
- CircuitPython-compatible board (e.g., MatrixPortal S3)
- RGB LED Matrix (typically 64x32)
- 5V power supply (2-4A depending on matrix size)
- USB cable for programming
- (Optional) WiFi network for internet features

### Software Requirements
- CircuitPython 8.x or 9.x
- Required libraries from Adafruit Bundle
- Text editor or IDE
- (Optional) `circup` for library management

## Installation Steps

### Step 1: Install CircuitPython

1. **Download CircuitPython**
   ```bash
   # Visit https://circuitpython.org/downloads
   # Find your board (e.g., "MatrixPortal S3")
   # Download the .UF2 file
   ```

2. **Enter Bootloader Mode**
   - Connect board via USB
   - Double-press the reset button
   - A drive named `BOOT` should appear

3. **Install CircuitPython**
   - Drag the .UF2 file to the `BOOT` drive
   - Board will restart automatically
   - A drive named `CIRCUITPY` should appear

### Step 2: Install Required Libraries

#### Method 1: Using circup (Recommended)

```bash
# Install circup
pip install circup

# Install required libraries
circup install adafruit_matrixportal
circup install adafruit_display_text
circup install adafruit_requests
circup install adafruit_minimqtt  # If using MQTT
```

#### Method 2: Manual Installation

1. Download the [Adafruit CircuitPython Bundle](https://circuitpython.org/libraries)
2. Extract the bundle
3. Copy these folders to `CIRCUITPY/lib/`:
   - `adafruit_matrixportal/`
   - `adafruit_display_text/`
   - `adafruit_requests.mpy`
   - `adafruit_bitmap_font/` (if using custom fonts)

### Step 3: Install the Framework

1. **Clone or download the framework**
   ```bash
   git clone https://github.com/yourusername/circuitpython-app-framework.git
   cd circuitpython-app-framework
   ```

2. **Copy to CircuitPython**
   ```bash
   # Using make (if available)
   make copy_to_circuitpy
   
   # Or manually copy
   cp -r src/cpyapp /Volumes/CIRCUITPY/
   # Windows: copy src\cpyapp X:\cpyapp
   ```

### Step 4: Configure WiFi (Optional)

Create `secrets.py` on the CIRCUITPY drive:

```python
# CIRCUITPY/secrets.py
secrets = {
    "ssid": "Your_WiFi_Network_Name",
    "password": "Your_WiFi_Password",
    
    # Optional: API keys
    "weather_api_key": "your_openweather_key",
    "news_api_key": "your_newsapi_key",
    "stock_api_key": "your_alphavantage_key"
}
```

### Step 5: Create Your Application

Create `code.py` on the CIRCUITPY drive:

```python
# CIRCUITPY/code.py
from cpyapp import SimpleScrollApp

# Your application
app = SimpleScrollApp("Hello CircuitPython!")
app.run()
```

## Project Structure

```
CIRCUITPY/
├── code.py              # Your main application
├── secrets.py           # WiFi and API credentials
├── cpyapp/              # Framework files
│   ├── __init__.py
│   ├── simple.py
│   ├── core/
│   ├── data/
│   ├── display/
│   ├── network/
│   ├── presets/
│   └── utils/
├── lib/                 # CircuitPython libraries
│   ├── adafruit_matrixportal/
│   ├── adafruit_display_text/
│   └── adafruit_requests.mpy
└── data/                # Optional: local data files
    ├── config.json
    └── messages.txt
```

## Deployment Methods

### Method 1: Direct USB Copy

The simplest method - just copy files:

```bash
# macOS/Linux
cp code.py /Volumes/CIRCUITPY/
cp -r my_app/ /Volumes/CIRCUITPY/

# Windows
copy code.py D:\
copy my_app\* D:\
```

### Method 2: Using Make

If you have the framework's Makefile:

```bash
# Deploy everything
make copy_to_circuitpy

# Deploy without linting
make copy_to_circuitpy-no-lint

# Just lint check
make lint-errors
```

### Method 3: Deployment Script

Create a deployment script:

```python
#!/usr/bin/env python3
# deploy.py
import os
import shutil
import subprocess

def find_circuitpy():
    """Find CIRCUITPY drive."""
    if os.path.exists("/Volumes/CIRCUITPY"):
        return "/Volumes/CIRCUITPY"
    elif os.path.exists("D:\\"):
        return "D:\\"
    # Add more paths as needed
    return None

def deploy():
    circuitpy = find_circuitpy()
    if not circuitpy:
        print("CIRCUITPY drive not found!")
        return
    
    print(f"Deploying to {circuitpy}")
    
    # Copy files
    files = [
        "code.py",
        "secrets.py",
        # Add more files
    ]
    
    for file in files:
        if os.path.exists(file):
            print(f"Copying {file}")
            shutil.copy(file, circuitpy)
    
    # Copy directories
    dirs = [
        "cpyapp",
        "data"
    ]
    
    for dir in dirs:
        if os.path.exists(dir):
            print(f"Copying {dir}/")
            dest = os.path.join(circuitpy, dir)
            if os.path.exists(dest):
                shutil.rmtree(dest)
            shutil.copytree(dir, dest)
    
    print("Deployment complete!")

if __name__ == "__main__":
    deploy()
```

### Method 4: Over-the-Air Updates

For boards with WiFi, implement OTA updates:

```python
# ota_update.py
from cpyapp.utils import OTAUpdater

updater = OTAUpdater(
    github_repo="username/repo",
    current_version="1.0.0"
)

# Check for updates
if updater.check_for_update():
    print("Update available!")
    updater.download_and_install()
    # Board will restart automatically
```

## Configuration Management

### Application Settings

Create `config.json` for app configuration:

```json
{
    "display": {
        "brightness": 0.3,
        "scroll_speed": 0.04,
        "font_size": 12
    },
    "network": {
        "timeout": 10,
        "retry_count": 3
    },
    "app": {
        "update_interval": 300,
        "city": "New York",
        "units": "imperial"
    }
}
```

Load in your app:

```python
from cpyapp.utils import ConfigManager

config = ConfigManager("config.json")
brightness = config.get("display.brightness", 0.3)
```

### Environment-Specific Settings

```python
# settings.py
import board

# Detect environment
if hasattr(board, 'DISPLAY'):
    # Has built-in display
    ENVIRONMENT = "production"
else:
    # External display
    ENVIRONMENT = "development"

# Environment-specific settings
if ENVIRONMENT == "production":
    DEBUG = False
    LOG_LEVEL = "ERROR"
    UPDATE_INTERVAL = 300
else:
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    UPDATE_INTERVAL = 60
```

## Memory Management

CircuitPython has limited memory. Here's how to optimize:

### Check Memory Usage

```python
import gc

# Check free memory
gc.collect()
print(f"Free memory: {gc.mem_free()} bytes")

# Add to your app for monitoring
class MemoryMonitor:
    def __init__(self, threshold=10000):
        self.threshold = threshold
    
    def check(self):
        gc.collect()
        free = gc.mem_free()
        if free < self.threshold:
            print(f"Low memory warning: {free} bytes")
            # Take action: clear caches, etc.
```

### Memory Optimization Tips

1. **Use .mpy files**
   ```bash
   # Install mpy-cross
   pip install mpy-cross
   
   # Compile Python files
   mpy-cross -o utils.mpy utils.py
   ```

2. **Minimize imports**
   ```python
   # Bad: Import everything
   from cpyapp import *
   
   # Good: Import only what you need
   from cpyapp import SimpleScrollApp
   ```

3. **Clear unused objects**
   ```python
   # Clear large objects when done
   data = fetch_large_dataset()
   process_data(data)
   del data  # Free memory
   gc.collect()
   ```

## Debugging Deployment

### Serial Console

Connect to the serial console for debugging:

```bash
# macOS/Linux
screen /dev/tty.usbmodem* 115200

# Or using Mu editor's serial console
# Or using Thonny's serial console
```

### Common Issues and Solutions

#### "No module named 'cpyapp'"
- Ensure framework is copied to CIRCUITPY/cpyapp/
- Check that __init__.py exists in cpyapp/

#### "MemoryError"
- Reduce import statements
- Use .mpy compiled files
- Simplify your application
- Check for memory leaks

#### "OSError: [Errno 28] No space left on device"
- Delete unnecessary files from CIRCUITPY
- Use smaller libraries (.mpy versions)
- Remove unused fonts or images

#### WiFi Connection Issues
- Verify credentials in secrets.py
- Check 2.4GHz network (5GHz not supported)
- Ensure strong signal strength
- Add connection retry logic

### Debug Mode

Add debug mode to your app:

```python
# code.py
import os

# Enable debug mode via file presence
DEBUG = os.path.exists("/debug.txt")

if DEBUG:
    import sys
    sys.path.append("/debug")
    from debug_tools import Inspector
    inspector = Inspector()

# Your app with debug hooks
app = SimpleScrollApp("Hello")

if DEBUG:
    inspector.watch(app)
    
app.run()
```

## Production Best Practices

### 1. Error Recovery

```python
# main.py
import supervisor

def safe_main():
    try:
        from cpyapp import SimpleScrollApp
        app = SimpleScrollApp("Production App")
        app.run()
    except Exception as e:
        # Show error on display
        import displayio
        import terminalio
        from adafruit_display_text import label
        
        display = displayio.Display()
        text = label.Label(
            terminalio.FONT,
            text=f"Error: {e}",
            color=0xFF0000
        )
        display.show(text)
        
        # Restart in 10 seconds
        import time
        time.sleep(10)
        supervisor.reload()

# Run with recovery
while True:
    safe_main()
```

### 2. Watchdog Timer

```python
import watchdog
import microcontroller

# Enable watchdog
w = microcontroller.watchdog
w.timeout = 30  # 30 seconds
w.mode = watchdog.WatchDogMode.RESET
w.feed()

# In your main loop
while True:
    # Your app logic
    do_work()
    
    # Feed watchdog
    w.feed()
    
    # If app hangs, watchdog resets board
```

### 3. Logging

```python
# logger.py
import time

class Logger:
    def __init__(self, filename="/log.txt", max_size=10000):
        self.filename = filename
        self.max_size = max_size
    
    def log(self, message, level="INFO"):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        try:
            # Check file size
            import os
            if os.stat(self.filename)[6] > self.max_size:
                # Rotate log
                self._rotate_log()
            
            # Append to log
            with open(self.filename, "a") as f:
                f.write(log_entry)
        except:
            pass  # Fail silently
    
    def _rotate_log(self):
        try:
            os.rename(self.filename, "/log.old.txt")
        except:
            os.remove(self.filename)

# Use in your app
logger = Logger()
logger.log("App started")
```

### 4. Configuration Validation

```python
def validate_config(config):
    """Validate configuration before using."""
    required = ["wifi.ssid", "wifi.password", "api.key"]
    
    for key in required:
        if not config.get(key):
            raise ValueError(f"Missing required config: {key}")
    
    # Validate types
    if not isinstance(config.get("display.brightness"), (int, float)):
        config.set("display.brightness", 0.3)
    
    # Validate ranges
    brightness = config.get("display.brightness")
    if not 0 <= brightness <= 1:
        config.set("display.brightness", 0.3)
    
    return config
```

## Deployment Checklist

### Pre-Deployment

- [ ] CircuitPython installed and working
- [ ] Required libraries installed
- [ ] Framework files copied to CIRCUITPY
- [ ] WiFi credentials in secrets.py
- [ ] API keys configured (if needed)
- [ ] Code tested on target hardware
- [ ] Memory usage checked
- [ ] Error handling implemented

### Deployment

- [ ] Backup existing code
- [ ] Copy new files to CIRCUITPY
- [ ] Verify file structure
- [ ] Test basic functionality
- [ ] Check serial output for errors
- [ ] Verify network connectivity
- [ ] Test all features

### Post-Deployment

- [ ] Monitor for crashes/resets
- [ ] Check memory usage over time
- [ ] Verify data updates working
- [ ] Test error recovery
- [ ] Document any issues
- [ ] Create backup of working config

## Next Steps

- Explore [example applications](../examples/)
- Read about [board configuration](BOARDS.md)
- Learn [troubleshooting techniques](TROUBLESHOOTING.md)
- Join the [CircuitPython community](https://circuitpython.org/community)