"""
Abstract display interface for LED matrix displays.
This interface allows for different implementations (hardware or simulated).
"""


class DisplayInterface:
    """Abstract base class for display implementations"""
    
    def initialize(self):
        """Initialize the display hardware or simulator"""
        pass
        
    def set_text(self, text, color=None):
        """
        Set the text to be displayed
        
        Args:
            text: The text to display
            color: The color to use for the text (RGB tuple or hex)
        """
        pass
    
    def scroll(self, frame_delay=0.04):
        """
        Scroll the text across the display
        
        Args:
            frame_delay: Time delay between scroll frames in seconds
        """
        pass
    
    def clear(self):
        """Clear the display"""
        pass
    
    def update(self):
        """Update the display to show latest changes"""
        pass
    
    def show_image(self, image, x=0, y=0):
        """
        Show an image on the display
        
        Args:
            image: The image to display
            x: X position
            y: Y position
        """
        pass
    
    def set_brightness(self, brightness):
        """
        Set the brightness of the display
        
        Args:
            brightness: Brightness value between 0.0 and 1.0
        """
        pass
    
    def set_rotation(self, rotation):
        """
        Set the rotation of the display
        
        Args:
            rotation: Rotation in degrees (0, 90, 180, 270)
        """
        pass
        
    async def show_splash(self, duration=10, reveal_style=False):
        """
        Show splash screen
        
        Args:
            duration: Duration to show splash in seconds
            reveal_style: Whether to use reveal animation
        """
        pass
        
    async def show_scroll_message(self, message, delay=2):
        """
        Show a scrolling message
        
        Args:
            message: Text to scroll
            delay: Delay after scrolling completes
        """
        pass
        
    async def show_static_message(self, message, duration=3):
        """
        Show a static message for a duration
        
        Args:
            message: Text to display
            duration: How long to show the message
        """
        pass
        
    async def show_ride_wait_time(self, wait_time):
        """
        Show ride wait time (theme park specific - can be overridden)
        
        Args:
            wait_time: Wait time in minutes
        """
        await self.show_static_message(f"{wait_time} min", 2)
        
    async def show_ride_name(self, ride_name):
        """
        Show ride name (theme park specific - can be overridden)
        
        Args:
            ride_name: Name of the ride
        """
        await self.show_scroll_message(ride_name, 1)
        
    async def show_ride_closed(self, message="Closed"):
        """
        Show ride closed message (theme park specific - can be overridden)
        
        Args:
            message: Closed message to display
        """
        await self.show_static_message(message, 2)
        
    def set_colors(self, settings_manager):
        """
        Set display colors from settings
        
        Args:
            settings_manager: Settings manager instance
        """
        pass