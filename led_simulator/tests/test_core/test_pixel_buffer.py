"""Unit tests for PixelBuffer class."""

import unittest
import numpy as np
from pyledsimulator.core.pixel_buffer import PixelBuffer


class TestPixelBuffer(unittest.TestCase):
    """Test cases for PixelBuffer functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.buffer = PixelBuffer(10, 10)
        
    def test_initialization(self):
        """Test PixelBuffer initialization."""
        self.assertEqual(self.buffer.width, 10)
        self.assertEqual(self.buffer.height, 10)
        self.assertTrue(self.buffer.is_dirty())
        
        # Check buffer is initialized to black
        buffer_data = self.buffer.get_buffer()
        self.assertTrue(np.all(buffer_data == 0))
        
    def test_set_pixel(self):
        """Test setting individual pixels."""
        # Set pixel with tuple
        self.buffer.set_pixel(5, 5, (255, 128, 64))
        color = self.buffer.get_pixel(5, 5)
        self.assertEqual(color, (255, 128, 64))
        
        # Set pixel with packed RGB
        self.buffer.set_pixel(3, 3, 0xFF8040)  # RGB(255, 128, 64)
        color = self.buffer.get_pixel(3, 3)
        self.assertEqual(color, (255, 128, 64))
        
        # Test bounds checking
        self.buffer.set_pixel(-1, 5, (255, 0, 0))  # Should not crash
        self.buffer.set_pixel(5, 10, (255, 0, 0))  # Should not crash
        
    def test_fill(self):
        """Test filling entire buffer."""
        # Fill with tuple
        self.buffer.fill((128, 64, 32))
        for y in range(10):
            for x in range(10):
                self.assertEqual(self.buffer.get_pixel(x, y), (128, 64, 32))
                
        # Fill with packed RGB
        self.buffer.fill(0x204080)  # RGB(32, 64, 128)
        color = self.buffer.get_pixel(0, 0)
        self.assertEqual(color, (32, 64, 128))
        
    def test_clear(self):
        """Test clearing buffer."""
        self.buffer.fill((255, 255, 255))
        self.buffer.clear()
        for y in range(10):
            for x in range(10):
                self.assertEqual(self.buffer.get_pixel(x, y), (0, 0, 0))
                
    def test_blit(self):
        """Test blitting from another buffer."""
        # Create source buffer
        source = PixelBuffer(5, 5)
        source.fill((255, 0, 0))
        
        # Blit to destination
        self.buffer.blit(source, 2, 2)
        
        # Check blitted area
        for y in range(2, 7):
            for x in range(2, 7):
                self.assertEqual(self.buffer.get_pixel(x, y), (255, 0, 0))
                
        # Check non-blitted area remains black
        self.assertEqual(self.buffer.get_pixel(0, 0), (0, 0, 0))
        self.assertEqual(self.buffer.get_pixel(8, 8), (0, 0, 0))
        
    def test_blit_with_transparency(self):
        """Test blitting with transparent color."""
        # Set up destination with pattern
        self.buffer.fill((0, 255, 0))
        
        # Create source with transparent pixels
        source = PixelBuffer(3, 3)
        source.set_pixel(0, 0, (255, 0, 0))
        source.set_pixel(1, 1, (0, 0, 0))  # This will be transparent
        source.set_pixel(2, 2, (0, 0, 255))
        
        # Blit with black as transparent
        self.buffer.blit(source, 4, 4, key_color=(0, 0, 0))
        
        # Check results
        self.assertEqual(self.buffer.get_pixel(4, 4), (255, 0, 0))
        self.assertEqual(self.buffer.get_pixel(5, 5), (0, 255, 0))  # Transparent, so green shows through
        self.assertEqual(self.buffer.get_pixel(6, 6), (0, 0, 255))
        
    def test_dirty_tracking(self):
        """Test dirty region tracking."""
        self.buffer.clear_dirty()
        self.assertFalse(self.buffer.is_dirty())
        
        # Set a pixel
        self.buffer.set_pixel(5, 5, (255, 0, 0))
        self.assertTrue(self.buffer.is_dirty())
        region = self.buffer.get_dirty_region()
        self.assertEqual(region, (5, 5, 5, 5))
        
        # Expand dirty region
        self.buffer.set_pixel(7, 8, (0, 255, 0))
        region = self.buffer.get_dirty_region()
        self.assertEqual(region, (5, 5, 7, 8))
        
        # Fill makes entire buffer dirty
        self.buffer.clear_dirty()
        self.buffer.fill((255, 255, 255))
        self.assertTrue(self.buffer.is_dirty())
        self.assertIsNone(self.buffer.get_dirty_region())
        
    def test_apply_brightness(self):
        """Test brightness adjustment."""
        self.buffer.fill((200, 100, 50))
        self.buffer.apply_brightness(0.5)
        
        # Check dimmed values
        color = self.buffer.get_pixel(0, 0)
        self.assertEqual(color, (100, 50, 25))


if __name__ == '__main__':
    unittest.main()