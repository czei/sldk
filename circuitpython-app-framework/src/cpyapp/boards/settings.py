"""
Board-specific settings and configuration management.
"""
import os
import json
import sys

# Platform detection
IS_CIRCUITPYTHON = hasattr(sys, 'implementation') and sys.implementation.name == 'circuitpython'


class BoardSettings:
    """Manages board-specific settings and defaults"""
    
    # Default settings for different board types
    _BOARD_DEFAULTS = {
        'matrixportal_s3': {
            'display': {
                'brightness': 0.5,
                'auto_brightness': True,
                'min_brightness': 0.1,
                'max_brightness': 1.0,
                'refresh_rate': 60
            },
            'power': {
                'low_power_threshold': 20,  # Battery percentage
                'sleep_timeout': 300,  # Seconds
                'wake_on_button': True
            },
            'network': {
                'wifi_timeout': 30,
                'retry_count': 3,
                'ap_mode_timeout': 120
            }
        },
        
        'matrixportal_m4': {
            'display': {
                'brightness': 0.5,
                'auto_brightness': True,
                'min_brightness': 0.1,
                'max_brightness': 1.0,
                'refresh_rate': 60
            },
            'power': {
                'low_power_threshold': 20,
                'sleep_timeout': 300,
                'wake_on_button': True
            },
            'network': {
                'wifi_timeout': 45,  # ESP32 can be slower
                'retry_count': 3,
                'ap_mode_timeout': 120
            }
        },
        
        'raspberry_pi': {
            'display': {
                'brightness': 0.7,
                'auto_brightness': False,
                'refresh_rate': 120  # Pi can handle higher refresh
            },
            'power': {
                'always_on': True  # Usually powered from wall
            },
            'network': {
                'wifi_timeout': 20,
                'retry_count': 5,
                'prefer_ethernet': True
            }
        },
        
        'simulator': {
            'display': {
                'brightness': 1.0,
                'auto_brightness': False,
                'refresh_rate': 60
            },
            'power': {
                'always_on': True
            },
            'network': {
                'wifi_timeout': 5,
                'retry_count': 1,
                'simulate_failures': False
            }
        }
    }
    
    def __init__(self, board_name, settings_file=None):
        """
        Initialize board settings
        
        Args:
            board_name: Name of the board
            settings_file: Optional path to settings file
        """
        self.board_name = board_name
        self.settings_file = settings_file or self._get_default_settings_path()
        self._settings = {}
        self._load_settings()
    
    def _get_default_settings_path(self):
        """Get the default settings file path"""
        if IS_CIRCUITPYTHON:
            return f"/settings/{self.board_name}_settings.json"
        else:
            # Development environment
            return os.path.expanduser(f"~/.config/cpyapp/{self.board_name}_settings.json")
    
    def _load_settings(self):
        """Load settings from file and apply defaults"""
        # Start with board defaults
        self._settings = self._BOARD_DEFAULTS.get(self.board_name, {}).copy()
        
        # Load from file if exists
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    file_settings = json.load(f)
                    self._deep_update(self._settings, file_settings)
            except Exception as e:
                print(f"Error loading settings: {e}")
    
    def _deep_update(self, base, updates):
        """Deep update dictionary"""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value
    
    def get(self, key, default=None):
        """
        Get a setting value
        
        Args:
            key: Setting key (supports dot notation: 'display.brightness')
            default: Default value if not found
            
        Returns:
            Setting value
        """
        keys = key.split('.')
        value = self._settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key, value):
        """
        Set a setting value
        
        Args:
            key: Setting key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        target = self._settings
        
        # Navigate to the parent dict
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        # Set the value
        target[keys[-1]] = value
    
    def save(self):
        """Save settings to file"""
        # Create directory if needed
        settings_dir = os.path.dirname(self.settings_file)
        if settings_dir and not os.path.exists(settings_dir):
            os.makedirs(settings_dir)
        
        # Save settings
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self._settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def reset_to_defaults(self):
        """Reset settings to board defaults"""
        self._settings = self._BOARD_DEFAULTS.get(self.board_name, {}).copy()
        self.save()
    
    def get_all(self):
        """Get all settings"""
        return self._settings.copy()
    
    def update_from_env(self):
        """Update settings from environment variables"""
        # Look for environment variables with CPYAPP_ prefix
        prefix = f"CPYAPP_{self.board_name.upper()}_"
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Convert env var name to setting key
                setting_key = key[len(prefix):].lower().replace('_', '.')
                
                # Try to parse value as JSON, fallback to string
                try:
                    parsed_value = json.loads(value)
                except:
                    parsed_value = value
                
                self.set(setting_key, parsed_value)


class BoardSettingsManager:
    """Manages settings for multiple boards"""
    
    def __init__(self, base_path=None):
        """
        Initialize settings manager
        
        Args:
            base_path: Base path for settings files
        """
        if base_path is None:
            if IS_CIRCUITPYTHON:
                base_path = "/settings"
            else:
                base_path = os.path.expanduser("~/.config/cpyapp")
        
        self.base_path = base_path
        self._board_settings = {}
    
    def get_board_settings(self, board_name):
        """
        Get settings for a specific board
        
        Args:
            board_name: Board name
            
        Returns:
            BoardSettings instance
        """
        if board_name not in self._board_settings:
            settings_file = os.path.join(self.base_path, f"{board_name}_settings.json")
            self._board_settings[board_name] = BoardSettings(board_name, settings_file)
        
        return self._board_settings[board_name]
    
    def export_settings(self, board_name, export_file):
        """
        Export board settings to file
        
        Args:
            board_name: Board name
            export_file: Export file path
        """
        settings = self.get_board_settings(board_name)
        
        with open(export_file, 'w') as f:
            json.dump(settings.get_all(), f, indent=2)
    
    def import_settings(self, board_name, import_file):
        """
        Import board settings from file
        
        Args:
            board_name: Board name
            import_file: Import file path
        """
        with open(import_file, 'r') as f:
            imported = json.load(f)
        
        settings = self.get_board_settings(board_name)
        settings._deep_update(settings._settings, imported)
        settings.save()


def get_runtime_config(board, settings_manager=None):
    """
    Get runtime configuration by merging board config with settings
    
    Args:
        board: Board instance
        settings_manager: Optional settings manager
        
    Returns:
        dict: Runtime configuration
    """
    config = {
        'board': {
            'name': board.name,
            'display_name': board.display_name,
            'manufacturer': board.manufacturer,
            'capabilities': list(board.capabilities)
        },
        'display': board.display_config.copy(),
        'network': board.network_config.copy(),
        'power': board.power_config.copy(),
        'pins': board.pin_mappings.copy()
    }
    
    # Merge with settings if available
    if settings_manager:
        board_settings = settings_manager.get_board_settings(board.name)
        
        # Update display settings
        if 'display' in board_settings._settings:
            config['display'].update(board_settings._settings['display'])
        
        # Update network settings
        if 'network' in board_settings._settings:
            config['network'].update(board_settings._settings['network'])
        
        # Update power settings
        if 'power' in board_settings._settings:
            config['power'].update(board_settings._settings['power'])
    
    return config