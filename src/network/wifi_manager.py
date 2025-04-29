"""
WiFi connection management.
Copyright 2024 3DUPFitters LLC
"""
import asyncio

from src.config.settings_manager import SettingsManager
from src.utils.error_handler import ErrorHandler
from src.utils.url_utils import load_credentials
import socketpool
import wifi
import adafruit_httpserver
from adafruit_httpserver import (
    Status,
    REQUEST_HANDLED_RESPONSE_SENT,
    Request,
    Response,
    Headers,
    GET,
    POST,
    Server
)

# Initialize logger
logger = ErrorHandler("error_log")

class WiFiManager:
    """
    Manages WiFi connections for the application
    """
    
    def __init__(self, settings_manager):
        """
        Initialize the WiFi manager
        
        Args:
            settings_manager: The settings manager
        """
        self.settings_manager = settings_manager
        self.ssid, self.password = load_credentials()
        self.is_connected = False
        self.wifi_client = None
        self.ap_enabled = False

        try:
            # Try to import CircuitPython specific modules
            import wifi
            self.wifi = wifi
            self.HAS_WIFI = True
            # extract access point mac address
            mac_ap = ' '.join([hex(i) for i in self.wifi.radio.mac_address_ap])
            mac_ap = mac_ap.replace('0x', '').replace(' ', '').upper()
            # access point settings
            self.AP_SSID = "WifiManager_" + mac_ap[5:10] + mac_ap[1:2]
            self.AP_PASSWORD = "password"
            self.AP_AUTHMODES = [self.wifi.AuthMode.WPA2, self.wifi.AuthMode.PSK]
            
            self.web_server = None

        except ImportError:
            # Mock for non-CircuitPython environments
            self.wifi = None
            self.HAS_WIFI = False
            logger.debug("WiFi module not available, using mock implementation")


            
    async def connect(self, display_callback=None):
        """
        Connect to WiFi
        
        Args:
            display_callback: Optional callback function to update display during connection attempts
            
        Returns:
            True if connected, False otherwise
        """
        if not self.HAS_WIFI:
            logger.debug("WiFi not available, simulating connection")
            self.is_connected = True
            return True
            
        try:
            if not self.ssid or not self.password:
                logger.error(ValueError("Missing WiFi credentials"), "WiFi credentials not found")
                return False
                
            logger.info(f"Connecting to WiFi network: {self.ssid}")
            
            # Maximum connection attempts
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    # Connect to the network
                    self.wifi.radio.connect(self.ssid, self.password)
                    self.is_connected = True
                    break
                except Exception as conn_err:
                    # Only log on final attempt, otherwise just try again
                    if attempt == max_attempts - 1:
                        logger.error(conn_err, f"Failed to connect to WiFi after {max_attempts} attempts")
                    
                    # Update display if callback provided
                    if display_callback:
                        await display_callback(f"Attempt {attempt+1}/{max_attempts}")
                    
                    # Short delay before retry
                    await asyncio.sleep(1)
            
            if self.is_connected:
                # Log connection info
                ip_address = self.wifi.radio.ipv4_address
                logger.info(f"Connected to WiFi. IP address: {ip_address}")
                
                # Now that we're connected, create the HTTP session
                # This should only happen AFTER a successful WiFi connection
                try:
                    session = self.create_http_session()
                    logger.info("Created HTTP session after WiFi connection")
                except Exception as session_error:
                    logger.error(session_error, "Failed to create HTTP session after WiFi connection")
                
                return True
            else:
                return False
            
        except Exception as e:
            logger.error(e, "Error connecting to WiFi")
            self.is_connected = False
            return False
            
    def create_http_session(self):
        """
        Create and return a new HTTP session
        This should only be called after WiFi is connected
        
        Returns:
            A new adafruit_requests.Session or None if not available
        """
        if not self.HAS_WIFI or not self.is_connected:
            logger.debug("Cannot create HTTP session without WiFi connection")
            return None
            
        try:
            import ssl
            import socketpool
            import adafruit_requests
            
            # Create a fresh socket pool from the radio
            pool = socketpool.SocketPool(self.wifi.radio)
            
            # Create a new SSL context
            ssl_context = ssl.create_default_context()
            
            # Create and return the session
            session = adafruit_requests.Session(pool, ssl_context)
            
            # Update any HTTP clients that need the session
            self.update_http_clients(session)
            
            return session
            
        except Exception as e:
            logger.error(e, "Error creating HTTP session")
            return None
            
    def update_http_clients(self, session):
        """
        Update any HTTP clients with the new session
        Mainly used by ThemeParkApp to update its HTTP client
        
        Args:
            session: The new adafruit_requests.Session
        """
        # This function will be called from the app to update HTTP clients
        # The implementation is in the app class
            
    async def disconnect(self):
        """Disconnect from WiFi"""
        if not self.HAS_WIFI or not self.is_connected:
            return
            
        try:
            logger.info("Disconnecting from WiFi")
            # Some CircuitPython versions may not have the disconnect method
            if hasattr(self.wifi.radio, 'disconnect'):
                self.wifi.radio.disconnect()
            self.is_connected = False
            
        except Exception as e:
            logger.error(e, "Error disconnecting from WiFi")
            
    async def reconnect(self):
        """
        Reconnect to WiFi if disconnected
        
        Returns:
            True if connected, False otherwise
        """
        if self.is_connected:
            return True
            
        # Try to reconnect
        return await self.connect()
        
    def is_available(self):
        """
        Check if WiFi is available
        
        Returns:
            True if WiFi is available, False otherwise
        """
        return self.HAS_WIFI
        
    def is_connected(self):
        """
        Check if connected to WiFi
        
        Returns:
            True if connected, False otherwise
        """
        if not self.HAS_WIFI:
            return self.is_connected
            
        try:
            return self.wifi.radio.connected
        except Exception:
            return False
            
    def get_ip_address(self):
        """
        Get the current IP address
        
        Returns:
            The IP address as a string, or None if not connected
        """
        if not self.HAS_WIFI or not self.is_connected:
            return None
            
        try:
            return str(self.wifi.radio.ipv4_address)
        except Exception:
            return None
            
    def save_credentials(self):
        """
        Save WiFi credentials to settings manager
        """
        if hasattr(self, 'settings_manager') and self.settings_manager:
            try:
                # Save SSID and password to settings
                self.settings_manager.settings["wifi_ssid"] = self.ssid
                self.settings_manager.settings["wifi_password"] = self.password
                
                # Save settings to disk
                self.settings_manager.save_settings()
                logger.info(f"Saved WiFi credentials to settings manager")
                
                # Also try to save to a secrets.py file for CircuitPython
                try:
                    self._save_to_secrets_file()
                except Exception as secrets_err:
                    logger.error(secrets_err, "Could not save to secrets.py file")
                    
            except Exception as e:
                logger.error(e, "Failed to save WiFi credentials to settings manager")
                
    def _save_to_secrets_file(self):
        """
        Save WiFi credentials to secrets.py file
        """
        try:
            # Read existing secrets file if it exists
            secrets_content = ""
            try:
                with open("/secrets.py", "r") as f:
                    secrets_content = f.read()
            except OSError:
                # Create a new secrets file with default structure
                secrets_content = """# This file is automatically generated - do not edit manually
secrets = {
    # WiFi credentials
    'ssid': '',
    'password': '',
}
"""

            # Update the SSID and password values
            import re
            
            # Pattern to match the SSID line
            ssid_pattern = r"('ssid'|\"ssid\")\s*:\s*('.*'|\".*\")"
            if re.search(ssid_pattern, secrets_content):
                # Replace existing SSID
                secrets_content = re.sub(ssid_pattern, f"'ssid': '{self.ssid}'", secrets_content)
            else:
                # Add SSID if not found
                secrets_content = secrets_content.replace("secrets = {", "secrets = {\n    'ssid': '" + self.ssid + "',")
                
            # Pattern to match password line
            password_pattern = r"('password'|\"password\")\s*:\s*('.*'|\".*\")"
            if re.search(password_pattern, secrets_content):
                # Replace existing password
                secrets_content = re.sub(password_pattern, f"'password': '{self.password}'", secrets_content)
            else:
                # Add password if not found
                secrets_content = secrets_content.replace("secrets = {", "secrets = {\n    'password': '" + self.password + "',")
            
            # Write the updated contents back to the file
            with open("/secrets.py", "w") as f:
                f.write(secrets_content)
                
            logger.info("Updated secrets.py file with new WiFi credentials")
            
        except Exception as e:
            logger.error(e, "Failed to save WiFi credentials to secrets.py file")

    def start_access_point(self,port=80):
        self.wifi.radio.enabled = True
        if self.ap_enabled is False:
            # to use encrypted AP, use authmode=[wifi.AuthMode.WPA2, wifi.AuthMode.PSK]
            if (self.AP_AUTHMODES[0] == self.wifi.AuthMode.OPEN):
                self.wifi.radio.start_ap(ssid=self.AP_SSID, authmode=self.AP_AUTHMODES)
            else:
                self.wifi.radio.start_ap(ssid=self.AP_SSID, password=self.AP_PASSWORD, authmode=self.AP_AUTHMODES)
            self.ap_enabled = True

    def stop_access_point(self):
        wifi.radio.stop_ap()
        self.ap_enabled = False
        
    def scan_networks(self):
        """
        Scan for available WiFi networks
        
        Returns:
            List of network info (SSID, RSSI, channel, security)
        """
        if not self.HAS_WIFI:
            logger.debug("WiFi not available, returning mock networks")
            # Return mock data for testing
            return [
                {"ssid": "HomeNetwork", "rssi": -65, "channel": 6},
                {"ssid": "GuestWiFi", "rssi": -70, "channel": 11}
            ]
            
        try:
            logger.debug("Scanning for WiFi networks...")
            networks = []
            
            # Scan for networks
            for network in self.wifi.radio.start_scanning_networks():
                # Skip hidden networks
                if not network.ssid:
                    continue
                    
                net_info = {
                    "ssid": network.ssid,
                    "rssi": network.rssi,
                    "channel": network.channel
                }
                networks.append(net_info)
                
            # Sort networks by signal strength (strongest first)
            networks.sort(key=lambda x: x["rssi"], reverse=True)
            
            self.wifi.radio.stop_scanning_networks()
            logger.debug(f"Found {len(networks)} WiFi networks")
            return networks
            
        except Exception as e:
            logger.error(e, "Error scanning for WiFi networks")
            # Return empty list on error
            return []
            
    def generate_wifi_setup_page(self):
        """
        Generate a WiFi setup page with available networks
        
        Returns:
            HTML content as string
        """
        # Scan for networks
        networks = self.scan_networks()
        
        # Get the page template
        try:
            with open("/src/wifi-setup.html", "r") as f:
                template = f.read()
                
            # Replace the networks section
            # Look for form start and insert networks before password field
            form_start = "<form action=\"configure\" method=\"post\">"
            password_field = "<div><label>Password:</label>"
            
            # Create networks HTML
            networks_html = ""
            for i, network in enumerate(networks):
                ssid = network["ssid"]
                rssi = network["rssi"]
                # Convert RSSI to signal bars (1-4)
                bars = min(4, max(1, int((network["rssi"] + 100) / 15)))
                
                networks_html += f"""
                <div class="network">
                  <input type="radio" id="ssid_{i}" name="ssid" value="{ssid}" />
                  <label for="ssid_{i}">{ssid} ({bars} bars, {rssi} dBm)</label>
                </div>
                <br>
                """
                
            # If we found the template sections, replace them
            if form_start in template and password_field in template:
                # Split the template
                parts = template.split(password_field)
                if len(parts) == 2:
                    # Replace content between form start and password field
                    start_index = parts[0].find(form_start) + len(form_start)
                    # Insert networks and modify the button section to include scan button
                    result = parts[0][:start_index] + "\n" + networks_html + password_field + parts[1]
                    
                    # Replace the button section with one that includes scan button
                    button_line = "<p><button>Connect</button></p>"
                    scan_buttons = """<div style="display: flex; justify-content: space-between; margin-top: 20px;">
                        <button type="submit">Connect</button>
                        <a href="/?scan=true" style="display: inline-block; padding: 8px 16px; background-color: #4285f4; color: white; text-decoration: none; border-radius: 4px;">Scan Networks</a>
                    </div>"""
                    
                    result = result.replace(button_line, scan_buttons)
                    return result
                    
            # If we couldn't modify the template, return it as is
            return template
                
        except OSError:
            # If we can't read the template, create a minimal page
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>WiFi Setup</title>
                <link rel="stylesheet" href="/wifi_style.css">
                <meta name="viewport" content="width=device-width, initial-scale=1">
            </head>
            <body>
                <h1>WiFi Setup</h1>
                <form action="configure" method="post">
            """
            
            # Add networks
            if networks:
                for i, network in enumerate(networks):
                    ssid = network["ssid"]
                    rssi = network["rssi"]
                    # Convert RSSI to signal bars (1-4)
                    bars = min(4, max(1, int((network["rssi"] + 100) / 15)))
                    
                    html += f"""
                    <div class="network">
                      <input type="radio" id="ssid_{i}" name="ssid" value="{ssid}" />
                      <label for="ssid_{i}">{ssid} ({bars} bars, {rssi} dBm)</label>
                    </div>
                    <br>
                    """
            else:
                html += "<p>No networks found. Please refresh to scan again.</p>"
                
            # Complete the form
            html += """
                    <div><label>Password:</label> <input class="text" name="password" type="password"></div>
                    <div style="display: flex; justify-content: space-between; margin-top: 20px;">
                        <button type="submit">Connect</button>
                        <a href="/?scan=true" style="display: inline-block; padding: 8px 16px; background-color: #4285f4; color: white; text-decoration: none; border-radius: 4px;">Scan Networks</a>
                    </div>
                </form>
            </body>
            </html>
            """
            
            return html

    def start_web_server(self):
        logger.debug("starting web server..")
        pool = socketpool.SocketPool(wifi.radio)
        self.web_server = Server(pool, "/www", debug=False)
        
        # Register routes for WiFi setup
        self.register_routes()
        
        # Start the server
        self.web_server.start(str(wifi.radio.ipv4_address_ap), 80)
        logger.debug("Listening on http://%s:80" % str(wifi.radio.ipv4_address_ap))

    async def run_web_server(self, termination_func):
        """
        Run the web server in a loop until termination function returns True
        
        Args:
            termination_func: A function that returns True when the server should stop
        """
        # Don't call termination_func here, just log the function reference
        logger.debug(f"Starting web server loop with termination function")
        
        if not hasattr(self, 'web_server') or self.web_server is None:
            logger.error("Web server not initialized")
            return
            
        # If you want you can stop the server by calling server.stop() anywhere in your code
        while not termination_func() and not self.web_server.stopped:
            try:
                # Process any waiting HTTP requests
                self.web_server.poll()
                await asyncio.sleep(1)
            except OSError as error:
                logger.error(f"Web server loop stopped with error: {str(error)}")
                # traceback.print_exc()
                continue
        logger.debug(f"Exiting wifimgr:run_web_server()")


    def register_routes(self):
        """Register HTTP routes for WiFi setup"""

        @self.web_server.route("/", [GET])
        def root(request: Request):
            """Handle root endpoint - show WiFi setup page with networks list"""
            try:
                # Check if scan requested
                query_params = str(request.query_params) if request.query_params else ""
                if "scan=true" in query_params:
                    logger.debug("Network scan requested")
                    # Force a fresh scan before generating the page
                    self.wifi.radio.stop_scanning_networks()

                # Generate a dynamic page with available networks
                html_content = self.generate_wifi_setup_page()
                logger.debug("Serving dynamic WiFi setup page")
                return Response(request, html_content, content_type="text/html")
            except OSError as e:
                logger.error(e, "Error serving WiFi setup page")
                error_html = "<html><body><h1>Error loading WiFi setup page</h1></body></html>"
                return Response(request, error_html, content_type="text/html")

        @self.web_server.route("/wifi_style.css", [GET])
        def wifi_style(request: Request):
            """Serve WiFi CSS styles"""
            try:
                with open("/www/wifi_style.css", "r") as f:
                    content = f.read()
                logger.debug("Successfully served wifi_style.css")
                return Response(request, content, content_type="text/css")
            except OSError as e:
                logger.error(e, "Error serving wifi_style.css")
                fallback_css = """
                body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
                .network { margin-bottom: 10px; }
                input[type="radio"] { margin-right: 10px; }
                """
                return Response(request, fallback_css, content_type="text/css")

        @self.web_server.route("/configure", [POST])
        def configure(request: Request):
            """Handle WiFi configuration form submission"""
            try:
                # Get form data from request
                content_length = int(request.headers.get("Content-Length", 0))
                form_data = request.body.read(content_length).decode("utf-8")
                logger.debug(f"Received form data: {form_data}")

                # Parse form data to get SSID and password
                ssid = None
                password = None

                # Simple parsing of form data
                params = form_data.split("&")
                for param in params:
                    if "=" in param:
                        key, value = param.split("=", 1)
                        if key == "ssid":
                            ssid = value
                        elif key == "password":
                            password = value

                if ssid and password:
                    # Update credentials
                    self.ssid = ssid.replace("+", " ")  # Replace + with space in form-encoded data
                    self.password = password
                    # Save credentials to settings manager
                    self.save_credentials()
                    logger.info(f"Updated WiFi credentials, SSID: {self.ssid}")

                    # Try to connect
                    response_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>WiFi Configuration</title>
                        <meta http-equiv="refresh" content="10;url=/" />
                    </head>
                    <body>
                        <h1>WiFi Configuration</h1>
                        <p>Connecting to network: {self.ssid}</p>
                        <p>The device will attempt to connect to the network.</p>
                        <p>If successful, you will need to connect to your regular WiFi network to access the device.</p>
                        <p>If connection fails, the access point will remain active and you can try again.</p>
                    </body>
                    </html>
                    """

                    # Create a task to connect to the new network (after sending response)
                    # This won't block the response
                    asyncio.create_task(self.connect())

                    return Response(request, response_html, content_type="text/html")
                else:
                    error_html = """
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Error</title>
                        <meta http-equiv="refresh" content="5;url=/" />
                    </head>
                    <body>
                        <h1>Configuration Error</h1>
                        <p>Missing SSID or password.</p>
                        <p>Returning to setup page in 5 seconds...</p>
                    </body>
                    </html>
                    """
                    return Response(request, error_html, content_type="text/html")

            except Exception as e:
                logger.error(e, "Error processing WiFi configuration")
                error_html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Error</title>
                    <meta http-equiv="refresh" content="5;url=/" />
                </head>
                <body>
                    <h1>Configuration Error</h1>
                    <p>An error occurred while processing your request.</p>
                    <p>Returning to setup page in 5 seconds...</p>
                </body>
                </html>
                """
                return Response(request, error_html, content_type="text/html")