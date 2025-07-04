"""
CircuitPython entry point for Theme Park Wait Times Display.

This file demonstrates both the legacy and simplified approaches.
By default, it uses the new simplified version.
"""
import sys

# Configuration - change this to switch between versions
USE_SIMPLIFIED = True  # Set to False to use legacy version
PARK_PRESET = "magic_kingdom"  # or "disney_world", "universal_orlando", etc.

if USE_SIMPLIFIED:
    # ===== SIMPLIFIED VERSION (Recommended) =====
    # Just 3 lines for a fully functional display!
    
    from cpyapp.apps.simple import SimpleScrollApp
    
    app = SimpleScrollApp.from_preset(PARK_PRESET)
    app.run()
    
else:
    # ===== LEGACY VERSION (For comparison) =====
    # The old way - 85+ lines of code
    
    import asyncio
    import os
    
    # Add the framework to the path
    framework_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src')
    if framework_path not in sys.path:
        sys.path.insert(0, framework_path)
    
    # Add legacy app to path
    legacy_path = os.path.join(os.path.dirname(__file__), '..', 'theme_park_waits_legacy', 'src')
    if legacy_path not in sys.path:
        sys.path.insert(0, legacy_path)
    
    from cpyapp.core.application import BaseApplication
    from cpyapp.display.factory import create_display
    from cpyapp.network.http_client import HttpClient
    from cpyapp.config.settings import SettingsManager
    from cpyapp.utils.error_handler import ErrorHandler
    
    # Legacy imports
    try:
        from api.queue_times import QueueTimesAPI
        from plugins.park_display import ThemeParkDisplayPlugin
    except ImportError:
        print("Legacy modules not found. Please use simplified version.")
        sys.exit(1)
    
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
        logger.info("Starting Theme Park Wait Times Display (Legacy)")
        
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
    
    # Run legacy version
    main()

# Note: To add custom configuration to the simplified version:
# app = SimpleScrollApp.from_preset(
#     PARK_PRESET,
#     min_wait=30,        # Only show 30+ minute waits
#     update_interval=600 # Update every 10 minutes
# )