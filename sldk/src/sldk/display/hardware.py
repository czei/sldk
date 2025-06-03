"""Hardware display implementation for SLDK.

Provides display interface for actual LED matrix hardware.
"""

import sys

# Verify we're on CircuitPython
if not (hasattr(sys, 'implementation') and sys.implementation.name == 'circuitpython'):
    raise ImportError("Hardware display can only be used on CircuitPython")

import displayio
import terminalio
from adafruit_matrixportal.matrix import Matrix
from adafruit_display_text.label import Label

from .interface import DisplayInterface


class HardwareDisplay(DisplayInterface):
    """Hardware display implementation for LED matrices."""
    
    def __init__(self, width=64, height=32):
        """Initialize hardware display.
        
        Args:
            width: Display width in pixels
            height: Display height in pixels
        """
        self._width = width
        self._height = height
        self._brightness = 0.3
        
        # Hardware components
        self.matrix = None
        self.display = None
        
        # Display groups
        self.main_group = None
        self._initialized = False
        
        # Default font
        self.font = terminalio.FONT
        
    @property
    def width(self):
        """Display width in pixels."""
        return self._width
        
    @property
    def height(self):
        """Display height in pixels."""
        return self._height
    
    async def initialize(self):
        """Initialize the display hardware."""
        if self._initialized:
            return
            
        try:
            # Initialize Matrix hardware
            self.matrix = Matrix(width=self._width, height=self._height)
            self.display = self.matrix.display
            
            # Set up display groups
            self.main_group = displayio.Group()
            self.display.root_group = self.main_group
            
            # Set initial brightness
            await self.set_brightness(self._brightness)
            
            self._initialized = True
            print("Hardware display initialized")
            
        except Exception as e:
            print(f"Failed to initialize hardware: {e}")
            raise
    
    async def clear(self):
        """Clear the display."""
        # Hide all groups
        for i in range(len(self.main_group)):
            self.main_group.pop()
        
        # Fill with black
        self.matrix.fill(0x000000)
    
    async def show(self):
        """Update the physical display."""
        if self.display:
            self.display.refresh(minimum_frames_per_second=0)
        return True
    
    async def set_pixel(self, x, y, color):
        """Set a single pixel color.
        
        Args:
            x: X coordinate
            y: Y coordinate
            color: Color as 24-bit RGB integer
        """
        if self.matrix and 0 <= x < self._width and 0 <= y < self._height:
            self.matrix[x, y] = color
    
    async def fill(self, color):
        """Fill entire display with color.
        
        Args:
            color: Color as 24-bit RGB integer
        """
        if self.matrix:
            self.matrix.fill(color)
    
    async def set_brightness(self, brightness):
        """Set display brightness.
        
        Args:
            brightness: Float between 0.0 and 1.0
        """
        self._brightness = max(0.0, min(1.0, brightness))
        
        if self.display:
            try:
                self.display.brightness = self._brightness
            except Exception as e:
                print(f"Failed to set brightness: {e}")
    
    async def draw_text(self, text, x=0, y=0, color=0xFFFFFF, font=None):
        """Draw text on display.
        
        Args:
            text: Text to display
            x: Starting X coordinate
            y: Starting Y coordinate
            color: Text color as 24-bit RGB
            font: Font to use (uses default if None)
        """
        # Use provided font or default
        if font is None:
            font = self.font
            
        # Create label
        label = Label(font, text=text, color=color)
        label.x = x
        label.y = y
        
        # Create a group for this label
        label_group = displayio.Group()
        label_group.append(label)
        self.main_group.append(label_group)
    
    async def scroll_text(self, text, y=0, color=0xFFFFFF, speed=0.05):
        """Scroll text across display.
        
        Args:
            text: Text to scroll
            y: Y coordinate for text
            color: Text color as 24-bit RGB
            speed: Scroll speed in seconds per pixel
        """
        # Create label
        label = Label(self.font, text=text, color=color)
        label.x = self._width  # Start from right edge
        label.y = y
        
        # Create group
        scroll_group = displayio.Group()
        scroll_group.append(label)
        self.main_group.append(scroll_group)
        
        # Estimate text width (6 pixels per char)
        text_width = len(text) * 6
        
        # Scroll until text is off screen
        import time
        while label.x > -text_width:
            label.x -= 1
            await self.show()
            time.sleep(speed)
        
        # Remove the group
        self.main_group.remove(scroll_group)