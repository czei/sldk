"""Deployment tool for SLDK applications.

Handles deployment to CircuitPython devices and remote servers.
"""

import os
import shutil
import time
import json
from pathlib import Path
from .packager import SLDKPackager


class SLDKDeployer:
    """Deploys SLDK applications to various targets.
    
    Supports:
    - Local CircuitPython device deployment
    - Remote deployment via web interface
    - OTA update package creation
    - Development environment setup
    """
    
    def __init__(self, project_dir="."):
        """Initialize deployer.
        
        Args:
            project_dir: Project directory
        """
        self.project_dir = Path(project_dir).resolve()
        self.packager = SLDKPackager(project_dir)
        
        # Deployment targets
        self.circuitpy_drive = None
        self.remote_server = None
        
        # Auto-detect CircuitPython drive
        self._detect_circuitpy_drive()
    
    def _detect_circuitpy_drive(self):
        """Auto-detect CircuitPython drive."""
        # Common mount points for CircuitPython devices
        possible_drives = [
            "/Volumes/CIRCUITPY",  # macOS
            "/media/CIRCUITPY",    # Linux
            "D:\\",                # Windows (common)
            "E:\\",                # Windows (common)
            "F:\\",                # Windows (common)
        ]
        
        for drive in possible_drives:
            if os.path.exists(drive):
                # Check if it looks like a CircuitPython drive
                boot_py = os.path.join(drive, "boot.py")
                if os.path.exists(boot_py):
                    self.circuitpy_drive = drive
                    print(f"Found CircuitPython device at: {drive}")
                    break
    
    def deploy_to_device(self, target=None, backup=True, verify=True):
        """Deploy to CircuitPython device.
        
        Args:
            target: Target drive path (auto-detect if None)
            backup: Create backup before deployment
            verify: Verify files after deployment
            
        Returns:
            tuple: (success, error_message)
        """
        if target is None:
            target = self.circuitpy_drive
        
        if not target:
            return False, "No CircuitPython device found"
        
        if not os.path.exists(target):
            return False, f"Target device not found: {target}"
        
        try:
            print(f"Deploying to CircuitPython device: {target}")
            
            # Create backup if requested
            if backup:
                print("Creating backup...")
                backup_success, backup_path = self._create_device_backup(target)
                if backup_success:
                    print(f"Backup created: {backup_path}")
                else:
                    print(f"Warning: Backup failed: {backup_path}")
            
            # Package application
            print("Packaging application...")
            success, package_path = self.packager.package()
            if not success:
                return False, f"Packaging failed: {package_path}"
            
            # Extract and deploy
            print("Extracting package...")
            success, error = self._extract_package_to_device(package_path, target)
            if not success:
                return False, error
            
            # Verify deployment
            if verify:
                print("Verifying deployment...")
                success, error = self._verify_deployment(target)
                if not success:
                    return False, f"Verification failed: {error}"
            
            print("Deployment complete!")
            print("Device will restart automatically.")
            
            return True, ""
            
        except Exception as e:
            return False, str(e)
    
    def _create_device_backup(self, device_path):
        """Create backup of device contents.
        
        Args:
            device_path: Device mount path
            
        Returns:
            tuple: (success, backup_path_or_error)
        """
        try:
            # Create backup directory
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_dir = self.project_dir / "backups" / f"device_backup_{timestamp}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy all files from device
            for item in os.listdir(device_path):
                source = os.path.join(device_path, item)
                target = backup_dir / item
                
                if os.path.isfile(source):
                    shutil.copy2(source, target)
                elif os.path.isdir(source):
                    shutil.copytree(source, target)
            
            return True, str(backup_dir)
            
        except Exception as e:
            return False, str(e)
    
    def _extract_package_to_device(self, package_path, device_path):
        """Extract package to device.
        
        Args:
            package_path: Package ZIP path
            device_path: Device mount path
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            import zipfile
            import tempfile
            
            # Extract package to temporary directory first
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Extract ZIP
                with zipfile.ZipFile(package_path, 'r') as zf:
                    zf.extractall(temp_path)
                
                # Copy files to device
                for root, dirs, files in os.walk(temp_path):
                    for file in files:
                        source_path = Path(root) / file
                        relative_path = source_path.relative_to(temp_path)
                        target_path = Path(device_path) / relative_path
                        
                        # Create target directory
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Copy file
                        shutil.copy2(source_path, target_path)
                        
                        # Show progress
                        print(f"  Copied: {relative_path}")
            
            return True, ""
            
        except Exception as e:
            return False, str(e)
    
    def _verify_deployment(self, device_path):
        """Verify deployment by checking key files.
        
        Args:
            device_path: Device mount path
            
        Returns:
            tuple: (success, error_message)
        """
        # Check required files
        required_files = [
            "boot.py",
            "code.py", 
            "main.py"
        ]
        
        for file in required_files:
            file_path = os.path.join(device_path, file)
            if not os.path.exists(file_path):
                return False, f"Required file missing: {file}"
        
        # Check that we can read main files
        try:
            code_py_path = os.path.join(device_path, "code.py")
            with open(code_py_path, 'r') as f:
                content = f.read()
                if "import" not in content:
                    return False, "code.py appears invalid"
                    
        except Exception as e:
            return False, f"Cannot read code.py: {e}"
        
        return True, ""
    
    def deploy_via_ota(self, server_url, version=None):
        """Deploy via OTA update server.
        
        Args:
            server_url: OTA server URL
            version: Package version
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            # Package application
            print("Creating OTA update package...")
            success, package_path = self.packager.package(version=version)
            if not success:
                return False, f"Packaging failed: {package_path}"
            
            # Upload to OTA server
            print(f"Uploading to OTA server: {server_url}")
            success, error = self._upload_ota_package(server_url, package_path, version)
            if not success:
                return False, error
            
            print("OTA package deployed successfully!")
            return True, ""
            
        except Exception as e:
            return False, str(e)
    
    def _upload_ota_package(self, server_url, package_path, version):
        """Upload package to OTA server.
        
        Args:
            server_url: Server URL
            package_path: Package file path
            version: Package version
            
        Returns:
            tuple: (success, error_message)
        """
        try:
            import requests
            
            # Prepare upload data
            files = {
                'package': open(package_path, 'rb')
            }
            
            data = {
                'version': version or 'latest',
                'description': f'SLDK Application {version or "latest"}'
            }
            
            # Upload to server
            response = requests.post(
                f"{server_url}/admin/ota/upload",
                files=files,
                data=data,
                timeout=60
            )
            
            if response.status_code == 200:
                return True, ""
            else:
                return False, f"Upload failed: {response.status_code} - {response.text}"
                
        except Exception as e:
            return False, str(e)
        finally:
            # Clean up file handle
            if 'files' in locals():
                files['package'].close()
    
    def create_development_environment(self, target_dir=None):
        """Create development environment setup.
        
        Args:
            target_dir: Target directory (uses dev/ if None)
            
        Returns:
            tuple: (success, error_message)
        """
        if target_dir is None:
            target_dir = self.project_dir / "dev"
        else:
            target_dir = Path(target_dir)
        
        try:
            print(f"Creating development environment: {target_dir}")
            
            # Create directory structure
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy source files
            src_target = target_dir / "src"
            if src_target.exists():
                shutil.rmtree(src_target)
            
            shutil.copytree(self.project_dir / "src", src_target)
            
            # Create development configuration
            dev_config = {
                'platform': 'development',
                'debug': True,
                'hot_reload': True,
                'web_interface': True,
                'simulator': True,
                'log_level': 'DEBUG'
            }
            
            config_path = target_dir / "dev_config.json"
            with open(config_path, 'w') as f:
                json.dump(dev_config, f, indent=2)
            
            # Create run script
            run_script = '''#!/usr/bin/env python3
"""Development runner for SLDK application."""

import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run application
try:
    from main import main
    main()
except KeyboardInterrupt:
    print("\\nShutting down...")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
'''
            
            run_script_path = target_dir / "run_dev.py"
            with open(run_script_path, 'w') as f:
                f.write(run_script)
            
            # Make executable on Unix systems
            try:
                import stat
                run_script_path.chmod(run_script_path.stat().st_mode | stat.S_IEXEC)
            except Exception:
                pass
            
            print("Development environment created!")
            print(f"Run with: cd {target_dir} && python run_dev.py")
            
            return True, ""
            
        except Exception as e:
            return False, str(e)
    
    def monitor_device(self, device_path=None, follow_logs=True):
        """Monitor CircuitPython device.
        
        Args:
            device_path: Device path (auto-detect if None)
            follow_logs: Follow log output
            
        Returns:
            tuple: (success, error_message)
        """
        if device_path is None:
            device_path = self.circuitpy_drive
        
        if not device_path:
            return False, "No CircuitPython device found"
        
        try:
            print(f"Monitoring device: {device_path}")
            print("Press Ctrl+C to stop monitoring")
            
            # Look for REPL output or log files
            if follow_logs:
                # Try to find serial port for REPL
                success, port = self._find_device_serial_port()
                if success:
                    print(f"Connecting to REPL on {port}")
                    self._monitor_serial_output(port)
                else:
                    print("Could not find serial port, monitoring files...")
                    self._monitor_file_changes(device_path)
            
            return True, ""
            
        except KeyboardInterrupt:
            print("\\nMonitoring stopped.")
            return True, ""
        except Exception as e:
            return False, str(e)
    
    def _find_device_serial_port(self):
        """Find CircuitPython device serial port.
        
        Returns:
            tuple: (success, port_or_error)
        """
        try:
            import serial.tools.list_ports
            
            # Look for CircuitPython devices
            for port in serial.tools.list_ports.comports():
                if "CircuitPython" in str(port.description) or "CDC" in str(port.description):
                    return True, port.device
            
            return False, "No CircuitPython serial port found"
            
        except ImportError:
            return False, "pyserial not installed (pip install pyserial)"
        except Exception as e:
            return False, str(e)
    
    def _monitor_serial_output(self, port):
        """Monitor serial output from device.
        
        Args:
            port: Serial port
        """
        try:
            import serial
            
            with serial.Serial(port, 115200, timeout=1) as ser:
                print(f"Connected to {port}")
                
                while True:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        print(line)
                        
        except ImportError:
            print("pyserial not installed (pip install pyserial)")
        except Exception as e:
            print(f"Serial monitoring error: {e}")
    
    def _monitor_file_changes(self, device_path):
        """Monitor device for file changes.
        
        Args:
            device_path: Device mount path
        """
        print("Monitoring for file changes...")
        
        last_modified = {}
        
        while True:
            try:
                # Check modification times
                for root, dirs, files in os.walk(device_path):
                    for file in files:
                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)
                            try:
                                mtime = os.path.getmtime(file_path)
                                
                                if file_path in last_modified:
                                    if mtime > last_modified[file_path]:
                                        print(f"File changed: {file}")
                                        last_modified[file_path] = mtime
                                else:
                                    last_modified[file_path] = mtime
                                    
                            except Exception:
                                pass
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(5)
    
    def set_circuitpy_drive(self, drive_path):
        """Set CircuitPython drive path manually.
        
        Args:
            drive_path: Drive path
        """
        self.circuitpy_drive = drive_path
        print(f"CircuitPython drive set to: {drive_path}")
    
    def list_available_drives(self):
        """List available drives that might be CircuitPython devices.
        
        Returns:
            list: Possible drive paths
        """
        drives = []
        
        # Platform-specific drive detection
        import platform
        system = platform.system()
        
        if system == "Darwin":  # macOS
            volumes_dir = "/Volumes"
            if os.path.exists(volumes_dir):
                for volume in os.listdir(volumes_dir):
                    drives.append(os.path.join(volumes_dir, volume))
        
        elif system == "Linux":
            media_dirs = ["/media", "/mnt"]
            for media_dir in media_dirs:
                if os.path.exists(media_dir):
                    for user_dir in os.listdir(media_dir):
                        user_path = os.path.join(media_dir, user_dir)
                        if os.path.isdir(user_path):
                            for volume in os.listdir(user_path):
                                drives.append(os.path.join(user_path, volume))
        
        elif system == "Windows":
            import string
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    drives.append(drive)
        
        # Filter for likely CircuitPython drives
        circuitpy_drives = []
        for drive in drives:
            if os.path.exists(os.path.join(drive, "boot.py")):
                circuitpy_drives.append(drive)
        
        return circuitpy_drives