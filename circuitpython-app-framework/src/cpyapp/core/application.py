"""
Base application class for CircuitPython LED matrix applications.
"""
import asyncio
import gc
import time

from ..utils.error_handler import ErrorHandler
from ..utils.timer import Timer
from ..ui.message_queue import MessageQueue
from ..config.settings import SettingsManager
from ..network.wifi_manager import WiFiManager
from ..ota.updater import OTAUpdater

# Initialize logger
logger = ErrorHandler("error_log")


class BaseApplication:
    """
    Base class for CircuitPython LED matrix applications.
    
    Provides core functionality including:
    - Display management
    - Network connectivity
    - Settings persistence
    - OTA updates
    - Message queue for content rotation
    - Plugin system for extensibility
    """
    
    def __init__(self, display, http_client, settings_manager=None):
        """
        Initialize the application.
        
        Args:
            display: Display implementation (hardware or simulator)
            http_client: HTTP client for network requests
            settings_manager: Optional settings manager (creates default if not provided)
        """
        self.display = display
        self.http_client = http_client
        self.settings_manager = settings_manager or SettingsManager("settings.json")
        self.message_queue = MessageQueue(display, self.get_message_delay())
        self.update_timer = Timer(self.get_update_interval())
        self.wifi_manager = WiFiManager(self.settings_manager)
        self.plugins = []
        self._running = False
        
        # Initialize OTA updater if configured
        ota_repo = self.settings_manager.get("ota_repo", "")
        ota_token = self.settings_manager.get("ota_token", "")
        if ota_repo:
            self.ota_updater = OTAUpdater(
                http_client,
                ota_repo,
                main_dir="src",
                headers={'Authorization': f'token {ota_token}'} if ota_token else {},
                use_prerelease=self.settings_manager.get("use_prerelease", False)
            )
        else:
            self.ota_updater = None
            
        # Set up WiFi callback
        self.wifi_manager.update_http_clients = self.update_http_client
        
    def get_message_delay(self):
        """
        Get the delay between messages in seconds.
        Override to customize.
        
        Returns:
            Delay in seconds (default: 4)
        """
        return self.settings_manager.get("message_delay", 4)
        
    def get_update_interval(self):
        """
        Get the data update interval in seconds.
        Override to customize.
        
        Returns:
            Update interval in seconds (default: 300 = 5 minutes)
        """
        return self.settings_manager.get("update_interval", 300)
        
    def register_plugin(self, plugin):
        """
        Register a display plugin.
        
        Args:
            plugin: Plugin instance to register
        """
        self.plugins.append(plugin)
        logger.info(f"Registered plugin: {plugin.__class__.__name__}")
        
    async def initialize(self):
        """
        Initialize the application.
        Override to add app-specific initialization.
        """
        logger.info("Initializing application")
        
        # Set display colors from settings
        if hasattr(self.display, 'set_colors'):
            self.display.set_colors(self.settings_manager)
            
        # Show splash screen
        await self.display.show_splash(10, True)
        
        # Connect to WiFi
        await self._initialize_network()
        
        # Check for OTA updates
        if self.ota_updater:
            await self._check_ota_updates()
            
        # Application-specific initialization
        await self.initialize_app()
        
    async def initialize_app(self):
        """
        Override this method for application-specific initialization.
        Called after network is connected.
        """
        pass
        
    async def _initialize_network(self):
        """Initialize network connection."""
        logger.info("Initializing network connection")
        
        # WiFi connection with display callback
        async def update_display(message):
            await self.display.show_static_message(message, duration=2)
            
        connected = await self.wifi_manager.connect(update_display)
        
        if connected:
            logger.info("Network connection established")
            # Set system clock if possible
            try:
                from ..utils.system import set_system_clock
                await set_system_clock(self.http_client, self.wifi_manager.socket_pool)
            except Exception as e:
                logger.error(e, "Error setting system clock")
        else:
            logger.error(None, "Failed to establish network connection")
            
    async def _check_ota_updates(self):
        """Check for OTA updates."""
        try:
            logger.info("Checking for OTA updates")
            if self.ota_updater.check_for_update_to_install_during_next_reboot():
                await self.display.show_static_message("Update available! Rebooting...", duration=3)
                await asyncio.sleep(3)
                # Trigger reboot
                import microcontroller
                microcontroller.reset()
        except Exception as e:
            logger.error(e, "Error checking OTA updates")
            
    def update_http_client(self, session):
        """
        Update HTTP client session.
        
        Args:
            session: New HTTP session
        """
        self.http_client.session = session
        
    async def before_update(self):
        """
        Hook called before data update.
        Override to add pre-update logic.
        """
        pass
        
    async def update_data(self):
        """
        Fetch and update application data.
        Override this method to implement data fetching.
        
        Returns:
            Updated data or None if update failed
        """
        raise NotImplementedError("Subclasses must implement update_data()")
        
    async def after_update(self, data):
        """
        Hook called after successful data update.
        Override to add post-update logic.
        
        Args:
            data: The data returned from update_data()
        """
        pass
        
    def create_display_content(self, data):
        """
        Create display content from data.
        Override this method to generate messages for display.
        
        Args:
            data: Data from update_data()
            
        Returns:
            List of display messages or None
        """
        raise NotImplementedError("Subclasses must implement create_display_content()")
        
    async def build_message_queue(self, data):
        """
        Build the message queue from data.
        Can be overridden for custom queue building logic.
        
        Args:
            data: Data to build queue from
        """
        # Clear existing queue
        self.message_queue.init()
        
        # Add splash/branding if configured
        if self.settings_manager.get("show_splash", True):
            await self.message_queue.add_splash(duration=5)
            
        # Get messages from plugins first
        for plugin in self.plugins:
            try:
                messages = plugin.get_messages(data)
                for message in messages:
                    await self._add_message_to_queue(message)
            except Exception as e:
                logger.error(e, f"Error getting messages from plugin {plugin.__class__.__name__}")
                
        # Get messages from app implementation
        messages = self.create_display_content(data)
        if messages:
            for message in messages:
                await self._add_message_to_queue(message)
                
    async def _add_message_to_queue(self, message):
        """
        Add a message to the display queue.
        
        Args:
            message: Message dict with 'type' and other parameters
        """
        msg_type = message.get('type', 'scroll')
        
        if msg_type == 'scroll':
            await self.message_queue.add_scroll_message(
                message.get('text', ''),
                message.get('delay', 2)
            )
        elif msg_type == 'static':
            await self.message_queue.add_static_message(
                message.get('text', ''),
                message.get('duration', 3)
            )
        elif msg_type == 'animation':
            await self.message_queue.add_animation(
                message.get('animation'),
                message.get('duration', 5)
            )
            
    async def run(self):
        """
        Main application loop.
        Handles initialization, updates, and display cycling.
        """
        try:
            # Initialize application
            await self.initialize()
            
            # Initial data fetch
            await self.before_update()
            data = await self.update_data()
            if data:
                await self.after_update(data)
                await self.build_message_queue(data)
                
            self._running = True
            
            # Main loop
            while self._running:
                # Check if update needed
                if self.update_timer.is_expired():
                    logger.info("Update timer expired, fetching new data")
                    
                    await self.before_update()
                    new_data = await self.update_data()
                    
                    if new_data:
                        data = new_data
                        await self.after_update(data)
                        await self.build_message_queue(data)
                        
                    self.update_timer.reset()
                    gc.collect()
                    
                # Show next message
                await self.message_queue.show()
                
                # Small delay to prevent tight loop
                await asyncio.sleep(0.1)
                
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
            self._running = False
        except Exception as e:
            logger.error(e, "Fatal error in application")
            raise
            
    def stop(self):
        """Stop the application."""
        self._running = False
        logger.info("Application stopped")