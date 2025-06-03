"""OTA update server.

Serves update packages to CircuitPython devices.
"""

import os
import json
import hashlib
from .manifest import UpdateManifest


class OTAServer:
    """OTA update server.
    
    Serves update packages to devices:
    - Hosts update manifests
    - Serves individual files
    - Manages update packages
    - Provides web interface for uploads
    """
    
    def __init__(self, updates_dir="./updates", web_interface=None):
        """Initialize OTA server.
        
        Args:
            updates_dir: Directory containing update packages
            web_interface: Optional web server instance
        """
        self.updates_dir = updates_dir
        self.web_interface = web_interface
        self.current_manifest = None
        self.update_packages = {}  # version -> manifest
        
        # Ensure updates directory exists
        os.makedirs(updates_dir, exist_ok=True)
        
        # Load existing packages
        self._load_existing_packages()
    
    def _load_existing_packages(self):
        """Load existing update packages from disk."""
        try:
            for item in os.listdir(self.updates_dir):
                item_path = os.path.join(self.updates_dir, item)
                
                if os.path.isdir(item_path):
                    manifest_path = os.path.join(item_path, "manifest.json")
                    
                    if os.path.exists(manifest_path):
                        try:
                            with open(manifest_path, 'r') as f:
                                manifest_data = json.loads(f.read())
                            
                            manifest = UpdateManifest.from_dict(manifest_data)
                            self.update_packages[manifest.version] = manifest
                            
                            # Set as current if newest
                            if (not self.current_manifest or 
                                manifest.compare_version(self.current_manifest.version) > 0):
                                self.current_manifest = manifest
                                
                        except Exception as e:
                            print(f"Error loading package {item}: {e}")
                            
        except Exception as e:
            print(f"Error loading packages: {e}")
    
    def create_package(self, version, description="", source_dir="./src"):
        """Create new update package.
        
        Args:
            version: Version string
            description: Package description
            source_dir: Source directory to package
            
        Returns:
            tuple: (success, manifest_or_error)
        """
        try:
            # Create manifest
            manifest = UpdateManifest(version=version, description=description)
            
            # Add files from source directory
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    if file.endswith('.py') or file.endswith('.mpy'):
                        source_path = os.path.join(root, file)
                        relative_path = os.path.relpath(source_path, source_dir)
                        
                        # Convert to device path
                        device_path = "/" + relative_path.replace(os.sep, "/")
                        
                        manifest.add_file(device_path, file_path=source_path)
            
            # Validate manifest
            is_valid, error = manifest.validate()
            if not is_valid:
                return False, f"Invalid manifest: {error}"
            
            # Create package directory
            package_dir = os.path.join(self.updates_dir, version)
            os.makedirs(package_dir, exist_ok=True)
            
            # Save manifest
            manifest_path = os.path.join(package_dir, "manifest.json")
            with open(manifest_path, 'w') as f:
                f.write(manifest.to_json())
            
            # Copy files to package
            files_dir = os.path.join(package_dir, "files")
            os.makedirs(files_dir, exist_ok=True)
            
            for device_path in manifest.files.keys():
                source_path = os.path.join(source_dir, device_path.lstrip('/'))
                target_path = os.path.join(files_dir, device_path.lstrip('/'))
                
                # Ensure target directory exists
                target_dir = os.path.dirname(target_path)
                if target_dir:
                    os.makedirs(target_dir, exist_ok=True)
                
                # Copy file
                with open(source_path, 'rb') as src:
                    with open(target_path, 'wb') as dst:
                        dst.write(src.read())
            
            # Update package registry
            self.update_packages[version] = manifest
            
            # Set as current if newest
            if (not self.current_manifest or 
                manifest.compare_version(self.current_manifest.version) > 0):
                self.current_manifest = manifest
            
            return True, manifest
            
        except Exception as e:
            return False, str(e)
    
    def get_manifest_json(self, version=None):
        """Get manifest as JSON.
        
        Args:
            version: Specific version (uses current if None)
            
        Returns:
            str: JSON manifest or None
        """
        manifest = self.current_manifest
        
        if version and version in self.update_packages:
            manifest = self.update_packages[version]
        
        if manifest:
            return manifest.to_json()
        return None
    
    def get_file_content(self, file_path, version=None):
        """Get file content from package.
        
        Args:
            file_path: File path
            version: Package version (uses current if None)
            
        Returns:
            bytes: File content or None
        """
        if version is None and self.current_manifest:
            version = self.current_manifest.version
        
        if not version or version not in self.update_packages:
            return None
        
        try:
            package_dir = os.path.join(self.updates_dir, version)
            files_dir = os.path.join(package_dir, "files")
            full_path = os.path.join(files_dir, file_path.lstrip('/'))
            
            if os.path.exists(full_path):
                with open(full_path, 'rb') as f:
                    return f.read()
                    
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
        
        return None
    
    def list_packages(self):
        """List all available packages.
        
        Returns:
            list: Package info dictionaries
        """
        packages = []
        
        for version, manifest in self.update_packages.items():
            packages.append({
                'version': version,
                'description': manifest.description,
                'file_count': len(manifest.files),
                'total_size': manifest.calculate_total_size(),
                'is_current': manifest == self.current_manifest
            })
        
        # Sort by version (newest first)
        packages.sort(key=lambda p: p['version'], reverse=True)
        return packages
    
    def delete_package(self, version):
        """Delete update package.
        
        Args:
            version: Version to delete
            
        Returns:
            bool: Success
        """
        if version not in self.update_packages:
            return False
        
        try:
            # Remove from registry
            del self.update_packages[version]
            
            # Remove from disk
            package_dir = os.path.join(self.updates_dir, version)
            if os.path.exists(package_dir):
                import shutil
                shutil.rmtree(package_dir)
            
            # Update current manifest if needed
            if self.current_manifest and self.current_manifest.version == version:
                # Find newest remaining package
                self.current_manifest = None
                for manifest in self.update_packages.values():
                    if (not self.current_manifest or 
                        manifest.compare_version(self.current_manifest.version) > 0):
                        self.current_manifest = manifest
            
            return True
            
        except Exception as e:
            print(f"Error deleting package {version}: {e}")
            return False
    
    def register_web_routes(self, web_server):
        """Register OTA routes with web server.
        
        Args:
            web_server: SLDK web server instance
        """
        from ..web.handlers import WebHandler
        from ..web.adapters import route
        
        class OTAHandler(WebHandler):
            def __init__(self, server, ota_server):
                super().__init__(server)
                self.ota_server = ota_server
            
            @route("/manifest.json")
            def get_manifest(self, request):
                """Serve current manifest."""
                manifest_json = self.ota_server.get_manifest_json()
                if manifest_json:
                    return self.create_response(
                        manifest_json, 
                        content_type="application/json"
                    )
                else:
                    return self.create_response(
                        '{"error": "No manifest available"}',
                        status=404,
                        content_type="application/json"
                    )
            
            @route("/files/<path:file_path>")
            def get_file(self, request, file_path):
                """Serve update file."""
                content = self.ota_server.get_file_content(file_path)
                if content:
                    return self.create_response(
                        content,
                        content_type="application/octet-stream"
                    )
                else:
                    return self.create_response("File not found", status=404)
            
            @route("/packages")
            def list_packages(self, request):
                """List available packages."""
                packages = self.ota_server.list_packages()
                return self.create_response(
                    json.dumps(packages, indent=2),
                    content_type="application/json"
                )
            
            @route("/admin/ota")
            def ota_admin(self, request):
                """OTA administration interface."""
                from ..web.templates import HTMLBuilder
                
                builder = HTMLBuilder("OTA Administration")
                builder.add_heading("OTA Update Management", 1)
                
                # Package list
                packages = self.ota_server.list_packages()
                if packages:
                    builder.add_heading("Available Packages", 2)
                    
                    # Create table
                    table_html = "<table border='1' style='border-collapse: collapse; width: 100%;'>"
                    table_html += "<tr><th>Version</th><th>Description</th><th>Files</th><th>Size</th><th>Current</th><th>Actions</th></tr>"
                    
                    for pkg in packages:
                        current_marker = "✓" if pkg['is_current'] else ""
                        size_kb = pkg['total_size'] // 1024
                        
                        table_html += f"""
                        <tr>
                            <td>{pkg['version']}</td>
                            <td>{pkg['description']}</td>
                            <td>{pkg['file_count']}</td>
                            <td>{size_kb}KB</td>
                            <td>{current_marker}</td>
                            <td>
                                <a href='/admin/ota/delete/{pkg['version']}'>Delete</a>
                            </td>
                        </tr>
                        """
                    
                    table_html += "</table>"
                    builder.add_to_body(table_html)
                else:
                    builder.add_paragraph("No update packages available.")
                
                # Upload form
                builder.add_heading("Create New Package", 2)
                form = builder.add_form(action="/admin/ota/create", method="POST")
                form.add_label("Version:")
                form.add_input("text", "version", placeholder="1.0.0", required=True)
                form.add_raw("<br><br>")
                form.add_label("Description:")
                form.add_input("text", "description", placeholder="Package description")
                form.add_raw("<br><br>")
                form.add_button("Create Package")
                form.end_form()
                
                return self.create_response(builder.build())
            
            @route("/admin/ota/create", methods=["POST"])
            def create_package(self, request):
                """Create new update package."""
                # Parse form data
                form_data = self.parse_form_data(request)
                version = form_data.get('version', '').strip()
                description = form_data.get('description', '').strip()
                
                if not version:
                    return self.create_response("Version required", status=400)
                
                # Create package
                success, result = self.ota_server.create_package(version, description)
                
                if success:
                    return self.redirect("/admin/ota")
                else:
                    return self.create_response(f"Error creating package: {result}", status=500)
            
            @route("/admin/ota/delete/<version>")
            def delete_package(self, request, version):
                """Delete update package."""
                if self.ota_server.delete_package(version):
                    return self.redirect("/admin/ota")
                else:
                    return self.create_response("Error deleting package", status=500)
        
        # Register handler
        handler = OTAHandler(web_server, self)
        web_server.add_handler(handler)