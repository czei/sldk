"""
Board detection utilities for automatic hardware identification.
"""
import sys
import os

# Platform detection
IS_CIRCUITPYTHON = hasattr(sys, 'implementation') and sys.implementation.name == 'circuitpython'


class BoardDetector:
    """Detects the current board and its capabilities"""
    
    # Known board identifiers
    MATRIXPORTAL_S3 = "matrixportal_s3"
    MATRIXPORTAL_M4 = "matrixportal_m4"
    RASPBERRY_PI = "raspberry_pi"
    SIMULATOR = "simulator"
    UNKNOWN = "unknown"
    
    @classmethod
    def detect_board(cls):
        """
        Detect the current board type
        
        Returns:
            str: Board identifier
        """
        if not IS_CIRCUITPYTHON:
            return cls.SIMULATOR
        
        try:
            import board
            
            # Check board.board_id if available (CircuitPython 7.0+)
            if hasattr(board, 'board_id'):
                board_id = board.board_id.lower()
                
                if 'matrixportal_s3' in board_id:
                    return cls.MATRIXPORTAL_S3
                elif 'matrixportal_m4' in board_id or 'matrixportal' in board_id:
                    return cls.MATRIXPORTAL_M4
                elif 'raspberry' in board_id or 'raspberrypi' in board_id:
                    return cls.RASPBERRY_PI
            
            # Fallback: check for specific pins
            if hasattr(board, 'ESP_CS') and hasattr(board, 'ESP_BUSY'):
                # MatrixPortal boards have ESP32 co-processor
                if hasattr(board, 'A0') and hasattr(board, 'A1'):
                    # S3 has different analog pins
                    return cls.MATRIXPORTAL_S3
                else:
                    return cls.MATRIXPORTAL_M4
            
            # Check for Raspberry Pi specific features
            if hasattr(board, 'SDA') and hasattr(board, 'SCL') and not hasattr(board, 'NEOPIXEL'):
                return cls.RASPBERRY_PI
            
        except ImportError:
            # board module not available
            pass
        
        return cls.UNKNOWN
    
    @classmethod
    def detect_display_type(cls):
        """
        Detect the type of display connected
        
        Returns:
            dict: Display information
        """
        display_info = {
            'type': None,
            'width': None,
            'height': None,
            'color_depth': None
        }
        
        if not IS_CIRCUITPYTHON:
            # Simulator default
            display_info.update({
                'type': 'simulator',
                'width': 64,
                'height': 32,
                'color_depth': 16
            })
            return display_info
        
        try:
            import displayio
            import board
            
            # Check for RGB matrix
            try:
                from rgbmatrix import RGBMatrix
                # Try to detect matrix size
                # MatrixPortal typically uses 64x32
                display_info.update({
                    'type': 'rgb_matrix',
                    'width': 64,
                    'height': 32,
                    'color_depth': 16
                })
            except ImportError:
                pass
            
            # Check for built-in display
            if hasattr(board, 'DISPLAY'):
                display = board.DISPLAY
                display_info.update({
                    'type': 'built_in',
                    'width': display.width,
                    'height': display.height,
                    'color_depth': 16
                })
            
        except ImportError:
            pass
        
        return display_info
    
    @classmethod
    def detect_network_capabilities(cls):
        """
        Detect available network hardware
        
        Returns:
            dict: Network capabilities
        """
        capabilities = {
            'wifi': False,
            'ethernet': False,
            'bluetooth': False,
            'wifi_module': None
        }
        
        if not IS_CIRCUITPYTHON:
            # Simulator has "virtual" WiFi
            capabilities['wifi'] = True
            capabilities['wifi_module'] = 'simulator'
            return capabilities
        
        # Check for WiFi
        try:
            import wifi
            capabilities['wifi'] = True
            capabilities['wifi_module'] = 'native'
        except ImportError:
            # Check for ESP32 co-processor (MatrixPortal)
            try:
                import board
                if hasattr(board, 'ESP_CS'):
                    capabilities['wifi'] = True
                    capabilities['wifi_module'] = 'esp32'
            except ImportError:
                pass
        
        # Check for Ethernet
        try:
            import board
            if hasattr(board, 'ETH_CS'):
                capabilities['ethernet'] = True
        except ImportError:
            pass
        
        # Check for Bluetooth
        try:
            import _bleio
            capabilities['bluetooth'] = True
        except ImportError:
            pass
        
        return capabilities
    
    @classmethod
    def detect_storage_capabilities(cls):
        """
        Detect available storage options
        
        Returns:
            dict: Storage capabilities
        """
        capabilities = {
            'internal_flash': True,  # Always present
            'sd_card': False,
            'qspi_flash': False,
            'internal_size': None
        }
        
        if not IS_CIRCUITPYTHON:
            # Simulator uses regular filesystem
            capabilities['internal_size'] = 'unlimited'
            return capabilities
        
        try:
            import storage
            import os
            
            # Get internal storage size
            stat = os.statvfs('/')
            capabilities['internal_size'] = stat[0] * stat[2]  # block size * total blocks
            
            # Check for SD card
            try:
                import board
                import sdcardio
                if hasattr(board, 'SD_CS'):
                    capabilities['sd_card'] = True
            except ImportError:
                pass
            
            # Check for QSPI flash
            try:
                import board
                if hasattr(board, 'QSPI_SCK'):
                    capabilities['qspi_flash'] = True
            except ImportError:
                pass
            
        except ImportError:
            pass
        
        return capabilities
    
    @classmethod
    def detect_peripheral_capabilities(cls):
        """
        Detect other peripherals and sensors
        
        Returns:
            dict: Peripheral capabilities
        """
        capabilities = {
            'rtc': False,
            'temperature_sensor': False,
            'accelerometer': False,
            'neopixels': False,
            'battery_monitor': False
        }
        
        if not IS_CIRCUITPYTHON:
            # Simulator has virtual RTC
            capabilities['rtc'] = True
            return capabilities
        
        try:
            import board
            
            # Check for RTC
            try:
                import rtc
                capabilities['rtc'] = True
            except ImportError:
                # Check for external RTC pins
                if hasattr(board, 'RTC_SDA') or (hasattr(board, 'SDA') and hasattr(board, 'SCL')):
                    capabilities['rtc'] = True  # Possible external RTC
            
            # Check for temperature sensor
            try:
                import microcontroller
                if hasattr(microcontroller.cpu, 'temperature'):
                    capabilities['temperature_sensor'] = True
            except:
                pass
            
            # Check for accelerometer (common on many boards)
            if hasattr(board, 'ACCELEROMETER_SDA') or hasattr(board, 'I2C'):
                capabilities['accelerometer'] = True
            
            # Check for NeoPixels
            if hasattr(board, 'NEOPIXEL'):
                capabilities['neopixels'] = True
            
            # Check for battery monitoring
            if hasattr(board, 'BATTERY') or hasattr(board, 'VOLTAGE_MONITOR'):
                capabilities['battery_monitor'] = True
            
        except ImportError:
            pass
        
        return capabilities
    
    @classmethod
    def get_full_hardware_report(cls):
        """
        Get a complete hardware detection report
        
        Returns:
            dict: Complete hardware information
        """
        return {
            'board': cls.detect_board(),
            'platform': 'circuitpython' if IS_CIRCUITPYTHON else 'desktop',
            'display': cls.detect_display_type(),
            'network': cls.detect_network_capabilities(),
            'storage': cls.detect_storage_capabilities(),
            'peripherals': cls.detect_peripheral_capabilities()
        }