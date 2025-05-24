"""
Web server implementation for the ThemeParkAPI.
Copyright 2024 3DUPFitters LLC
"""
import asyncio
import time

from adafruit_datetime import datetime
from adafruit_httpserver import Server, Redirect
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

                # Redirect to base URL without query parameters
                # This ensures a clean URL and proper page state
                # response = Response(request, "", content_type="text/html", headers={"Location": "/"})
                # response.status_code = 302
                response = Redirect(request, "/")
                return response

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
                    return Redirect(request, "/")
                except Exception as e:
                    logger.error(e, f"Error processing settings query params: {query_params}")

            # Generate settings page
            # Generate settings page with success message if query params were processed
            if query_params:
                page = self.generate_settings_page(success=True)
            else:
                page = self.generate_settings_page()
            return Response(request, page, content_type="text/html")

        @self.server.route("/api/park", [GET])
        def api_park(request: Request):
            """API endpoint to get data for a specific park"""
            import json
            
            try:
                # Extract park ID from query parameters
                park_id = None
                if request.query_params and "id" in request.query_params:
                    park_id = int(request.query_params["id"])
                
                # If no park ID provided, use current park
                if not park_id and hasattr(self.app, 'theme_park_service'):
                    if (hasattr(self.app.theme_park_service, 'park_list') and
                        hasattr(self.app.theme_park_service.park_list, 'current_park')):
                        park_id = self.app.theme_park_service.park_list.current_park.id
                
                if not park_id:
                    error_json = json.dumps({"error": "No park ID provided and no current park set"})
                    response = Response(request, error_json, content_type="application/json")
                    response.status_code = 400
                    return response
                
                # Get park data
                park_data = {}
                
                if hasattr(self.app, 'theme_park_service'):
                    # Get park from park list
                    park = None
                    if hasattr(self.app.theme_park_service, 'park_list'):
                        park = self.app.theme_park_service.park_list.get_park_by_id(park_id)
                    
                    if park:
                        # Build park data response
                        rides = []
                        # If park has no rides, try to fetch them from the API
                        if not park.rides:
                            logger.info(f"Park {park.name} has no rides, attempting to fetch from API")
                            # Use asyncio to run the async method
                            if hasattr(self.app.theme_park_service, 'get_rides_for_park_async'):
                                import asyncio
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                                try:
                                    rides = loop.run_until_complete(self.app.theme_park_service.get_rides_for_park_async(park_id))
                                finally:
                                    loop.close()
                            else:
                                available_rides = self.app.theme_park_service.get_available_rides(park_id)
                                for ride_info in available_rides:
                                    rides.append(ride_info)
                        else:
                            for ride in park.rides:
                                rides.append({
                                    "name": ride.name,
                                    "wait_time": ride.wait_time,
                                    "is_open": ride.open_flag
                                })
                        
                        park_data = {
                            "id": park.id,
                            "name": park.name,
                            "is_open": park.is_open,
                            "rides": rides,
                            "latitude": park.latitude,
                            "longitude": park.longitude
                        }
                    else:
                        error_json = json.dumps({"error": f"Park with ID {park_id} not found"})
                        response = Response(request, error_json, content_type="application/json")
                        response.status_code = 404
                        return response
                else:
                    error_json = json.dumps({"error": "Theme park service not available"})
                    response = Response(request, error_json, content_type="application/json")
                    response.status_code = 500
                    return response
                
                # Return JSON response
                response_json = json.dumps(park_data)
                return Response(request, response_json, content_type="application/json")
                
            except Exception as e:
                logger.error(e, f"Error in park API endpoint")
                error_json = json.dumps({"error": "Failed to get park data"})
                response = Response(request, error_json, content_type="application/json")
                response.status_code = 500
                return response

    def start(self, ip_address):
        """
        Start the web server with improved reliability
        
        Args:
            ip_address: The IP address to bind to
        """
        try:
            # Make sure to convert IP to string and specify port 80
            logger.debug(f"Starting server on {ip_address}:80")

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
                        # Reset selected ride when park changes
                        self.app.settings_manager.settings["selected_ride_name"] = ""
                        
                        # Fetch ride data for the newly selected park
                        # Set flag to trigger update in the main loop
                        if hasattr(self.app.theme_park_service, 'update_needed'):
                            self.app.theme_park_service.update_needed = True
                        else:
                            # Add the attribute if it doesn't exist
                            self.app.theme_park_service.update_needed = True
                        logger.info(f"Park changed to {new_park_id}, triggering data update")
            except Exception as e:
                logger.error(e, "Error updating park selection")
        
        # Process display mode parameter
        settings_changed = False
        import re
        display_mode_match = re.search(r'display_mode=([^&]+)', query_params)
        if display_mode_match:
            old_display_mode = self.app.settings_manager.settings.get("display_mode", "all_rides")
            new_display_mode = display_mode_match.group(1)
            
            if old_display_mode != new_display_mode:
                self.app.settings_manager.settings["display_mode"] = new_display_mode
                settings_changed = True
                logger.info(f"Display mode changed to: {new_display_mode}")
        
        # Process selected ride name
        selected_ride_match = re.search(r'selected_ride_name=([^&]+)', query_params)
        if selected_ride_match:
            old_selected_ride = self.app.settings_manager.settings.get("selected_ride_name", "")
            new_selected_ride = self._url_decode(selected_ride_match.group(1))
            
            if old_selected_ride != new_selected_ride:
                self.app.settings_manager.settings["selected_ride_name"] = new_selected_ride
                settings_changed = True
                logger.info(f"Selected ride changed to: {new_selected_ride}")

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
            # When park changes, we need to ensure the new park's data is fetched
            # Set the update timer to expire immediately
            if hasattr(self.app, 'update_timer'):
                self.app.update_timer.reset(expired=True)
                logger.info("Forced immediate park data update after park change")
                
        if settings_changed and hasattr(self.app, 'message_queue'):
            self.app.display.set_colors(self.app.settings_manager)
            logger.debug("Reset message queue after display mode/ride change")

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
            
            # In CircuitPython, we can't test if port is in use with socket module
            # Just wait to ensure previous connections are closed
            logger.debug("Waiting for port to be released before restart")
            await asyncio.sleep(2)  # Wait for connections to close
                
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
        # Add gear icon using image for better sizing control
        page += "<div class=\"gear-icon\">"
        page += "<a href=\"/settings\"><img src=\"gear.png\" alt=\"Settings\"></a>"
        page += "</div>"
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

            # Display Mode Selection
            page += "<div class=\"form-group\">"
            # page += "<h3 style=\"margin-top: 0; margin-bottom: 10px; text-align: left; padding-left: 20px;\">Display Mode</h3>"
            
            display_mode = settings.get("display_mode", "all_rides")
            
            # All Rides option
            all_rides_checked = "checked" if display_mode == "all_rides" else ""
            page += f"<div class=\"radio-group\"><input type=\"radio\" id=\"all_rides\" name=\"display_mode\" value=\"all_rides\" {all_rides_checked}>"
            page += "<label for=\"all_rides\">Show All Rides</label></div>"
            
            # Single Ride option - disabled until a park is selected
            single_ride_checked = "checked" if display_mode == "single_ride" else ""
            # Check if we have a current park selected
            has_current_park = "current_park" in response_data and response_data["current_park"]
            disabled_attr = "" if has_current_park else "disabled"
            page += f"<div class=\"radio-group\"><input type=\"radio\" id=\"single_ride\" name=\"display_mode\" value=\"single_ride\" {single_ride_checked} {disabled_attr}>"
            page += "<label for=\"single_ride\">Show Single Ride"
            if not has_current_park:
                page += " (select a park first)"
            page += "</label></div>"
            
            # Ride Selection Dropdown
            selected_ride = settings.get("selected_ride_name", "")
            ride_selector_style = "display: " + ("block" if display_mode == "single_ride" else "none")
            
            page += f"<div id=\"ride-selector\" style=\"{ride_selector_style}; margin-top: 10px; margin-bottom: 15px;\">"
            page += "<label for=\"selected_ride_name\">Select Ride:</label>"
            page += "<select name=\"selected_ride_name\" id=\"selected_ride_name\">"
            
            # Get available rides for the current park
            current_park_rides = []
            try:
                if hasattr(self.app, 'theme_park_service') and current_park_id:
                    # Get rides for the specific park
                    if hasattr(self.app.theme_park_service, 'get_available_rides'):
                        current_park_rides = self.app.theme_park_service.get_available_rides(current_park_id)
                    elif hasattr(self.app.theme_park_service, 'park_list'):
                        # Fallback: get rides from park object
                        park = self.app.theme_park_service.park_list.get_park_by_id(current_park_id)
                        if park and hasattr(park, 'rides'):
                            current_park_rides = park.rides
            except Exception as e:
                logger.error(e, "Error getting rides for selector")
            
            # Add rides to dropdown
            if current_park_rides:
                for ride in current_park_rides:
                    ride_name = ride.get("name", "")
                    is_selected = "selected" if ride_name == selected_ride else ""
                    page += f"<option value=\"{ride_name}\" {is_selected}>{ride_name}</option>"
            else:
                page += "<option value=\"\">No rides available</option>"
                
            page += "</select>"
            page += "</div>"
            
            # Add JavaScript for toggling ride selector and updating rides when park changes
            page += """
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    var radios = document.querySelectorAll('input[name="display_mode"]');
                    var rideSelector = document.getElementById('ride-selector');
                    var parkSelect = document.getElementById('park-select');
                    var rideSelect = document.getElementById('selected_ride_name');
                    var singleRideRadio = document.getElementById('single_ride');
                    var singleRideLabel = singleRideRadio.nextElementSibling;
                    
                    // Toggle ride selector visibility
                    radios.forEach(function(radio) {
                        radio.addEventListener('change', function() {
                            rideSelector.style.display = (radio.value === 'single_ride') ? 'block' : 'none';
                        });
                    });
                    
                    // Fetch rides when park changes
                    parkSelect.addEventListener('change', function() {
                        var parkId = parkSelect.value;
                        
                        if (!parkId) {
                            // No park selected
                            singleRideRadio.disabled = true;
                            singleRideLabel.textContent = 'Show Single Ride (select a park first)';
                            return;
                        }
                        
                        // Clear and disable ride selector, show updating message
                        rideSelect.innerHTML = '<option value="">Updating...</option>';
                        rideSelect.disabled = true;
                        
                        // Disable Single Ride option temporarily
                        singleRideRadio.disabled = true;
                        singleRideLabel.textContent = 'Show Single Ride (loading rides...)';
                        
                        // If Single Ride was selected, keep it selected but show loading
                        if (singleRideRadio.checked) {
                            rideSelector.style.display = 'block';
                        }
                        
                        // Fetch park data asynchronously
                        fetch('/api/park?id=' + parkId)
                            .then(function(response) {
                                if (!response.ok) {
                                    throw new Error('Failed to fetch park data');
                                }
                                return response.json();
                            })
                            .then(function(data) {
                                // Clear the ride selector
                                rideSelect.innerHTML = '';
                                
                                if (data.rides && data.rides.length > 0) {
                                    // Add rides to dropdown
                                    data.rides.forEach(function(ride) {
                                        var option = document.createElement('option');
                                        option.value = ride.name;
                                        option.textContent = ride.name;
                                        rideSelect.appendChild(option);
                                    });
                                    
                                    // Enable the ride selector and Single Ride option
                                    rideSelect.disabled = false;
                                    singleRideRadio.disabled = false;
                                    singleRideLabel.textContent = 'Show Single Ride';
                                } else {
                                    // No rides available
                                    rideSelect.innerHTML = '<option value="">No rides available</option>';
                                    singleRideRadio.disabled = true;
                                    singleRideLabel.textContent = 'Show Single Ride (no rides available)';
                                    
                                    // If Single Ride was selected, switch to All Rides
                                    if (singleRideRadio.checked) {
                                        document.getElementById('all_rides').checked = true;
                                        rideSelector.style.display = 'none';
                                    }
                                }
                            })
                            .catch(function(error) {
                                console.error('Error fetching park data:', error);
                                rideSelect.innerHTML = '<option value="">Error loading rides</option>';
                                singleRideRadio.disabled = true;
                                singleRideLabel.textContent = 'Show Single Ride (error loading rides)';
                                
                                // If Single Ride was selected, switch to All Rides
                                if (singleRideRadio.checked) {
                                    document.getElementById('all_rides').checked = true;
                                    rideSelector.style.display = 'none';
                                }
                            });
                    });
                });
            </script>
            """
            
            page += "</div>"
            
            # Skip Rides Section
            page += "<div class=\"display-options\">"
            # page += "<h3 style=\"margin-top: 10px; margin-bottom: 10px; text-align: left; padding-left: 20px;\">Display Options</h3>"
            
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
        # Add gear icon using image for consistent styling with main page
        page += "<div class=\"gear-icon\">"
        page += "<a href=\"/settings\"><img src=\"gear.png\" alt=\"Settings\"></a>"
        page += "</div>"
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

