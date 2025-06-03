#!/usr/bin/env python3
"""Web server demo for SLDK.

Demonstrates the SLDK web framework with forms, templates, and handlers.
"""

import sys
import os

# Add parent directory to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import asyncio
except ImportError:
    # CircuitPython
    import asyncio

from sldk import SLDKApp, ScrollingText, StaticText
from sldk.web import SLDKWebServer, WebHandler
from sldk.web.adapters import route
from sldk.web.templates import HTMLBuilder, TemplateEngine
from sldk.web.forms import FormBuilder


class DemoWebHandler(WebHandler):
    """Custom web handler for the demo application."""
    
    def __init__(self, adapter):
        super().__init__(adapter)
        self.settings = {
            'message': 'Hello from SLDK!',
            'color': '#FF0000',
            'speed': 0.05,
            'brightness': 50
        }
    
    @route("/")
    def route_index(self, request):
        """Handle index page with settings form."""
        # Create form for settings
        form = FormBuilder(action="/", method="POST")
        form.text_field('message', label='Display Message', 
                       default=self.settings['message'], required=True)
        form.color_field('color', label='Text Color', 
                        default=self.settings['color'])
        form.number_field('speed', label='Scroll Speed', 
                         default=self.settings['speed'], 
                         min_value=0.01, max_value=1.0, step=0.01)
        form.number_field('brightness', label='Brightness (%)', 
                         default=self.settings['brightness'],
                         min_value=1, max_value=100)
        
        # Create HTML page
        builder = HTMLBuilder("SLDK Web Demo")
        builder.add_viewport()
        builder.add_css_link("/style.css")
        
        # Add content
        builder.add_to_body('<div class="container">')
        builder.add_to_body('<div class="header">')
        builder.add_heading("SLDK Web Framework Demo", level=1)
        builder.add_paragraph("Configure your LED display settings below.")
        builder.add_to_body('</div>')
        
        builder.add_to_body('<div class="content">')
        
        # Current settings display
        builder.add_to_body('<div class="card">')
        builder.add_heading("Current Settings", level=3)
        builder.add_to_body(f'<p><strong>Message:</strong> {self.settings["message"]}</p>')
        builder.add_to_body(f'<p><strong>Color:</strong> <span style="color: {self.settings["color"]}">{self.settings["color"]}</span></p>')
        builder.add_to_body(f'<p><strong>Speed:</strong> {self.settings["speed"]}s per pixel</p>')
        builder.add_to_body(f'<p><strong>Brightness:</strong> {self.settings["brightness"]}%</p>')
        builder.add_to_body('</div>')
        
        # Settings form
        builder.add_to_body('<div class="card">')
        builder.add_heading("Update Settings", level=3)
        builder.add_to_body(form.render(self.settings))
        builder.add_to_body('</div>')
        
        builder.add_to_body('</div>')  # content
        builder.add_to_body('</div>')  # container
        
        return self.create_response(builder.build())
    
    @route("/", methods=["POST"])
    def route_update_settings(self, request):
        """Handle settings form submission."""
        # Create form for validation
        form = FormBuilder()
        form.text_field('message', required=True)
        form.color_field('color')
        form.number_field('speed', min_value=0.01, max_value=1.0)
        form.number_field('brightness', min_value=1, max_value=100)
        
        # Validate form data
        if form.validate(request.form_data):
            # Update settings
            self.settings.update(form.get_data(request.form_data))
            
            # Update display if app is available
            if hasattr(self.adapter, 'app') and self.adapter.app:
                app = self.adapter.app
                # Convert hex color to integer
                color_hex = self.settings['color']
                color_int = int(color_hex[1:], 16) if color_hex.startswith('#') else 0xFF0000
                
                # Add new scrolling text to content queue
                app.content_queue.clear()
                app.content_queue.add(ScrollingText(
                    self.settings['message'],
                    y=12,
                    color=color_int,
                    speed=self.settings['speed']
                ))
                
                # Set display brightness
                if app.display:
                    brightness = self.settings['brightness'] / 100.0
                    import asyncio
                    asyncio.create_task(app.display.set_brightness(brightness))
            
            return self.create_redirect_response(
                f"Settings updated! Message: '{self.settings['message']}'",
                "success"
            )
        else:
            return self.create_redirect_response(
                f"Validation errors: {', '.join(form.errors)}",
                "error"
            )
    
    @route("/api/settings")
    def route_api_settings(self, request):
        """API endpoint to get current settings."""
        return self.create_response(
            str(self.settings).replace("'", '"'),  # Simple JSON-like
            content_type="application/json"
        )
    
    @route("/api/status")
    def route_api_status(self, request):
        """API endpoint for application status."""
        status = {
            'running': True,
            'framework': 'SLDK',
            'version': '0.1.0',
            'has_display': hasattr(self.adapter, 'app') and getattr(self.adapter.app, 'display', None) is not None
        }
        return self.create_response(
            str(status).replace("'", '"').replace('True', 'true').replace('False', 'false'),
            content_type="application/json"
        )


class WebDemoApp(SLDKApp):
    """Demo application with web interface."""
    
    def __init__(self):
        # Enable web server
        super().__init__(enable_web=True, update_interval=10)
        self.web_server = None
        
    async def setup(self):
        """Initialize the application."""
        print("Web demo app starting...")
        
        # Add initial content
        self.content_queue.add(StaticText(
            "SLDK", 
            x=15, y=8,
            color=0x00FF00,
            duration=3
        ))
        
        self.content_queue.add(StaticText(
            "Web Demo",
            x=5, y=20,
            color=0x0080FF,
            duration=3
        ))
        
        self.content_queue.add(ScrollingText(
            "Configure me via web interface!",
            y=12,
            color=0xFFFF00,
            speed=0.05
        ))
    
    async def create_display(self):
        """Create display and set up web server."""
        # Create display using parent method
        from sldk.display import UnifiedDisplay
        display = UnifiedDisplay()
        
        # Create web server with custom handler
        self.web_server = SLDKWebServer(
            app=self,
            handler_class=DemoWebHandler
        )
        
        # Store app reference in adapter for handler access
        self.web_server.adapter.app = self
        
        return display
    
    async def _web_server_process(self):
        """Override web server process to use SLDK web server."""
        if not self.web_server:
            return
        
        # Check memory
        import gc
        gc.collect()
        free_memory = gc.mem_free() if hasattr(gc, 'mem_free') else 100000
        
        if free_memory < 50000:
            print(f"Web server disabled - insufficient memory: {free_memory}")
            return
        
        try:
            print("Starting SLDK web server...")
            if await self.web_server.start():
                print(f"Web interface available at: {self.web_server.get_server_url()}")
                
                # Run web server
                await self.web_server.run_forever()
            else:
                print("Failed to start web server")
                
        except Exception as e:
            print(f"Web server error: {e}")
    
    async def update_data(self):
        """Update data periodically."""
        print("Web demo: Data update called")
        # Could fetch external data here


async def main():
    """Main entry point."""
    app = WebDemoApp()
    
    try:
        print("Starting SLDK web demo...")
        print("Open your browser to the web interface URL to configure the display!")
        
        # Initialize the display first
        await app._initialize_display()
        
        # Create window for simulator
        if hasattr(app.display, 'create_window'):
            await app.display.create_window("SLDK Web Demo")
            
        # For simulator, start event loop in background
        if hasattr(app.display, 'run_event_loop'):
            asyncio.create_task(app.display.run_event_loop())
        
        # Run the app
        await app.run()
        
    except KeyboardInterrupt:
        print("\nShutting down...")
        app.stop()
        if app.web_server:
            await app.web_server.stop()


if __name__ == "__main__":
    # Run with asyncio
    asyncio.run(main())