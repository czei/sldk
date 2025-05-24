"""
Development web server implementation for the ThemeParkAPI.
Provides a local web server when running in development mode.
Copyright 2024 3DUPFitters LLC
"""
import asyncio
import json
import re
import os
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import threading

from src.utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")

class DevThemeParkWebHandler(BaseHTTPRequestHandler):
    """Handler for dev mode web server requests"""
    
    # Class attribute to store app instance
    app_instance = None
    
    def log_message(self, format, *args):
        """Override to use our logger instead of stderr"""
        logger.info(f"Web: {format % args}")
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            # Parse URL path and query string
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            
            # Convert query_params to string format expected by existing code
            query_string = "&".join([f"{k}={v[0]}" for k, v in query_params.items()])
            
            # Log request details
            logger.debug(f"GET request: {path} with params: {query_string}")
            
            # Handle static files
            if path.endswith(".css"):
                self.serve_static_file(path, "text/css")
                return
            elif path.endswith(".png") or path.endswith(".jpg"):
                self.serve_static_file(path, "image/png" if path.endswith(".png") else "image/jpeg")
                return
            elif path.endswith(".html"):
                self.serve_static_file(path, "text/html")
                return
            
            # Handle application routes
            if path == "/" or path == "/index.html":
                self.serve_main_page(query_params, query_string)
            elif path == "/settings":
                self.serve_settings_page(query_params, query_string)
            elif path == "/api/park":
                self.serve_api_park(query_params)
            elif path == "/api/parks":
                self.serve_api_parks(query_params)
            elif path == "/api/rides":
                self.serve_api_rides(query_params)
            else:
                # Try to serve it as a static file
                success = self.serve_static_file(path, "text/html")
                if not success:
                    # File not found, return 404
                    self.send_response(404)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"404 - Not Found")
                
        except Exception as e:
            logger.error(e, f"Error handling request: {self.path}")
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def serve_static_file(self, path, content_type):
        """Serve a static file from the www directory"""
        # Strip leading slash
        if path.startswith('/'):
            path = path[1:]
            
        # Look for file in multiple locations
        search_paths = [
            os.path.join("src", "www", path),
            os.path.join("www", path)
        ]
        
        for file_path in search_paths:
            if os.path.exists(file_path) and os.path.isfile(file_path):
                try:
                    with open(file_path, "rb") as f:
                        content = f.read()
                    
                    self.send_response(200)
                    self.send_header("Content-type", content_type)
                    self.end_headers()
                    self.wfile.write(content)
                    return True
                except Exception as e:
                    logger.error(e, f"Error serving static file: {file_path}")
                    
        return False
    
    def serve_main_page(self, query_params, query_string):
        """Serve the main page"""
        if query_params and self.app_instance:
            # Process query parameters
            try:
                self._process_query_params(query_string)
            except Exception as e:
                logger.error(e, f"Error processing query params: {query_string}")
            
            # Redirect to base URL without query parameters
            # This ensures a clean URL and proper page state
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
            return
        
        # Generate and serve the main page
        page = self.generate_main_page()
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(page.encode("utf-8"))
    
    def serve_settings_page(self, query_params, query_string):
        """Serve the settings page"""
        success = False
        
        if query_params and self.app_instance:
            # Process query parameters
            try:
                self._process_query_params(query_string)
                success = True
                # Redirect to /settings without query parameters
                self.send_response(302)
                self.send_header("Location", "/settings")
                self.end_headers()
                return
            except Exception as e:
                logger.error(e, f"Error processing settings params: {query_string}")
        
        # Generate and serve the settings page
        page = self.generate_settings_page(success)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(page.encode("utf-8"))
    
    def _process_query_params(self, query_params):
        """Process query parameters using the app instance's theme park service"""
        if not query_params or not self.app_instance or not hasattr(self.app_instance, 'theme_park_service'):
            return False
        
        app = self.app_instance
        park_changed = False
        settings_changed = False
        
        # Parse park-id-1 through park-id-4 parameters
        park_ids = []
        for i in range(1, 5):
            park_param = f"park-id-{i}="
            if park_param in query_params:
                try:
                    # Extract park ID value
                    match = re.search(f'park-id-{i}=([^&]+)', query_params)
                    if match:
                        park_id = int(match.group(1))
                        if park_id > 0:  # Only add valid park IDs
                            park_ids.append(park_id)
                except (ValueError, TypeError):
                    pass
        
        # Check if parks changed
        if park_ids or "park-id-" in query_params:
            try:
                # Get current selected parks
                current_park_ids = []
                if (hasattr(app.theme_park_service, 'park_list') and
                        hasattr(app.theme_park_service.park_list, 'selected_parks')):
                    current_park_ids = [p.id for p in app.theme_park_service.park_list.selected_parks]
                
                # Update selected parks
                if hasattr(app.theme_park_service, 'park_list'):
                    # Clear existing selections
                    app.theme_park_service.park_list.selected_parks = []
                    
                    # Add new selections
                    for park_id in park_ids:
                        park = app.theme_park_service.park_list.get_park_by_id(park_id)
                        if park:
                            app.theme_park_service.park_list.selected_parks.append(park)
                    
                    # Check if parks changed
                    new_park_ids = [p.id for p in app.theme_park_service.park_list.selected_parks]
                    park_changed = (sorted(current_park_ids) != sorted(new_park_ids))
                    
                    if park_changed:
                        logger.info(f"Parks changed from {current_park_ids} to {new_park_ids}")
                        
                        settings_changed = True
                        
                        # Set update needed flag
                        if hasattr(app.theme_park_service, 'update_needed'):
                            app.theme_park_service.update_needed = True
                        else:
                            app.theme_park_service.update_needed = True
                        
                        # Fetch ride data for newly selected parks
                        if hasattr(app.theme_park_service, 'update_selected_parks'):
                            import asyncio
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                loop.run_until_complete(app.theme_park_service.update_selected_parks())
                                logger.info(f"Fetched ride data for parks {new_park_ids}")
                            except Exception as e:
                                logger.error(e, f"Error fetching ride data for parks {new_park_ids}")
                            finally:
                                loop.close()
            except Exception as e:
                logger.error(e, "Error updating park selection")
        
        # Handle checkboxes
        if hasattr(app.theme_park_service, 'park_list'):
            # Skip closed rides
            skip_closed = "skip_closed=on" in query_params
            app.theme_park_service.park_list.skip_closed = skip_closed
            
            # Skip meet & greets
            skip_meet = "skip_meet=on" in query_params
            app.theme_park_service.park_list.skip_meet = skip_meet
        
        # Always use all_rides display mode (single ride functionality removed)
        app.settings_manager.settings["display_mode"] = "all_rides"
        
        # Process vacation parameters
        if "Year=" in query_params and hasattr(app.theme_park_service, 'vacation'):
            try:
                app.theme_park_service.vacation.parse(query_params)
            except Exception as e:
                logger.error(e, "Error updating vacation settings")
        
        # Process domain name
        if "domain_name=" in query_params:
            try:
                domain_match = re.search(r'domain_name=([^&]+)', query_params)
                if domain_match:
                    domain_name = domain_match.group(1)
                    app.settings_manager.settings["domain_name"] = domain_name
            except Exception as e:
                logger.error(e, "Error updating domain name")
        
        # Process brightness
        brightness_match = re.search(r'brightness_scale=([^&]+)', query_params)
        if brightness_match:
            brightness = brightness_match.group(1)
            app.settings_manager.settings["brightness_scale"] = brightness
        
        # Process scroll speed
        scroll_match = re.search(r'scroll_speed=([^&]+)', query_params)
        if scroll_match:
            scroll_speed = scroll_match.group(1)
            app.settings_manager.settings["scroll_speed"] = scroll_speed
        
        # Process color parameters
        self._process_color_params(query_params)
        
        # Save settings
        try:
            app.settings_manager.save_settings()
            
            # Update display colors if needed
            if hasattr(app, 'display') and hasattr(app.display, 'set_colors'):
                app.display.set_colors(app.settings_manager)
        except Exception as e:
            logger.error(e, "Error saving settings")
        
        # Trigger park update if needed
        if (park_changed or settings_changed) and hasattr(app, 'theme_park_service'):
            app.theme_park_service.update_needed = True
        
        return park_changed or settings_changed
    
    def _process_color_params(self, query_params):
        """Process color parameters from query string"""
        app = self.app_instance
        color_params = ["default_color", "ride_name_color", "ride_wait_time_color"]
        
        for color_param in color_params:
            try:
                color_pattern = f'{color_param}=([^&]+)'
                match = re.search(color_pattern, query_params)
                if match:
                    color_value = match.group(1)
                    app.settings_manager.set(color_param, color_value)
            except Exception as e:
                logger.error(e, f"Error updating {color_param}")
    
    def generate_main_page(self):
        """Generate the main HTML page"""
        # Use list for efficient string building
        page_parts = []
        
        # Pre-build static header
        page_parts.extend([
            "<!DOCTYPE html><html><head>",
            "<title>Theme Park Waits (Dev)</title>",
            "<link rel=\"stylesheet\" href=\"/style.css\">",
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
            "</head>",
            "<body>",
            "<div class=\"navbar\">",
            "<a href=\"/\">Theme Park Wait Times (Development Mode)</a>",
            "<div class=\"gear-icon\">",
            "<a href=\"/settings\"><img src=\"gear.png\" alt=\"Settings\"></a>",
            "</div>",
            "</div>",
            "<div class=\"main-content\">",
            "<h2>Theme Park Selection</h2>"
        ])
        
        app = self.app_instance
        parks = []
        selected_park_ids = []
        settings = {}
        
        # Get parks list
        try:
            if (hasattr(app, 'theme_park_service') and 
                app.theme_park_service and 
                hasattr(app.theme_park_service, 'park_list') and
                app.theme_park_service.park_list):
                
                # Get parks
                if hasattr(app.theme_park_service.park_list, 'park_list'):
                    for park in app.theme_park_service.park_list.park_list:
                        if hasattr(park, 'id') and hasattr(park, 'name'):
                            parks.append({"id": park.id, "name": park.name})
                
                # Get selected parks
                if hasattr(app.theme_park_service.park_list, 'selected_parks'):
                    selected_park_ids = [p.id for p in app.theme_park_service.park_list.selected_parks]
                
                # Get settings
                if hasattr(app, 'settings_manager') and hasattr(app.settings_manager, 'settings'):
                    settings = app.settings_manager.settings
        except Exception as e:
            logger.error(e, "Error getting app data")
        
        # Create the park selection form
        page_parts.append("<form action=\"/\" method=\"get\">")
        
        # Create 4 park dropdowns
        page_parts.append("<div class=\"park-selection\">")
        page_parts.append("<h3>Select Parks (up to 4)</h3>")
        
        for i in range(1, 5):  # 1 through 4
            page_parts.append(f"<div class=\"park-dropdown\">")
            page_parts.append(f"<label for=\"park-id-{i}\">Park {i}:</label>")
            page_parts.append(f"<select name=\"park-id-{i}\" id=\"park-select-{i}\">")
            
            # Default option
            page_parts.append(f"<option value=\"0\">Select Park {i}</option>")
            
            if not parks:
                page_parts.append("<option value=\"0\">No parks available - check connection</option>")
            else:
                # Get the park ID for this position
                current_selection = selected_park_ids[i-1] if i <= len(selected_park_ids) else None
                
                for park in parks:
                    park_id = park.get("id", "")
                    park_name = park.get("name", "Unknown Park")
                    selected = "selected" if park_id == current_selection else ""
                    page_parts.append(f"<option value=\"{park_id}\" {selected}>{park_name}</option>")
            
            page_parts.append("</select>")
            page_parts.append("</div>")
        
        page_parts.append("</div>")
        
        # Create options div
        page_parts.append("<div class=\"options\">")
        page_parts.append("<h3 style=\"margin-top: 0; margin-bottom: 10px; text-align: left; padding-left: 20px;\">Display Options</h3>")
        
        # Display Mode - Always show all rides (single ride functionality removed)
        page_parts.append("<div class=\"form-group\">")
        page_parts.append("<input type=\"hidden\" name=\"display_mode\" value=\"all_rides\">")
        
        
        
        page_parts.append("</div>")
        
        # Skip Closed Rides option
        page_parts.append("<div class=\"display-options\">")
        # page += "<h3 style=\"margin-top: 10px; margin-bottom: 10px; text-align: left; padding-left: 20px;\">Display Options</h3>"
        
        page_parts.append("<div class=\"form-group checkbox-group\">")
        # Get skip_closed value from park_list with safe fallback
        skip_closed = False
        try:
            if hasattr(app.theme_park_service, 'park_list') and hasattr(app.theme_park_service.park_list, 'skip_closed'):
                skip_closed = bool(app.theme_park_service.park_list.skip_closed)
            else:
                skip_closed = bool(settings.get("skip_closed", False))
        except (TypeError, ValueError, AttributeError):
            skip_closed = False
        
        checked = "checked" if skip_closed else ""
        page_parts.append(f"<input type=\"checkbox\" id=\"skip_closed\" name=\"skip_closed\" {checked}>")
        page_parts.append("<label for=\"skip_closed\">Skip Closed Rides</label>")
        page_parts.append("</div>")
        
        # Skip Meet & Greets option
        page_parts.append("<div class=\"form-group checkbox-group\">")
        # Get skip_meet value from park_list with safe fallback
        skip_meet = False
        try:
            if hasattr(app.theme_park_service, 'park_list') and hasattr(app.theme_park_service.park_list, 'skip_meet'):
                skip_meet = bool(app.theme_park_service.park_list.skip_meet)
            else:
                skip_meet = bool(settings.get("skip_meet", False))
        except (TypeError, ValueError, AttributeError):
            skip_meet = False
        
        checked = "checked" if skip_meet else ""
        page_parts.append(f"<input type=\"checkbox\" id=\"skip_meet\" name=\"skip_meet\" {checked}>")
        page_parts.append("<label for=\"skip_meet\">Skip Meet & Greets</label>")
        page_parts.append("</div>")
        page_parts.append("</div>")
        
        page_parts.append("</div>")
        
        # Vacation date configuration
        vacation_date = None
        try:
            if hasattr(app, 'theme_park_service') and hasattr(app.theme_park_service, 'vacation'):
                vacation_date = app.theme_park_service.vacation
        except Exception as e:
            logger.error(e, "Error getting vacation data")
        
        if vacation_date:
            page_parts.append("<h2>Configure Countdown</h2>")
            page_parts.append("<div class=\"countdown-section\">")
            page_parts.append("<p>")
            page_parts.append("<label for=\"Name\">Event:</label>")
            page_parts.append(f"<input type=\"text\" name=\"Name\" value=\"{vacation_date.name}\">")
            page_parts.append("</p>")
            
            page_parts.append("<p>")
            page_parts.append("<label for=\"Date\">Date:</label>")
            page_parts.append("<div class=\"date-selectors\">")
            
            # Year dropdown
            page_parts.append("<select id=\"Year\" name=\"Year\">")
            from datetime import datetime
            year_now = datetime.now().year
            for year in range(year_now, 2044):
                if vacation_date.is_set() is True and year == vacation_date.year:
                    page_parts.append(f"<option value=\"{year}\" selected>{year}</option>\n")
                else:
                    page_parts.append(f"<option value=\"{year}\">{year}</option>\n")
            page_parts.append("</select>")
            
            # Month dropdown
            month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            page_parts.append("<select id=\"Month\" name=\"Month\">")
            for month in range(1, 13):
                if vacation_date.is_set() is True and month == vacation_date.month:
                    page_parts.append(f"<option value=\"{month}\" selected>{month_names[month-1]}</option>\n")
                else:
                    page_parts.append(f"<option value=\"{month}\">{month_names[month-1]}</option>\n")
            page_parts.append("</select>")
            
            # Day dropdown
            page_parts.append("<select id=\"Day\" name=\"Day\">")
            for day in range(1, 32):
                if vacation_date.is_set() is True and day == vacation_date.day:
                    page_parts.append(f"<option value=\"{day}\" selected>{day}</option>\n")
                else:
                    page_parts.append(f"<option value=\"{day}\">{day}</option>\n")
            page_parts.append("</select>")
            page_parts.append("</div>")
            page_parts.append("</p>")
            
            # Show countdown if vacation is set
            if vacation_date.is_set():
                days_until = vacation_date.get_days_until()
                if days_until > 0:
                    page_parts.append(f"<p style=\"text-align: center; font-weight: bold; margin-top: 10px;\">")
                    page_parts.append(f"Days until {vacation_date.name}: {days_until}")
                    page_parts.append("</p>")
            
            page_parts.append("</div>")
        
        page_parts.append("<button type=\"submit\">Update</button>")
        page_parts.append("</form>")
        
        page_parts.append("</div></body></html>")
        return ''.join(page_parts)
    
    def serve_api_park(self, query_params):
        """API endpoint to get data for a specific park"""
        import json
        
        try:
            # Extract park ID from query parameters
            park_id = None
            if "id" in query_params:
                park_id = int(query_params["id"][0])
            
            app = self.app_instance
            
            # If no park ID provided, use current park
            if not park_id and hasattr(app, 'theme_park_service'):
                if (hasattr(app.theme_park_service, 'park_list') and
                    hasattr(app.theme_park_service.park_list, 'current_park')):
                    park_id = app.theme_park_service.park_list.current_park.id
            
            if not park_id:
                error_json = json.dumps({"error": "No park ID provided and no current park set"})
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(error_json.encode("utf-8"))
                return
            
            # Get park data
            park_data = {}
            
            if hasattr(app, 'theme_park_service'):
                # Get park from park list
                park = None
                if hasattr(app.theme_park_service, 'park_list'):
                    park = app.theme_park_service.park_list.get_park_by_id(park_id)
                
                if park:
                    # Build park data response
                    rides = []
                    # If park has no rides, try to fetch them from the API
                    if not park.rides:
                        logger.info(f"Park {park.name} has no rides, attempting to fetch from API")
                        # Use asyncio to run the async method
                        if hasattr(app.theme_park_service, 'get_rides_for_park_async'):
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                rides = loop.run_until_complete(app.theme_park_service.get_rides_for_park_async(park_id))
                            finally:
                                loop.close()
                        else:
                            available_rides = app.theme_park_service.get_available_rides(park_id)
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
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(error_json.encode("utf-8"))
                    return
            else:
                error_json = json.dumps({"error": "Theme park service not available"})
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(error_json.encode("utf-8"))
                return
            
            # Return JSON response
            response_json = json.dumps(park_data)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(response_json.encode("utf-8"))
            
        except Exception as e:
            logger.error(e, f"Error in park API endpoint")
            error_json = json.dumps({"error": "Failed to get park data"})
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(error_json.encode("utf-8"))
    
    def serve_api_parks(self, query_params):
        """API endpoint to get list of parks"""
        # Implementation not needed for this fix
        pass
    
    def serve_api_rides(self, query_params):
        """API endpoint to get rides"""
        # Implementation not needed for this fix
        pass
    
    def generate_settings_page(self, success=False):
        """Generate the settings HTML page"""
        app = self.app_instance
        settings = {}
        
        try:
            if hasattr(app, 'settings_manager') and hasattr(app.settings_manager, 'settings'):
                settings = app.settings_manager.settings
        except Exception as e:
            logger.error(e, "Error getting settings")
        
        page = "<!DOCTYPE html><html><head>"
        page += "<title>Settings - Theme Park Waits (Dev)</title>"
        page += "<link rel=\"stylesheet\" href=\"/style.css\">"
        page += "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        page += "</head>"
        page += "<body>"
        
        page += "<div class=\"navbar\">"
        page += "<a href=\"/\">Theme Park Wait Times (Development Mode)</a>"
        page += "<div class=\"gear-icon\">"
        page += "<a href=\"/settings\"><img src=\"gear.png\" alt=\"Settings\"></a>"
        page += "</div>"
        page += "</div>"
        
        page += "<div class=\"main-content\">"
        page += "<h2>Settings</h2>"
        
        # Show success message
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
        page += "<label for=\"domain_name\">Hostname:</label>"
        domain_name = settings.get("domain_name", "themeparkwaits")
        page += f"<input type=\"text\" id=\"domain_name\" name=\"domain_name\" value=\"{domain_name}\">"
        page += "<label for=\"domain_name\">.local</label>"
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
        
        # Import color utilities
        from src.utils.color_utils import ColorUtils
        
        for color_setting_name, color_value in settings.items():
            if "color" in color_setting_name:
                page += "<p>"
                pretty_name = color_setting_name.replace("_", " ").title()
                if hasattr(app.settings_manager, 'get_pretty_name'):
                    pretty_name = app.settings_manager.get_pretty_name(color_setting_name)
                page += f"<label for=\"{color_setting_name}\">{pretty_name}</label>"
                page += ColorUtils.html_color_chooser(color_setting_name, hex_num_str=color_value)
                page += "</p>"
        
        page += "</div>"
        
        page += "<button type=\"submit\">Save Settings</button>"
        page += "</form>"
        
        page += "</div></body></html>"
        return page


class DevThemeParkWebServer:
    """Development web server implementation for ThemeParkAPI"""
    
    def __init__(self, app_instance):
        """
        Initialize the development web server
        
        Args:
            app_instance: The ThemeParkApp instance to interact with
        """
        self.app = app_instance
        self.server = None
        self.is_running = False
        self.server_thread = None
        self.port = 8080  # Use a standard development port
        
        # Set the app instance as a class attribute for the handler
        DevThemeParkWebHandler.app_instance = app_instance
    
    def start(self, ip_address=None):
        """
        Start the web server on a separate thread
        
        Args:
            ip_address: Optional IP address to bind to (ignored in dev mode, always uses localhost)
        """
        if self.is_running:
            logger.info("Server already running, skipping start")
            return True
        
        try:
            logger.info(f"Attempting to start dev server on localhost:{self.port}")
            
            # Create the server on localhost
            self.server = HTTPServer(('localhost', self.port), DevThemeParkWebHandler)
            logger.info("HTTPServer instance created")
            
            # Start server in a separate thread
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True  # Allow the thread to exit when the program does
            self.server_thread.start()
            logger.info("Server thread started")
            
            # Give server time to start
            time.sleep(0.5)
            
            # Verify server is running
            try:
                import socket
                test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_sock.settimeout(1)
                result = test_sock.connect_ex(('localhost', self.port))
                test_sock.close()
                
                if result == 0:
                    logger.info(f"Server verified accessible at localhost:{self.port}")
                else:
                    logger.info(f"Warning: Server started but not accessible, result: {result}")
            except Exception as verify_error:
                logger.error(verify_error, "Error verifying server")
            
            self.is_running = True
            logger.info(f"Development web server started at http://localhost:{self.port}")
            
            return True
        except Exception as e:
            logger.error(e, "Failed to start development web server")
            self.is_running = False
            return False
    
    def stop(self):
        """Stop the web server"""
        if not self.is_running:
            return
        
        try:
            # Stop the server
            if self.server:
                self.server.shutdown()
                self.server.server_close()
            
            # Wait for the thread to terminate
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=1.0)
            
            self.is_running = False
            logger.info("Development web server stopped")
        except Exception as e:
            logger.error(e, "Error stopping development web server")
        finally:
            self.is_running = False
    
    async def poll(self):
        """
        Simulate polling for the development server (not needed as it runs in its own thread)
        
        Returns:
            False since no polling is needed
        """
        # No polling needed for the threaded server
        await asyncio.sleep(0.1)
        return False