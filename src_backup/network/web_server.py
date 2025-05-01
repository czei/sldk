"""
Web server implementation for the ThemeParkAPI.
Copyright 2024 3DUPFitters LLC
"""
import asyncio
import time

from adafruit_datetime import datetime
from adafruit_httpserver import Server
from adafruit_httpserver import Request
from adafruit_httpserver import Response
from adafruit_httpserver.methods import GET, POST

from src.models.vacation import Vacation
from src.utils.color_utils import ColorUtils
from src.utils.error_handler import ErrorHandler
from adafruit_httpserver import REQUEST_HANDLED_RESPONSE_SENT

# Initialize logger
logger = ErrorHandler("error_log")

class ThemeParkWebServer:
    """Web server implementation for ThemeParkAPI"""
    COLOR_PARAMS = ["default_color", "ride_name_color", "ride_wait_time_color"]

    def __init__(self, socket_pool, app_instance):
        """
        Initialize the web server
        
        Args:
            socket_pool: The socket pool to use
            app_instance: The ThemeParkApp instance to interact with
        """
        self.app = app_instance
        # Use a more secure root path instead of "/" to prevent exposing sensitive files
        self.server = Server(socket_pool, "src/www", debug=True)
        self.is_running = False
        self.last_settings_save = 0  # Track when settings were last saved

        # Register routes
        self.register_routes()

    def register_routes(self):
        """Register HTTP routes with the server"""

        @self.server.route("/", [GET])
        def base(request: Request):
            """Handle root endpoint"""
            query_params = str(request.query_params) if request.query_params else None

            if query_params:
                # Process parameters and update settings synchronously
                try:
                    # Process parameters directly with a non-async approach
                    self._process_query_params(query_params)
                    logger.info(f"Processed main page form params: {query_params}")
                except Exception as e:
                    logger.error(e, f"Error processing query params: {query_params}")

                # Generate response page with updated settings
                # No redirect - return the updated page directly
                page = self.generate_main_page()
                return Response(request, page, content_type="text/html")

            # Generate main page (no query params)
            page = self.generate_main_page()
            return Response(request, page, content_type="text/html")

        @self.server.route("/style.css", [GET])
        def style(request: Request):
            """Serve CSS styles"""
            try:
                # First try to read from www directory (preferred location)
                try:
                    with open("/src/www/style.css", "r") as f:
                        content = f.read()
                    logger.debug("Successfully served style.css from /www")
                    return Response(request, content, content_type="text/css")
                except OSError:
                    # Fallback to src directory for backward compatibility
                    with open("/www/style.css", "r") as f:
                        content = f.read()
                    logger.debug("Successfully served style.css from /src")
                    return Response(request, content, content_type="text/css")
            except OSError as e:
                logger.error(e, "Error serving style.css from all locations")
                # Create a minimal fallback CSS if the file can't be read
                fallback_css = """
                body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
                .navbar { background-color: #faa538; color: white; padding: 1rem; display: flex; justify-content: space-between; }
                .navbar a { color: white; text-decoration: none; }
                .main-content { padding: 1rem; }
                button { background-color: #faa538; border: none; padding: 8px 16px; color: white; cursor: pointer; }
                input, select { margin: 5px 0; padding: 5px; }
                .form-group { margin-bottom: 1rem; }
                """
                return Response(request, fallback_css, content_type="text/css")

        @self.server.route("/settings", [GET])
        def settings(request: Request):
            """Handle settings endpoint"""
            query_params = str(request.query_params) if request.query_params else None

            if query_params:
                # Process settings form submission
                try:
                    self._process_query_params(query_params)
                    logger.info(f"Processed settings form params: {query_params}")
                except Exception as e:
                    logger.error(e, f"Error processing settings query params: {query_params}")

            # Generate settings page
            # Generate settings page with success message if query params were processed
            if query_params:
                page = self.generate_settings_page(success=True)
            else:
                page = self.generate_settings_page()
            return Response(request, page, content_type="text/html")

    def start(self, ip_address):
        """
        Start the web server with improved reliability
        
        Args:
            ip_address: The IP address to bind to
        """
        try:
            # Make sure to convert IP to string and specify port 80
            logger.debug(f"Starting server on {ip_address}:80")

            # Try to stop any existing server first
            # try:
            #     self.server.stop()
            #     # Add a delay to ensure socket is properly released
            #     import time
            #     time.sleep(1)
            # except Exception as stop_error:
            #     logger.error(stop_error, "Error stopping existing server - continuing anyway")
                
            # Before starting, check if port is in use - CircuitPython doesn't have socket.SO_REUSEADDR
            # so we need to ensure the port is free
            # try:
            #     import socket
            #     test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #     test_socket.bind(("0.0.0.0", 80))
            #     test_socket.close()
            #     # Port is available
            # except OSError as sock_error:
            #     # Port is still in use, try to forcefully clear it
            #     logger.error(sock_error, "Port 80 is still in use. Attempting to reset networking...")
            #     try:
            #         # Reset the network interface to clear all sockets
            #         import wifi
            #         self.is_running = False
            #         # Wait for any in-flight connections to complete
            #         time.sleep(2)
            #     except Exception as reset_error:
            #         logger.error(reset_error, "Failed to reset networking")
            #         self.is_running = False
            #         return

            # Start the server with "0.0.0.0" to listen on all interfaces
            # This is important for ensuring the server responds to all incoming connections
            self.server.start("0.0.0.0", 80)

            # Verify server started
            logger.info(f"Web server started on all interfaces, access at http://{ip_address}")
            self.is_running = True

        except Exception as e:
            logger.error(e, f"Failed to start web server on {ip_address}:80")
            self.is_running = False

    def stop(self):
        """Stop the web server with improved error handling"""
        if not self.is_running:
            return
            
        try:
            # Mark as not running first to prevent further poll operations
            self.is_running = False
            
            # Add delay to allow any in-flight requests to complete
            import time
            time.sleep(0.5)
            
            try:
                # Check if server has a valid socket before stopping
                if hasattr(self.server, 'server_socket') and self.server.server_socket:
                    self.server.stop()
                    logger.debug("Web server stopped successfully")
                else:
                    logger.debug("Server already stopped or has invalid socket")
            except Exception as stop_error:
                logger.error(stop_error, "Error stopping web server")
                
            # Ensure we release resources associated with the server
            if hasattr(self.server, 'server_socket'):
                try:
                    if self.server.server_socket:
                        self.server.server_socket.close()
                except Exception:
                    pass
                    
        except Exception as e:
            logger.error(e, "Unexpected error in web server stop")
        finally:
            # Always mark as not running, regardless of exceptions
            self.is_running = False

    def _process_query_params(self, query_params):
        """
        Process query parameters synchronously without using async/await
        
        Args:
            query_params: Query parameters from the request as a string
            
        Returns:
            True if a park change was detected, False otherwise
        """
        if not query_params or not self.app or not hasattr(self.app, 'theme_park_service'):
            return False

        # Track if park was changed
        park_changed = False

        # Parse park-id parameter
        if "park-id=" in query_params:
            try:
                # Check current park ID before updating
                current_park_id = None
                if (hasattr(self.app.theme_park_service, 'park_list') and
                        hasattr(self.app.theme_park_service.park_list, 'current_park')):
                    current_park_id = self.app.theme_park_service.park_list.current_park.id

                # Direct access to park_list to update current park
                if hasattr(self.app.theme_park_service, 'park_list'):
                    # Save park list state before update
                    self.app.theme_park_service.park_list.parse(query_params)
                    logger.debug(f"Updated park selection from query params")

                    # Check if park ID changed
                    new_park_id = self.app.theme_park_service.park_list.current_park.id
                    park_changed = (current_park_id != new_park_id)
                    if park_changed:
                        logger.info(f"Park changed from ID {current_park_id} to {new_park_id}")
            except Exception as e:
                logger.error(e, "Error updating park selection")

        # Always set checkbox values (they'll be missing from query_params if unchecked)
        if hasattr(self.app.theme_park_service, 'park_list'):
            # Handle skip_closed checkbox
            skip_closed = "skip_closed=on" in query_params
            self.app.theme_park_service.park_list.skip_closed = skip_closed
            logger.debug(f"Set skip_closed to {skip_closed}")

            # Handle skip_meet checkbox
            skip_meet = "skip_meet=on" in query_params
            self.app.theme_park_service.park_list.skip_meet = skip_meet
            logger.debug(f"Set skip_meet to {skip_meet}")

        # Process vacation parameters if present
        vacation_updated = False
        if "Year=" in query_params and hasattr(self.app.theme_park_service, 'vacation'):
            try:
                # Always parse vacation data if any field is present
                self.app.theme_park_service.vacation.parse(query_params)
                vacation_updated = True
                logger.debug(f"Updated vacation settings from query params")
            except Exception as e:
                logger.error(e, "Error updating vacation settings")

        # Track display settings changes
        brightness_changed = False
        brightness_match = False
        scroll_changed = False
        import re
        # Process display settings
        if "domain_name=" in query_params:
            try:
                # Extract domain name value

                domain_match = re.search(r'domain_name=([^&]+)', query_params)
                if domain_match:
                    domain_name = domain_match.group(1)
                    self.app.settings_manager.settings["domain_name"] = domain_name
                    logger.debug(f"Updated domain name to {domain_name}")
            except Exception as e:
                logger.error(e, "Error updating display settings")

        # Extract brightness scale
        brightness_match = re.search(r'brightness_scale=([^&]+)', query_params)
        if brightness_match:
            brightness = brightness_match.group(1)
            self.app.settings_manager.settings["brightness_scale"] = brightness
            logger.debug(f"Updated brightness to {brightness}")
            brightness_changed = True

        self._process_color_params(query_params)

        # Save settings after changes
        try:
            self.app.settings_manager.save_settings()
            logger.debug("Settings saved successfully after processing query params")

            if (brightness_changed or scroll_changed) and hasattr(self.app, 'message_queue'):
                self.app.display.set_colors(self.app.settings_manager)
                logger.debug("Reset message queue after display settings change")
        except Exception as e:
            logger.error(e, "Error saving settings")

        # Extract scroll speed
        scroll_match = re.search(r'scroll_speed=([^&]+)', query_params)
        if scroll_match:
            scroll_speed = scroll_match.group(1)
            self.app.settings_manager.settings["scroll_speed"] = scroll_speed
            logger.debug(f"Updated scroll speed to {scroll_speed}")
            # No immediate action needed for scroll speed as it's read on demand when scrolling

        # Save settings
        try:
            if hasattr(self.app.theme_park_service, 'save_settings'):
                self.app.theme_park_service.save_settings()
                self.last_settings_save = time.monotonic()
                logger.debug("Settings saved successfully")

                # Reset message queue if display settings changed
                if (brightness_changed or scroll_changed) and hasattr(self.app, 'message_queue'):
                    # Schedule message queue rebuild on next display refresh
                    self.app.display.set_colors(self.app.settings_manager)
                    logger.debug("Reset message queue after display settings change")
        except Exception as e:
            logger.error(e, "Error saving settings")

        # Trigger park update if needed
        if park_changed:
            self._trigger_park_update()

        return park_changed

    def _trigger_park_update(self):
        """Trigger an update of the current park's ride times"""
        try:
            if not hasattr(self.app, 'theme_park_service'):
                return

            logger.info("Triggering park data update after park change")

            # Schedule the update task if the app has the update_data method
            # This needs to be handled carefully since we can't use await here
            if hasattr(self.app, 'update_timer'):
                # Force timer to expire to trigger update on next cycle
                self.app.update_timer.reset(expired=True)
                logger.debug("Reset update timer to trigger immediate update")

            # Alternative approach - create a flag to signal update needed
            if hasattr(self.app, 'theme_park_service'):
                self.app.theme_park_service.update_needed = True
                logger.debug("Set update_needed flag to trigger update")

        except Exception as e:
            logger.error(e, "Error triggering park update")

    async def poll(self):
        """
        Poll the server for incoming requests with improved error recovery
        
        Returns:
            True if a request was handled, False/None otherwise
        """
        if not self.is_running:
            return None

        try:
            # Poll the server for requests
            result = self.server.poll()

            # Short sleep to allow other tasks to run - essential for cooperative multitasking
            await asyncio.sleep(0.10)  # Slightly longer yield to reduce CPU usage

            # Only return a meaningful result for actual requests

            if result == REQUEST_HANDLED_RESPONSE_SENT:
                return True

            return False

        except BrokenPipeError as pipe_error:
            # BrokenPipeError is common when client disconnects prematurely
            # Log but no need to restart server as it's a client-side issue
            logger.debug(f"Client disconnected prematurely: {pipe_error}")
            await asyncio.sleep(0.1)  # Brief pause
            return False
            
        except OSError as os_error:
            # Handle specific OSError cases
            if os_error.args and os_error.args[0] == 32:  # Broken pipe
                logger.debug("OSError: Broken pipe - client disconnected")
                await asyncio.sleep(0.1)
                return False
            elif os_error.args and os_error.args[0] == 104:  # Connection reset
                logger.debug("OSError: Connection reset by client")
                await asyncio.sleep(0.1)
                return False
            else:
                # Other OS errors might require restart
                logger.error(os_error, f"OS Error in web server poll: {os_error}")
                await self._attempt_server_restart()
                return False
                
        except Exception as e:
            # Log the error but don't crash the server
            logger.error(e, f"Error in web server poll: {type(e).__name__}")

            # Brief pause to avoid error loops
            await asyncio.sleep(0.5)  # Longer pause for more serious errors

            # Check if server still needs to be restarted
            await self._attempt_server_restart()
            
            return False
    
    async def _attempt_server_restart(self):
        """Helper method to attempt server restart with proper error handling"""
        # First check if the server socket is still valid
        try:
            # Access a server property to check if it's functioning
            if hasattr(self.server, 'server_socket') and self.server.server_socket:
                addr = self.server.server_socket.getsockname()
                # If we get here, server socket is still valid
                return
        except Exception:
            # Server socket appears invalid, needs restart
            pass
            
        # If we get here, server needs restart
        logger.info("Restarting web server after error")
        
        # Implement a circuit breaker pattern to avoid restart loops
        import time
        # Track restart time in a module variable
        if not hasattr(self, '_last_restart_time'):
            self._last_restart_time = 0
            self._restart_attempts = 0
            
        current_time = time.monotonic()
        # Limit restarts to max once per 10 seconds to avoid rapid restarts
        if current_time - self._last_restart_time < 10:
            self._restart_attempts += 1
            # If we've had multiple rapid restart attempts, wait longer before trying again
            if self._restart_attempts > 3:
                logger.error(None, f"Multiple restart attempts ({self._restart_attempts}), waiting longer...")
                await asyncio.sleep(5)  # Longer cooldown period
                if self._restart_attempts > 10:
                    logger.error(None, "Too many restart attempts, server may be unstable")
                    self.is_running = False  # Mark as not running to prevent further attempts
                    return
            return
            
        # Try to restart the server
        try:
            # Record this attempt
            self._last_restart_time = current_time
            self._restart_attempts += 1
            
            # Stop all current connections
            self.is_running = False
            try:
                self.server.stop()
            except Exception as stop_error:
                logger.error(stop_error, "Error stopping server during restart")
            
            # Wait to ensure sockets are released
            await asyncio.sleep(2)
            
            # Create a fresh server instance to avoid any stale state
            import socketpool
            import wifi
            
            # Try to clear port 80 if it's still in use
            try:
                import socket
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.bind(("0.0.0.0", 80))
                test_socket.close()
            except OSError as sock_error:
                logger.error(sock_error, "Port 80 still in use during restart, may fail")
                # Continue anyway as we'll catch the error on start
                await asyncio.sleep(2)  # Additional wait time
                
            # Start the server fresh
            try:
                self.server = Server(socketpool.SocketPool(wifi.radio), "src/www", debug=True)
                self.register_routes()  # Re-register the routes
                self.server.start("0.0.0.0", 80)
                self.is_running = True
                logger.info("Web server restarted successfully")
                
                # Reset restart counter on success
                self._restart_attempts = 0
            except Exception as start_error:
                logger.error(start_error, "Failed to restart web server")
                self.is_running = False
                
        except Exception as restart_error:
            logger.error(restart_error, "Unexpected error during server restart")
            self.is_running = False

    def generate_main_page(self):
        """
        Generate the main HTML page
        
        Returns:
            HTML content for the main page
            
        Note:
            This method uses direct access to app data to avoid asyncio conflicts
        """
        page = "<!DOCTYPE html><html><head>"
        page += "<title>Theme Park Waits</title>"
        page += "<link rel=\"stylesheet\" href=\"/style.css\">"
        page += "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        page += "</head>"
        page += "<body>"

        page += "<div class=\"navbar\">"
        page += "<a href=\"/\">Theme Park Wait Times</a>"
        page += "</div>"
        # Add gear icon using image for better sizing control
        page += "<div class=\"gear-icon\">"
        page += "<a href=\"/settings\"><img src=\"gear.png\" alt=\"Settings\"></a>"
        page += "</div>"

        # Main content
        page += "<div class=\"main-content\">"
        page += "<h2>Theme Park Selection</h2>"

        # Get parks from app - without using asyncio.run()
        try:
            # Create basic response data first
            response_data = {
                "parks": [],
                "settings": self.app.settings_manager.settings,  # Include settings directly
                "success": True
            }

            # Use direct data access - no event loop
            parks = []

            # Safely access theme park data directly with full error handling
            try:
                # Check theme park service exists
                if (hasattr(self.app, 'theme_park_service') and
                        self.app.theme_park_service and
                        hasattr(self.app.theme_park_service, 'park_list') and
                        self.app.theme_park_service.park_list):

                    # Get parks list
                    if hasattr(self.app.theme_park_service.park_list, 'park_list'):
                        for park in self.app.theme_park_service.park_list.park_list:
                            if hasattr(park, 'id') and hasattr(park, 'name'):
                                parks.append({"id": park.id, "name": park.name})

                    # Get current park
                    if (hasattr(self.app.theme_park_service.park_list, 'current_park') and
                            self.app.theme_park_service.park_list.current_park and
                            hasattr(self.app.theme_park_service.park_list.current_park, 'is_valid')):

                        try:
                            if self.app.theme_park_service.park_list.current_park.is_valid():
                                current_park = self.app.theme_park_service.park_list.current_park
                                ride_count = 0
                                if hasattr(current_park, 'rides'):
                                    ride_count = len(current_park.rides)

                                response_data["current_park"] = {
                                    "id": current_park.id,
                                    "name": current_park.name,
                                    "ride_count": ride_count
                                }
                        except Exception as park_error:
                            logger.error(park_error, "Error getting current park data")

                # Update response data with parks
                response_data["parks"] = parks
                logger.debug(f"Using direct access for parks data - found {len(parks)} parks")

            except Exception as data_error:
                logger.error(data_error, "Error accessing theme park data")
                # Keep empty parks list
                response_data["parks"] = []

        except Exception as e:
            logger.error(e, "Error getting app data for main page")
            # Ensure response data exists with settings
            response_data = {"parks": [], "settings": {}, "success": False}

            # Try to get settings directly if available
            if hasattr(self.app, 'settings_manager') and hasattr(self.app.settings_manager, 'settings'):
                response_data["settings"] = self.app.settings_manager.settings

        if "parks" in response_data:
            page += "<form action=\"/\" method=\"get\">"
            page += "<select name=\"park-id\" id=\"park-select\">"

            # Check if we have parks and provide a message if empty
            parks = response_data.get("parks", [])
            if not parks:
                page += "<option value=\"\">No parks available - check connection</option>"
                logger.error(None, "No parks available for dropdown - empty park list")
            else:
                logger.debug(f"Generating dropdown with {len(parks)} parks")

                current_park_id = None
                if "current_park" in response_data:
                    current_park_id = response_data["current_park"]["id"]
                
                # Add "Select Park" as first option
                select_park_selected = "selected" if current_park_id is None else ""
                page += f"<option value=\"\" {select_park_selected}>Select Park</option>"

                for park in parks:
                    selected = "selected" if park["id"] == current_park_id else ""
                    park_name = park.get("name", "Unknown Park")
                    park_id = park.get("id", "")
                    page += f"<option value=\"{park_id}\" {selected}>{park_name}</option>"

            page += "</select>"
            # Safe access to settings
            settings = response_data.get("settings", {})
            if not isinstance(settings, dict):
                settings = {}

            # Create options div with better formatting
            page += "<div class=\"options\">"
            page += "<h3 style=\"margin-top: 0; margin-bottom: 10px; text-align: left; padding-left: 20px;\">Display Options</h3>"

            # Skip Closed Rides option - Fixed alignment with label
            page += "<div class=\"form-group checkbox-group\">"

            # Get skip_closed value with safe fallback
            skip_closed = False
            try:
                skip_closed = bool(settings.get("skip_closed", False))
            except (TypeError, ValueError):
                skip_closed = False

            checked = "checked" if skip_closed else ""
            # Keep checkbox and label together in a tight layout
            page += f"<input type=\"checkbox\" id=\"skip_closed\" name=\"skip_closed\" {checked}>"
            page += "<label for=\"skip_closed\">Skip Closed Rides</label>"
            page += "</div>"

            # Skip Meet & Greets option - Fixed alignment with label
            page += "<div class=\"form-group checkbox-group\">"

            # Get skip_meet value with safe fallback
            skip_meet = False
            try:
                skip_meet = bool(settings.get("skip_meet", False))
            except (TypeError, ValueError):
                skip_meet = False

            checked = "checked" if skip_meet else ""
            # Keep checkbox and label together in a tight layout
            page += f"<input type=\"checkbox\" id=\"skip_meet\" name=\"skip_meet\" {checked}>"
            page += "<label for=\"skip_meet\">Skip Meet & Greets</label>"
            page += "</div>"

            page += "</div>"

        else:
            page += "<p>No theme parks available.</p>"


        vacation_date = Vacation()
        vacation_date.load_settings(self.app.settings_manager)
        page += "<h2>Configure Countdown</h2>"
        page += "<div class=\"countdown-section\">"
        page += "<p>"
        page += "<label for=\"Name\">Event:</label>"
        page += f"<input type=\"text\" name=\"Name\" value=\"{vacation_date.name}\">"
        page += "</p>"

        page += "<p>"
        page += "<label for=\"Date\">Date:</label>"
        page += "<div class=\"date-selectors\">"
        
        # Year dropdown
        page += "<select id=\"Year\" name=\"Year\">"
        year_now = datetime.now().year
        for year in range(year_now, 2044):
            if vacation_date.is_set() is True and year == vacation_date.year:
                page += f"<option value=\"{year}\" selected>{year}</option>\n"
            else:
                page += f"<option value=\"{year}\">{year}</option>\n"
        page += "</select>"

        # Month dropdown with names
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        page += "<select id=\"Month\" name=\"Month\">"
        for month in range(1, 13):
            if vacation_date.is_set() is True and month == vacation_date.month:
                page += f"<option value=\"{month}\" selected>{month_names[month-1]}</option>\n"
            else:
                page += f"<option value=\"{month}\">{month_names[month-1]}</option>\n"
        page += "</select>"

        # Day dropdown
        page += "<select id=\"Day\" name=\"Day\">"
        for day in range(1, 32):
            if vacation_date.is_set() is True and day == vacation_date.day:
                page += f"<option value=\"{day}\" selected>{day}</option>\n"
            else:
                page += f"<option value=\"{day}\">{day}</option>\n"
        page += "</select>"
        page += "</div>" # end date-selectors
        page += "</p>"

        # If vacation is set, show countdown
        if vacation_date.is_set():
            days_until = vacation_date.get_days_until()
            if days_until > 0:
                page += f"<p style=\"text-align: center; font-weight: bold; margin-top: 10px;\">"
                page += f"Days until {vacation_date.name}: {days_until}"
                page += "</p>"
        
        page += "</div>" # end countdown-section

        page += "<button type=\"submit\">Update</button>"
        page += "</form>"

        page += "</div></body></html>"
        return page

    def generate_settings_page(self, success=False):
        """
        Generate the settings HTML page

        Args:
            success: Whether to show a success message

        Returns:
            HTML content for the settings page
        """
        # Get current settings - without using asyncio.run()
        response_data = {"settings": {}}

        try:
            # Always use direct access for settings - no event loop needed
            # This is more reliable in CircuitPython environment
            if hasattr(self.app, 'settings_manager') and hasattr(self.app.settings_manager, 'settings'):
                response_data = {"settings": self.app.settings_manager.settings}
                logger.debug("Using direct settings access - skipping event loop")
            else:
                logger.error(None, "Settings manager not available")
                response_data = {"settings": {}}
        except Exception as e:
            # Fallback if any error occurs
            logger.error(e, "Error getting settings data")
            response_data = {"settings": {}}

        settings = response_data.get("settings", {})

        page = "<!DOCTYPE html><html><head>"
        page += "<title>Settings - Theme Park Waits</title>"
        page += "<link rel=\"stylesheet\" href=\"/style.css\">"
        page += "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        page += "</head>"
        page += "<body>"

        page += "<div class=\"navbar\">"
        page += "<a href=\"/\">Theme Park Wait Times</a>"
        page += "</div>"
        # Add gear icon using image for consistent styling with main page
        page += "<div class=\"gear-icon\">"
        page += "<a href=\"/settings\"><img src=\"gear.png\" alt=\"Settings\"></a>"
        page += "</div>"

        page += "<div class=\"main-content\">"
        page += "<h2>Settings</h2>"

        # Show success message if settings were saved
        if success:
            page += "<div class=\"success-message\" style=\"background-color: #4CAF50; color: white; padding: 10px; margin-bottom: 15px; border-radius: 4px;\">"
            page += "Settings saved successfully!"
            page += "</div>"

        page += "<form action=\"/settings\" method=\"get\">"

        # Display settings
        page += "<div class=\"settings-section\">"
        page += "<h3>Display Settings</h3>"

        # Hostname/domain name
        page += "<div class=\"form-group\">"
        page += "<label for=\"domain_name\">Hostname (.local):</label>"
        domain_name = settings.get("domain_name", "themeparkwaits")
        page += f"<input type=\"text\" id=\"domain_name\" name=\"domain_name\" value=\"{domain_name}\">"
        page += "<br><small>Hostname change requires a device restart</small>"
        page += "</div>"

        # Brightness
        page += "<div class=\"form-group\">"
        page += "<label for=\"brightness_scale\">Brightness:</label>"
        brightness = settings.get("brightness_scale", "0.5")
        page += f"<input type=\"range\" id=\"brightness_scale\" name=\"brightness_scale\" min=\"0.3\" max=\"1.0\" step=\"0.1\" value=\"{brightness}\">"
        page += "</div>"

        # Scroll speed
        page += "<div class=\"form-group\">"
        page += "<label for=\"scroll_speed\">Scroll Speed:</label>"
        scroll_speed = settings.get("scroll_speed", "Medium")
        page += "<select id=\"scroll_speed\" name=\"scroll_speed\">"
        for speed in ["Slow", "Medium", "Fast"]:
            selected = "selected" if speed == scroll_speed else ""
            page += f"<option value=\"{speed}\" {selected}>{speed}</option>"
        page += "</select>"
        page += "</div>"
        page += "</div>"

        # Color settings
        page += "<div class=\"settings-section\">"
        page += "<h3>Color Settings</h3>"
        for color_setting_name, color_value in settings.items():
            if "color" in color_setting_name:
                page += "<p>"
                page += f"<label for=\"Name\">{self.app.settings_manager.get_pretty_name(color_setting_name)}</label>"
                page += ColorUtils.html_color_chooser(color_setting_name, hex_num_str=color_value)
                page += "</p>"
        page += "</div>"

        page += "<button type=\"submit\">Save Settings</button>"
        page += "</form>"

        page += "</div></body></html>"
        return page

    def _process_color_params(self, query_params: str) -> None:
        """
        Extract and update color-related settings from query parameters,
        decoding URL-encoded values without using urllib.parse.unquote.
        """
        import re

        for color_param in self.COLOR_PARAMS:
            try:
                color_pattern = f'{color_param}=([^&]+)'
                match = re.search(color_pattern, query_params)
                if match:
                    color_value = self._url_decode(match.group(1))
                    self.app.settings_manager.set(color_param, color_value)
                    logger.debug(f"Updated {color_param} to {color_value}")
            except Exception as e:
                logger.error(e, f"Error updating {color_param}")

    def _url_decode(self, encoded_str: str) -> str:
        """
        Decodes a percent-encoded string (e.g., 'Hello%20World') and plus signs ('+') to spaces,
        replicating urllib.parse.unquote's basic functionality compatible with CircuitPython.
        """
        import binascii
        res = []
        i = 0
        length = len(encoded_str)
        while i < length:
            char = encoded_str[i]
            if char == '+':
                res.append(' ')
                i += 1
            elif char == '%' and i + 2 < length:
                hex_value = encoded_str[i+1:i+3]
                try:
                    decoded_char = chr(int(hex_value, 16))
                    res.append(decoded_char)
                    i += 3
                except ValueError:
                    # Invalid percent-encoding, keep as is
                    res.append('%')
                    i += 1
            else:
                res.append(char)
                i += 1
        return ''.join(res)

