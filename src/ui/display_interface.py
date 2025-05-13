"""
Abstract display interface for LED matrix displays.
This interface allows for different implementations (hardware or simulated).
Copyright 2024 3DUPFitters LLC
"""
from abc import ABC, abstractmethod


class DisplayInterface(ABC):
    """Abstract base class for display implementations"""
    
    @abstractmethod
    def initialize(self):
        """Initialize the display hardware or simulator"""
        pass
        
    @abstractmethod
    def set_text(self, text, color=None):
        """
        Set the text to be displayed
        
        Args:
            text: The text to display
            color: The color to use for the text (RGB tuple or hex)
        """
        pass
    
    @abstractmethod
    def scroll(self, frame_delay=0.04):
        """
        Scroll the text across the display
        
        Args:
            frame_delay: Time delay between scroll frames in seconds
        """
        pass
    
    @abstractmethod
    def clear(self):
        """Clear the display"""
        pass
    
    @abstractmethod
    def update(self):
        """Update the display to show latest changes"""
        pass
    
    @abstractmethod
    def show_image(self, image, x=0, y=0):
        """
        Show an image on the display
        
        Args:
            image: The image to display
            x: X position
            y: Y position
        """
        pass
    
    @abstractmethod
    def set_brightness(self, brightness):
        """
        Set the brightness of the display
        
        Args:
            brightness: Brightness value between 0.0 and 1.0
        """
        pass
    
    @abstractmethod
    def set_rotation(self, rotation):
        """
        Set the rotation of the display
        
        Args:
            rotation: Rotation in degrees (0, 90, 180, 270)
        """
        pass