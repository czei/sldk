"""Update manifest for OTA updates.

Manages versioning, file lists, and integrity checking.
"""

import json
import hashlib


class UpdateManifest:
    """Manages update manifest for OTA system.
    
    The manifest describes an update package:
    - Version information
    - File list with checksums
    - Dependencies and requirements
    - Update instructions
    """
    
    def __init__(self, version=None, description=None):
        """Initialize update manifest.
        
        Args:
            version: Version string (e.g., "1.2.3")
            description: Human-readable description
        """
        self.version = version or "1.0.0"
        self.description = description or "SLDK Update"
        self.files = {}  # path -> {size, checksum, required}
        self.dependencies = []
        self.requirements = {
            'circuitpython_version': '8.0.0',
            'memory_required': 50000,  # bytes
            'storage_required': 100000  # bytes
        }
        self.pre_update_scripts = []
        self.post_update_scripts = []
    
    def add_file(self, path, content=None, file_path=None, required=True):
        """Add file to manifest.
        
        Args:
            path: Target path on device
            content: File content (bytes or str)
            file_path: Path to source file (alternative to content)
            required: Whether file is required for update
        """
        if content is None and file_path is None:
            raise ValueError("Must provide either content or file_path")
        
        if file_path and content is None:
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
            except (OSError, IOError) as e:
                raise ValueError(f"Cannot read file {file_path}: {e}")
        
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        # Calculate checksum
        checksum = hashlib.sha256(content).hexdigest()
        
        self.files[path] = {
            'size': len(content),
            'checksum': checksum,
            'required': required
        }
    
    def add_dependency(self, name, version_spec="*"):
        """Add dependency requirement.
        
        Args:
            name: Package name
            version_spec: Version specification (e.g., ">=1.0.0")
        """
        self.dependencies.append({
            'name': name,
            'version': version_spec
        })
    
    def set_requirement(self, key, value):
        """Set system requirement.
        
        Args:
            key: Requirement key
            value: Requirement value
        """
        self.requirements[key] = value
    
    def add_script(self, script_content, stage='post'):
        """Add update script.
        
        Args:
            script_content: Python code to execute
            stage: 'pre' or 'post' update
        """
        if stage == 'pre':
            self.pre_update_scripts.append(script_content)
        elif stage == 'post':
            self.post_update_scripts.append(script_content)
        else:
            raise ValueError("Stage must be 'pre' or 'post'")
    
    def to_dict(self):
        """Convert manifest to dictionary.
        
        Returns:
            dict: Manifest data
        """
        return {
            'version': self.version,
            'description': self.description,
            'files': self.files,
            'dependencies': self.dependencies,
            'requirements': self.requirements,
            'pre_update_scripts': self.pre_update_scripts,
            'post_update_scripts': self.post_update_scripts
        }
    
    def to_json(self, indent=2):
        """Convert manifest to JSON string.
        
        Args:
            indent: JSON indentation
            
        Returns:
            str: JSON manifest
        """
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_dict(cls, data):
        """Create manifest from dictionary.
        
        Args:
            data: Manifest dictionary
            
        Returns:
            UpdateManifest: Parsed manifest
        """
        manifest = cls(
            version=data.get('version', '1.0.0'),
            description=data.get('description', 'SLDK Update')
        )
        
        manifest.files = data.get('files', {})
        manifest.dependencies = data.get('dependencies', [])
        manifest.requirements = data.get('requirements', {})
        manifest.pre_update_scripts = data.get('pre_update_scripts', [])
        manifest.post_update_scripts = data.get('post_update_scripts', [])
        
        return manifest
    
    @classmethod
    def from_json(cls, json_str):
        """Create manifest from JSON string.
        
        Args:
            json_str: JSON manifest string
            
        Returns:
            UpdateManifest: Parsed manifest
        """
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Invalid manifest JSON: {e}")
    
    def validate(self):
        """Validate manifest data.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check version format
        if not self.version or not isinstance(self.version, str):
            return False, "Invalid version format"
        
        # Check files
        for path, info in self.files.items():
            if not isinstance(path, str) or not path:
                return False, f"Invalid file path: {path}"
            
            required_keys = ['size', 'checksum', 'required']
            for key in required_keys:
                if key not in info:
                    return False, f"Missing {key} for file {path}"
            
            if not isinstance(info['size'], int) or info['size'] < 0:
                return False, f"Invalid size for file {path}"
            
            if not isinstance(info['checksum'], str) or len(info['checksum']) != 64:
                return False, f"Invalid checksum for file {path}"
        
        # Check dependencies
        for dep in self.dependencies:
            if not isinstance(dep, dict) or 'name' not in dep:
                return False, "Invalid dependency format"
        
        # Check requirements
        if not isinstance(self.requirements, dict):
            return False, "Invalid requirements format"
        
        return True, ""
    
    def compare_version(self, other_version):
        """Compare version with another version.
        
        Args:
            other_version: Version string to compare
            
        Returns:
            int: -1 if older, 0 if same, 1 if newer
        """
        def parse_version(version_str):
            """Parse version string into comparable tuple."""
            try:
                parts = version_str.split('.')
                return tuple(int(part) for part in parts)
            except (ValueError, AttributeError):
                return (0, 0, 0)
        
        self_ver = parse_version(self.version)
        other_ver = parse_version(other_version)
        
        if self_ver < other_ver:
            return -1
        elif self_ver > other_ver:
            return 1
        else:
            return 0
    
    def calculate_total_size(self):
        """Calculate total size of all files.
        
        Returns:
            int: Total size in bytes
        """
        return sum(info['size'] for info in self.files.values())
    
    def get_required_files(self):
        """Get list of required file paths.
        
        Returns:
            list: Required file paths
        """
        return [path for path, info in self.files.items() if info['required']]
    
    def get_optional_files(self):
        """Get list of optional file paths.
        
        Returns:
            list: Optional file paths
        """
        return [path for path, info in self.files.items() if not info['required']]