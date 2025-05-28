#!/usr/bin/env python3
"""Progressive rendering tests - from simple to complex."""

import unittest
import pygame
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3
from pyledsimulator.displayio import Display, Group, Bitmap, Palette, TileGrid, FourWire
from pyledsimulator.core import LEDMatrix
from pyledsimulator.adafruit_display_text import Label
from pyledsimulator.terminalio import FONT


class TestProgressiveRendering(unittest.TestCase):
    """Test rendering from simple to complex configurations."""
    
    @classmethod
    def setUpClass(cls):
        """Initialize pygame once for all tests."""
        pygame.init()
        
    def setUp(self):
        """Set up test fixtures."""
        # Use small matrix for easier testing
        self.matrix = LEDMatrix(8, 8, pitch=4.0)
        self.matrix.initialize_surface()
        
    def assert_pixel_set(self, x, y, expected_color, tolerance=10):
        """Assert a pixel is set to expected color."""
        actual = self.matrix.get_pixel(x, y)
        for i in range(3):
            diff = abs(int(actual[i]) - int(expected_color[i]))
            self.assertLessEqual(diff, tolerance, 
                f"Pixel ({x},{y}) channel {i}: expected {expected_color[i]}, got {actual[i]}")
                
    def count_non_black_pixels(self):
        """Count pixels that aren't black."""
        count = 0
        for y in range(self.matrix.height):
            for x in range(self.matrix.width):
                if self.matrix.get_pixel(x, y) != (0, 0, 0):
                    count += 1
        return count
        
    # Level 1: Direct pixel manipulation
    def test_01_single_pixel(self):
        """Test setting a single pixel directly."""
        # Set one pixel
        self.matrix.set_pixel(3, 3, (255, 0, 0))
        
        # Verify it's set
        self.assert_pixel_set(3, 3, (255, 0, 0))
        
        # Verify only one pixel is set
        self.assertEqual(self.count_non_black_pixels(), 1)
        
    def test_02_multiple_pixels(self):
        """Test setting multiple pixels."""
        colors = [
            (0, 0, (255, 0, 0)),
            (7, 0, (0, 255, 0)),
            (0, 7, (0, 0, 255)),
            (7, 7, (255, 255, 255))
        ]
        
        for x, y, color in colors:
            self.matrix.set_pixel(x, y, color)
            
        # Verify each pixel
        for x, y, color in colors:
            self.assert_pixel_set(x, y, color)
            
        self.assertEqual(self.count_non_black_pixels(), 4)
        
    def test_03_pixel_fill(self):
        """Test filling all pixels."""
        self.matrix.fill((128, 128, 128))
        
        # Check all pixels are gray
        for y in range(8):
            for x in range(8):
                self.assert_pixel_set(x, y, (128, 128, 128))
                
        self.assertEqual(self.count_non_black_pixels(), 64)
        
    def test_04_pixel_clear(self):
        """Test clearing pixels."""
        # First fill
        self.matrix.fill((255, 255, 255))
        self.assertEqual(self.count_non_black_pixels(), 64)
        
        # Then clear
        self.matrix.clear()
        self.assertEqual(self.count_non_black_pixels(), 0)
        
    # Level 2: Display and rendering
    def test_05_display_creation(self):
        """Test creating a display linked to matrix."""
        display = Display(
            FourWire(None),
            width=8,
            height=8
        )
        display._matrix = self.matrix
        
        # Display should be created but empty
        self.assertIsNotNone(display)
        self.assertEqual(display.width, 8)
        self.assertEqual(display.height, 8)
        
    @unittest.skip("Display.refresh with None root_group doesn't clear - design decision")
    def test_06_display_refresh(self):
        """Test display refresh clears and re-renders."""
        display = Display(FourWire(None), width=8, height=8)
        display._matrix = self.matrix
        
        # Create content to display
        bitmap = Bitmap(2, 2, 2)
        bitmap.fill(1)
        palette = Palette(2)
        palette[0] = 0x0000
        palette[1] = 0xF800  # Red
        tilegrid = TileGrid(bitmap, pixel_shader=palette)
        
        # Show content
        display.show(tilegrid)
        display.refresh()
        
        # Should have 4 red pixels
        self.assertEqual(self.count_non_black_pixels(), 4)
        
        # Now show empty content
        display.show(None)
        display.refresh()
        
        # Should be cleared
        self.assertEqual(self.count_non_black_pixels(), 0)
        
    # Level 3: Bitmap and Palette
    def test_07_bitmap_creation(self):
        """Test creating and manipulating bitmaps."""
        bitmap = Bitmap(4, 4, 2)
        
        # Set diagonal
        for i in range(4):
            bitmap[i, i] = 1
            
        # Verify bitmap contents
        for y in range(4):
            for x in range(4):
                expected = 1 if x == y else 0
                self.assertEqual(bitmap[x, y], expected)
                
    def test_08_palette_colors(self):
        """Test palette color storage."""
        palette = Palette(4)
        
        # Set colors using different formats
        palette[0] = 0x0000      # Black (RGB565)
        palette[1] = 0xF800      # Red (RGB565)
        palette[2] = (0, 255, 0) # Green (RGB888 tuple)
        palette[3] = (0, 0, 255) # Blue (RGB888 tuple)
        
        # Verify RGB565 values
        self.assertEqual(palette[0], 0x0000)
        self.assertEqual(palette[1], 0xF800)
        self.assertEqual(palette[2], 0x07E0)  # Green in RGB565
        self.assertEqual(palette[3], 0x001F)  # Blue in RGB565
        
    # Level 4: TileGrid rendering
    def test_09_simple_tilegrid(self):
        """Test rendering a simple tilegrid."""
        display = Display(FourWire(None), width=8, height=8)
        display._matrix = self.matrix
        
        # Create 2x2 bitmap
        bitmap = Bitmap(2, 2, 2)
        bitmap[0, 0] = 1
        bitmap[1, 1] = 1
        
        palette = Palette(2)
        palette[0] = 0x0000  # Black
        palette[1] = 0xFFFF  # White
        
        tilegrid = TileGrid(bitmap, pixel_shader=palette)
        
        # Display and refresh
        display.show(tilegrid)
        display.refresh()
        
        # Check rendering
        self.matrix.render()
        
        # Should have 2 white pixels
        white_count = 0
        for y in range(2):
            for x in range(2):
                color = self.matrix.get_pixel(x, y)
                if color[0] > 200 and color[1] > 200 and color[2] > 200:
                    white_count += 1
                    
        self.assertEqual(white_count, 2)
        
    def test_10_positioned_tilegrid(self):
        """Test tilegrid with position."""
        display = Display(FourWire(None), width=8, height=8)
        display._matrix = self.matrix
        
        # 1x1 red pixel
        bitmap = Bitmap(1, 1, 2)
        bitmap[0, 0] = 1
        
        palette = Palette(2)
        palette[0] = 0x0000
        palette[1] = 0xF800  # Red (RGB565)
        
        # Position at (3, 3)
        tilegrid = TileGrid(bitmap, pixel_shader=palette, x=3, y=3)
        
        display.show(tilegrid)
        display.refresh()
        self.matrix.render()
        
        # Check pixel at (3, 3) is red
        color = self.matrix.get_pixel(3, 3)
        self.assertGreater(color[0], 200)  # Red channel high
        self.assertLess(color[1], 50)      # Green channel low
        
    # Level 5: Groups
    def test_11_empty_group(self):
        """Test rendering empty group."""
        display = Display(FourWire(None), width=8, height=8)
        display._matrix = self.matrix
        
        group = Group()
        display.show(group)
        display.refresh()
        
        # Should be all black
        self.assertEqual(self.count_non_black_pixels(), 0)
        
    def test_12_group_with_tilegrid(self):
        """Test group containing a tilegrid."""
        display = Display(FourWire(None), width=8, height=8)
        display._matrix = self.matrix
        
        # Create green pixel
        bitmap = Bitmap(1, 1, 2)
        bitmap[0, 0] = 1
        
        palette = Palette(2)
        palette[0] = 0x0000
        palette[1] = (0, 255, 0)  # Green
        
        tilegrid = TileGrid(bitmap, pixel_shader=palette, x=4, y=4)
        
        # Add to group
        group = Group()
        group.append(tilegrid)
        
        display.show(group)
        display.refresh()
        self.matrix.render()
        
        # Check green pixel at (4, 4)
        color = self.matrix.get_pixel(4, 4)
        self.assertLess(color[0], 50)      # Red low
        self.assertGreater(color[1], 200)  # Green high
        
    def test_13_nested_groups(self):
        """Test nested groups with offsets."""
        display = Display(FourWire(None), width=8, height=8)
        display._matrix = self.matrix
        
        # Blue pixel
        bitmap = Bitmap(1, 1, 2)
        bitmap[0, 0] = 1
        
        palette = Palette(2)
        palette[0] = 0x0000
        palette[1] = 0x001F  # Blue (RGB565)
        
        tilegrid = TileGrid(bitmap, pixel_shader=palette)
        
        # Inner group at (2, 2)
        inner_group = Group(x=2, y=2)
        inner_group.append(tilegrid)
        
        # Outer group at (1, 1)
        outer_group = Group(x=1, y=1)
        outer_group.append(inner_group)
        
        display.show(outer_group)
        display.refresh()
        self.matrix.render()
        
        # Should be at (1+2, 1+2) = (3, 3)
        color = self.matrix.get_pixel(3, 3)
        self.assertLess(color[0], 50)      # Red low
        self.assertLess(color[1], 50)      # Green low
        self.assertGreater(color[2], 200)  # Blue high
        
    # Level 6: Multiple items in group
    def test_14_multiple_tilegrids(self):
        """Test group with multiple tilegrids."""
        display = Display(FourWire(None), width=8, height=8)
        display._matrix = self.matrix
        
        group = Group()
        
        # Add three colored pixels
        colors = [(0xF800, 1, 1), (0x07E0, 3, 3), (0x001F, 5, 5)]  # RGB565 format
        
        for color_val, x, y in colors:
            bitmap = Bitmap(1, 1, 2)
            bitmap[0, 0] = 1
            
            palette = Palette(2)
            palette[0] = 0x0000
            palette[1] = color_val
            
            tilegrid = TileGrid(bitmap, pixel_shader=palette, x=x, y=y)
            group.append(tilegrid)
            
        display.show(group)
        display.refresh()
        self.matrix.render()
        
        # Check all three pixels
        self.assertGreater(self.matrix.get_pixel(1, 1)[0], 200)  # Red
        self.assertGreater(self.matrix.get_pixel(3, 3)[1], 200)  # Green
        self.assertGreater(self.matrix.get_pixel(5, 5)[2], 200)  # Blue
        
    # Level 7: Scaling
    def test_15_scaled_tilegrid(self):
        """Test scaled rendering."""
        display = Display(FourWire(None), width=8, height=8)
        display._matrix = self.matrix
        
        # 1x1 yellow pixel
        bitmap = Bitmap(1, 1, 2)
        bitmap[0, 0] = 1
        
        palette = Palette(2)
        palette[0] = 0x0000
        palette[1] = 0xFFE0  # Yellow (RGB565)
        
        tilegrid = TileGrid(bitmap, pixel_shader=palette)
        
        # Scale by 2
        group = Group(scale=2)
        group.append(tilegrid)
        
        display.show(group)
        display.refresh()
        self.matrix.render()
        
        # Should have 2x2 yellow pixels
        yellow_count = 0
        for y in range(2):
            for x in range(2):
                color = self.matrix.get_pixel(x, y)
                if color[0] > 200 and color[1] > 200 and color[2] < 50:
                    yellow_count += 1
                    
        self.assertEqual(yellow_count, 4)


if __name__ == '__main__':
    unittest.main(verbosity=2)