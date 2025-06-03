"""Server adapters for different platforms (CircuitPython and Development).

Provides a common interface while handling platform-specific HTTP server implementations.
Extracted from Theme Park API for SLDK web framework.
"""

import sys

try:
    import asyncio
except ImportError:
    # CircuitPython
    import asyncio

# Platform detection
IS_CIRCUITPYTHON = hasattr(sys, 'implementation') and sys.implementation.name == 'circuitpython'


class ServerAdapter:
    """Base class for server adapters.
    
    Note: Using duck typing instead of ABC since CircuitPython doesn't have abc module.
    """
    
    def start_server(self, host, port):
        """Start the HTTP server.
        
        Args:
            host: Host address to bind to
            port: Port number to bind to
            
        Returns:
            bool: True if started successfully
        """
        raise NotImplementedError("Subclass must implement start_server()")
    
    def stop_server(self):
        """Stop the HTTP server."""
        raise NotImplementedError("Subclass must implement stop_server()")
    
    def parse_query_params(self, query_string):
        """Parse query parameters from URL.
        
        Args:
            query_string: Raw query string
            
        Returns:
            dict: Parsed parameters
        """
        raise NotImplementedError("Subclass must implement parse_query_params()")
    
    def parse_form_data(self, request_body):
        """Parse form data from POST request.
        
        Args:
            request_body: Raw request body
            
        Returns:
            dict: Parsed form data
        """
        raise NotImplementedError("Subclass must implement parse_form_data()")
    
    def url_decode(self, text):
        """Decode URL-encoded text (CircuitPython compatible).
        
        Args:
            text: URL-encoded text
            
        Returns:
            str: Decoded text
        """
        if not text:
            return text
            
        # Replace common encodings
        text = text.replace('%20', ' ')
        text = text.replace('%21', '!')
        text = text.replace('%22', '"')
        text = text.replace('%23', '#')
        text = text.replace('%24', '$')
        text = text.replace('%25', '%')
        text = text.replace('%26', '&')
        text = text.replace('%27', "'")
        text = text.replace('%28', '(')
        text = text.replace('%29', ')')
        text = text.replace('%2A', '*')
        text = text.replace('%2B', '+')
        text = text.replace('%2C', ',')
        text = text.replace('%2D', '-')
        text = text.replace('%2E', '.')
        text = text.replace('%2F', '/')
        text = text.replace('%3A', ':')
        text = text.replace('%3B', ';')
        text = text.replace('%3C', '<')
        text = text.replace('%3D', '=')
        text = text.replace('%3E', '>')
        text = text.replace('%3F', '?')
        text = text.replace('%40', '@')
        text = text.replace('+', ' ')  # Plus signs become spaces
        
        return text


if IS_CIRCUITPYTHON:
    class CircuitPythonAdapter(ServerAdapter):
        """Server adapter for CircuitPython using adafruit_httpserver."""
        
        def __init__(self, handler_class, socket_pool=None, static_dir="/www"):
            """Initialize CircuitPython adapter.
            
            Args:
                handler_class: Handler class with route methods
                socket_pool: Socket pool for networking
                static_dir: Directory for static files
            """
            self.handler_class = handler_class
            self.socket_pool = socket_pool
            self.static_dir = static_dir
            self.server = None
            self._running = False
            
        def start_server(self, host="0.0.0.0", port=80):
            """Start the CircuitPython HTTP server."""
            try:
                from adafruit_httpserver import HTTPServer, HTTPRoute, HTTPResponse
                
                if not self.socket_pool:
                    print("Error: Socket pool required for CircuitPython adapter")
                    return False
                
                # Create server
                self.server = HTTPServer(self.socket_pool, self.static_dir)
                
                # Set up routes from handler
                self._setup_routes()
                
                # Start server
                self.server.start(host, port)
                self._running = True
                print(f"CircuitPython web server started on {host}:{port}")
                
                return True
                
            except Exception as e:
                print(f"Failed to start CircuitPython web server: {e}")
                return False
        
        def stop_server(self):
            """Stop the CircuitPython HTTP server."""
            if self.server:
                try:
                    self.server.stop()
                    self._running = False
                    print("CircuitPython web server stopped")
                except Exception as e:
                    print(f"Error stopping CircuitPython web server: {e}")
        
        @property
        def is_running(self):
            """Check if server is running."""
            return self._running
        
        async def handle_requests(self):
            """Handle incoming requests (CircuitPython)."""
            if self.server:
                # CircuitPython's HTTPServer handles requests automatically
                # This is just a placeholder for the async interface
                await asyncio.sleep(0.1)
        
        def _setup_routes(self):
            """Set up HTTP routes from handler class."""
            from adafruit_httpserver import HTTPRoute, HTTPResponse
            
            handler = self.handler_class(self)
            
            # Get all route methods from handler
            for attr_name in dir(handler):
                if attr_name.startswith('route_'):
                    method = getattr(handler, attr_name)
                    if callable(method) and hasattr(method, '_route_info'):
                        route_info = method._route_info
                        path = route_info['path']
                        methods = route_info.get('methods', ['GET'])
                        
                        # Create route for each HTTP method
                        for http_method in methods:
                            @self.server.route(path, methods=[http_method])
                            def route_handler(request, method=method):
                                return method(request)
        
        def parse_query_params(self, query_string):
            """Parse query parameters from URL."""
            params = {}
            if not query_string:
                return params
                
            try:
                for pair in query_string.split('&'):
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        # URL decode
                        key = self.url_decode(key)
                        value = self.url_decode(value)
                        params[key] = value
            except Exception as e:
                print(f"Error parsing query parameters: {e}")
                
            return params
        
        def parse_form_data(self, request_body):
            """Parse form data from POST request."""
            if not request_body:
                return {}
                
            # Convert bytes to string if needed
            if isinstance(request_body, bytes):
                try:
                    request_body = request_body.decode('utf-8')
                except UnicodeDecodeError:
                    print("Failed to decode form data")
                    return {}
            
            return self.parse_query_params(request_body)

else:
    import threading
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import parse_qs, urlparse
    
    class DevelopmentAdapter(ServerAdapter):
        """Server adapter for development using Python's http.server."""
        
        def __init__(self, handler_class, static_dir="./www"):
            """Initialize development adapter.
            
            Args:
                handler_class: Handler class with route methods
                static_dir: Directory for static files
            """
            self.handler_class = handler_class
            self.static_dir = static_dir
            self.server = None
            self.server_thread = None
            self._running = False
            
        def start_server(self, host="localhost", port=8080):
            """Start the development HTTP server."""
            try:
                # Create request handler class with access to adapter
                adapter = self
                handler_instance = self.handler_class(self)
                
                class SLDKRequestHandler(BaseHTTPRequestHandler):
                    def log_message(self, format, *args):
                        """Override to use print for logging."""
                        print(f"HTTP: {format % args}")
                    
                    def do_GET(self):
                        """Handle GET requests."""
                        try:
                            parsed_url = urlparse(self.path)
                            path = parsed_url.path
                            query = parsed_url.query
                            
                            # Try to find a matching route handler
                            response = self._handle_route('GET', path, query, None)
                            if response:
                                self._send_response_obj(response)
                            else:
                                self._send_response(404, "text/plain", "Not Found")
                                
                        except Exception as e:
                            print(f"Error handling GET request: {e}")
                            self._send_response(500, "text/plain", "Internal Server Error")
                    
                    def do_POST(self):
                        """Handle POST requests."""
                        try:
                            parsed_url = urlparse(self.path)
                            path = parsed_url.path
                            query = parsed_url.query
                            
                            # Read form data
                            content_length = int(self.headers.get('Content-Length', 0))
                            post_data = self.rfile.read(content_length).decode('utf-8')
                            
                            # Try to find a matching route handler
                            response = self._handle_route('POST', path, query, post_data)
                            if response:
                                self._send_response_obj(response)
                            else:
                                self._send_response(404, "text/plain", "Not Found")
                            
                        except Exception as e:
                            print(f"Error handling POST request: {e}")
                            self._send_response(500, "text/plain", "Internal Server Error")
                    
                    def _handle_route(self, method, path, query, body):
                        """Handle route matching and execution."""
                        # Check for route handlers
                        for attr_name in dir(handler_instance):
                            if attr_name.startswith('route_'):
                                route_method = getattr(handler_instance, attr_name)
                                if callable(route_method) and hasattr(route_method, '_route_info'):
                                    route_info = route_method._route_info
                                    route_path = route_info['path']
                                    route_methods = route_info.get('methods', ['GET'])
                                    
                                    if path == route_path and method in route_methods:
                                        # Create mock request object
                                        request = MockRequest(method, path, query, body, adapter)
                                        return route_method(request)
                        
                        return None
                    
                    def _send_response_obj(self, response):
                        """Send response object."""
                        status = getattr(response, 'status', 200)
                        content_type = getattr(response, 'content_type', 'text/html')
                        body = getattr(response, 'body', '')
                        
                        self._send_response(status, content_type, body)
                    
                    def _send_response(self, status, content_type, content):
                        """Send HTTP response."""
                        self.send_response(status)
                        self.send_header('Content-type', content_type)
                        self.end_headers()
                        
                        if isinstance(content, str):
                            self.wfile.write(content.encode('utf-8'))
                        else:
                            self.wfile.write(content)
                
                # Create and start server
                self.server = HTTPServer((host, port), SLDKRequestHandler)
                self.server_thread = threading.Thread(target=self.server.serve_forever)
                self.server_thread.daemon = True
                self.server_thread.start()
                self._running = True
                
                print(f"Development web server started on http://{host}:{port}")
                return True
                
            except Exception as e:
                print(f"Failed to start development web server: {e}")
                return False
        
        def stop_server(self):
            """Stop the development HTTP server."""
            if self.server:
                try:
                    self.server.shutdown()
                    self.server.server_close()
                    if self.server_thread:
                        self.server_thread.join(timeout=5)
                    self._running = False
                    print("Development web server stopped")
                except Exception as e:
                    print(f"Error stopping development web server: {e}")
        
        @property
        def is_running(self):
            """Check if server is running."""
            return self._running
        
        async def handle_requests(self):
            """Handle incoming requests (Development)."""
            # Development server handles requests in separate thread
            # This is just a placeholder for the async interface
            await asyncio.sleep(0.1)
        
        def parse_query_params(self, query_string):
            """Parse query parameters from URL."""
            if not query_string:
                return {}
            
            try:
                parsed = parse_qs(query_string, keep_blank_values=True)
                # Convert lists to single values (take first value if multiple)
                params = {}
                for key, values in parsed.items():
                    params[key] = values[0] if values else ""
                return params
            except Exception as e:
                print(f"Error parsing query parameters: {e}")
                return {}
        
        def parse_form_data(self, request_body):
            """Parse form data from POST request."""
            return self.parse_query_params(request_body)


class MockRequest:
    """Mock request object for development adapter."""
    
    def __init__(self, method, path, query, body, adapter):
        self.method = method
        self.path = path
        self.query = query
        self.body = body
        self.adapter = adapter
        
        # Parse query parameters
        self.query_params = adapter.parse_query_params(query)
        
        # Parse form data if POST
        if method == 'POST' and body:
            self.form_data = adapter.parse_form_data(body)
        else:
            self.form_data = {}


class MockResponse:
    """Mock response object for both adapters."""
    
    def __init__(self, body, status=200, content_type="text/html"):
        self.body = body
        self.status = status
        self.content_type = content_type


def route(path, methods=None):
    """Decorator to mark methods as route handlers.
    
    Args:
        path: URL path to handle
        methods: List of HTTP methods (default: ['GET'])
    """
    if methods is None:
        methods = ['GET']
    
    def decorator(func):
        func._route_info = {
            'path': path,
            'methods': methods
        }
        return func
    return decorator


def create_server_adapter(handler_class, socket_pool=None, static_dir=None):
    """Factory function to create the appropriate server adapter.
    
    Args:
        handler_class: Handler class with route methods
        socket_pool: Socket pool (CircuitPython only)
        static_dir: Directory for static files
        
    Returns:
        ServerAdapter instance
    """
    if static_dir is None:
        static_dir = "/www" if IS_CIRCUITPYTHON else "./www"
    
    if IS_CIRCUITPYTHON:
        return CircuitPythonAdapter(handler_class, socket_pool, static_dir)
    else:
        return DevelopmentAdapter(handler_class, static_dir)