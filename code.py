"""
ThemeParkAPI - Main entry point
Copyright 2024 3DUPFitters LLC
"""
import sys
sys.path.append('/src/lib')
import asyncio

from src.app import ThemeParkApp
from src.utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")

# Initialize ThemeParkApp and run it
async def main():

    display_impl = None
    try:
        # Import hardware-specific modules conditionally
        try:
            # For CircuitPython hardware
            import board
            import terminalio
            import displayio
            from adafruit_matrixportal.matrix import Matrix
            import adafruit_requests
            import socketpool
            import wifi
            from src.config.settings_manager import SettingsManager
            
            # Initialize display
            from src.ui.display_impl import AsyncScrollingDisplay
            
            # Set up the display
            matrix = Matrix()
            display = matrix.display
            
            # Import networking modules but don't initialize yet
            # We'll do this after WiFi is connected in the app
            import ssl
            import mdns
            
            # Import HTTP client without creating a session yet
            from src.network.http_client import HttpClient
            
            # Create a placeholder client that will be properly initialized after WiFi connects
            http_client = HttpClient()
            
            # Create settings manager once and reuse
            settings_manager = SettingsManager("settings.json")
            
            # Configure mDNS for hostname resolution
            # Use domain_name from settings (with fallback to "themeparkwaits" if not set)
            hostname = settings_manager.settings.get("domain_name", "themeparkwaits")
            
            mdns_server = mdns.Server(wifi.radio)
            mdns_server.hostname = hostname
            mdns_server.advertise_service(service_type="_http", protocol="_tcp", port=80)
            logger.info(f"Advertising mDNS hostname: {hostname}.local")
            display_impl = AsyncScrollingDisplay(display, settings_manager)
            
        except ImportError as e:
            # For non-hardware testing
            logger.error(e, "Running in simulation mode (no hardware)")
            from src.ui.display_base import Display
            from src.network.http_client import HttpClient
            
            # Create mock display
            display_impl = Display(None)
            http_client = HttpClient()

            logger.debug(f"Display implementation type: {type(display_impl)}")

        # Create app instance

        logger.debug(f"Display implementation type: {type(display_impl)}")
        app = ThemeParkApp(display_impl, http_client)
        
        # Run the app
        await app.run()
        
    except Exception as e:
        logger.error(e, "Error in main application")
        
# Run the main function
try:
    asyncio.run(main())
except (KeyboardInterrupt, Exception) as e:
    logger.error(e, "Application terminated")