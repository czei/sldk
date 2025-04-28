"""
WiFi connection management.
Copyright 2024 3DUPFitters LLC
"""
import asyncio

from src.config.settings_manager import SettingsManager
from src.utils.error_handler import ErrorHandler
from src.utils.url_utils import load_credentials

# Initialize logger
logger = ErrorHandler("error_log")


class WiFiManager:
    """
    Manages WiFi connections for the application
    """
    
    def __init__(self, settings_manager):
        """
        Initialize the WiFi manager
        
        Args:
            settings_manager: The settings manager
        """
        self.settings_manager = settings_manager
        self.ssid, self.password = load_credentials()
        self.is_connected = False
        self.wifi_client = None
        
        try:
            # Try to import CircuitPython specific modules
            import wifi
            self.wifi = wifi
            self.HAS_WIFI = True
        except ImportError:
            # Mock for non-CircuitPython environments
            self.wifi = None
            self.HAS_WIFI = False
            logger.debug("WiFi module not available, using mock implementation")
            
    async def connect(self, display_callback=None):
        """
        Connect to WiFi
        
        Args:
            display_callback: Optional callback function to update display during connection attempts
            
        Returns:
            True if connected, False otherwise
        """
        if not self.HAS_WIFI:
            logger.debug("WiFi not available, simulating connection")
            self.is_connected = True
            return True
            
        try:
            if not self.ssid or not self.password:
                logger.error(ValueError("Missing WiFi credentials"), "WiFi credentials not found")
                return False
                
            logger.info(f"Connecting to WiFi network: {self.ssid}")
            
            # Maximum connection attempts
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    # Connect to the network
                    self.wifi.radio.connect(self.ssid, self.password)
                    self.is_connected = True
                    break
                except Exception as conn_err:
                    # Only log on final attempt, otherwise just try again
                    if attempt == max_attempts - 1:
                        logger.error(conn_err, f"Failed to connect to WiFi after {max_attempts} attempts")
                    
                    # Update display if callback provided
                    if display_callback:
                        await display_callback(f"Attempt {attempt+1}/{max_attempts}")
                    
                    # Short delay before retry
                    await asyncio.sleep(1)
            
            if self.is_connected:
                # Log connection info
                ip_address = self.wifi.radio.ipv4_address
                logger.info(f"Connected to WiFi. IP address: {ip_address}")
                
                # Now that we're connected, create the HTTP session
                # This should only happen AFTER a successful WiFi connection
                try:
                    session = self.create_http_session()
                    logger.info("Created HTTP session after WiFi connection")
                except Exception as session_error:
                    logger.error(session_error, "Failed to create HTTP session after WiFi connection")
                
                return True
            else:
                return False
            
        except Exception as e:
            logger.error(e, "Error connecting to WiFi")
            self.is_connected = False
            return False
            
    def create_http_session(self):
        """
        Create and return a new HTTP session
        This should only be called after WiFi is connected
        
        Returns:
            A new adafruit_requests.Session or None if not available
        """
        if not self.HAS_WIFI or not self.is_connected:
            logger.debug("Cannot create HTTP session without WiFi connection")
            return None
            
        try:
            import ssl
            import socketpool
            import adafruit_requests
            
            # Create a fresh socket pool from the radio
            pool = socketpool.SocketPool(self.wifi.radio)
            
            # Create a new SSL context
            ssl_context = ssl.create_default_context()
            
            # Create and return the session
            session = adafruit_requests.Session(pool, ssl_context)
            
            # Update any HTTP clients that need the session
            self.update_http_clients(session)
            
            return session
            
        except Exception as e:
            logger.error(e, "Error creating HTTP session")
            return None
            
    def update_http_clients(self, session):
        """
        Update any HTTP clients with the new session
        Mainly used by ThemeParkApp to update its HTTP client
        
        Args:
            session: The new adafruit_requests.Session
        """
        # This function will be called from the app to update HTTP clients
        # The implementation is in the app class
            
    async def disconnect(self):
        """Disconnect from WiFi"""
        if not self.HAS_WIFI or not self.is_connected:
            return
            
        try:
            logger.info("Disconnecting from WiFi")
            # Some CircuitPython versions may not have the disconnect method
            if hasattr(self.wifi.radio, 'disconnect'):
                self.wifi.radio.disconnect()
            self.is_connected = False
            
        except Exception as e:
            logger.error(e, "Error disconnecting from WiFi")
            
    async def reconnect(self):
        """
        Reconnect to WiFi if disconnected
        
        Returns:
            True if connected, False otherwise
        """
        if self.is_connected:
            return True
            
        # Try to reconnect
        return await self.connect()
        
    def is_available(self):
        """
        Check if WiFi is available
        
        Returns:
            True if WiFi is available, False otherwise
        """
        return self.HAS_WIFI
        
    def is_connected(self):
        """
        Check if connected to WiFi
        
        Returns:
            True if connected, False otherwise
        """
        if not self.HAS_WIFI:
            return self.is_connected
            
        try:
            return self.wifi.radio.connected
        except Exception:
            return False
            
    def get_ip_address(self):
        """
        Get the current IP address
        
        Returns:
            The IP address as a string, or None if not connected
        """
        if not self.HAS_WIFI or not self.is_connected:
            return None
            
        try:
            return str(self.wifi.radio.ipv4_address)
        except Exception:
            return None