#!/usr/bin/env python3
"""
Font test program for PyLEDSimulator
Displays all characters in the font, scrolling across the screen
"""

import sys
import os
import asyncio
import pygame

# Add PyLEDSimulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'PyLEDSimulator'))

from pyledsimulator.devices.matrixportal_s3 import MatrixPortalS3
from pyledsimulator import displayio
from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.terminalio import FONT as terminalio_FONT
from pyledsimulator.adafruit_bitmap_font import bitmap_font


class FontTest:
    def __init__(self):
        # Create device
        self.device = MatrixPortalS3(width=64, height=32)
        self.device.initialize()
        
        self.matrix = self.device.matrix
        self.display = self.device.display
        
        # Initialize pygame
        if hasattr(self.matrix, 'initialize_surface'):
            self.matrix.initialize_surface()
            
        pygame.init()
        self.screen = pygame.display.set_mode((self.matrix.surface_width, self.matrix.surface_height))
        pygame.display.set_caption("Font Test - PyLEDSimulator")
        
        # Create main group
        self.main_group = displayio.Group()
        self.display.root_group = self.main_group
        
        # Load fonts to test
        self.fonts = {
            "terminalio (viii)": terminalio_FONT,
            "viii.bdf": self.load_font("PyLEDSimulator/fonts/viii.bdf"),
            "tom-thumb": self.load_font("PyLEDSimulator/fonts/tom-thumb.bdf"),
            "Arial_16": self.load_font("PyLEDSimulator/fonts/Arial_16.bdf"),
        }
        
        # Create label for testing
        self.label = Label(terminalio_FONT)
        self.label.x = 64  # Start off screen
        self.label.y = 16
        self.label_group = displayio.Group()
        self.label_group.append(self.label)
        self.main_group.append(self.label_group)
        
        # Font info label
        self.info_label = Label(terminalio_FONT)
        self.info_label.x = 0
        self.info_label.y = 6
        self.info_group = displayio.Group()
        self.info_group.append(self.info_label)
        self.main_group.append(self.info_group)
        
        # Add grid lines for visual reference
        self.grid_group = displayio.Group()
        self.main_group.append(self.grid_group)
        self.show_grid()
        
    def show_grid(self):
        """Show a grid with 8-pixel spacing"""
        # Create horizontal lines every 8 pixels
        for y in [8, 16, 24]:
            bitmap = displayio.Bitmap(64, 1, 2)
            palette = displayio.Palette(2)
            palette[0] = 0x000000  # Black
            palette[1] = 0x333333  # Dark gray
            
            # Fill with gray
            for x in range(64):
                bitmap[x, 0] = 1
                
            tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
            tile_grid.y = y
            self.grid_group.append(tile_grid)
        
    def load_font(self, path):
        """Load a font, return None if it fails"""
        try:
            return bitmap_font.load_font(path)
        except Exception as e:
            print(f"Failed to load {path}: {e}")
            return None
            
    def get_font_height(self, font):
        """Get the actual height of a font"""
        # Try creating a test label with various characters
        test_label = Label(font, text="Hg|yj")
        if test_label.bounding_box:
            # bounding_box is (x, y, width, height)
            return test_label.bounding_box[3]
        
        return 8  # Default guess
        
    async def test_font(self, font_name, font):
        """Test a single font"""
        if font is None:
            return
            
        print(f"\nTesting font: {font_name}")
        
        # Get font metrics
        height = self.get_font_height(font)
        print(f"Font height: {height} pixels")
        
        # Test at scale 1
        await self.test_font_at_scale(font_name, font, scale=1)
        
        # Test at scale 2
        await self.test_font_at_scale(font_name, font, scale=2)
        
    async def test_font_at_scale(self, font_name, font, scale):
        """Test a font at a specific scale"""
        print(f"\nScale {scale}:")
        
        # Update info
        self.info_label.font = font
        self.info_label.text = f"{font_name} @{scale}x"
        self.info_label.scale = 1  # Info always at scale 1
        
        # Configure main label
        self.label.font = font
        self.label.scale = scale
        
        # Adjust Y position based on scale
        if scale == 1:
            self.label.y = 20
        else:
            self.label.y = 24  # Lower for scale 2
        
        # Test uppercase
        test_text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789"
        self.label.text = test_text
        self.label.x = 64
        
        print(f"Testing uppercase: {test_text}")
        await self.scroll_text()
        
        # Test lowercase
        test_text = "abcdefghijklmnopqrstuvwxyz !@#$%^&*()"
        self.label.text = test_text
        self.label.x = 64
        
        print(f"Testing lowercase: {test_text}")
        await self.scroll_text()
        
        # Test specific height test
        test_text = "HgMWyj|_"  # Characters that test ascenders and descenders
        self.label.text = test_text
        self.label.x = 10
        
        print(f"Testing height chars: {test_text}")
        await asyncio.sleep(3)
        
    async def scroll_text(self):
        """Scroll the current text"""
        while self.label.x > -len(self.label.text) * 6:  # Approximate
            self.label.x -= 1
            await self.update_display()
            await asyncio.sleep(0.04)
            
    async def update_display(self):
        """Update the display"""
        # Update displayio
        self.display.refresh(minimum_frames_per_second=0)
        
        # Render to pygame
        if hasattr(self.matrix, 'render'):
            self.matrix.render()
            if hasattr(self.matrix, 'surface'):
                self.screen.blit(self.matrix.surface, (0, 0))
        
        pygame.display.flip()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                    
    async def run(self):
        """Run all font tests"""
        print("Font Test Program")
        print("=================")
        print("Testing all available fonts...")
        
        for font_name, font in self.fonts.items():
            await self.test_font(font_name, font)
            await asyncio.sleep(1)
            
        print("\nFont test complete!")
        
        # Keep running
        while True:
            self.info_label.text = "Test Complete"
            self.label.text = "Press ESC to exit"
            self.label.x = 0
            await self.update_display()
            await asyncio.sleep(0.1)


async def main():
    tester = FontTest()
    await tester.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit(0)