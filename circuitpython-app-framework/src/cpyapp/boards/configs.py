"""
Built-in board configurations for common CircuitPython boards.
"""
import sys
from .base import BoardBase, BoardCapabilities
from .hardware import PinMapper, DisplayController, NetworkController, PowerController, RTCController

# Platform detection
IS_CIRCUITPYTHON = hasattr(sys, 'implementation') and sys.implementation.name == 'circuitpython'

if IS_CIRCUITPYTHON:
    import board


class MatrixPortalS3(BoardBase):
    """Adafruit MatrixPortal S3 with 64x32 RGB LED matrix"""
    
    def __init__(self):
        super().__init__()
        
        # Set capabilities
        self._capabilities = {
            BoardCapabilities.HAS_RGB_MATRIX,
            BoardCapabilities.HAS_WIFI,
            BoardCapabilities.HAS_NEOPIXELS,
            BoardCapabilities.HAS_ACCELEROMETER,
            BoardCapabilities.HAS_QSPI_FLASH
        }
        
        # Display configuration for 64x32 RGB matrix
        self._display_config = {
            'type': 'rgb_matrix',
            'width': 64,
            'height': 32,
            'bit_depth': 4,
            'brightness': 0.5,
            'rgb_pins': None,  # Will be set in setup
            'addr_pins': None,
            'clock_pin': None,
            'latch_pin': None,
            'output_enable_pin': None
        }
        
        # Network configuration
        self._network_config = {
            'type': 'wifi',
            'module': 'native',  # S3 has native WiFi
        }
        
        # Power configuration
        self._power_config = {
            'default_brightness': 0.5,
            'low_power_brightness': 0.2
        }
        
        # Pin mappings
        self._setup_pin_mappings()
    
    @property
    def name(self):
        return "matrixportal_s3"
    
    @property
    def display_name(self):
        return "Adafruit MatrixPortal S3"
    
    @property
    def manufacturer(self):
        return "Adafruit Industries"
    
    def _setup_pin_mappings(self):
        """Set up pin mappings for MatrixPortal S3"""
        if not IS_CIRCUITPYTHON:
            return
        
        # RGB Matrix pins
        self._display_config['rgb_pins'] = [
            board.MTX_R1, board.MTX_G1, board.MTX_B1,
            board.MTX_R2, board.MTX_G2, board.MTX_B2
        ]
        self._display_config['addr_pins'] = [
            board.MTX_ADDRA, board.MTX_ADDRB, 
            board.MTX_ADDRC, board.MTX_ADDRD
        ]
        self._display_config['clock_pin'] = board.MTX_CLK
        self._display_config['latch_pin'] = board.MTX_LAT
        self._display_config['output_enable_pin'] = board.MTX_OE
        
        # Other pins
        self._pin_mappings = {
            'neopixel': board.NEOPIXEL if hasattr(board, 'NEOPIXEL') else None,
            'button_up': board.BUTTON_UP if hasattr(board, 'BUTTON_UP') else None,
            'button_down': board.BUTTON_DOWN if hasattr(board, 'BUTTON_DOWN') else None,
            'accelerometer_interrupt': board.ACCELEROMETER_INTERRUPT if hasattr(board, 'ACCELEROMETER_INTERRUPT') else None,
        }
    
    def setup_display(self):
        """Set up the RGB matrix display"""
        controller = DisplayController('rgb_matrix', self._display_config)
        return controller.initialize()
    
    def setup_network(self):
        """Set up WiFi"""
        controller = NetworkController('wifi', self._network_config)
        return controller.initialize()


class MatrixPortalM4(BoardBase):
    """Adafruit MatrixPortal M4 with 64x32 RGB LED matrix"""
    
    def __init__(self):
        super().__init__()
        
        # Set capabilities
        self._capabilities = {
            BoardCapabilities.HAS_RGB_MATRIX,
            BoardCapabilities.HAS_WIFI,
            BoardCapabilities.HAS_NEOPIXELS,
            BoardCapabilities.HAS_ACCELEROMETER,
            BoardCapabilities.HAS_QSPI_FLASH
        }
        
        # Display configuration for 64x32 RGB matrix
        self._display_config = {
            'type': 'rgb_matrix',
            'width': 64,
            'height': 32,
            'bit_depth': 4,
            'brightness': 0.5,
            'rgb_pins': None,
            'addr_pins': None,
            'clock_pin': None,
            'latch_pin': None,
            'output_enable_pin': None
        }
        
        # Network configuration - ESP32 co-processor
        self._network_config = {
            'type': 'wifi',
            'module': 'esp32',
            'esp32_cs': None,
            'esp32_ready': None,
            'esp32_reset': None,
            'spi_clock': None,
            'spi_mosi': None,
            'spi_miso': None
        }
        
        # Power configuration
        self._power_config = {
            'default_brightness': 0.5,
            'low_power_brightness': 0.2
        }
        
        # Pin mappings
        self._setup_pin_mappings()
    
    @property
    def name(self):
        return "matrixportal_m4"
    
    @property
    def display_name(self):
        return "Adafruit MatrixPortal M4"
    
    @property
    def manufacturer(self):
        return "Adafruit Industries"
    
    def _setup_pin_mappings(self):
        """Set up pin mappings for MatrixPortal M4"""
        if not IS_CIRCUITPYTHON:
            return
        
        # RGB Matrix pins (same as S3)
        self._display_config['rgb_pins'] = [
            board.MTX_R1, board.MTX_G1, board.MTX_B1,
            board.MTX_R2, board.MTX_G2, board.MTX_B2
        ]
        self._display_config['addr_pins'] = [
            board.MTX_ADDRA, board.MTX_ADDRB, 
            board.MTX_ADDRC, board.MTX_ADDRD
        ]
        self._display_config['clock_pin'] = board.MTX_CLK
        self._display_config['latch_pin'] = board.MTX_LAT
        self._display_config['output_enable_pin'] = board.MTX_OE
        
        # ESP32 pins
        self._network_config['esp32_cs'] = board.ESP_CS
        self._network_config['esp32_ready'] = board.ESP_BUSY
        self._network_config['esp32_reset'] = board.ESP_RESET
        self._network_config['spi_clock'] = board.SCK
        self._network_config['spi_mosi'] = board.MOSI
        self._network_config['spi_miso'] = board.MISO
        
        # Other pins
        self._pin_mappings = {
            'neopixel': board.NEOPIXEL if hasattr(board, 'NEOPIXEL') else None,
            'button_up': board.BUTTON_UP if hasattr(board, 'BUTTON_UP') else None,
            'button_down': board.BUTTON_DOWN if hasattr(board, 'BUTTON_DOWN') else None,
            'accelerometer_interrupt': board.ACCELEROMETER_INTERRUPT if hasattr(board, 'ACCELEROMETER_INTERRUPT') else None,
        }
    
    def setup_display(self):
        """Set up the RGB matrix display"""
        controller = DisplayController('rgb_matrix', self._display_config)
        return controller.initialize()
    
    def setup_network(self):
        """Set up WiFi via ESP32"""
        controller = NetworkController('wifi', self._network_config)
        return controller.initialize()


class RaspberryPi(BoardBase):
    """Raspberry Pi with RGB LED hat/bonnet"""
    
    def __init__(self):
        super().__init__()
        
        # Set capabilities
        self._capabilities = {
            BoardCapabilities.HAS_RGB_MATRIX,
            BoardCapabilities.HAS_WIFI,
            BoardCapabilities.HAS_ETHERNET,
            BoardCapabilities.HAS_BLUETOOTH,
            BoardCapabilities.HAS_SD_CARD,
            BoardCapabilities.HAS_RTC
        }
        
        # Display configuration
        self._display_config = {
            'type': 'rgb_matrix',
            'width': 64,
            'height': 32,
            'bit_depth': 4,
            'brightness': 0.5,
            # Raspberry Pi RGB matrix pins vary by hat/bonnet
            # These would need to be configured based on specific hardware
        }
        
        # Network configuration
        self._network_config = {
            'type': 'wifi',
            'module': 'native'
        }
        
        # Power configuration
        self._power_config = {
            'default_brightness': 0.5,
            'low_power_brightness': 0.3
        }
    
    @property
    def name(self):
        return "raspberry_pi"
    
    @property
    def display_name(self):
        return "Raspberry Pi with RGB Matrix"
    
    @property
    def manufacturer(self):
        return "Raspberry Pi Foundation"
    
    def setup_display(self):
        """Set up the RGB matrix display"""
        # Note: Actual implementation would depend on the specific
        # RGB matrix library being used (e.g., rpi-rgb-led-matrix)
        controller = DisplayController('rgb_matrix', self._display_config)
        return controller.initialize()
    
    def setup_network(self):
        """Set up network (WiFi or Ethernet)"""
        controller = NetworkController('wifi', self._network_config)
        return controller.initialize()


class SimulatorBoard(BoardBase):
    """Development simulator environment"""
    
    def __init__(self):
        super().__init__()
        
        # Set all capabilities for testing
        self._capabilities = {
            BoardCapabilities.HAS_RGB_MATRIX,
            BoardCapabilities.HAS_WIFI,
            BoardCapabilities.HAS_RTC,
            BoardCapabilities.HAS_NEOPIXELS
        }
        
        # Display configuration
        self._display_config = {
            'type': 'simulator',
            'width': 64,
            'height': 32,
            'bit_depth': 16,
            'brightness': 1.0
        }
        
        # Network configuration
        self._network_config = {
            'type': 'simulator'
        }
        
        # Power configuration
        self._power_config = {
            'default_brightness': 1.0,
            'battery_simulation': True
        }
    
    @property
    def name(self):
        return "simulator"
    
    @property
    def display_name(self):
        return "LED Simulator (Development)"
    
    @property
    def manufacturer(self):
        return "Software Simulator"
    
    def setup_display(self):
        """Set up the simulator display"""
        # The display factory handles simulator setup
        return None
    
    def setup_network(self):
        """Set up simulated network"""
        # Use standard Python networking in simulator
        return None
    
    def set_display_brightness(self, brightness):
        """Set display brightness (simulated)"""
        self._display_config['brightness'] = brightness
    
    def get_battery_level(self):
        """Get simulated battery level"""
        # Simulate battery level for testing
        import random
        return random.uniform(0.7, 1.0)
    
    def get_temperature(self):
        """Get simulated temperature"""
        # Simulate temperature for testing
        import random
        return random.uniform(20.0, 30.0)