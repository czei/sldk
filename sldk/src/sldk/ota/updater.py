"""Main OTA updater class for SLDK applications.

Provides easy-to-use OTA update functionality.
"""

import gc
from .client import OTAClient
from .server import OTAServer
from .manifest import UpdateManifest


class OTAUpdater:
    """High-level OTA updater for SLDK applications.
    
    Provides a simple interface for OTA updates:
    - Automatic update checking
    - Progress tracking
    - Error handling
    - Integration with SLDK apps
    """
    
    def __init__(self, app, server_url=None, current_version=None, 
                 auto_check=True, check_interval=3600):
        """Initialize OTA updater.
        
        Args:
            app: SLDK application instance
            server_url: Update server URL
            current_version: Current app version
            auto_check: Enable automatic update checking
            check_interval: Check interval in seconds
        """
        self.app = app
        self.server_url = server_url
        self.current_version = current_version or getattr(app, 'version', '1.0.0')
        self.auto_check = auto_check
        self.check_interval = check_interval
        
        # Update client
        self.client = None
        if server_url:
            self.client = OTAClient(server_url, self.current_version)
            self._setup_client_callbacks()
        
        # Status tracking
        self.last_check_time = 0
        self.update_available = False
        self.available_manifest = None
        self.update_status = "idle"  # idle, checking, downloading, installing
        self.update_progress = 0.0
        self.update_error = None
        
        # User callbacks
        self.on_update_available = None
        self.on_update_progress = None
        self.on_update_complete = None
        self.on_update_error = None
    
    def _setup_client_callbacks(self):
        """Setup OTA client callbacks."""
        if not self.client:
            return
        
        def on_available(manifest):
            self.update_available = True
            self.available_manifest = manifest
            print(f"Update available: {manifest.version}")
            
            if self.on_update_available:
                self.on_update_available(manifest)
        
        def on_progress(message, progress):
            self.update_progress = progress
            print(f"Update progress: {message} ({progress*100:.1f}%)")
            
            if self.on_update_progress:
                self.on_update_progress(message, progress)
        
        def on_complete(version):
            self.update_status = "idle"
            self.update_progress = 1.0
            self.current_version = version
            print(f"Update complete: {version}")
            
            if self.on_update_complete:
                self.on_update_complete(version)
        
        def on_error(error):
            self.update_status = "idle"
            self.update_error = error
            print(f"Update error: {error}")
            
            if self.on_update_error:
                self.on_update_error(error)
        
        self.client.set_callbacks(
            on_available=on_available,
            on_progress=on_progress,
            on_complete=on_complete,
            on_error=on_error
        )
    
    def set_callbacks(self, on_available=None, on_progress=None, 
                     on_complete=None, on_error=None):
        """Set update callbacks.
        
        Args:
            on_available: Called when update is available
            on_progress: Called during update progress
            on_complete: Called when update completes
            on_error: Called on error
        """
        if on_available:
            self.on_update_available = on_available
        if on_progress:
            self.on_update_progress = on_progress
        if on_complete:
            self.on_update_complete = on_complete
        if on_error:
            self.on_update_error = on_error
    
    async def check_for_updates(self):
        """Check for available updates.
        
        Returns:
            tuple: (has_update, manifest_or_error)
        """
        if not self.client:
            return False, "No update server configured"
        
        try:
            self.update_status = "checking"
            self.update_error = None
            
            # Update last check time
            try:
                import time
                self.last_check_time = time.monotonic()
            except Exception:
                pass
            
            # Check for updates
            has_update, result = self.client.check_for_updates()
            
            if has_update:
                self.update_available = True
                self.available_manifest = result
            
            self.update_status = "idle"
            return has_update, result
            
        except Exception as e:
            self.update_status = "idle"
            self.update_error = str(e)
            return False, str(e)
        finally:
            gc.collect()
    
    async def download_update(self, manifest=None):
        """Download available update.
        
        Args:
            manifest: Update manifest (uses available if None)
            
        Returns:
            tuple: (success, error_message)
        """
        if not self.client:
            return False, "No update client available"
        
        if not manifest and not self.available_manifest:
            return False, "No update available"
        
        try:
            self.update_status = "downloading"
            self.update_error = None
            
            # Download update
            success, error = self.client.download_update(manifest)
            
            if not success:
                self.update_status = "idle"
                self.update_error = error
            
            return success, error
            
        except Exception as e:
            self.update_status = "idle"
            self.update_error = str(e)
            return False, str(e)
        finally:
            gc.collect()
    
    async def install_update(self, manifest=None, reboot=True):
        """Install downloaded update.
        
        Args:
            manifest: Update manifest (uses available if None)
            reboot: Whether to reboot after install
            
        Returns:
            tuple: (success, error_message)
        """
        if not self.client:
            return False, "No update client available"
        
        try:
            self.update_status = "installing"
            self.update_error = None
            
            # Install update
            success, error = self.client.apply_update(manifest)
            
            if success:
                self.update_available = False
                self.available_manifest = None
                
                if reboot:
                    print("Rebooting to complete update...")
                    # Give a moment for message to be seen
                    try:
                        import time
                        time.sleep(2)
                    except Exception:
                        pass
                    
                    self.client.reboot_device()
            else:
                self.update_status = "idle"
                self.update_error = error
            
            return success, error
            
        except Exception as e:
            self.update_status = "idle"
            self.update_error = str(e)
            return False, str(e)
        finally:
            gc.collect()
    
    async def update_now(self, reboot=True):
        """Download and install update immediately.
        
        Args:
            reboot: Whether to reboot after install
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            # Check for updates first if we don't have one
            if not self.available_manifest:
                has_update, result = await self.check_for_updates()
                if not has_update:
                    return False, f"No updates available: {result}"
            
            # Download update
            success, error = await self.download_update()
            if not success:
                return False, f"Download failed: {error}"
            
            # Install update
            success, error = await self.install_update(reboot=reboot)
            if not success:
                return False, f"Install failed: {error}"
            
            return True, ""
            
        except Exception as e:
            return False, str(e)
    
    async def auto_update_check(self):
        """Perform automatic update check.
        
        This method should be called periodically by the application.
        """
        if not self.auto_check or not self.client:
            return
        
        try:
            import time
            current_time = time.monotonic()
            
            # Check if enough time has passed
            if current_time - self.last_check_time < self.check_interval:
                return
            
            # Perform check
            await self.check_for_updates()
            
        except Exception as e:
            print(f"Auto update check error: {e}")
    
    def get_status(self):
        """Get current update status.
        
        Returns:
            dict: Status information
        """
        return {
            'current_version': self.current_version,
            'update_available': self.update_available,
            'available_version': self.available_manifest.version if self.available_manifest else None,
            'status': self.update_status,
            'progress': self.update_progress,
            'error': self.update_error,
            'last_check': self.last_check_time,
            'auto_check': self.auto_check
        }
    
    def enable_auto_check(self, enabled=True, interval=None):
        """Enable/disable automatic update checking.
        
        Args:
            enabled: Whether to enable auto-check
            interval: Check interval in seconds
        """
        self.auto_check = enabled
        if interval is not None:
            self.check_interval = interval
    
    def register_web_routes(self, web_server):
        """Register OTA web routes.
        
        Args:
            web_server: SLDK web server instance
        """
        from ..web.handlers import WebHandler
        from ..web.adapters import route
        import json
        
        class OTAWebHandler(WebHandler):
            def __init__(self, server, ota_updater):
                super().__init__(server)
                self.ota = ota_updater
            
            @route("/api/ota/status")
            def get_status(self, request):
                """Get OTA status."""
                status = self.ota.get_status()
                return self.create_response(
                    json.dumps(status, indent=2),
                    content_type="application/json"
                )
            
            @route("/api/ota/check", methods=["POST"])
            async def check_updates(self, request):
                """Check for updates."""
                has_update, result = await self.ota.check_for_updates()
                
                response_data = {
                    'has_update': has_update,
                    'message': str(result) if not has_update else result.version,
                    'status': self.ota.get_status()
                }
                
                return self.create_response(
                    json.dumps(response_data, indent=2),
                    content_type="application/json"
                )
            
            @route("/api/ota/download", methods=["POST"])
            async def download_update(self, request):
                """Download update."""
                success, error = await self.ota.download_update()
                
                response_data = {
                    'success': success,
                    'error': error,
                    'status': self.ota.get_status()
                }
                
                return self.create_response(
                    json.dumps(response_data, indent=2),
                    content_type="application/json"
                )
            
            @route("/api/ota/install", methods=["POST"])
            async def install_update(self, request):
                """Install update."""
                # Parse form data to check for reboot option
                form_data = self.parse_form_data(request)
                reboot = form_data.get('reboot', 'true').lower() == 'true'
                
                success, error = await self.ota.install_update(reboot=reboot)
                
                response_data = {
                    'success': success,
                    'error': error,
                    'status': self.ota.get_status()
                }
                
                return self.create_response(
                    json.dumps(response_data, indent=2),
                    content_type="application/json"
                )
            
            @route("/api/ota/update-now", methods=["POST"])
            async def update_now(self, request):
                """Download and install update immediately."""
                # Parse form data to check for reboot option
                form_data = self.parse_form_data(request)
                reboot = form_data.get('reboot', 'true').lower() == 'true'
                
                success, error = await self.ota.update_now(reboot=reboot)
                
                response_data = {
                    'success': success,
                    'error': error,
                    'status': self.ota.get_status()
                }
                
                return self.create_response(
                    json.dumps(response_data, indent=2),
                    content_type="application/json"
                )
            
            @route("/admin/updates")
            def updates_admin(self, request):
                """OTA updates administration interface."""
                from ..web.templates import HTMLBuilder
                
                builder = HTMLBuilder("Update Management")
                builder.add_heading("Over-The-Air Updates", 1)
                
                # Current status
                status = self.ota.get_status()
                
                builder.add_heading("Current Status", 2)
                builder.add_paragraph(f"Current Version: {status['current_version']}")
                builder.add_paragraph(f"Status: {status['status']}")
                
                if status['update_available']:
                    builder.add_paragraph(f"Available Version: {status['available_version']}")
                    builder.add_paragraph("Update available!", style="color: green; font-weight: bold;")
                else:
                    builder.add_paragraph("No updates available.")
                
                if status['error']:
                    builder.add_paragraph(f"Last Error: {status['error']}", style="color: red;")
                
                # Progress bar if updating
                if status['status'] != 'idle':
                    progress_pct = status['progress'] * 100
                    progress_html = f"""
                    <div style="width: 100%; background-color: #f0f0f0; border-radius: 4px;">
                        <div style="width: {progress_pct}%; background-color: #4CAF50; height: 20px; border-radius: 4px;"></div>
                    </div>
                    <p>Progress: {progress_pct:.1f}%</p>
                    """
                    builder.add_to_body(progress_html)
                
                # Control buttons
                builder.add_heading("Actions", 2)
                
                # Check for updates button
                form = builder.add_form(action="/api/ota/check", method="POST")
                form.add_button("Check for Updates")
                form.end_form()
                
                # Update now button (if update available)
                if status['update_available']:
                    form = builder.add_form(action="/api/ota/update-now", method="POST")
                    form.add_input("checkbox", "reboot", "true", checked=True)
                    form.add_label("Reboot after update")
                    form.add_raw("<br><br>")
                    form.add_button("Install Update Now", style="background-color: #f44336; color: white;")
                    form.end_form()
                
                # Auto-refresh for progress updates
                if status['status'] != 'idle':
                    builder.add_to_head('<meta http-equiv="refresh" content="2">')
                
                return self.create_response(builder.build())
        
        # Register handler
        handler = OTAWebHandler(web_server, self)
        web_server.add_handler(handler)