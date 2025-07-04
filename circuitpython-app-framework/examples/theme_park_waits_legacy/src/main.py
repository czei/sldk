"""
Theme Park Wait Times Display Application
"""
import asyncio
import sys
import os

# Add the framework to the path
framework_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src')
if framework_path not in sys.path:
    sys.path.insert(0, framework_path)

from cpyapp.core.application import BaseApplication
from cpyapp.display.factory import create_display
from cpyapp.network.http_client import HttpClient
from cpyapp.network.wifi_manager import WiFiManager
from cpyapp.config.settings import SettingsManager
from cpyapp.utils.error_handler import ErrorHandler

from .api.queue_times import QueueTimesAPI
from .plugins.park_display import ThemeParkDisplayPlugin

# Initialize logger
logger = ErrorHandler("error_log")


class ThemeParkApplication(BaseApplication):
    """Theme park wait times display application."""
    
    def __init__(self, display, http_client, settings_manager):
        """Initialize theme park application."""
        super().__init__(display, http_client, settings_manager)
        
        # Theme park specific components
        self.queue_times_api = QueueTimesAPI(http_client, settings_manager)
        self.park_plugin = ThemeParkDisplayPlugin()
        
        # Register plugin
        self.register_plugin(self.park_plugin)
        
    async def initialize_app(self):
        """Initialize theme park specific components."""
        logger.info("Initializing theme park application")
        await self.queue_times_api.initialize()
        
    async def update_data(self):
        """Fetch updated theme park data."""
        logger.info("Updating theme park data")
        return await self.queue_times_api.update_parks()
        
    def create_display_content(self, data):
        """Create display messages from theme park data."""
        # The plugin handles message creation
        return []


def main():
    """Main entry point."""
    logger.info("Starting Theme Park Wait Times Display")
    
    try:
        # Create settings manager
        settings_manager = SettingsManager("settings.json")
        
        # Create display
        display = create_display({'settings_manager': settings_manager})
        
        # Create HTTP client
        http_client = HttpClient()
        
        # Create application
        app = ThemeParkApplication(display, http_client, settings_manager)
        
        # Run the application
        asyncio.run(app.run())
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(e, "Fatal error in theme park application")
        raise


if __name__ == "__main__":
    main()