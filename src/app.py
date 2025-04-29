"""
Main application for Theme Park Waits.
Copyright 2024 3DUPFitters LLC
"""
import asyncio
import json
import gc
import socketpool
import wifi

from src.config.settings_manager import SettingsManager
from src.api.theme_park_service import ThemeParkService
from src.ui.message_queue import MessageQueue
from src.utils.error_handler import ErrorHandler
from src.utils.timer import Timer
from src.network.wifi_manager import WiFiManager
from src.utils.url_utils import load_credentials

# Initialize logger
logger = ErrorHandler("error_log")


class ThemeParkApp:
    """
    Main application class for Theme Park Waits
    """

    def __init__(self, display, http_client):
        """
        Initialize the application
        
        Args:
            display: The display to use
            http_client: The HTTP client for network requests
        """
        self.display = display
        self.http_client = http_client
        self.socket_pool = None
        self.settings_manager = SettingsManager("settings.json")
        self.theme_park_service = ThemeParkService(self.http_client, self.settings_manager)
        self.message_queue = MessageQueue(display, 4)
        self.update_timer = Timer(300)  # Update every 5 minutes
        self.wifi_manager = WiFiManager(self.settings_manager)
        self.web_server = socketpool.SocketPool(wifi.radio)

        # Set up the callback for session updates in the WiFi manager
        self.wifi_manager.update_http_clients = self.update_http_client

    async def initialize_all(self):
        """Initialize the application"""
        logger.info("Initializing Theme Park Waits application")

        # Set display colors from settings
        if hasattr(self.display, 'set_colors'):
            self.display.set_colors(self.settings_manager)

        # Show splash screen first before any network operations
        await self.display.show_splash(4)

        # Create a task for network and data initialization (runs in background)
        # TODO: Figure out how to make the initialization process async to talk to an event-drive display to update users.
        # init_task = asyncio.create_task(self._initialize_background_data())

        await self._initialize_wifi_password()
        await self._initialize_wifi()
        await self._initialize_clock()
        await self._initialize_park_list()
        await self._initialize_wait_times()

    async def _initialize_wifi_password(self):
        # Load Current Wifi Password
        ssid, password = load_credentials()

        #
        # True when first starting device or the Wifi has been reset
        #
        if ssid != "" and password != "":
            return

        # Have to configure Wi-FI before the network will work
        # Run the Wifi configure GUI and the configure message at the same time
        try:
            self.wifi_manager.start_access_point()
            self.wifi_manager.start_web_server()
            #wifimgr.web_server.serve_forever(str(wifi.radio.ipv4_address_ap))

            # Pass a lambda that calls is_wifi_password_configured instead of calling it directly
            asyncio.run(asyncio.gather(
                self.wifi_manager.run_web_server(lambda: self.is_wifi_password_configured()),
                self.run_configure_wifi_message()
            ))

            self.wifi_manager.web_server.stop()
            self.wifi_manager.stop_access_point()

        except OSError as e:
            logger.error(e,"Exception starting wifi access point and web server: {e}")

        # Now that we've got an ssid and password, time to connect to
        # the network.
        # asyncio.run(asyncio.gather(self.try_wifi_until_connected()))

    async def _initialize_wifi(self):
        """Initialize network and theme park data in the background"""
        # Show WiFi connection message with actual SSID
        ssid = self.wifi_manager.ssid
        await self.display.show_centered(f"Connecting to WiFi:", f"{ssid}", 0)

        # Create a display callback for connection status updates
        # async def update_connection_status(status):
        # await self.display.show_centered(f"Connecting to WiFi:", f"{ssid} {status}", 0)

        # Initialize networking with status updates
        connected = await self.wifi_manager.connect()

        # Show appropriate message based on connection result
        if connected:
            await self.display.show_centered("WiFi Connected", f"{ssid}", 1)
            # Create HTTP session after WiFi is connected
            self.socket_pool = socketpool.SocketPool(wifi.radio)
            await self._initialize_http_client(self.socket_pool)
        else:
            await self.display.show_centered("WiFi Failed", f"Check settings", 2)

    async def run_configure_wifi_message(self):
        while self.is_wifi_password_configured() is False:
            setup_text1 = f"Connect your phone to Wifi channel {self.wifi_manager.AP_SSID}, password \"{self.wifi_manager.AP_PASSWORD}\"."
            setup_text2 = "  Then load page http://192.168.4.1"
            await self.display.show_centered(setup_text1, setup_text2, 1)

    async def try_wifi_until_connected(self):
        ssid, password = load_credentials()

        # Try to connect 3 times before giving up in
        # case the Wifi is unstable.
        attempts = 1
        if wifi.radio.connected is True:
            logger.debug(f"Already connected to wifi {ssid}: at {wifi.radio.ipv4_address}")
        else:
            logger.debug(f"Connecting to wifi {ssid}: at {wifi.radio.ipv4_address}")

        while wifi.radio.connected is not True:
            try:
                setup_text1 = f"Connecting to Wifi:"
                setup_text2 = f"{ssid}"
                await self.display.show_centered(setup_text1, setup_text2, 2)
                wifi.radio.connect(ssid, password)
            except (RuntimeError) as e:
                logger.error(e,f"Wifi runtime error: {str(e)} at {wifi.radio.ipv4_address}")
                await self.display.show_scroll_message(f"Wifi runtime error: {str(e)}")
            except (ConnectionError) as e:
                logger.error(e, f"Wifi connection error: {str(e)} at {wifi.radio.ipv4_address}")
                if "Authentication" in str(e):
                    await self.display.show_scroll_message(f"Bad password.  Please reset the LED scroller using the INIT button as described in the instructions.")
                else:
                    await self.display.show_scroll_message(f"Wifi connection error: {str(e)}")
            except (ValueError) as e:
                logger.error(e, "Wifi value error")
                # logger.error(f"Wifi value error: {str(e)} at {wifi.radio.ipv4_address}")
                await self.display.show_scroll_message(f"Wifi value error: {str(e)}")

            except OSError as e:
                logger.error(e, "Unknown error connecting to Wifi")


    async def _initialize_park_list(self):
        # Initialize theme park service
        # await self.display.show_scroll_message("Downloading list of theme parks...")
        await self.theme_park_service.initialize()

    async def _initialize_wait_times(self):
        # Update data for the first time, not checking timer
        # (This will show its own update message)
        await self.update_data(True)

        # Get accurate wait until next update
        self.update_timer.reset()

    async def _initialize_clock(self):
        # Takes too much time
        await self.display.show_scroll_message("Setting time...")
        try:
            logger.info("Setting system clock...")
            # Get the actual socket pool, not from HTTP client
            import wifi
            
            # Import set_system_clock function
            from src.utils.system_utils import set_system_clock
            
            # Pass both HTTP client and socketpool for flexibility
            await set_system_clock(self.http_client, self.socket_pool)
        except Exception as clock_error:
            logger.error(clock_error, "Warning: Could not set system clock, continuing without it")
            # Continue initialization even if clock setting fails

    async def update_data(self, ignore_timer):
        """Update theme park data from the API"""
        # Check if there's a valid park selected
        if not self.theme_park_service.park_list or not self.theme_park_service.park_list.current_park.is_valid():
            # No valid park selected, no need to update data
            # Just regenerate message queue to show prompt to select park
            self.message_queue.init()
            await self.build_messages()
            return

        # Check for forced update flag in theme_park_service
        force_update = False
        if hasattr(self.theme_park_service, 'update_needed'):
            force_update = self.theme_park_service.update_needed
            # Reset the flag
            self.theme_park_service.update_needed = False

        # Check if update is needed
        if not self.update_timer.finished() and not ignore_timer and not force_update:
            return

        logger.info("Updating theme park data")

        # Show scrolling message that data is being updated
        park_name = self.theme_park_service.park_list.current_park.name
        await self.display.show_scroll_message(f"Updating {park_name} wait times from queue-times.com...")

        # Reset the timer immediately to prevent multiple updates
        self.update_timer.reset()

        # Update current park data
        await self.theme_park_service.update_current_park()

        # Regenerate the message queue
        self.message_queue.init()
        await self.build_messages()

        # Force garbage collection to free memory
        gc.collect()

        # For some reason Claude recommended running it twice.
        gc.collect()

    async def build_messages(self):
        """Build the message queue for displaying information"""

        # Always add splash screen at front
        await self.message_queue.add_splash(4)

        # Get domain name for configuration URL
        domain_name = self.settings_manager.get("domain_name", "themeparkwaits")
        
        # Check if a park is selected
        if not self.theme_park_service.park_list or not self.theme_park_service.park_list.current_park.is_valid():
            # No park selected - show message to choose a park
            await self.message_queue.add_scroll_message(f"Choose theme park at http://{domain_name}.local", 1)
            # Repeat the message
            await self.message_queue.add_scroll_message(f"Choose theme park at http://{domain_name}.local", 1)
            # Add vacation information if set
            # await self.message_queue.add_vacation(self.theme_park_service.vacation)
            return
        
        # Park is selected - show regular configuration message
        await self.message_queue.add_scroll_message(f"Configure at http://{domain_name}.local", 1)

        # Add vacation information if set
        await self.message_queue.add_vacation(self.theme_park_service.vacation)

        # Add park data
        await self.message_queue.add_rides(self.theme_park_service.park_list)

        # Add attribution message
        await self.message_queue.add_required_message(
            self.theme_park_service.park_list.current_park.name)

    async def _initialize_http_client(self, socket_pool):
        """Initialize the HTTP client with a fresh session after WiFi is connected"""
        try:
            # Import necessary modules
            import ssl
            import socketpool
            import wifi
            import adafruit_requests

            # Create a socket pool and session
            logger.info("Creating new socket pool and HTTP session after WiFi connection")
            # pool = socketpool.SocketPool(wifi.radio)
            ssl_context = ssl.create_default_context()
            session = adafruit_requests.Session(socket_pool, ssl_context)

            # Update the HTTP client with the new session
            self.update_http_client(session)
            logger.info("HTTP client successfully initialized with new session")

        except Exception as e:
            logger.error(e, "Failed to initialize HTTP client")

    def update_http_client(self, session):
        """
        Update the HTTP client with a new session
        
        Args:
            session: The new HTTP session
        """
        try:
            if hasattr(self.http_client, 'session'):
                self.http_client.session = session
                logger.info("HTTP client session updated")

                # Also update session in the theme park service
                # if hasattr(self.theme_park_service, 'http_client'):
                #     self.theme_park_service.http_client.session = session
                #     logger.info("Theme park service HTTP client session updated")

        except Exception as e:
            logger.error(e, "Error updating HTTP client session")

    async def handle_web_request(self, request_path, query_params):
        """
        Handle a web request from the configuration interface
        
        Args:
            request_path: The requested path
            query_params: Query parameters from the request
            
        Returns:
            A dictionary with response data
        """
        if query_params:
            self.theme_park_service.parse_query_params(query_params)

            # Clear the message queue and rebuild it
            self.message_queue.init()
            await self.build_messages()

        # Prepare response data
        response = {
            "success": True,
            "settings": self.settings_manager.settings
        }

        if self.theme_park_service.park_list:
            park_list = []
            for park in self.theme_park_service.park_list.park_list:
                park_list.append({
                    "id": park.id,
                    "name": park.name
                })
            response["parks"] = park_list

            if self.theme_park_service.park_list.current_park.is_valid():
                response["current_park"] = {
                    "id": self.theme_park_service.park_list.current_park.id,
                    "name": self.theme_park_service.park_list.current_park.name,
                    "ride_count": len(self.theme_park_service.park_list.current_park.rides)
                }

        return response

    def start_web_server(self, socket_pool):
        """
        Start the web server
        
        Args:
            socket_pool: The socket pool to use
            
        Returns:
            The web server instance
        """
        from src.network.web_server import ThemeParkWebServer

        # Create and start web server
        web_server = ThemeParkWebServer(socket_pool, self)

        try:
            import wifi
            ip_address = wifi.radio.ipv4_address
            logger.info(f"Starting web server on IP: {ip_address}")

            # Start the web server with explicit IP binding
            web_server.start(ip_address)

            # Verify if server is running
            if web_server.is_running:
                logger.info(f"Web server successfully started at http://{ip_address}")
            else:
                logger.error(ValueError("Web server failed to start"), "Web server did not start properly")

            return web_server
        except Exception as e:
            logger.error(e, "Failed to start web server")
            return None

    async def run_display_loop(self):
        """Run the display update loop"""
        while True:
            try:
                # Update data if needed
                await self.update_data(False)

                # Show the next message in the queue
                await self.message_queue.show()

                # Small delay to prevent CPU hogging
                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(e, "Error in display loop")
                await asyncio.sleep(1)  # Delay to prevent rapid error loops

    async def run_web_server_loop(self, web_server):
        """Run the web server polling loop"""
        if not web_server:
            return

        while True:
            try:
                # Poll web server for requests without excessive logging
                await web_server.poll()

                # Small delay to prevent CPU hogging
                await asyncio.sleep(0.01)

            except Exception as e:
                logger.error(e, "Error in web server loop")
                await asyncio.sleep(1)  # Delay to prevent rapid error loops

    async def run(self):
        """Run the main application loop with concurrent tasks"""
        await self.initialize_all()

        # Start web server if in hardware mode
        web_server = None
        try:
            web_server = self.start_web_server(self.socket_pool)
        except ImportError as e:
            logger.error(e,"Running without web server in simulation mode")

        if web_server:
            # Run display and web server concurrently
            logger.info("Starting display and web server concurrently")
            await asyncio.gather(
                self.run_display_loop(),
                self.run_web_server_loop(web_server)
            )
        else:
            # Just run the display loop if no web server
            logger.info("Running display loop only")
            await self.run_display_loop()

    @staticmethod
    def is_wifi_password_configured() -> bool:
        ssid, password = load_credentials()
        # logger.debug(f"SSID: {ssid} Password: {password}")
        is_configured = ssid != "" and password != ""
        return is_configured
