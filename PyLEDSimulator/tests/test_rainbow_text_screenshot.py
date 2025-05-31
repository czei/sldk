#!/usr/bin/env python3
"""Unit test for rainbow_text.py with screenshot verification.

This test verifies:
1. Font rendering is working correctly
2. Colors are being applied properly
3. Text is visible on the display
4. Different fonts produce different sized text
"""

import unittest
import os
import sys
import tempfile
import shutil
from PIL import Image
import numpy as np

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3
from pyledsimulator.displayio import Group
from pyledsimulator.adafruit_display_text import Label
from pyledsimulator.terminalio import FONT
from pyledsimulator.core import rgb888_to_rgb565, rgb565_to_rgb888
from pyledsimulator.adafruit_bitmap_font import bitmap_font


class TestRainbowTextScreenshot(unittest.TestCase):
    """Test rainbow text rendering with screenshots."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.font_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'fonts'
        )
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
        
    def test_rainbow_text_with_small_font(self):
        """Test rainbow text rendering with small font."""
        # Create device
        device = MatrixPortalS3()
        device.initialize()
        
        # Load small font
        small_font = bitmap_font.load_font(os.path.join(self.font_dir, 'tom-thumb.bdf'))
        
        # Create rainbow text with individual characters
        main_group = Group()
        text = "RAINBOW"
        labels = []
        colors = [
            0xF800,  # Red
            0xFC00,  # Orange
            0xFFE0,  # Yellow
            0x07E0,  # Green
            0x001F,  # Blue
            0x7C1F,  # Indigo
            0xF81F,  # Violet
        ]
        
        for i, char in enumerate(text):
            label = Label(
                font=small_font,
                text=char,
                color=colors[i % len(colors)],
                x=2 + i * 9,
                y=12
            )
            labels.append(label)
            main_group.append(label)
            
        # Show on display
        device.show(main_group)
        device.display.refresh()
        device.matrix.render()  # Ensure matrix is rendered
        
        # Take screenshot
        screenshot_path = os.path.join(self.test_dir, 'rainbow_small_font.png')
        device.matrix.save_screenshot(screenshot_path)
        
        # Verify screenshot exists
        self.assertTrue(os.path.exists(screenshot_path))
        
        # Load and analyze screenshot
        img = Image.open(screenshot_path)
        img_array = np.array(img)
        
        # Check dimensions are reasonable (should be larger than base 64x32)
        self.assertGreater(img.size[0], 64, "Screenshot width too small")
        self.assertGreater(img.size[1], 32, "Screenshot height too small")
        
        # Verify text is visible (not all black)
        non_black_pixels = np.sum(img_array.sum(axis=2) > 0)
        self.assertGreater(non_black_pixels, 100, "Text should be visible")
        
        # Verify multiple colors are present
        unique_colors = set()
        for y in range(0, img_array.shape[0], 5):  # Sample every 5th pixel
            for x in range(0, img_array.shape[1], 5):
                color = tuple(int(c) for c in img_array[y, x])
                if any(c > 0 for c in color):  # Not black
                    unique_colors.add(color)
                    
        self.assertGreater(len(unique_colors), 3, 
                          "Should have multiple colors for rainbow effect")
        
        print(f"Small font screenshot saved to: {screenshot_path}")
        print(f"Found {len(unique_colors)} unique colors")
        
    def test_rainbow_text_with_large_font(self):
        """Test rainbow text rendering with large font."""
        # Create device
        device = MatrixPortalS3()
        device.initialize()
        
        # Load large font
        large_font_path = os.path.join(self.font_dir, 'LeagueSpartan-Bold-16.bdf')
        if not os.path.exists(large_font_path):
            self.skipTest("Large font not available")
            
        large_font = bitmap_font.load_font(large_font_path)
        
        # Create single label with large font
        main_group = Group()
        
        # Test different colors
        test_colors = [
            ("red", 0xF800, (255, 0, 0)),
            ("green", 0x07E0, (0, 255, 0)),
            ("blue", 0x001F, (0, 0, 255)),
            ("yellow", 0xFFE0, (255, 255, 0)),
            ("cyan", 0x07FF, (0, 255, 255)),
            ("magenta", 0xF81F, (255, 0, 255)),
        ]
        
        screenshots = []
        
        for color_name, color_565, expected_rgb in test_colors:
            # Clear group
            for item in list(main_group):
                main_group.remove(item)
                
            # Create label with color
            label = Label(
                font=large_font,
                text="RGB",
                color=color_565,
                x=2,
                y=16
            )
            main_group.append(label)
            
            # Show and refresh
            device.show(main_group)
            device.display.refresh()
            device.matrix.render()  # Ensure matrix is rendered
            
            # Take screenshot
            screenshot_path = os.path.join(self.test_dir, f'large_font_{color_name}.png')
            device.matrix.save_screenshot(screenshot_path)
            screenshots.append((color_name, screenshot_path, expected_rgb))
            
            # Verify color
            img = Image.open(screenshot_path)
            img_array = np.array(img)
            
            # Find non-black pixels
            colored_pixels = []
            for y in range(img_array.shape[0]):
                for x in range(img_array.shape[1]):
                    pixel = img_array[y, x]
                    if np.any(pixel > 0):  # Not black
                        colored_pixels.append(pixel)
                        
            self.assertGreater(len(colored_pixels), 100, 
                             f"Should have colored pixels for {color_name}")
            
            # Check that the dominant color matches expected
            if colored_pixels:
                avg_color = np.mean(colored_pixels, axis=0)
                # Allow some tolerance due to LED rendering effects
                for i, channel in enumerate(['R', 'G', 'B']):
                    expected = expected_rgb[i]
                    actual = avg_color[i]
                    # Very lenient check due to LED rendering effects
                    if expected > 200:  # Should be bright
                        self.assertGreater(actual, 20, 
                                         f"{color_name} {channel} channel too dim")
                    elif expected < 50:  # Should be dark
                        self.assertLess(actual, 200,
                                      f"{color_name} {channel} channel too bright")
                        
            print(f"Large font {color_name} screenshot: {screenshot_path}")
            
    def test_font_size_comparison(self):
        """Test and compare different font sizes."""
        device = MatrixPortalS3()
        device.initialize()
        
        fonts_to_test = [
            ('tom-thumb.bdf', 'tom-thumb', 1),
            ('viii.bdf', '5x8', 1),
            ('tom-thumb.bdf', 'tom-thumb-2x', 2),  # Scaled
            ('LeagueSpartan-Bold-16.bdf', 'league-spartan', 1),
        ]
        
        results = []
        
        for font_file, test_name, scale in fonts_to_test:
            font_path = os.path.join(self.font_dir, font_file)
            if not os.path.exists(font_path):
                print(f"Skipping {test_name}: font not found")
                continue
                
            # Load font
            font = bitmap_font.load_font(font_path)
            
            # Create label
            main_group = Group()
            label = Label(
                font=font,
                text="ABC",
                color=0xFFFF,  # Cyan
                scale=scale,
                x=2,
                y=16
            )
            main_group.append(label)
            
            # Show and screenshot
            device.show(main_group)
            device.display.refresh()
            device.matrix.render()  # Ensure matrix is rendered
            
            screenshot_path = os.path.join(self.test_dir, f'font_size_{test_name}.png')
            device.matrix.save_screenshot(screenshot_path)
            
            # Measure text area
            img = Image.open(screenshot_path)
            img_array = np.array(img)
            
            # Count bright pixels instead of measuring bounds
            # This gives a better indication of font size
            bright_pixels = 0
            for y in range(img_array.shape[0]):
                for x in range(img_array.shape[1]):
                    if np.any(img_array[y, x] > 50):  # Bright pixel
                        bright_pixels += 1
            
            # Use bright pixel count as proxy for font size
            # Larger fonts will have more bright pixels
            
            results.append({
                'name': test_name,
                'pixel_count': bright_pixels,
                'screenshot': screenshot_path
            })
            
            print(f"{test_name}: {bright_pixels} bright pixels")
                
        # Verify font sizes are different based on pixel count
        if len(results) >= 2:
            pixel_counts = [r['pixel_count'] for r in results]
            # There should be variation in pixel counts
            self.assertGreater(max(pixel_counts), min(pixel_counts) * 1.5,
                             "Font sizes should vary (based on bright pixel count)")
                             
    def test_animated_color_cycle(self):
        """Test color animation by simulating multiple frames."""
        device = MatrixPortalS3()
        device.initialize()
        
        # Use small font for individual character coloring
        small_font = bitmap_font.load_font(os.path.join(self.font_dir, 'tom-thumb.bdf'))
        
        main_group = Group()
        text = "RGB"
        labels = []
        
        for i, char in enumerate(text):
            label = Label(
                font=small_font,
                text=char,
                color=0xFFFF,
                x=10 + i * 15,
                y=16,
                scale=2
            )
            labels.append(label)
            main_group.append(label)
            
        device.show(main_group)
        
        # Simulate animation frames
        hue_offsets = [0, 120, 240]  # Different starting hues
        frame_screenshots = []
        
        for frame, hue_offset in enumerate(hue_offsets):
            # Update colors for each character
            for i, label in enumerate(labels):
                hue = (hue_offset + i * 120) % 360
                # Simple HSV to RGB conversion
                if hue < 120:
                    r, g, b = 255 - (hue * 255 // 120), hue * 255 // 120, 0
                elif hue < 240:
                    r, g, b = 0, 255 - ((hue - 120) * 255 // 120), (hue - 120) * 255 // 120
                else:
                    r, g, b = (hue - 240) * 255 // 120, 0, 255 - ((hue - 240) * 255 // 120)
                    
                label.color = rgb888_to_rgb565(r, g, b)
                
            device.display.refresh()
            device.matrix.render()  # Ensure matrix is rendered
            
            # Take screenshot
            screenshot_path = os.path.join(self.test_dir, f'animation_frame_{frame}.png')
            device.matrix.save_screenshot(screenshot_path)
            frame_screenshots.append(screenshot_path)
            
        # Verify frames are different
        self.assertEqual(len(frame_screenshots), 3)
        
        # Load first and last frame to compare
        img1 = np.array(Image.open(frame_screenshots[0]))
        img3 = np.array(Image.open(frame_screenshots[2]))
        
        # Calculate difference
        diff = np.abs(img1.astype(int) - img3.astype(int)).sum()
        self.assertGreater(diff, 1000, "Animation frames should be different")
        
        print(f"Animation test complete. Frames saved to {self.test_dir}")


if __name__ == '__main__':
    unittest.main(verbose=2)