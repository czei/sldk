"""Unit tests for Display class with rendering verification."""

import unittest
import pygame
from pyledsimulator.displayio import Display, Group, Bitmap, Palette, TileGrid, FourWire
from pyledsimulator.core import LEDMatrix
from pyledsimulator.adafruit_display_text import Label
from pyledsimulator.terminalio import FONT


class TestDisplay(unittest.TestCase):
    """Test cases for Display functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Initialize pygame once for all tests."""
        pygame.init()
        
    def setUp(self):
        """Set up test fixtures."""
        # Create display with small size for testing
        self.display = Display(
            FourWire(None),
            width=16,
            height=8,
            rotation=0
        )
        
    def test_initialization(self):
        """Test Display initialization."""
        self.assertEqual(self.display.width, 16)
        self.assertEqual(self.display.height, 8)
        self.assertEqual(self.display.rotation, 0)
        self.assertEqual(self.display.brightness, 1.0)
        self.assertTrue(self.display.auto_refresh)
        self.assertIsNone(self.display.root_group)
        
    def test_brightness_control(self):
        """Test brightness property."""
        self.display.brightness = 0.5
        self.assertEqual(self.display.brightness, 0.5)
        
        # Test clamping
        self.display.brightness = 1.5
        self.assertEqual(self.display.brightness, 1.0)
        
        self.display.brightness = -0.5
        self.assertEqual(self.display.brightness, 0.0)
        
    def test_show_group(self):
        """Test showing a Group."""
        group = Group()
        self.display.show(group)
        self.assertEqual(self.display.root_group, group)
        
    def test_render_empty_group(self):
        """Test rendering an empty group."""
        group = Group()
        self.display.show(group)
        self.display.refresh()
        
        # Should not crash, matrix should be cleared
        matrix = self.display.get_matrix()
        # Check a pixel is black
        color = matrix.get_pixel(0, 0)
        self.assertEqual(color, (0, 0, 0))
        
    def test_render_simple_tilegrid(self):
        """Test rendering a simple TileGrid."""
        # Create bitmap with one white pixel
        bitmap = Bitmap(4, 4, 2)
        bitmap.fill(0)  # Black
        bitmap[1, 1] = 1  # White pixel
        
        # Create palette
        palette = Palette(2)
        palette[0] = 0x000000  # Black
        palette[1] = 0xFFFFFF  # White
        
        # Create TileGrid
        tilegrid = TileGrid(bitmap, pixel_shader=palette)
        
        # Show and render
        self.display.show(tilegrid)
        self.display.refresh()
        
        # Verify rendering
        matrix = self.display.get_matrix()
        # White pixel should be at (1, 1)
        color = matrix.get_pixel(1, 1)
        self.assertEqual(color, (255, 255, 255))
        
        # Other pixels should be black
        color = matrix.get_pixel(0, 0)
        self.assertEqual(color, (0, 0, 0))
        
    def test_render_group_with_position(self):
        """Test rendering a positioned group."""
        # Create small bitmap
        bitmap = Bitmap(2, 2, 2)
        bitmap.fill(1)  # All white
        
        palette = Palette(2)
        palette[0] = 0x000000
        palette[1] = 0xFF0000  # Red
        
        tilegrid = TileGrid(bitmap, pixel_shader=palette)
        
        # Create positioned group
        group = Group(x=5, y=3)
        group.append(tilegrid)
        
        # Render
        self.display.show(group)
        self.display.refresh()
        
        # Check rendering position
        matrix = self.display.get_matrix()
        # Red should be at offset position
        color = matrix.get_pixel(5, 3)
        self.assertEqual(color, (255, 0, 0))
        
        # Original position should be black
        color = matrix.get_pixel(0, 0)
        self.assertEqual(color, (0, 0, 0))
        
    def test_render_scaled_group(self):
        """Test rendering a scaled group."""
        # Create 1x1 bitmap
        bitmap = Bitmap(1, 1, 2)
        bitmap[0, 0] = 1
        
        palette = Palette(2)
        palette[0] = 0x000000
        palette[1] = 0x00FF00  # Green
        
        tilegrid = TileGrid(bitmap, pixel_shader=palette)
        
        # Create scaled group (2x scale)
        group = Group(scale=2)
        group.append(tilegrid)
        
        # Render
        self.display.show(group)
        self.display.refresh()
        
        # Check that pixel is scaled to 2x2
        matrix = self.display.get_matrix()
        for y in range(2):
            for x in range(2):
                color = matrix.get_pixel(x, y)
                self.assertEqual(color, (0, 255, 0))
                
    def test_render_nested_groups(self):
        """Test rendering nested groups."""
        # Create bitmap
        bitmap = Bitmap(1, 1, 2)
        bitmap[0, 0] = 1
        
        palette = Palette(2)
        palette[0] = 0x000000
        palette[1] = 0x0000FF  # Blue
        
        tilegrid = TileGrid(bitmap, pixel_shader=palette)
        
        # Create nested groups
        inner_group = Group(x=2, y=2)
        inner_group.append(tilegrid)
        
        outer_group = Group(x=3, y=1)
        outer_group.append(inner_group)
        
        # Render
        self.display.show(outer_group)
        self.display.refresh()
        
        # Check cumulative position (3+2, 1+2) = (5, 3)
        matrix = self.display.get_matrix()
        color = matrix.get_pixel(5, 3)
        self.assertEqual(color, (0, 0, 255))
        
    def test_render_hidden_group(self):
        """Test that hidden groups are not rendered."""
        # Create visible content
        bitmap = Bitmap(2, 2, 2)
        bitmap.fill(1)
        
        palette = Palette(2)
        palette[0] = 0x000000
        palette[1] = 0xFFFFFF  # White
        
        tilegrid = TileGrid(bitmap, pixel_shader=palette)
        
        # Create hidden group
        group = Group()
        group.hidden = True
        group.append(tilegrid)
        
        # Render
        self.display.show(group)
        self.display.refresh()
        
        # Should be all black (nothing rendered)
        matrix = self.display.get_matrix()
        color = matrix.get_pixel(0, 0)
        self.assertEqual(color, (0, 0, 0))
        
    def test_render_label(self):
        """Test rendering a text label."""
        # Create label
        label = Label(
            font=FONT,
            text="Hi",
            color=0xFFFF00,  # Yellow
            x=0,
            y=5
        )
        
        # Show and render
        self.display.show(label)
        self.display.refresh()
        
        # Check that some pixels are yellow (text rendered)
        matrix = self.display.get_matrix()
        
        # Look for any yellow pixels in expected area
        found_yellow = False
        for y in range(8):
            for x in range(16):
                color = matrix.get_pixel(x, y)
                if color[0] > 200 and color[1] > 200 and color[2] < 50:
                    found_yellow = True
                    break
            if found_yellow:
                break
                
        self.assertTrue(found_yellow, "No yellow pixels found - label not rendered")
        
    def test_render_with_transparency(self):
        """Test rendering with transparent palette entries."""
        # Create bitmap with mixed content
        bitmap = Bitmap(4, 4, 3)
        bitmap[0, 0] = 0  # Transparent
        bitmap[1, 1] = 1  # Red
        bitmap[2, 2] = 2  # Green
        
        palette = Palette(3)
        palette[0] = 0x000000  # Will be made transparent
        palette[1] = 0xFF0000  # Red
        palette[2] = 0x00FF00  # Green
        palette.make_transparent(0)
        
        # First fill display with blue
        background = Bitmap(16, 8, 2)
        background.fill(1)
        bg_palette = Palette(2)
        bg_palette[0] = 0x000000
        bg_palette[1] = 0x0000FF  # Blue
        
        group = Group()
        group.append(TileGrid(background, pixel_shader=bg_palette))
        group.append(TileGrid(bitmap, pixel_shader=palette))
        
        # Render
        self.display.show(group)
        self.display.refresh()
        
        # Check results
        matrix = self.display.get_matrix()
        
        # (0,0) should be blue (transparent shows through)
        color = matrix.get_pixel(0, 0)
        self.assertEqual(color, (0, 0, 255))
        
        # (1,1) should be red
        color = matrix.get_pixel(1, 1)
        self.assertEqual(color, (255, 0, 0))
        
        # (2,2) should be green
        color = matrix.get_pixel(2, 2)
        self.assertEqual(color, (0, 255, 0))


if __name__ == '__main__':
    unittest.main()