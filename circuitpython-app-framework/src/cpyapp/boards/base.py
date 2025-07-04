"""
Base board configuration class for CircuitPython applications.
Provides abstract interface for all board configurations.
"""
from abc import ABC, abstractmethod
import sys

# Platform detection
IS_CIRCUITPYTHON = hasattr(sys, 'implementation') and sys.implementation.name == 'circuitpython'


class BoardCapabilities:
    """Enumeration of board capabilities"""
    # Display capabilities
    HAS_RGB_MATRIX = "rgb_matrix"
    HAS_OLED = "oled"
    HAS_EPAPER = "epaper"
    
    # Network capabilities
    HAS_WIFI = "wifi"
    HAS_ETHERNET = "ethernet"
    HAS_BLUETOOTH = "bluetooth"
    
    # Storage capabilities
    HAS_SD_CARD = "sd_card"
    HAS_QSPI_FLASH = "qspi_flash"
    
    # Other hardware
    HAS_RTC = "rtc"
    HAS_BATTERY = "battery"
    HAS_ACCELEROMETER = "accelerometer"
    HAS_TEMPERATURE_SENSOR = "temperature"
    HAS_NEOPIXELS = "neopixels"


class BoardBase(ABC):
    """
    Abstract base class for board configurations.
    All board implementations must inherit from this class.
    """
    
    def __init__(self):
        """Initialize the board configuration"""
        self._capabilities = set()
        self._pin_mappings = {}
        self._display_config = {}
        self._network_config = {}
        self._power_config = {}
        
    @property
    @abstractmethod
    def name(self):
        """
        Get the board name
        
        Returns:
            str: Board name identifier
        """
        pass
    
    @property
    @abstractmethod
    def display_name(self):
        """
        Get the human-readable board name
        
        Returns:
            str: Human-readable board name
        """
        pass
    
    @property
    @abstractmethod
    def manufacturer(self):
        """
        Get the board manufacturer
        
        Returns:
            str: Manufacturer name
        """
        pass
    
    @property
    def capabilities(self):
        """
        Get the set of board capabilities
        
        Returns:
            set: Set of capability strings from BoardCapabilities
        """
        return self._capabilities
    
    def has_capability(self, capability):
        """
        Check if the board has a specific capability
        
        Args:
            capability: Capability to check (from BoardCapabilities)
            
        Returns:
            bool: True if board has the capability
        """
        return capability in self._capabilities
    
    @property
    def display_config(self):
        """
        Get display configuration
        
        Returns:
            dict: Display configuration parameters
        """
        return self._display_config
    
    @property
    def pin_mappings(self):
        """
        Get pin mappings for the board
        
        Returns:
            dict: Pin name to pin number/object mappings
        """
        return self._pin_mappings
    
    @property
    def network_config(self):
        """
        Get network configuration
        
        Returns:
            dict: Network configuration parameters
        """
        return self._network_config
    
    @property
    def power_config(self):
        """
        Get power configuration
        
        Returns:
            dict: Power configuration parameters
        """
        return self._power_config
    
    @abstractmethod
    def setup_display(self):
        """
        Set up the display hardware
        
        Returns:
            Display object appropriate for the board
        """
        pass
    
    @abstractmethod
    def setup_network(self):
        """
        Set up network hardware (WiFi, Ethernet, etc.)
        
        Returns:
            Network interface object or None if not available
        """
        pass
    
    def setup_rtc(self):
        """
        Set up real-time clock if available
        
        Returns:
            RTC object or None if not available
        """
        if not self.has_capability(BoardCapabilities.HAS_RTC):
            return None
        return self._setup_rtc_hardware()
    
    def _setup_rtc_hardware(self):
        """Override in subclass to set up RTC hardware"""
        return None
    
    def setup_storage(self):
        """
        Set up additional storage (SD card, QSPI flash, etc.)
        
        Returns:
            Storage object or None if not available
        """
        return None
    
    def get_pin(self, pin_name):
        """
        Get a pin by name
        
        Args:
            pin_name: Name of the pin
            
        Returns:
            Pin object or number, or None if not found
        """
        return self._pin_mappings.get(pin_name)
    
    def set_display_brightness(self, brightness):
        """
        Set display brightness if supported
        
        Args:
            brightness: Brightness level (0.0 to 1.0)
        """
        pass
    
    def get_battery_level(self):
        """
        Get battery level if available
        
        Returns:
            float: Battery level (0.0 to 1.0) or None if not available
        """
        if not self.has_capability(BoardCapabilities.HAS_BATTERY):
            return None
        return self._get_battery_level_hardware()
    
    def _get_battery_level_hardware(self):
        """Override in subclass to get battery level"""
        return None
    
    def get_temperature(self):
        """
        Get temperature if sensor available
        
        Returns:
            float: Temperature in Celsius or None if not available
        """
        if not self.has_capability(BoardCapabilities.HAS_TEMPERATURE_SENSOR):
            return None
        return self._get_temperature_hardware()
    
    def _get_temperature_hardware(self):
        """Override in subclass to get temperature"""
        return None
    
    def validate_hardware(self):
        """
        Validate that expected hardware is present and functional
        
        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []
        
        # Check display
        if BoardCapabilities.HAS_RGB_MATRIX in self._capabilities:
            try:
                display = self.setup_display()
                if display is None:
                    errors.append("RGB matrix display not found")
            except Exception as e:
                errors.append(f"Display setup failed: {e}")
        
        # Check network
        if BoardCapabilities.HAS_WIFI in self._capabilities:
            try:
                network = self.setup_network()
                if network is None:
                    errors.append("WiFi hardware not found")
            except Exception as e:
                errors.append(f"Network setup failed: {e}")
        
        return len(errors) == 0, errors
    
    def __repr__(self):
        """String representation of the board"""
        return f"<{self.__class__.__name__} '{self.display_name}' capabilities={len(self._capabilities)}>"