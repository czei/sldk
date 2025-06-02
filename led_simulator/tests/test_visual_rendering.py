#!/usr/bin/env python3
"""Visual rendering tests with image comparison."""

import unittest
import pygame
import numpy as np
import os
import tempfile
from PIL import Image

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3
from pyledsimulator.displayio import Group, Bitmap, Palette, TileGrid
from pyledsimulator.adafruit_display_text import Label
from pyledsimulator.terminalio import FONT
from pyledsimulator.core import RED, GREEN, BLUE, WHITE, BLACK


class TestVisualRendering(unittest.TestCase):
    """Test visual rendering with actual image comparison."""
    
    @classmethod
    def setUpClass(cls):
        """Initialize pygame once for all tests."""
        pygame.init()
        
    def setUp(self):
        """Set up test fixtures."""
        self.device = MatrixPortalS3(width=16, height=8)  # Smaller for easier testing
        self.device.initialize()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up temp files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def capture_display(self):
        """Capture the current display as a numpy array."""
        # Ensure display is refreshed
        self.device.display.refresh()
        
        # Get the LED matrix and render it
        matrix = self.device.display.get_matrix()
        matrix.render()
        
        # Get the surface
        surface = matrix.get_surface()
        
        # Convert to numpy array
        pixels = pygame.surfarray.array3d(surface)
        
        # Return as (height, width, channels) instead of pygame's (width, height, channels)
        return np.transpose(pixels, (1, 0, 2))
        
    def save_debug_image(self, name, pixels):
        """Save a debug image for manual inspection."""
        path = os.path.join(self.temp_dir, f"{name}.png")
        Image.fromarray(pixels.astype(np.uint8)).save(path)
        return path
        
    def get_led_pixel_color(self, x, y):
        """Get the color of a specific LED pixel from the rendered surface."""
        matrix = self.device.display.get_matrix()
        
        # Calculate the center position of the LED
        led_center_x = x * (matrix.led_size + matrix.spacing) + matrix.led_size // 2
        led_center_y = y * (matrix.led_size + matrix.spacing) + matrix.led_size // 2
        
        # Get surface and pixels
        surface = matrix.get_surface()
        pixels = pygame.surfarray.array3d(surface)
        
        # Get color at LED center (remember pygame uses x,y not y,x)
        color = pixels[led_center_x, led_center_y]
        
        return tuple(color)
        
    def assert_led_color(self, x, y, expected_color, tolerance=120):
        """Assert that an LED has the expected color."""
        actual_color = self.get_led_pixel_color(x, y)
        
        # Check each channel
        for i in range(3):
            diff = abs(int(actual_color[i]) - int(expected_color[i]))
            self.assertLessEqual(
                diff, tolerance,
                f"LED ({x},{y}) color channel {i}: expected {expected_color[i]}, "
                f"got {actual_color[i]} (full color: {actual_color})"
            )
            
    def test_direct_pixel_rendering(self):
        """Test that direct pixel setting works."""
        # Set pixels directly on the matrix
        matrix = self.device.display.get_matrix()
        
        matrix.set_pixel(0, 0, (255, 0, 0))    # Red
        matrix.set_pixel(5, 3, (0, 255, 0))    # Green
        matrix.set_pixel(10, 6, (0, 0, 255))   # Blue
        matrix.set_pixel(15, 7, (255, 255, 255))  # White
        
        # Render
        matrix.render()
        
        # Save debug image
        pixels = self.capture_display()
        path = self.save_debug_image("test_direct_pixels", pixels)
        print(f"Debug image saved to: {path}")
        
        # Check colors
        self.assert_led_color(0, 0, (255, 0, 0))
        self.assert_led_color(5, 3, (0, 255, 0))
        self.assert_led_color(10, 6, (0, 0, 255))
        self.assert_led_color(15, 7, (255, 255, 255))
        
    def test_bitmap_rendering(self):
        """Test that bitmap rendering through displayio works."""
        # Create a bitmap with a pattern
        bitmap = Bitmap(8, 4, 4)
        
        # Create pattern
        bitmap[0, 0] = 1  # Red
        bitmap[2, 0] = 2  # Green
        bitmap[4, 0] = 3  # Blue
        bitmap[0, 2] = 3  # Blue
        bitmap[2, 2] = 1  # Red
        bitmap[4, 2] = 2  # Green
        
        # Create palette
        palette = Palette(4)
        palette[0] = 0x000000  # Black
        palette[1] = 0xFF0000  # Red
        palette[2] = 0x00FF00  # Green
        palette[3] = 0x0000FF  # Blue
        
        # Create tilegrid
        tilegrid = TileGrid(bitmap, pixel_shader=palette, x=4, y=2)
        
        # Display it
        self.device.display.show(tilegrid)
        self.device.display.refresh()
        
        # Save debug image
        pixels = self.capture_display()
        path = self.save_debug_image("test_bitmap", pixels)
        print(f"Debug image saved to: {path}")
        
        # Check colors at offset positions
        self.assert_led_color(4, 2, (255, 0, 0))   # Red
        self.assert_led_color(6, 2, (0, 255, 0))   # Green
        self.assert_led_color(8, 2, (0, 0, 255))   # Blue
        
    def test_label_rendering(self):
        """Test that labels render correctly."""
        # Create a label
        label = Label(
            font=FONT,
            text="Hi",
            color=0xFFFF00,  # Yellow
            x=2,
            y=4
        )
        
        # Display it
        self.device.display.show(label)
        self.device.display.refresh()
        
        # Save debug image
        pixels = self.capture_display()
        path = self.save_debug_image("test_label", pixels)
        print(f"Debug image saved to: {path}")
        
        # Check that there are yellow pixels somewhere
        found_yellow = False
        for y in range(8):
            for x in range(16):
                color = self.get_led_pixel_color(x, y)
                # Yellow is high red and green, low blue
                if color[0] > 200 and color[1] > 200 and color[2] < 50:
                    found_yellow = True
                    break
            if found_yellow:
                break
                
        self.assertTrue(found_yellow, "No yellow pixels found - label not rendered")
        
    def test_group_with_background(self):
        """Test rendering a group with background and foreground."""
        group = Group()
        
        # Blue background
        bg_bitmap = Bitmap(16, 8, 2)
        bg_bitmap.fill(1)
        bg_palette = Palette(2)
        bg_palette[0] = 0x000000
        bg_palette[1] = 0x0000FF  # Blue
        group.append(TileGrid(bg_bitmap, pixel_shader=bg_palette))
        
        # Red square on top
        fg_bitmap = Bitmap(4, 4, 2)
        fg_bitmap.fill(1)
        fg_palette = Palette(2)
        fg_palette[0] = 0x000000
        fg_palette[1] = 0xFF0000  # Red
        group.append(TileGrid(fg_bitmap, pixel_shader=fg_palette, x=6, y=2))
        
        # Display
        self.device.display.show(group)
        self.device.display.refresh()
        
        # Save debug image
        pixels = self.capture_display()
        path = self.save_debug_image("test_group_bg", pixels)
        print(f"Debug image saved to: {path}")
        
        # Check background is blue
        self.assert_led_color(0, 0, (0, 0, 255))
        self.assert_led_color(15, 7, (0, 0, 255))
        
        # Check foreground is red
        self.assert_led_color(6, 2, (255, 0, 0))
        self.assert_led_color(9, 5, (255, 0, 0))
        
    def test_scaled_rendering(self):
        """Test that scaling works correctly."""
        # 2x2 bitmap
        bitmap = Bitmap(2, 2, 2)
        bitmap[0, 0] = 1
        bitmap[1, 1] = 1
        
        palette = Palette(2)
        palette[0] = 0x000000
        palette[1] = 0x00FF00  # Green
        
        # Scale by 2
        group = Group(scale=2)
        group.append(TileGrid(bitmap, pixel_shader=palette))
        
        # Display
        self.device.display.show(group)
        self.device.display.refresh()
        
        # Save debug image
        pixels = self.capture_display()
        path = self.save_debug_image("test_scaled", pixels)
        print(f"Debug image saved to: {path}")
        
        # Check scaled pixels
        self.assert_led_color(0, 0, (0, 255, 0))
        self.assert_led_color(1, 0, (0, 255, 0))
        self.assert_led_color(0, 1, (0, 255, 0))
        self.assert_led_color(1, 1, (0, 255, 0))
        
        # And the other diagonal
        self.assert_led_color(2, 2, (0, 255, 0))
        self.assert_led_color(3, 2, (0, 255, 0))
        self.assert_led_color(2, 3, (0, 255, 0))
        self.assert_led_color(3, 3, (0, 255, 0))
        
    def test_compare_with_reference_image(self):
        """Test comparing rendered output with a reference image."""
        # Create a known pattern
        bitmap = Bitmap(4, 4, 2)
        # Checkerboard pattern
        for y in range(4):
            for x in range(4):
                bitmap[x, y] = (x + y) % 2
                
        palette = Palette(2)
        palette[0] = 0xFF0000  # Red
        palette[1] = 0x00FF00  # Green
        
        tilegrid = TileGrid(bitmap, pixel_shader=palette)
        
        # Display
        self.device.display.show(tilegrid)
        self.device.display.refresh()
        
        # Get the display content
        pixels = self.capture_display()
        
        # Save for inspection
        path = self.save_debug_image("test_checkerboard", pixels)
        print(f"Debug image saved to: {path}")
        
        # Verify checkerboard pattern
        for y in range(4):
            for x in range(4):
                expected_color = (255, 0, 0) if (x + y) % 2 == 0 else (0, 255, 0)
                self.assert_led_color(x, y, expected_color)


if __name__ == '__main__':
    unittest.main(verbosity=2)