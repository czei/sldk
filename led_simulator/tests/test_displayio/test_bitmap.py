"""Unit tests for Bitmap class."""

import unittest
import numpy as np
from pyledsimulator.displayio.bitmap import Bitmap


class TestBitmap(unittest.TestCase):
    """Test cases for Bitmap functionality."""
    
    def test_initialization(self):
        """Test Bitmap initialization with different value counts."""
        # 2 colors (1 bit)
        bmp2 = Bitmap(10, 10, 2)
        self.assertEqual(bmp2.width, 10)
        self.assertEqual(bmp2.height, 10)
        self.assertEqual(bmp2.value_count, 2)
        self.assertEqual(bmp2.bits_per_value, 1)
        
        # 16 colors (4 bits)
        bmp16 = Bitmap(8, 8, 16)
        self.assertEqual(bmp16.bits_per_value, 4)
        
        # 256 colors (8 bits)
        bmp256 = Bitmap(5, 5, 256)
        self.assertEqual(bmp256.bits_per_value, 8)
        
    def test_pixel_access_tuple(self):
        """Test setting and getting pixels with tuple indices."""
        bmp = Bitmap(10, 10, 16)
        
        # Set pixel
        bmp[5, 5] = 7
        self.assertEqual(bmp[5, 5], 7)
        
        # Test bounds
        with self.assertRaises(IndexError):
            bmp[10, 5] = 1
        with self.assertRaises(IndexError):
            _ = bmp[5, 10]
            
        # Test value range
        with self.assertRaises(ValueError):
            bmp[5, 5] = 16  # Max is 15 for 16 colors
            
    def test_pixel_access_flat(self):
        """Test setting and getting pixels with flat indices."""
        bmp = Bitmap(4, 3, 8)  # 12 pixels total
        
        # Set pixel at index 5 (x=1, y=1)
        bmp[5] = 3
        self.assertEqual(bmp[5], 3)
        self.assertEqual(bmp[1, 1], 3)
        
        # Test bounds
        with self.assertRaises(IndexError):
            bmp[12] = 1
            
    def test_fill(self):
        """Test filling bitmap with a value."""
        bmp = Bitmap(5, 5, 4)
        bmp.fill(2)
        
        for y in range(5):
            for x in range(5):
                self.assertEqual(bmp[x, y], 2)
                
        # Test invalid value
        with self.assertRaises(ValueError):
            bmp.fill(4)  # Max is 3 for 4 colors
            
    def test_blit_basic(self):
        """Test basic blit operation."""
        # Create destination
        dest = Bitmap(10, 10, 8)
        dest.fill(0)
        
        # Create source
        src = Bitmap(3, 3, 8)
        src.fill(5)
        
        # Blit
        dest.blit(2, 2, src)
        
        # Check blitted area
        for y in range(2, 5):
            for x in range(2, 5):
                self.assertEqual(dest[x, y], 5)
                
        # Check non-blitted area
        self.assertEqual(dest[0, 0], 0)
        self.assertEqual(dest[6, 6], 0)
        
    def test_blit_with_region(self):
        """Test blit with source region."""
        dest = Bitmap(10, 10, 8)
        dest.fill(0)
        
        # Create source with pattern
        src = Bitmap(6, 6, 8)
        for y in range(6):
            for x in range(6):
                src[x, y] = (x + y) % 8
                
        # Blit region (x1=1, y1=1, x2=4, y2=4)
        dest.blit(3, 3, src, x1=1, y1=1, x2=4, y2=4)
        
        # Check blitted region
        for dy in range(3):
            for dx in range(3):
                expected = ((1 + dx) + (1 + dy)) % 8
                self.assertEqual(dest[3 + dx, 3 + dy], expected)
                
    def test_blit_with_transparency(self):
        """Test blit with transparent index."""
        dest = Bitmap(5, 5, 4)
        dest.fill(1)
        
        src = Bitmap(3, 3, 4)
        src[0, 0] = 2
        src[1, 1] = 0  # This will be transparent
        src[2, 2] = 3
        
        # Blit with index 0 as transparent
        dest.blit(1, 1, src, skip_index=0)
        
        # Check results
        self.assertEqual(dest[1, 1], 2)
        self.assertEqual(dest[2, 2], 1)  # Transparent, so original value
        self.assertEqual(dest[3, 3], 3)
        
    def test_blit_clipping(self):
        """Test blit with clipping at edges."""
        dest = Bitmap(5, 5, 4)
        dest.fill(0)
        
        src = Bitmap(3, 3, 4)
        src.fill(2)
        
        # Blit partially off right edge
        dest.blit(3, 1, src)
        
        # Check clipped blit
        self.assertEqual(dest[3, 1], 2)
        self.assertEqual(dest[4, 1], 2)
        # This would be at x=5, which is out of bounds
        
        # Blit partially off top edge
        dest.fill(0)
        dest.blit(1, -1, src)
        
        # Only bottom 2 rows should be copied
        self.assertEqual(dest[1, 0], 2)
        self.assertEqual(dest[1, 1], 2)
        self.assertEqual(dest[1, 2], 0)  # Not affected


if __name__ == '__main__':
    unittest.main()