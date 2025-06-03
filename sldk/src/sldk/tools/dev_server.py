"""Development server for SLDK applications.

Provides hot-reload, debugging, and development tools.
"""

import os
import sys
import time
import threading
import importlib
from pathlib import Path

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    # Dummy classes for when watchdog is not available
    class Observer:
        def __init__(self): pass
        def schedule(self, *args, **kwargs): pass
        def start(self): pass
        def stop(self): pass
        def join(self): pass
    
    class FileSystemEventHandler:
        def on_modified(self, event): pass


class SLDKDevServer:
    """Development server for SLDK applications.
    
    Features:
    - Hot-reload on file changes
    - Development web interface
    - Memory monitoring
    - Performance profiling
    - Remote debugging support
    """
    
    def __init__(self, project_dir=".", src_dir="src", port=8000):
        """Initialize development server.
        
        Args:
            project_dir: Project directory
            src_dir: Source directory (relative to project)
            port: Web interface port
        """
        self.project_dir = Path(project_dir).resolve()
        self.src_dir = self.project_dir / src_dir
        self.port = port
        
        # Server state
        self.running = False
        self.app_instance = None
        self.app_thread = None
        self.file_observer = None
        self.web_server = None
        
        # Configuration
        self.hot_reload = True
        self.debug_mode = True
        self.memory_monitoring = True
        self.performance_profiling = False
        
        # Monitoring
        self.reload_count = 0
        self.last_reload_time = 0
        self.memory_usage = []
        self.performance_stats = {}
        
        # Add source directory to Python path
        if str(self.src_dir) not in sys.path:
            sys.path.insert(0, str(self.src_dir))
    
    def start(self, app_module="main", app_function="main"):
        """Start development server.
        
        Args:
            app_module: Main application module
            app_function: Main application function
            
        Returns:
            bool: Success
        """
        try:
            print(f"Starting SLDK Development Server")
            print(f"Project: {self.project_dir}")
            print(f"Source: {self.src_dir}")
            print(f"Hot-reload: {self.hot_reload}")
            print("-" * 50)
            
            self.running = True
            
            # Start file watcher for hot-reload
            if self.hot_reload:
                self._start_file_watcher()
            
            # Start web interface
            self._start_web_interface()
            
            # Start memory monitoring
            if self.memory_monitoring:
                self._start_memory_monitor()
            
            # Load and run application
            self._load_and_run_app(app_module, app_function)
            
            # Main server loop
            self._run_server_loop()
            
            return True
            
        except KeyboardInterrupt:
            print("\\nShutting down development server...")
            self.stop()
            return True
        except Exception as e:
            print(f"Development server error: {e}")
            self.stop()
            return False
    
    def stop(self):
        """Stop development server."""
        self.running = False
        
        # Stop file watcher
        if self.file_observer:
            self.file_observer.stop()
            self.file_observer.join()
        
        # Stop application
        if self.app_instance and hasattr(self.app_instance, 'stop'):
            self.app_instance.stop()
        
        # Stop web server
        if self.web_server:
            self.web_server.stop()
        
        print("Development server stopped.")
    
    def _start_file_watcher(self):
        """Start file system watcher for hot-reload."""
        if not WATCHDOG_AVAILABLE:
            print("Hot-reload disabled (watchdog not available)")
            print("Install with: pip install watchdog")
            return
        
        class ReloadHandler(FileSystemEventHandler):
            def __init__(self, dev_server):
                self.dev_server = dev_server
                self.last_reload = 0
                self.debounce_time = 1.0  # 1 second debounce
            
            def on_modified(self, event):
                if event.is_directory:
                    return
                
                # Only reload for Python files
                if not event.src_path.endswith('.py'):
                    return
                
                # Debounce rapid file changes
                current_time = time.time()
                if current_time - self.last_reload < self.debounce_time:
                    return
                
                self.last_reload = current_time
                
                print(f"\\nFile changed: {event.src_path}")
                self.dev_server._reload_application()
        
        self.file_observer = Observer()
        self.file_observer.schedule(
            ReloadHandler(self), 
            str(self.src_dir), 
            recursive=True
        )
        self.file_observer.start()
        print(f"File watcher started: {self.src_dir}")
    
    def _start_web_interface(self):
        """Start development web interface."""
        try:
            from ..web import SLDKWebServer
            from ..web.handlers import WebHandler
            from ..web.adapters import route
            import json
            
            # Create web server
            self.web_server = SLDKWebServer(host="localhost", port=self.port)
            
            class DevHandler(WebHandler):
                def __init__(self, server, dev_server):
                    super().__init__(server)
                    self.dev_server = dev_server
                
                @route("/")
                def dashboard(self, request):
                    """Development dashboard."""
                    from ..web.templates import HTMLBuilder
                    
                    builder = HTMLBuilder("SLDK Development Server")
                    
                    # Add refresh and styling
                    builder.add_to_head('<meta http-equiv="refresh" content="5">')
                    builder.add_inline_css("""
                        body { font-family: Arial, sans-serif; margin: 20px; }
                        .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
                        .running { background-color: #d4edda; color: #155724; }
                        .stopped { background-color: #f8d7da; color: #721c24; }
                        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
                        .stat-card { border: 1px solid #ddd; padding: 15px; border-radius: 5px; }
                        .controls { margin: 20px 0; }
                        .controls button { padding: 10px 20px; margin: 5px; }
                    """)
                    
                    builder.add_heading("SLDK Development Server", 1)
                    
                    # Status
                    status_class = "running" if self.dev_server.running else "stopped"
                    status_text = "Running" if self.dev_server.running else "Stopped"
                    builder.add_div(
                        f"Status: {status_text}",
                        class_=f"status {status_class}"
                    )
                    
                    # Statistics
                    builder.add_heading("Statistics", 2)
                    
                    stats_html = f"""
                    <div class="stats">
                        <div class="stat-card">
                            <h3>Reloads</h3>
                            <p>{self.dev_server.reload_count}</p>
                        </div>
                        <div class="stat-card">
                            <h3>Uptime</h3>
                            <p>{self._format_uptime()}</p>
                        </div>
                        <div class="stat-card">
                            <h3>Memory Usage</h3>
                            <p>{self._get_memory_usage()}</p>
                        </div>
                        <div class="stat-card">
                            <h3>Hot Reload</h3>
                            <p>{"Enabled" if self.dev_server.hot_reload else "Disabled"}</p>
                        </div>
                    </div>
                    """
                    builder.add_to_body(stats_html)
                    
                    # Controls
                    builder.add_heading("Controls", 2)
                    
                    controls_html = """
                    <div class="controls">
                        <button onclick="fetch('/api/reload', {method: 'POST'})">Force Reload</button>
                        <button onclick="fetch('/api/clear-cache', {method: 'POST'})">Clear Cache</button>
                        <button onclick="fetch('/api/gc', {method: 'POST'})">Garbage Collect</button>
                    </div>
                    """
                    builder.add_to_body(controls_html)
                    
                    # Memory usage chart (simple)
                    if self.dev_server.memory_usage:
                        builder.add_heading("Memory Usage", 2)
                        recent_usage = self.dev_server.memory_usage[-20:]  # Last 20 readings
                        chart_data = ', '.join(str(usage) for usage in recent_usage)
                        
                        chart_html = f"""
                        <canvas id="memoryChart" width="400" height="200"></canvas>
                        <script>
                            var canvas = document.getElementById('memoryChart');
                            var ctx = canvas.getContext('2d');
                            var data = [{chart_data}];
                            
                            // Simple line chart
                            ctx.strokeStyle = '#007bff';
                            ctx.lineWidth = 2;
                            ctx.beginPath();
                            
                            for (var i = 0; i < data.length; i++) {{
                                var x = (i / (data.length - 1)) * canvas.width;
                                var y = canvas.height - (data[i] / Math.max(...data)) * canvas.height;
                                
                                if (i === 0) {{
                                    ctx.moveTo(x, y);
                                }} else {{
                                    ctx.lineTo(x, y);
                                }}
                            }}
                            
                            ctx.stroke();
                        </script>
                        """
                        builder.add_to_body(chart_html)
                    
                    return self.create_response(builder.build())
                
                def _format_uptime(self):
                    """Format server uptime."""
                    # Simple uptime calculation
                    return "Running"
                
                def _get_memory_usage(self):
                    """Get current memory usage."""
                    try:
                        import psutil
                        process = psutil.Process()
                        memory_mb = process.memory_info().rss / 1024 / 1024
                        return f"{memory_mb:.1f} MB"
                    except ImportError:
                        return "Unknown"
                
                @route("/api/reload", methods=["POST"])
                def force_reload(self, request):
                    """Force application reload."""
                    self.dev_server._reload_application()
                    return self.create_response(
                        json.dumps({"status": "reloaded"}),
                        content_type="application/json"
                    )
                
                @route("/api/clear-cache", methods=["POST"])
                def clear_cache(self, request):
                    """Clear import cache."""
                    # Clear module cache
                    for module_name in list(sys.modules.keys()):
                        if module_name.startswith('main') or module_name.startswith('src'):
                            del sys.modules[module_name]
                    
                    return self.create_response(
                        json.dumps({"status": "cache cleared"}),
                        content_type="application/json"
                    )
                
                @route("/api/gc", methods=["POST"])
                def garbage_collect(self, request):
                    """Force garbage collection."""
                    import gc
                    collected = gc.collect()
                    return self.create_response(
                        json.dumps({"status": "gc completed", "collected": collected}),
                        content_type="application/json"
                    )
            
            # Register handler
            handler = DevHandler(self.web_server, self)
            self.web_server.add_handler(handler)
            
            # Start web server in background
            threading.Thread(
                target=self.web_server.start_background,
                daemon=True
            ).start()
            
            print(f"Development web interface: http://localhost:{self.port}")
            
        except ImportError:
            print("Web interface not available (missing dependencies)")
        except Exception as e:
            print(f"Failed to start web interface: {e}")
    
    def _start_memory_monitor(self):
        """Start memory monitoring."""
        def monitor_memory():
            try:
                import psutil
                process = psutil.Process()
                
                while self.running:
                    memory_mb = process.memory_info().rss / 1024 / 1024
                    self.memory_usage.append(memory_mb)
                    
                    # Keep only recent data
                    if len(self.memory_usage) > 100:
                        self.memory_usage = self.memory_usage[-100:]
                    
                    time.sleep(5)  # Check every 5 seconds
                    
            except ImportError:
                print("Memory monitoring disabled (psutil not available)")
            except Exception as e:
                print(f"Memory monitoring error: {e}")
        
        threading.Thread(target=monitor_memory, daemon=True).start()
    
    def _load_and_run_app(self, app_module, app_function):
        """Load and run the application.
        
        Args:
            app_module: Module name
            app_function: Function name
        """
        try:
            # Import application module
            if app_module in sys.modules:
                module = importlib.reload(sys.modules[app_module])
            else:
                module = importlib.import_module(app_module)
            
            # Get application function
            if hasattr(module, app_function):
                app_func = getattr(module, app_function)
                
                # Run application in background thread
                def run_app():
                    try:
                        if callable(app_func):
                            self.app_instance = app_func()
                        else:
                            print(f"Warning: {app_function} is not callable")
                    except Exception as e:
                        print(f"Application error: {e}")
                        import traceback
                        traceback.print_exc()
                
                self.app_thread = threading.Thread(target=run_app, daemon=True)
                self.app_thread.start()
                
                print(f"Application started: {app_module}.{app_function}")
            else:
                print(f"Function {app_function} not found in {app_module}")
                
        except Exception as e:
            print(f"Failed to load application: {e}")
            import traceback
            traceback.print_exc()
    
    def _reload_application(self):
        """Reload the application."""
        try:
            print("Reloading application...")
            
            # Stop current app instance
            if self.app_instance and hasattr(self.app_instance, 'stop'):
                self.app_instance.stop()
            
            # Clear module cache
            modules_to_clear = []
            for module_name in sys.modules.keys():
                if (module_name.startswith('main') or 
                    module_name.startswith('src') or
                    any(str(self.src_dir) in getattr(sys.modules[module_name], '__file__', '') 
                        for _ in [None] if sys.modules[module_name] is not None)):
                    modules_to_clear.append(module_name)
            
            for module_name in modules_to_clear:
                if module_name in sys.modules:
                    del sys.modules[module_name]
            
            # Force garbage collection
            import gc
            gc.collect()
            
            # Reload application
            self._load_and_run_app("main", "main")
            
            self.reload_count += 1
            self.last_reload_time = time.time()
            
            print(f"Application reloaded (#{self.reload_count})")
            
        except Exception as e:
            print(f"Reload failed: {e}")
            import traceback
            traceback.print_exc()
    
    def _run_server_loop(self):
        """Main server loop."""
        print("\\nDevelopment server running...")
        print("Press Ctrl+C to stop")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    
    def set_config(self, hot_reload=None, debug_mode=None, 
                  memory_monitoring=None, performance_profiling=None):
        """Set development server configuration.
        
        Args:
            hot_reload: Enable hot-reload
            debug_mode: Enable debug mode
            memory_monitoring: Enable memory monitoring
            performance_profiling: Enable performance profiling
        """
        if hot_reload is not None:
            self.hot_reload = hot_reload
        if debug_mode is not None:
            self.debug_mode = debug_mode
        if memory_monitoring is not None:
            self.memory_monitoring = memory_monitoring
        if performance_profiling is not None:
            self.performance_profiling = performance_profiling
    
    def get_stats(self):
        """Get development server statistics.
        
        Returns:
            dict: Statistics
        """
        return {
            'running': self.running,
            'reload_count': self.reload_count,
            'last_reload_time': self.last_reload_time,
            'memory_usage': self.memory_usage[-10:] if self.memory_usage else [],
            'hot_reload': self.hot_reload,
            'debug_mode': self.debug_mode,
            'memory_monitoring': self.memory_monitoring
        }