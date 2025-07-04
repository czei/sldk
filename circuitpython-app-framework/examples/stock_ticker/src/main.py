"""
Stock Ticker Display Application
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
from cpyapp.config.settings import SettingsManager
from cpyapp.utils.error_handler import ErrorHandler

from .api.stocks import StockAPI
from .plugins.ticker_display import StockTickerPlugin

# Initialize logger
logger = ErrorHandler("error_log")


class StockTickerApplication(BaseApplication):
    """Stock ticker display application."""
    
    def __init__(self, display, http_client, settings_manager):
        """Initialize stock ticker application."""
        super().__init__(display, http_client, settings_manager)
        
        # Stock specific components
        self.stock_api = StockAPI(http_client, settings_manager)
        self.ticker_plugin = StockTickerPlugin()
        
        # Register plugin
        self.register_plugin(self.ticker_plugin)
        
    async def initialize_app(self):
        """Initialize stock ticker specific components."""
        logger.info("Initializing stock ticker application")
        await self.stock_api.initialize()
        
    async def update_data(self):
        """Fetch updated stock data."""
        logger.info("Updating stock data")
        return await self.stock_api.get_stock_prices()
        
    def create_display_content(self, data):
        """Create display messages from stock data."""
        # The plugin handles message creation
        return []


def main():
    """Main entry point."""
    logger.info("Starting Stock Ticker Display")
    
    try:
        # Create settings manager with stock-specific defaults
        settings_manager = SettingsManager("settings.json")
        
        # Set stock-specific defaults
        if not settings_manager.get("symbols"):
            settings_manager.set("symbols", ["AAPL", "GOOGL", "MSFT"])
        if not settings_manager.get("show_percentage"):
            settings_manager.set("show_percentage", True)
        
        # Create display
        display = create_display({'settings_manager': settings_manager})
        
        # Create HTTP client
        http_client = HttpClient()
        
        # Create application
        app = StockTickerApplication(display, http_client, settings_manager)
        
        # Run the application
        asyncio.run(app.run())
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(e, "Fatal error in stock ticker application")
        raise


if __name__ == "__main__":
    main()