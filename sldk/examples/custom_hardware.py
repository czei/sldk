#!/usr/bin/env python3
"""Custom hardware example for SLDK.

Demonstrates how to implement custom hardware support.
"""

import sys
import os

# Add parent directory to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import asyncio
except ImportError:
    # CircuitPython
    import asyncio

from sldk import SLDKApp, ScrollingText, StaticText
from sldk.display import DisplayInterface


class MockHardwareDisplay(DisplayInterface):
    """Mock hardware display for demonstration.
    
    This shows how to implement a custom display driver.
    Replace this with your actual hardware implementation.
    """
    
    def __init__(self, width=64, height=32):
        self._width = width
        self._height = height
        self._brightness = 0.5
        self._pixels = {}
        self._initialized = False
        
    @property
    def width(self):
        return self._width
        
    @property
    def height(self):
        return self._height
    
    async def initialize(self):
        """Initialize your custom hardware."""
        print(f"Initializing mock hardware: {self._width}x{self._height}")
        # Your hardware initialization code here
        # Example: Initialize SPI, I2C, GPIO pins, etc.
        self._initialized = True
    
    async def clear(self):
        """Clear the display."""
        self._pixels.clear()
        print("Mock display cleared")
    
    async def show(self):
        """Update the physical display."""
        # This is where you'd push pixel data to your hardware
        print(f"Mock display updated with {len(self._pixels)} pixels")
        return True
    
    async def set_pixel(self, x, y, color):
        """Set a single pixel color."""
        if 0 <= x < self._width and 0 <= y < self._height:
            self._pixels[(x, y)] = color
    
    async def fill(self, color):
        """Fill entire display with color."""
        for y in range(self._height):
            for x in range(self._width):
                await self.set_pixel(x, y, color)
    
    async def set_brightness(self, brightness):
        """Set display brightness."""
        self._brightness = max(0.0, min(1.0, brightness))
        print(f"Mock brightness set to {self._brightness}")
    
    async def draw_text(self, text, x=0, y=0, color=0xFFFFFF, font=None):
        """Draw text on display (simplified implementation)."""
        print(f"Mock text: '{text}' at ({x}, {y}) color=0x{color:06X}")
        
        # Simple pixel-based text rendering (very basic)
        char_width = 6
        for i, char in enumerate(text):
            char_x = x + (i * char_width)
            if char_x < self._width:
                # Draw a simple rectangle for each character
                for py in range(y, min(y + 8, self._height)):
                    for px in range(char_x, min(char_x + char_width - 1, self._width)):
                        await self.set_pixel(px, py, color)


class CustomHardwareApp(SLDKApp):
    """Application using custom hardware."""
    
    def __init__(self):
        super().__init__(enable_web=False, update_interval=5)
        
    async def create_display(self):
        """Override to use custom hardware."""
        # Return your custom display implementation
        return MockHardwareDisplay(width=128, height=64)  # Different size
        
    async def setup(self):
        """Initialize the application."""
        print("Custom hardware app starting...")
        
        # Add some content to display
        self.content_queue.add(StaticText(
            "Custom HW", 
            x=10, y=10,
            color=0xFF0000,  # Red
            duration=3
        ))
        
        self.content_queue.add(StaticText(
            "128x64",
            x=10, y=30,
            color=0x00FF00,  # Green
            duration=3
        ))
        
        self.content_queue.add(ScrollingText(
            "This is running on custom hardware! SLDK makes it easy to support any display.",
            y=20,
            color=0x0080FF,  # Blue
            speed=0.03
        ))
        
    async def update_data(self):
        """Update data periodically."""
        print("Custom hardware: Data update called")
        # Your custom data update logic here


# Alternative approach: Create device driver and contribute to SLDK
class MyLEDMatrixDisplay(DisplayInterface):
    """Example of a device driver that could be contributed to SLDK.
    
    This would go in sldk/src/sldk/display/devices/my_led_matrix.py
    """
    
    def __init__(self, spi_bus=None, cs_pin=None, width=64, height=32, **kwargs):
        """Initialize My LED Matrix display.
        
        Args:
            spi_bus: SPI bus object
            cs_pin: Chip select pin
            width: Display width
            height: Display height
            **kwargs: Additional device parameters
        """
        self._width = width
        self._height = height
        self.spi_bus = spi_bus
        self.cs_pin = cs_pin
        self._initialized = False
        
        # Store any additional device-specific parameters
        self.device_kwargs = kwargs
        
    @property
    def width(self):
        return self._width
        
    @property
    def height(self):
        return self._height
    
    async def initialize(self):
        """Initialize the LED matrix hardware."""
        print(f"Initializing My LED Matrix: {self._width}x{self._height}")
        
        # Example initialization steps:
        # 1. Configure SPI
        # 2. Initialize display controller
        # 3. Set up GPIO pins
        # 4. Configure display parameters
        
        self._initialized = True
    
    async def clear(self):
        """Clear the display."""
        # Send clear command to hardware
        pass
    
    async def show(self):
        """Update the physical display."""
        # Send frame buffer to hardware
        return True
    
    async def set_pixel(self, x, y, color):
        """Set a single pixel color."""
        # Write pixel to frame buffer or directly to hardware
        pass
    
    async def set_brightness(self, brightness):
        """Set display brightness."""
        # Send brightness command to hardware
        pass


async def main():
    """Main entry point."""
    app = CustomHardwareApp()
    
    try:
        print("Starting custom hardware demo...")
        await app.run()
        
    except KeyboardInterrupt:
        print("\nShutting down...")
        app.stop()


if __name__ == "__main__":
    # Run with asyncio
    asyncio.run(main())