"""Level 7: Advanced Features - Plugins, Error Handling, and Complex Logic

This example demonstrates advanced framework features for
building robust, production-ready applications.

What you'll learn:
- Plugin system for extending functionality
- Comprehensive error handling
- State management
- Background tasks
- Performance optimization
"""

from cpyapp import SimpleScrollApp, BaseApplication
from cpyapp.plugins import Plugin, PluginManager
from cpyapp.utils import ErrorHandler, StateManager, TaskScheduler
import asyncio
import time
import gc

# Example 1: Creating a Custom Plugin
class WeatherAlertPlugin(Plugin):
    """Plugin that monitors weather and shows alerts."""
    
    def __init__(self, threshold_temp=90):
        super().__init__("weather_alert")
        self.threshold = threshold_temp
        self.last_alert = 0
        
    async def initialize(self, app):
        """Called when plugin is loaded."""
        self.app = app
        self.data_source = app.get_data_source("weather")
        
    async def update(self):
        """Called periodically by the framework."""
        if not self.data_source:
            return
            
        temp = self.data_source.get("temperature", 0)
        
        # Check for high temperature
        if temp > self.threshold:
            current_time = time.monotonic()
            # Alert every 5 minutes max
            if current_time - self.last_alert > 300:
                await self.show_alert(f"HIGH TEMP: {temp}°F!")
                self.last_alert = current_time
    
    async def show_alert(self, message):
        """Override display with alert."""
        # Save current display state
        saved_state = self.app.get_display_state()
        
        # Show alert with flashing effect
        for _ in range(3):
            self.app.set_text(message)
            self.app.set_style("text_color", (255, 0, 0))  # Red
            await asyncio.sleep(0.5)
            self.app.clear_display()
            await asyncio.sleep(0.5)
        
        # Restore previous state
        self.app.restore_display_state(saved_state)

# Example 2: Advanced Error Handling
class RobustWeatherApp(BaseApplication):
    """Weather app with comprehensive error handling."""
    
    def __init__(self):
        super().__init__()
        self.error_handler = ErrorHandler(
            log_to_file=True,
            max_retries=3,
            backoff_factor=2.0
        )
        self.weather_data = None
        
    async def fetch_weather(self):
        """Fetch weather with error handling."""
        try:
            # Attempt to fetch data
            response = await self.error_handler.retry_async(
                self.http_client.get,
                "https://api.weather.com/data",
                timeout=10
            )
            
            if response.status_code == 200:
                self.weather_data = response.json()
            else:
                raise Exception(f"API error: {response.status_code}")
                
        except asyncio.TimeoutError:
            self.error_handler.log("Weather fetch timeout", level="warning")
            self.show_fallback("Weather timeout")
            
        except Exception as e:
            self.error_handler.log(f"Weather error: {e}", level="error")
            self.show_fallback("Weather unavailable")
            
    def show_fallback(self, message):
        """Show fallback message when data unavailable."""
        self.display_text = message
        self.display_color = (128, 128, 128)  # Gray

# Example 3: State Management
class StatefulApp(BaseApplication):
    """App with persistent state management."""
    
    def __init__(self):
        super().__init__()
        self.state = StateManager(
            "app_state.json",
            auto_save=True,
            save_interval=60  # Save every minute
        )
        
        # Load or initialize state
        self.view_count = self.state.get("view_count", 0)
        self.last_viewed = self.state.get("last_viewed", None)
        self.user_prefs = self.state.get("user_prefs", {})
        
    def increment_view_count(self):
        """Track how many times app has been viewed."""
        self.view_count += 1
        self.state.set("view_count", self.view_count)
        self.state.set("last_viewed", time.time())
        
    def get_display_text(self):
        """Show state information."""
        return f"Views: {self.view_count} | Last: {self.last_viewed}"

# Example 4: Background Tasks with Task Scheduler
class MultiTaskApp(BaseApplication):
    """App that manages multiple background tasks."""
    
    def __init__(self):
        super().__init__()
        self.scheduler = TaskScheduler()
        
        # Schedule different tasks
        self.scheduler.schedule(
            self.update_weather,
            interval=300,  # Every 5 minutes
            name="weather_update"
        )
        
        self.scheduler.schedule(
            self.check_alerts,
            interval=60,  # Every minute
            name="alert_check"
        )
        
        self.scheduler.schedule(
            self.cleanup_memory,
            interval=600,  # Every 10 minutes
            name="memory_cleanup"
        )
        
    async def update_weather(self):
        """Background task to update weather."""
        # Fetch weather data
        pass
        
    async def check_alerts(self):
        """Check for any system alerts."""
        # Check conditions and raise alerts
        pass
        
    async def cleanup_memory(self):
        """Periodic memory cleanup."""
        gc.collect()
        free_memory = gc.mem_free()
        if free_memory < 10000:  # Less than 10KB free
            self.show_warning("Low memory!")

# Example 5: Performance Optimization
class OptimizedApp(BaseApplication):
    """App with performance optimizations."""
    
    def __init__(self):
        super().__init__()
        
        # Enable performance features
        self.enable_caching = True
        self.cache_duration = 300  # 5 minutes
        self.batch_updates = True
        self.update_batch_size = 5
        
        # Preallocate buffers
        self.display_buffer = bytearray(64 * 32 * 3)  # RGB buffer
        self.text_buffer = bytearray(256)  # Text buffer
        
    def optimize_display_update(self, text):
        """Optimized display update."""
        # Only update if text changed
        if text == self.last_text:
            return
            
        # Use preallocated buffers
        text_bytes = text.encode('utf-8')
        if len(text_bytes) <= len(self.text_buffer):
            self.text_buffer[:len(text_bytes)] = text_bytes
            # Process using buffer instead of creating new strings
            
        self.last_text = text

# Example 6: Plugin-Based Architecture
class PluginBasedApp(BaseApplication):
    """Extensible app using plugins."""
    
    def __init__(self):
        super().__init__()
        self.plugin_manager = PluginManager()
        
        # Load built-in plugins
        self.plugin_manager.load_plugin(WeatherAlertPlugin(85))
        self.plugin_manager.load_plugin(MemoryMonitorPlugin())
        self.plugin_manager.load_plugin(NetworkStatusPlugin())
        
        # Load user plugins from directory
        self.plugin_manager.load_from_directory("/plugins")
        
    async def run(self):
        """Main run loop with plugin support."""
        # Initialize all plugins
        await self.plugin_manager.initialize_all(self)
        
        while True:
            # Update all plugins
            await self.plugin_manager.update_all()
            
            # Normal app update
            await self.update_display()
            
            await asyncio.sleep(0.1)

# Example 7: Complete Advanced Application
class AdvancedDashboard(BaseApplication):
    """Full-featured dashboard with all advanced features."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize all components
        self.error_handler = ErrorHandler()
        self.state_manager = StateManager("dashboard.json")
        self.task_scheduler = TaskScheduler()
        self.plugin_manager = PluginManager()
        
        # Configuration
        self.config = {
            "update_interval": 1,
            "scroll_speed": 0.04,
            "brightness": 0.3,
            "rotation_interval": 10
        }
        
        # Data sources
        self.data_sources = {
            "time": lambda: time.strftime("%H:%M:%S"),
            "memory": lambda: f"Free: {gc.mem_free()//1024}KB",
            "uptime": lambda: f"Up: {int(time.monotonic())}s"
        }
        
        # Current display mode
        self.mode_index = 0
        self.modes = list(self.data_sources.keys())
        
    async def run(self):
        """Main application loop."""
        try:
            # Initialize everything
            await self.initialize()
            
            # Main loop
            while True:
                # Rotate through modes
                mode = self.modes[self.mode_index]
                text = self.data_sources[mode]()
                
                # Update display
                self.display.show_text(text)
                
                # Check for mode rotation
                if time.monotonic() % self.config["rotation_interval"] < 0.1:
                    self.mode_index = (self.mode_index + 1) % len(self.modes)
                
                # Let other tasks run
                await asyncio.sleep(0.1)
                
        except Exception as e:
            self.error_handler.handle_fatal(e)
            # Show error on display
            self.display.show_text("ERROR!", color=(255, 0, 0))

# Create and run the advanced app
if __name__ == "__main__":
    app = AdvancedDashboard()
    # Or use the simple wrapper with plugins
    simple_app = SimpleScrollApp(
        "Advanced Features Demo",
        plugins=[
            WeatherAlertPlugin(threshold_temp=85),
            MemoryMonitorPlugin(threshold_percent=80)
        ]
    )
    simple_app.run()