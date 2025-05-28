"""Unit tests for LEDMatrix class with visual verification."""

import unittest
import pygame
import numpy as np
from pyledsimulator.core.led_matrix import LEDMatrix
from pyledsimulator.core.color_utils import RED, GREEN, BLUE


class TestLEDMatrix(unittest.TestCase):
    """Test cases for LEDMatrix functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Initialize pygame once for all tests."""
        pygame.init()
        
    def setUp(self):
        """Set up test fixtures."""
        self.matrix = LEDMatrix(8, 8, pitch=4.0)
        self.matrix.initialize_surface()
        
    def test_initialization(self):
        """Test LEDMatrix initialization."""
        self.assertEqual(self.matrix.width, 8)
        self.assertEqual(self.matrix.height, 8)
        self.assertEqual(self.matrix.pitch, 4.0)
        
        # Check LED size calculation (80% of pitch * scale factor)
        expected_led_size = int(4.0 * 0.8 * 4)
        self.assertEqual(self.matrix.led_size, expected_led_size)
        
        # Check surface dimensions
        expected_width = 8 * (self.matrix.led_size + self.matrix.spacing) - self.matrix.spacing
        self.assertEqual(self.matrix.surface_width, expected_width)
        
    def test_set_pixel(self):
        """Test setting individual pixels."""
        # Set a red pixel
        self.matrix.set_pixel(0, 0, (255, 0, 0))
        color = self.matrix.get_pixel(0, 0)
        self.assertEqual(color, (255, 0, 0))
        
        # Set with RGB value
        self.matrix.set_pixel(1, 1, 0x00FF00)  # Green
        color = self.matrix.get_pixel(1, 1)
        self.assertEqual(color, (0, 255, 0))
        
    def test_fill_and_clear(self):
        """Test fill and clear operations."""
        # Fill with blue
        self.matrix.fill((0, 0, 255))
        for y in range(8):
            for x in range(8):
                self.assertEqual(self.matrix.get_pixel(x, y), (0, 0, 255))
                
        # Clear
        self.matrix.clear()
        for y in range(8):
            for x in range(8):
                self.assertEqual(self.matrix.get_pixel(x, y), (0, 0, 0))
                
    def test_brightness(self):
        """Test brightness control."""
        self.matrix.set_brightness(0.5)
        self.assertEqual(self.matrix.brightness, 0.5)
        
        # Test clamping
        self.matrix.set_brightness(1.5)
        self.assertEqual(self.matrix.brightness, 1.0)
        
        self.matrix.set_brightness(-0.5)
        self.assertEqual(self.matrix.brightness, 0.0)
        
    def test_render_creates_surface(self):
        """Test that render creates the pygame surface."""
        # Set some pixels
        self.matrix.set_pixel(0, 0, (255, 0, 0))
        self.matrix.set_pixel(7, 7, (0, 255, 0))
        
        # Render
        self.matrix.render()
        
        # Check surface exists
        surface = self.matrix.get_surface()
        self.assertIsNotNone(surface)
        self.assertIsInstance(surface, pygame.Surface)
        
    def test_visual_verification(self):
        """Test visual output by checking rendered surface pixels."""
        # Create a simple pattern
        self.matrix.set_pixel(0, 0, (255, 0, 0))  # Red top-left
        self.matrix.set_pixel(7, 0, (0, 255, 0))  # Green top-right
        self.matrix.set_pixel(0, 7, (0, 0, 255))  # Blue bottom-left
        self.matrix.set_pixel(7, 7, (255, 255, 255))  # White bottom-right
        
        # Render
        self.matrix.render()
        surface = self.matrix.get_surface()
        
        # Convert surface to array for testing
        pixels = pygame.surfarray.array3d(surface)
        
        # Check that the corners have the expected colors
        # Note: pygame.surfarray returns (x, y, rgb) not (y, x, rgb)
        
        # Top-left should be reddish
        led_center = self.matrix.led_size // 2
        top_left_color = pixels[led_center, led_center]
        self.assertGreater(top_left_color[0], 200)  # Red channel high
        self.assertLess(top_left_color[1], 100)     # Green channel low
        self.assertLess(top_left_color[2], 100)     # Blue channel low
        
        # Bottom-right should be whitish
        br_x = self.matrix.surface_width - led_center - 1
        br_y = self.matrix.surface_height - led_center - 1
        bottom_right_color = pixels[br_x, br_y]
        self.assertGreater(bottom_right_color[0], 200)  # All channels high
        self.assertGreater(bottom_right_color[1], 200)
        self.assertGreater(bottom_right_color[2], 200)
        
    def test_led_rendering_with_spacing(self):
        """Test that LEDs are rendered with proper spacing."""
        # Set alternating pattern
        for y in range(4):
            for x in range(4):
                if (x + y) % 2 == 0:
                    self.matrix.set_pixel(x * 2, y * 2, (255, 255, 255))
                    
        self.matrix.render()
        surface = self.matrix.get_surface()
        pixels = pygame.surfarray.array3d(surface)
        
        # Check that there's dark space between LEDs
        gap_x = self.matrix.led_size + self.matrix.spacing // 2
        gap_color = pixels[gap_x, gap_x]
        
        # Gap should be dark (background color)
        self.assertLess(gap_color[0], 50)
        self.assertLess(gap_color[1], 50)
        self.assertLess(gap_color[2], 50)
        
    def test_screenshot(self):
        """Test screenshot functionality."""
        import os
        import tempfile
        
        # Create pattern
        self.matrix.fill((128, 64, 32))
        self.matrix.render()
        
        # Save screenshot
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
            
        try:
            self.matrix.save_screenshot(temp_path)
            self.assertTrue(os.path.exists(temp_path))
            
            # Load and verify
            loaded_surface = pygame.image.load(temp_path)
            self.assertEqual(loaded_surface.get_size(), 
                           (self.matrix.surface_width, self.matrix.surface_height))
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()