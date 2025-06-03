"""SLDK Web Server

Unified web server that works on both CircuitPython and development environments.
Extracted from Theme Park API for the SLDK framework.
"""

import sys

try:
    import asyncio
except ImportError:
    # CircuitPython
    import asyncio

from .adapters import create_server_adapter, IS_CIRCUITPYTHON
from .handlers import WebHandler, StaticFileHandler, APIHandler


class SLDKWebServer:
    """SLDK web server that works on both CircuitPython and development platforms."""
    
    def __init__(self, app=None, handler_class=None, socket_pool=None, static_dir=None):
        """Initialize the SLDK web server.
        
        Args:
            app: SLDK application instance
            handler_class: Custom handler class (default: WebHandler)
            socket_pool: Socket pool (CircuitPython only)
            static_dir: Directory for static files
        """
        self.app = app
        self.socket_pool = socket_pool
        self.static_dir = static_dir
        
        # Use provided handler class or create composite handler
        if handler_class:
            self.handler_class = handler_class
        else:
            self.handler_class = self._create_composite_handler()
        
        # Create platform-specific adapter
        self.adapter = create_server_adapter(
            self.handler_class, 
            socket_pool=socket_pool,
            static_dir=static_dir
        )
        
        self._running = False
        self._host = None
        self._port = None
    
    def _create_composite_handler(self):
        """Create a composite handler that combines multiple handler types."""
        class CompositeHandler(WebHandler, StaticFileHandler, APIHandler):
            def __init__(self, adapter):
                WebHandler.__init__(self, adapter)
                StaticFileHandler.__init__(self, adapter)
                APIHandler.__init__(self, adapter)
        
        return CompositeHandler
    
    async def start(self, host=None, port=None):
        """Start the web server.
        
        Args:
            host: Host to bind to (optional, platform-specific defaults)
            port: Port to bind to (optional, platform-specific defaults)
            
        Returns:
            bool: True if server started successfully
        """
        try:
            # Set platform-appropriate defaults
            if IS_CIRCUITPYTHON:
                self._host = host or "0.0.0.0"
                self._port = port or 80
            else:
                self._host = host or "localhost"
                self._port = port or 8080
            
            print(f"Starting SLDK web server on {self._host}:{self._port}")
            
            success = self.adapter.start_server(self._host, self._port)
            if success:
                self._running = True
                print("SLDK web server started successfully")
            else:
                print("Failed to start SLDK web server")
                
            return success
            
        except Exception as e:
            print(f"Error starting SLDK web server: {e}")
            return False
    
    async def stop(self):
        """Stop the web server."""
        try:
            if self._running:
                print("Stopping SLDK web server")
                self.adapter.stop_server()
                self._running = False
                print("SLDK web server stopped")
        except Exception as e:
            print(f"Error stopping SLDK web server: {e}")
    
    @property
    def is_running(self):
        """Check if the web server is running."""
        return self._running and getattr(self.adapter, 'is_running', False)
    
    async def handle_requests(self):
        """Handle incoming requests.
        
        For CircuitPython, this polls for new requests.
        For development servers, this is mostly a no-op since
        requests are handled in a separate thread.
        """
        if self._running:
            await self.adapter.handle_requests()
    
    def get_server_url(self):
        """Get the server URL.
        
        Returns:
            str: Server URL
        """
        if IS_CIRCUITPYTHON and self.socket_pool:
            # Try to get IP from socket pool or WiFi manager
            try:
                # This would need to be adapted based on actual socket pool implementation
                return f"http://{self._host}:{self._port}"
            except Exception:
                return f"http://{self._host}:{self._port}"
        else:
            return f"http://{self._host}:{self._port}"
    
    async def run_forever(self):
        """Run the web server forever (async version).
        
        This method handles requests in a loop and should be run
        as a background task.
        """
        while self._running:
            await self.handle_requests()
            await asyncio.sleep(0.1)  # Small delay to prevent busy waiting


class SLDKWebApplication:
    """Web application framework for SLDK.
    
    Provides a more structured way to build web applications
    with multiple handlers and middleware.
    """
    
    def __init__(self, sldk_app=None):
        """Initialize web application.
        
        Args:
            sldk_app: Parent SLDK application instance
        """
        self.sldk_app = sldk_app
        self.handlers = []
        self.middleware = []
        self._routes = {}
    
    def add_handler(self, handler_class):
        """Add a handler class to the application.
        
        Args:
            handler_class: Handler class to add
        """
        self.handlers.append(handler_class)
    
    def add_middleware(self, middleware_func):
        """Add middleware to the application.
        
        Args:
            middleware_func: Middleware function
        """
        self.middleware.append(middleware_func)
    
    def route(self, path, methods=None):
        """Decorator to add routes to the application.
        
        Args:
            path: URL path
            methods: List of HTTP methods
        """
        def decorator(func):
            if methods is None:
                route_methods = ['GET']
            else:
                route_methods = methods
            
            self._routes[path] = {
                'function': func,
                'methods': route_methods
            }
            return func
        return decorator
    
    def create_server(self, socket_pool=None, static_dir=None):
        """Create a web server for this application.
        
        Args:
            socket_pool: Socket pool (CircuitPython only)
            static_dir: Directory for static files
            
        Returns:
            SLDKWebServer instance
        """
        # Create a composite handler from all registered handlers
        handler_classes = self.handlers or [WebHandler, StaticFileHandler, APIHandler]
        
        class ApplicationHandler(*handler_classes):
            def __init__(self, adapter):
                for handler_class in handler_classes:
                    handler_class.__init__(self, adapter)
                
                # Add routes from application
                for path, route_info in app._routes.items():
                    func = route_info['function']
                    methods = route_info['methods']
                    
                    # Create route method name
                    route_name = f"route_{path.replace('/', '_').replace('<', '').replace('>', '').strip('_')}"
                    
                    # Add route info to the function
                    func._route_info = {'path': path, 'methods': methods}
                    
                    # Add function as method
                    setattr(self, route_name, func)
        
        app = self  # Capture reference for closure
        
        return SLDKWebServer(
            app=self.sldk_app,
            handler_class=ApplicationHandler,
            socket_pool=socket_pool,
            static_dir=static_dir
        )


# Convenience functions

def create_web_server(app=None, handler_class=None, socket_pool=None, static_dir=None):
    """Create an SLDK web server instance.
    
    Args:
        app: SLDK application instance
        handler_class: Custom handler class
        socket_pool: Socket pool (CircuitPython only)
        static_dir: Directory for static files
        
    Returns:
        SLDKWebServer instance
    """
    return SLDKWebServer(
        app=app,
        handler_class=handler_class,
        socket_pool=socket_pool,
        static_dir=static_dir
    )


async def start_web_server(app=None, handler_class=None, socket_pool=None, 
                          static_dir=None, host=None, port=None):
    """Start an SLDK web server.
    
    Args:
        app: SLDK application instance
        handler_class: Custom handler class
        socket_pool: Socket pool (CircuitPython only)
        static_dir: Directory for static files
        host: Host to bind to
        port: Port to bind to
        
    Returns:
        SLDKWebServer instance if successful, None otherwise
    """
    server = create_web_server(app, handler_class, socket_pool, static_dir)
    if await server.start(host, port):
        return server
    else:
        return None