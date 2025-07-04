"""Level 8: Full Application - Complete BaseApplication Implementation

This example shows how to build a complete, production-ready application
using the BaseApplication class directly for maximum control.

What you'll learn:
- Complete BaseApplication implementation
- Custom display modes and transitions
- Web server integration
- Full state management
- Production error handling
- Modular architecture
"""

import asyncio
import time
import json
import gc
from cpyapp import BaseApplication
from cpyapp.display import DisplayManager, ScrollingText, StaticText
from cpyapp.network import NetworkManager, WebServer
from cpyapp.data import URLDataSource, FileDataSource
from cpyapp.utils import ErrorHandler, StateManager, ConfigManager
from cpyapp.styles import StyleManager, STYLE_PRESETS

class WeatherDashboard(BaseApplication):
    """Complete weather dashboard application."""
    
    def __init__(self):
        """Initialize the weather dashboard."""
        super().__init__()
        
        # Application info
        self.name = "Weather Dashboard"
        self.version = "2.0.0"
        
        # Core components
        self.display = None
        self.network = None
        self.web_server = None
        self.error_handler = ErrorHandler(log_to_file=True)
        self.state = StateManager("weather_state.json")
        self.config = ConfigManager("weather_config.json")
        
        # Display modes
        self.modes = [
            "current_weather",
            "forecast",
            "alerts",
            "statistics"
        ]
        self.current_mode = 0
        self.mode_switch_time = 0
        
        # Data sources
        self.weather_source = None
        self.forecast_source = None
        self.alert_source = None
        
        # Cache
        self.weather_cache = {}
        self.last_update = 0
        
    async def initialize(self):
        """Initialize all components."""
        try:
            # Load configuration
            await self.load_configuration()
            
            # Initialize display
            self.display = DisplayManager(
                width=self.config.get("display_width", 64),
                height=self.config.get("display_height", 32)
            )
            
            # Initialize network if available
            if self.board_has_wifi():
                self.network = NetworkManager()
                await self.network.connect(
                    ssid=self.config.get("wifi_ssid"),
                    password=self.config.get("wifi_password")
                )
                
                # Start web server
                self.web_server = WebServer(self)
                await self.web_server.start(port=80)
            
            # Initialize data sources
            await self.setup_data_sources()
            
            # Restore state
            self.current_mode = self.state.get("last_mode", 0)
            
            # Show startup message
            await self.show_startup_message()
            
        except Exception as e:
            self.error_handler.log(f"Initialization error: {e}")
            raise
    
    async def load_configuration(self):
        """Load application configuration."""
        # Default configuration
        defaults = {
            "api_key": "",
            "location": "Orlando, FL",
            "units": "imperial",
            "update_interval": 300,  # 5 minutes
            "rotation_interval": 10,  # 10 seconds per mode
            "display_width": 64,
            "display_height": 32,
            "brightness": 0.3,
            "scroll_speed": 0.04,
            "wifi_ssid": "",
            "wifi_password": ""
        }
        
        # Load with defaults
        self.config.load_with_defaults(defaults)
    
    async def setup_data_sources(self):
        """Initialize data sources."""
        api_key = self.config.get("api_key")
        location = self.config.get("location")
        units = self.config.get("units")
        
        if api_key:
            # Current weather
            self.weather_source = URLDataSource(
                url=f"https://api.openweathermap.org/data/2.5/weather"
                    f"?q={location}&appid={api_key}&units={units}",
                cache_duration=300
            )
            
            # Forecast
            self.forecast_source = URLDataSource(
                url=f"https://api.openweathermap.org/data/2.5/forecast"
                    f"?q={location}&appid={api_key}&units={units}",
                cache_duration=600
            )
            
            # Weather alerts (if available in your region)
            # self.alert_source = URLDataSource(...)
        else:
            # Use demo data
            self.weather_source = FileDataSource("/demo_weather.json")
    
    async def show_startup_message(self):
        """Display startup message."""
        messages = [
            f"{self.name} v{self.version}",
            "Initializing...",
            f"Location: {self.config.get('location')}"
        ]
        
        for msg in messages:
            self.display.show_text(msg, style=STYLE_PRESETS["info"])
            await asyncio.sleep(1)
    
    async def run(self):
        """Main application loop."""
        await self.initialize()
        
        try:
            while True:
                # Update data if needed
                await self.update_data()
                
                # Get current mode handler
                mode_handler = getattr(self, f"display_{self.modes[self.current_mode]}")
                
                # Display current mode
                await mode_handler()
                
                # Check for mode rotation
                if await self.should_rotate_mode():
                    await self.next_mode()
                
                # Handle web requests
                if self.web_server:
                    await self.web_server.process_requests()
                
                # Small delay to prevent CPU overload
                await asyncio.sleep(0.1)
                
        except KeyboardInterrupt:
            await self.shutdown()
        except Exception as e:
            self.error_handler.log(f"Runtime error: {e}")
            await self.show_error(str(e))
    
    async def update_data(self):
        """Update data from sources if needed."""
        current_time = time.monotonic()
        update_interval = self.config.get("update_interval", 300)
        
        if current_time - self.last_update > update_interval:
            try:
                # Update weather data
                if self.weather_source:
                    weather_data = await self.weather_source.get_async()
                    if weather_data:
                        self.weather_cache["current"] = weather_data
                        self.last_update = current_time
                
                # Update forecast
                if self.forecast_source:
                    forecast_data = await self.forecast_source.get_async()
                    if forecast_data:
                        self.weather_cache["forecast"] = forecast_data
                        
            except Exception as e:
                self.error_handler.log(f"Data update error: {e}")
    
    async def display_current_weather(self):
        """Display current weather conditions."""
        weather = self.weather_cache.get("current", {})
        
        if not weather:
            self.display.show_text("No weather data", style=STYLE_PRESETS["warning"])
            return
        
        # Extract data
        temp = weather.get("main", {}).get("temp", "--")
        feels_like = weather.get("main", {}).get("feels_like", "--")
        description = weather.get("weather", [{}])[0].get("description", "")
        humidity = weather.get("main", {}).get("humidity", "--")
        
        # Format display text
        text = f"{self.config.get('location')}: {temp}° (feels {feels_like}°) {description} {humidity}% humidity"
        
        # Choose color based on temperature
        color = self.get_temp_color(temp)
        
        # Display with scrolling
        style = {
            "text_color": color,
            "brightness": self.config.get("brightness", 0.3),
            "scroll_speed": self.config.get("scroll_speed", 0.04)
        }
        
        self.display.show_scrolling_text(text, style=style)
    
    async def display_forecast(self):
        """Display weather forecast."""
        forecast = self.weather_cache.get("forecast", {})
        
        if not forecast or "list" not in forecast:
            self.display.show_text("No forecast data", style=STYLE_PRESETS["warning"])
            return
        
        # Get next 3 forecasts (usually 3-hour intervals)
        items = forecast["list"][:3]
        forecast_text = "Forecast: "
        
        for item in items:
            dt = item.get("dt_txt", "").split()[1][:5]  # Time HH:MM
            temp = item.get("main", {}).get("temp", "--")
            forecast_text += f"{dt}:{temp}° "
        
        self.display.show_scrolling_text(forecast_text, style=STYLE_PRESETS["info"])
    
    async def display_alerts(self):
        """Display weather alerts."""
        # Check for extreme temperatures
        weather = self.weather_cache.get("current", {})
        temp = weather.get("main", {}).get("temp", 0)
        
        alerts = []
        
        if isinstance(temp, (int, float)):
            if temp > 95:
                alerts.append("EXTREME HEAT WARNING")
            elif temp > 85:
                alerts.append("Heat Advisory")
            elif temp < 32:
                alerts.append("Freeze Warning")
            elif temp < 40:
                alerts.append("Cold Advisory")
        
        if alerts:
            alert_text = " | ".join(alerts)
            self.display.show_scrolling_text(alert_text, style=STYLE_PRESETS["alert"])
        else:
            self.display.show_text("No weather alerts", style=STYLE_PRESETS["success"])
    
    async def display_statistics(self):
        """Display application statistics."""
        stats = [
            f"Uptime: {int(time.monotonic())}s",
            f"Updates: {self.state.get('update_count', 0)}",
            f"Free RAM: {gc.mem_free()//1024}KB",
            f"Mode: {self.modes[self.current_mode]}"
        ]
        
        stats_text = " | ".join(stats)
        self.display.show_scrolling_text(stats_text, style=STYLE_PRESETS["default"])
    
    async def should_rotate_mode(self):
        """Check if it's time to rotate display mode."""
        rotation_interval = self.config.get("rotation_interval", 10)
        current_time = time.monotonic()
        
        if current_time - self.mode_switch_time > rotation_interval:
            return True
        return False
    
    async def next_mode(self):
        """Switch to next display mode."""
        self.current_mode = (self.current_mode + 1) % len(self.modes)
        self.mode_switch_time = time.monotonic()
        self.state.set("last_mode", self.current_mode)
        
        # Log mode change
        self.error_handler.log(f"Switched to mode: {self.modes[self.current_mode]}")
    
    def get_temp_color(self, temp):
        """Get color based on temperature."""
        if not isinstance(temp, (int, float)):
            return (255, 255, 255)  # White for invalid
        
        if temp < 32:
            return (0, 0, 255)  # Blue - freezing
        elif temp < 50:
            return (0, 128, 255)  # Light blue - cold
        elif temp < 70:
            return (0, 255, 0)  # Green - comfortable
        elif temp < 85:
            return (255, 255, 0)  # Yellow - warm
        else:
            return (255, 0, 0)  # Red - hot
    
    async def show_error(self, error_msg):
        """Display error message."""
        self.display.show_text(f"ERROR: {error_msg}", style=STYLE_PRESETS["alert"])
        await asyncio.sleep(3)
    
    async def shutdown(self):
        """Clean shutdown of application."""
        self.error_handler.log("Shutting down...")
        
        # Save state
        self.state.save()
        
        # Stop web server
        if self.web_server:
            await self.web_server.stop()
        
        # Disconnect network
        if self.network:
            await self.network.disconnect()
        
        # Clear display
        self.display.clear()
        self.display.show_text("Goodbye!", style=STYLE_PRESETS["info"])
        await asyncio.sleep(2)
        self.display.clear()
    
    # Web server endpoints
    async def handle_web_request(self, request):
        """Handle incoming web requests."""
        if request.path == "/":
            return self.get_web_interface()
        elif request.path == "/api/status":
            return self.get_status_json()
        elif request.path == "/api/config" and request.method == "POST":
            return await self.update_config(request.json)
        else:
            return {"status": 404, "content": "Not found"}
    
    def get_web_interface(self):
        """Generate web interface HTML."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{self.name}</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: Arial; margin: 20px; }}
                .status {{ background: #f0f0f0; padding: 10px; border-radius: 5px; }}
                .config {{ margin-top: 20px; }}
                input {{ width: 100%; margin: 5px 0; padding: 5px; }}
                button {{ background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>{self.name} v{self.version}</h1>
            <div class="status">
                <h2>Current Status</h2>
                <p>Mode: {self.modes[self.current_mode]}</p>
                <p>Location: {self.config.get('location')}</p>
                <p>Last Update: {time.time() - self.last_update:.0f}s ago</p>
            </div>
            <div class="config">
                <h2>Configuration</h2>
                <form action="/api/config" method="post">
                    <label>Location: <input name="location" value="{self.config.get('location')}"></label>
                    <label>Update Interval (seconds): <input name="update_interval" type="number" value="{self.config.get('update_interval')}"></label>
                    <label>Rotation Interval (seconds): <input name="rotation_interval" type="number" value="{self.config.get('rotation_interval')}"></label>
                    <label>Brightness (0-1): <input name="brightness" type="number" step="0.1" value="{self.config.get('brightness')}"></label>
                    <button type="submit">Update</button>
                </form>
            </div>
        </body>
        </html>
        """
        return {"status": 200, "content": html, "content_type": "text/html"}
    
    def get_status_json(self):
        """Get current status as JSON."""
        status = {
            "name": self.name,
            "version": self.version,
            "mode": self.modes[self.current_mode],
            "uptime": int(time.monotonic()),
            "last_update": int(time.time() - self.last_update),
            "weather": self.weather_cache.get("current", {}),
            "memory_free": gc.mem_free(),
            "config": self.config.get_all()
        }
        return {"status": 200, "content": json.dumps(status), "content_type": "application/json"}
    
    async def update_config(self, new_config):
        """Update configuration from web interface."""
        try:
            # Update config
            for key, value in new_config.items():
                if key in ["location", "update_interval", "rotation_interval", "brightness"]:
                    self.config.set(key, value)
            
            # Save config
            self.config.save()
            
            # Reset update timer to force refresh
            self.last_update = 0
            
            return {"status": 200, "content": json.dumps({"success": True})}
        except Exception as e:
            return {"status": 400, "content": json.dumps({"error": str(e)})}

# Main entry point
if __name__ == "__main__":
    # Create and run the application
    app = WeatherDashboard()
    
    # For CircuitPython, we need to use asyncio properly
    try:
        import supervisor
        # CircuitPython environment
        async def main():
            await app.run()
        
        # Create event loop and run
        loop = asyncio.new_event_loop()
        loop.run_until_complete(main())
    except ImportError:
        # Development environment
        asyncio.run(app.run())