"""
Hardware abstraction layer for board components.
Provides unified interface for hardware access across different boards.
"""
import sys
import time

# Platform detection
IS_CIRCUITPYTHON = hasattr(sys, 'implementation') and sys.implementation.name == 'circuitpython'

if IS_CIRCUITPYTHON:
    import board
    import digitalio
    import analogio
    import pwmio
else:
    # Mock implementations for development
    class MockPin:
        """Mock pin for development"""
        def __init__(self, name):
            self.name = name
    
    class MockDigitalIO:
        """Mock digital I/O for development"""
        def __init__(self, pin):
            self.pin = pin
            self._value = False
            self._direction = None
            self._pull = None
        
        @property
        def value(self):
            return self._value
        
        @value.setter
        def value(self, val):
            self._value = bool(val)
        
        @property
        def direction(self):
            return self._direction
        
        @direction.setter
        def direction(self, val):
            self._direction = val
        
        @property
        def pull(self):
            return self._pull
        
        @pull.setter
        def pull(self, val):
            self._pull = val
        
        def deinit(self):
            pass
    
    # Create mock board module
    class board:
        """Mock board module for development"""
        pass
    
    digitalio = type('digitalio', (), {
        'DigitalInOut': MockDigitalIO,
        'Direction': type('Direction', (), {
            'INPUT': 'input',
            'OUTPUT': 'output'
        }),
        'Pull': type('Pull', (), {
            'UP': 'up',
            'DOWN': 'down'
        })
    })


class PinMapper:
    """Maps logical pin names to physical pins"""
    
    def __init__(self, mappings=None):
        """
        Initialize pin mapper
        
        Args:
            mappings: Dict of logical name to physical pin mappings
        """
        self._mappings = mappings or {}
        self._cache = {}
    
    def add_mapping(self, logical_name, physical_pin):
        """Add a pin mapping"""
        self._mappings[logical_name] = physical_pin
    
    def get_pin(self, name):
        """Get physical pin by logical name"""
        if name in self._cache:
            return self._cache[name]
        
        pin = self._mappings.get(name)
        if pin is None and IS_CIRCUITPYTHON and hasattr(board, name):
            pin = getattr(board, name)
        
        if pin is not None:
            self._cache[name] = pin
        
        return pin
    
    def get_all_mappings(self):
        """Get all pin mappings"""
        return self._mappings.copy()


class DisplayController:
    """Controls display hardware"""
    
    def __init__(self, display_type, config):
        """
        Initialize display controller
        
        Args:
            display_type: Type of display (rgb_matrix, oled, etc.)
            config: Display configuration
        """
        self.display_type = display_type
        self.config = config
        self._brightness = config.get('brightness', 1.0)
        self._display = None
    
    def initialize(self):
        """Initialize the display hardware"""
        if self.display_type == 'rgb_matrix':
            return self._init_rgb_matrix()
        elif self.display_type == 'oled':
            return self._init_oled()
        elif self.display_type == 'simulator':
            return self._init_simulator()
        else:
            raise ValueError(f"Unknown display type: {self.display_type}")
    
    def _init_rgb_matrix(self):
        """Initialize RGB LED matrix"""
        if not IS_CIRCUITPYTHON:
            return self._init_simulator()
        
        try:
            from rgbmatrix import RGBMatrix
            import displayio
            
            displayio.release_displays()
            
            matrix = RGBMatrix(
                width=self.config.get('width', 64),
                height=self.config.get('height', 32),
                bit_depth=self.config.get('bit_depth', 4),
                rgb_pins=self.config.get('rgb_pins'),
                addr_pins=self.config.get('addr_pins'),
                clock_pin=self.config.get('clock_pin'),
                latch_pin=self.config.get('latch_pin'),
                output_enable_pin=self.config.get('output_enable_pin')
            )
            
            self._display = matrix
            return matrix
            
        except ImportError as e:
            raise RuntimeError(f"RGB matrix support not available: {e}")
    
    def _init_oled(self):
        """Initialize OLED display"""
        # Implementation for OLED displays
        raise NotImplementedError("OLED support not yet implemented")
    
    def _init_simulator(self):
        """Initialize simulator display"""
        # Return None - the display factory will handle simulator setup
        return None
    
    def set_brightness(self, brightness):
        """
        Set display brightness
        
        Args:
            brightness: Brightness level (0.0 to 1.0)
        """
        self._brightness = max(0.0, min(1.0, brightness))
        
        if self._display and hasattr(self._display, 'brightness'):
            self._display.brightness = self._brightness
    
    def get_brightness(self):
        """Get current brightness level"""
        return self._brightness


class NetworkController:
    """Controls network hardware (WiFi, Ethernet, etc.)"""
    
    def __init__(self, network_type, config):
        """
        Initialize network controller
        
        Args:
            network_type: Type of network (wifi, ethernet, etc.)
            config: Network configuration
        """
        self.network_type = network_type
        self.config = config
        self._interface = None
    
    def initialize(self):
        """Initialize network hardware"""
        if self.network_type == 'wifi':
            return self._init_wifi()
        elif self.network_type == 'ethernet':
            return self._init_ethernet()
        elif self.network_type == 'simulator':
            return self._init_simulator()
        else:
            raise ValueError(f"Unknown network type: {self.network_type}")
    
    def _init_wifi(self):
        """Initialize WiFi"""
        if not IS_CIRCUITPYTHON:
            return self._init_simulator()
        
        wifi_module = self.config.get('module', 'native')
        
        if wifi_module == 'native':
            try:
                import wifi
                self._interface = wifi
                return wifi
            except ImportError:
                pass
        
        if wifi_module == 'esp32' or wifi_module == 'native':
            # Try ESP32 co-processor
            try:
                from adafruit_esp32spi import adafruit_esp32spi
                import busio
                
                esp32_cs = self.config.get('esp32_cs')
                esp32_ready = self.config.get('esp32_ready')
                esp32_reset = self.config.get('esp32_reset')
                
                spi = busio.SPI(
                    self.config.get('spi_clock'),
                    self.config.get('spi_mosi'),
                    self.config.get('spi_miso')
                )
                
                esp = adafruit_esp32spi.ESP_SPIcontrol(
                    spi, esp32_cs, esp32_ready, esp32_reset
                )
                
                self._interface = esp
                return esp
                
            except ImportError:
                pass
        
        raise RuntimeError("WiFi hardware not available")
    
    def _init_ethernet(self):
        """Initialize Ethernet"""
        raise NotImplementedError("Ethernet support not yet implemented")
    
    def _init_simulator(self):
        """Initialize simulator network"""
        # Return None - network operations will use standard Python
        return None


class PowerController:
    """Controls power management and monitoring"""
    
    def __init__(self, config):
        """
        Initialize power controller
        
        Args:
            config: Power configuration
        """
        self.config = config
        self._battery_pin = None
        self._charging_pin = None
    
    def initialize(self):
        """Initialize power monitoring"""
        if not IS_CIRCUITPYTHON:
            return
        
        # Set up battery monitoring
        battery_pin_name = self.config.get('battery_pin')
        if battery_pin_name:
            try:
                battery_pin = getattr(board, battery_pin_name)
                self._battery_pin = analogio.AnalogIn(battery_pin)
            except (AttributeError, NameError):
                pass
        
        # Set up charging status
        charging_pin_name = self.config.get('charging_pin')
        if charging_pin_name:
            try:
                charging_pin = getattr(board, charging_pin_name)
                self._charging_pin = digitalio.DigitalInOut(charging_pin)
                self._charging_pin.direction = digitalio.Direction.INPUT
                self._charging_pin.pull = digitalio.Pull.UP
            except (AttributeError, NameError):
                pass
    
    def get_battery_voltage(self):
        """Get battery voltage"""
        if not self._battery_pin:
            return None
        
        # Read voltage (assuming 3.3V reference)
        return (self._battery_pin.value * 3.3) / 65536
    
    def get_battery_percentage(self):
        """Get battery percentage"""
        voltage = self.get_battery_voltage()
        if voltage is None:
            return None
        
        # Convert voltage to percentage
        # Assumes LiPo battery: 4.2V = 100%, 3.0V = 0%
        min_voltage = self.config.get('battery_min_voltage', 3.0)
        max_voltage = self.config.get('battery_max_voltage', 4.2)
        
        percentage = (voltage - min_voltage) / (max_voltage - min_voltage) * 100
        return max(0, min(100, percentage))
    
    def is_charging(self):
        """Check if battery is charging"""
        if not self._charging_pin:
            return None
        
        # Usually charging pin is low when charging
        return not self._charging_pin.value
    
    def set_low_power_mode(self, enabled):
        """Enable/disable low power mode"""
        # Implementation depends on specific board capabilities
        pass


class RTCController:
    """Controls real-time clock"""
    
    def __init__(self, config):
        """
        Initialize RTC controller
        
        Args:
            config: RTC configuration
        """
        self.config = config
        self._rtc = None
    
    def initialize(self):
        """Initialize RTC"""
        if not IS_CIRCUITPYTHON:
            # Use system time in development
            return
        
        rtc_type = self.config.get('type', 'internal')
        
        if rtc_type == 'internal':
            try:
                import rtc
                self._rtc = rtc.RTC()
            except ImportError:
                pass
        elif rtc_type == 'ds3231':
            try:
                import busio
                import adafruit_ds3231
                
                i2c = busio.I2C(
                    self.config.get('scl_pin'),
                    self.config.get('sda_pin')
                )
                self._rtc = adafruit_ds3231.DS3231(i2c)
            except ImportError:
                pass
    
    def get_time(self):
        """Get current time"""
        if self._rtc:
            return self._rtc.datetime
        else:
            # Fallback to system time
            import time
            t = time.localtime()
            return time.struct_time((
                t.tm_year, t.tm_mon, t.tm_mday,
                t.tm_hour, t.tm_min, t.tm_sec,
                t.tm_wday, t.tm_yday, t.tm_isdst
            ))
    
    def set_time(self, datetime):
        """Set current time"""
        if self._rtc:
            self._rtc.datetime = datetime