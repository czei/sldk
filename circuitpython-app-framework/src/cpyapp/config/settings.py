"""
Settings manager for handling user configuration.
Copyright 2024 3DUPFitters LLC
"""
import json

from ..utils.error_handler import ErrorHandler
from ..utils.colors import ColorUtils

# Initialize logger
logger = ErrorHandler("error_log")


class SettingsManager:
    """
    Manages application settings with persistence to a JSON file
    """
    
    def __init__(self, filename):
        """
        Initialize the settings manager
        
        Args:
            filename: The name of the settings file
        """
        self.filename = filename
        self.settings = self.load_settings()
        self.scroll_speed = {"Slow": 0.06, "Medium": 0.04, "Fast": 0.02}

        # Set default framework settings if not present
        self._set_default_settings()

    def _set_default_settings(self):
        """Set default framework settings if not present."""
        # Core framework settings
        if self.settings.get("brightness_scale") is None:
            self.settings["brightness_scale"] = "0.5"
        if self.settings.get("default_color") is None:
            self.settings["default_color"] = ColorUtils.colors["Yellow"]
        if self.settings.get("scroll_speed") is None:
            self.settings["scroll_speed"] = "Medium"
        if self.settings.get("message_delay") is None:
            self.settings["message_delay"] = 4
        if self.settings.get("update_interval") is None:
            self.settings["update_interval"] = 300
        if self.settings.get("show_splash") is None:
            self.settings["show_splash"] = True
        if self.settings.get("ota_repo") is None:
            self.settings["ota_repo"] = ""
        if self.settings.get("ota_token") is None:
            self.settings["ota_token"] = ""
        if self.settings.get("use_prerelease") is None:
            self.settings["use_prerelease"] = False

    def get_scroll_speed(self):
        """
        Get the scroll speed based on the current setting
        
        Returns:
            The scroll speed in seconds per pixel
        """
        return self.scroll_speed[self.settings["scroll_speed"]]

    @staticmethod
    def get_pretty_name(settings_name):
        """
        Convert a settings key to a display-friendly name
        
        Args:
            settings_name: The settings key
            
        Returns:
            A display-friendly name
        """
        # Change underscore to spaces
        new_name = settings_name.replace("_", " ")
        return " ".join(word[0].upper() + word[1:] for word in new_name.split(' '))

    def load_settings(self):
        """
        Load settings from the settings file
        
        Returns:
            A dictionary of settings
        """
        logger.info(f"Loading settings {self.filename}")
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except OSError:
            return {}

    def save_settings(self):
        """Save settings to the settings file"""
        logger.info(f"Saving settings {self.filename}")
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.settings, f)
        except OSError as e:
            logger.error(e, f"Error saving settings to {self.filename}")
            
    def get(self, key, default=None):
        """
        Get a setting by key with a default value
        
        Args:
            key: The settings key
            default: The default value if the key is not found
            
        Returns:
            The setting value, or the default if not found
        """
        value = self.settings.get(key, default)
        
        # Special handling for boolean settings that might be stored as strings
        # This can happen with CircuitPython's JSON parser
        if key in ["group_by_park", "skip_closed", "skip_meet", "use_prerelease"] and isinstance(value, str):
            return value.lower() == "true"
            
        return value
        
    def set(self, key, value):
        """
        Set a setting by key
        
        Args:
            key: The settings key
            value: The value to set
        """
        self.settings[key] = value