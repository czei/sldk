"""OTA update client for CircuitPython devices.

Handles downloading and applying updates safely.
"""

import gc
import json
import hashlib
from .manifest import UpdateManifest

try:
    # CircuitPython
    import adafruit_requests as requests
    import storage
    import microcontroller
    import supervisor
    PLATFORM = 'circuitpython'
except ImportError:
    try:
        # Desktop Python
        import requests
        PLATFORM = 'desktop'
    except ImportError:
        requests = None
        PLATFORM = 'unknown'


class OTAClient:
    """OTA update client for CircuitPython devices.
    
    Handles the client side of OTA updates:
    - Check for updates
    - Download update packages
    - Verify integrity
    - Apply updates safely
    """
    
    def __init__(self, update_server_url, current_version="1.0.0", 
                 update_dir="/updates", backup_dir="/backup"):
        """Initialize OTA client.
        
        Args:
            update_server_url: URL of update server
            current_version: Current application version
            update_dir: Directory for downloaded updates
            backup_dir: Directory for backups
        """
        self.server_url = update_server_url.rstrip('/')
        self.current_version = current_version
        self.update_dir = update_dir
        self.backup_dir = backup_dir
        self.download_timeout = 30
        self.chunk_size = 1024
        
        # Status tracking
        self.last_check = None
        self.available_update = None
        self.update_in_progress = False
        
        # Callbacks
        self.on_update_available = None
        self.on_update_progress = None
        self.on_update_complete = None
        self.on_update_error = None
    
    def set_callbacks(self, on_available=None, on_progress=None, 
                     on_complete=None, on_error=None):
        """Set update callbacks.
        
        Args:
            on_available: Called when update is available
            on_progress: Called during download/install
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
    
    def check_for_updates(self):
        """Check if updates are available.
        
        Returns:
            tuple: (has_update, manifest_or_error)
        """
        if not requests:
            return False, "Requests library not available"
        
        try:
            # Request current manifest
            url = f"{self.server_url}/manifest.json"
            response = requests.get(url, timeout=self.download_timeout)
            
            if response.status_code != 200:
                return False, f"Server error: {response.status_code}"
            
            # Parse manifest
            try:
                manifest_data = response.json()
                manifest = UpdateManifest.from_dict(manifest_data)
            except (ValueError, json.JSONDecodeError) as e:
                return False, f"Invalid manifest: {e}"
            
            # Validate manifest
            is_valid, error = manifest.validate()
            if not is_valid:
                return False, f"Invalid manifest: {error}"
            
            # Check if newer version
            if manifest.compare_version(self.current_version) > 0:
                self.available_update = manifest
                if self.on_update_available:
                    self.on_update_available(manifest)
                return True, manifest
            
            return False, "No updates available"
            
        except Exception as e:
            error_msg = f"Update check failed: {e}"
            if self.on_update_error:
                self.on_update_error(error_msg)
            return False, error_msg
        finally:
            # Clean up response
            if 'response' in locals():
                try:
                    response.close()
                except Exception:
                    pass
            gc.collect()
    
    def download_update(self, manifest=None):
        """Download update package.
        
        Args:
            manifest: Update manifest (uses available_update if None)
            
        Returns:
            tuple: (success, error_message)
        """
        if manifest is None:
            manifest = self.available_update
        
        if not manifest:
            return False, "No update manifest available"
        
        if not requests:
            return False, "Requests library not available"
        
        try:
            self.update_in_progress = True
            
            # Ensure update directory exists
            self._ensure_directory(self.update_dir)
            
            # Check available space
            if PLATFORM == 'circuitpython':
                try:
                    import os
                    stat = os.statvfs('/')
                    free_space = stat[1] * stat[3]  # block_size * free_blocks
                    
                    required_space = manifest.calculate_total_size() * 2  # Files + backup
                    if free_space < required_space:
                        return False, f"Insufficient storage: {free_space} < {required_space}"
                except Exception:
                    pass  # Continue without space check
            
            # Download files
            total_files = len(manifest.files)
            completed_files = 0
            
            for file_path, file_info in manifest.files.items():
                if self.on_update_progress:
                    progress = (completed_files / total_files) * 0.8  # Reserve 20% for install
                    self.on_update_progress(f"Downloading {file_path}", progress)
                
                # Download file
                success, error = self._download_file(file_path, file_info)
                if not success:
                    return False, f"Failed to download {file_path}: {error}"
                
                completed_files += 1
                gc.collect()  # Free memory after each file
            
            # Save manifest
            manifest_path = f"{self.update_dir}/manifest.json"
            try:
                with open(manifest_path, 'w') as f:
                    f.write(manifest.to_json())
            except (OSError, IOError) as e:
                return False, f"Failed to save manifest: {e}"
            
            if self.on_update_progress:
                self.on_update_progress("Download complete", 0.8)
            
            return True, ""
            
        except Exception as e:
            error_msg = f"Download failed: {e}"
            if self.on_update_error:
                self.on_update_error(error_msg)
            return False, error_msg
        finally:
            gc.collect()
    
    def _download_file(self, file_path, file_info):
        """Download a single file.
        
        Args:
            file_path: Target file path
            file_info: File metadata dict
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            # Request file from server
            url = f"{self.server_url}/files/{file_path.lstrip('/')}"
            response = requests.get(url, timeout=self.download_timeout)
            
            if response.status_code != 200:
                return False, f"Server error: {response.status_code}"
            
            # Download content
            content = response.content
            
            # Verify size
            if len(content) != file_info['size']:
                return False, f"Size mismatch: {len(content)} != {file_info['size']}"
            
            # Verify checksum
            actual_checksum = hashlib.sha256(content).hexdigest()
            if actual_checksum != file_info['checksum']:
                return False, "Checksum mismatch"
            
            # Save to update directory
            local_path = f"{self.update_dir}/{file_path.lstrip('/')}"
            self._ensure_directory_for_file(local_path)
            
            with open(local_path, 'wb') as f:
                f.write(content)
            
            return True, ""
            
        except Exception as e:
            return False, str(e)
        finally:
            if 'response' in locals():
                try:
                    response.close()
                except Exception:
                    pass
    
    def apply_update(self, manifest=None):
        """Apply downloaded update.
        
        Args:
            manifest: Update manifest (loads from file if None)
            
        Returns:
            tuple: (success, error_message)
        """
        if not manifest:
            # Load manifest from update directory
            manifest_path = f"{self.update_dir}/manifest.json"
            try:
                with open(manifest_path, 'r') as f:
                    manifest_data = json.loads(f.read())
                manifest = UpdateManifest.from_dict(manifest_data)
            except Exception as e:
                return False, f"Cannot load manifest: {e}"
        
        try:
            if self.on_update_progress:
                self.on_update_progress("Preparing update", 0.8)
            
            # Create backup
            backup_success, backup_error = self._create_backup(manifest)
            if not backup_success:
                return False, f"Backup failed: {backup_error}"
            
            if self.on_update_progress:
                self.on_update_progress("Installing files", 0.85)
            
            # Run pre-update scripts
            for script in manifest.pre_update_scripts:
                try:
                    exec(script)
                except Exception as e:
                    print(f"Pre-update script error: {e}")
            
            # Install files
            install_success, install_error = self._install_files(manifest)
            if not install_success:
                # Restore from backup
                self._restore_backup(manifest)
                return False, f"Install failed: {install_error}"
            
            if self.on_update_progress:
                self.on_update_progress("Finalizing update", 0.95)
            
            # Run post-update scripts
            for script in manifest.post_update_scripts:
                try:
                    exec(script)
                except Exception as e:
                    print(f"Post-update script error: {e}")
            
            # Update version
            self.current_version = manifest.version
            
            # Clean up
            self._cleanup_update_files()
            
            if self.on_update_progress:
                self.on_update_progress("Update complete", 1.0)
            
            if self.on_update_complete:
                self.on_update_complete(manifest.version)
            
            return True, ""
            
        except Exception as e:
            error_msg = f"Update failed: {e}"
            if self.on_update_error:
                self.on_update_error(error_msg)
            return False, error_msg
        finally:
            self.update_in_progress = False
            gc.collect()
    
    def _create_backup(self, manifest):
        """Create backup of current files.
        
        Args:
            manifest: Update manifest
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            self._ensure_directory(self.backup_dir)
            
            for file_path in manifest.files.keys():
                if self._file_exists(file_path):
                    backup_path = f"{self.backup_dir}/{file_path.lstrip('/')}"
                    self._ensure_directory_for_file(backup_path)
                    
                    # Copy file to backup
                    with open(file_path, 'rb') as src:
                        with open(backup_path, 'wb') as dst:
                            # Copy in chunks to save memory
                            while True:
                                chunk = src.read(self.chunk_size)
                                if not chunk:
                                    break
                                dst.write(chunk)
            
            return True, ""
            
        except Exception as e:
            return False, str(e)
    
    def _install_files(self, manifest):
        """Install files from update directory.
        
        Args:
            manifest: Update manifest
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            for file_path in manifest.files.keys():
                source_path = f"{self.update_dir}/{file_path.lstrip('/')}"
                
                # Ensure target directory exists
                self._ensure_directory_for_file(file_path)
                
                # Copy file
                with open(source_path, 'rb') as src:
                    with open(file_path, 'wb') as dst:
                        while True:
                            chunk = src.read(self.chunk_size)
                            if not chunk:
                                break
                            dst.write(chunk)
            
            return True, ""
            
        except Exception as e:
            return False, str(e)
    
    def _restore_backup(self, manifest):
        """Restore files from backup.
        
        Args:
            manifest: Update manifest
        """
        try:
            for file_path in manifest.files.keys():
                backup_path = f"{self.backup_dir}/{file_path.lstrip('/')}"
                
                if self._file_exists(backup_path):
                    with open(backup_path, 'rb') as src:
                        with open(file_path, 'wb') as dst:
                            while True:
                                chunk = src.read(self.chunk_size)
                                if not chunk:
                                    break
                                dst.write(chunk)
        except Exception as e:
            print(f"Backup restore failed: {e}")
    
    def _cleanup_update_files(self):
        """Clean up downloaded update files."""
        try:
            import os
            
            # Remove update directory contents
            for root, dirs, files in os.walk(self.update_dir):
                for file in files:
                    try:
                        os.remove(os.path.join(root, file))
                    except Exception:
                        pass
                        
        except Exception:
            pass  # Ignore cleanup errors
    
    def _ensure_directory(self, path):
        """Ensure directory exists."""
        try:
            import os
            os.makedirs(path, exist_ok=True)
        except Exception:
            pass  # Ignore directory creation errors
    
    def _ensure_directory_for_file(self, file_path):
        """Ensure directory exists for file path."""
        try:
            import os
            directory = os.path.dirname(file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
        except Exception:
            pass
    
    def _file_exists(self, path):
        """Check if file exists."""
        try:
            with open(path, 'r'):
                return True
        except Exception:
            return False
    
    def reboot_device(self):
        """Reboot the device to complete update."""
        if PLATFORM == 'circuitpython':
            try:
                microcontroller.reset()
            except Exception:
                try:
                    supervisor.reload()
                except Exception:
                    print("Cannot reboot - please manually restart")
        else:
            print("Reboot not supported on this platform")