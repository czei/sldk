#!/usr/bin/env python3
"""Comprehensive font testing for PyLEDSimulator.

Tests all available fonts with:
- All uppercase letters A-Z
- All numbers 0-9
- Different font sizes
- Rendering accuracy
"""

import unittest
import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pyledsimulator.adafruit_bitmap_font import bitmap_font
from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.displayio import Display, Group, FourWire
from pyledsimulator.core import LEDMatrix


class TestFontsComprehensive(unittest.TestCase):
    """Test all fonts with all characters."""
    
    @classmethod
    def setUpClass(cls):
        """Load all available fonts."""
        font_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'fonts'
        )
        
        cls.fonts = {}
        cls.invalid_fonts = []
        
        # Load fonts with error handling
        font_files = {
            'tom-thumb': 'tom-thumb.bdf',
            '5x8': 'viii.bdf',
            # Note: The following fonts appear to be HTML files instead of BDF
            # They need to be properly downloaded or converted
            'LeagueSpartan-16': 'LeagueSpartan-Bold-16.bdf',
            'LibreBodoni-27': 'LibreBodoniv2002-Bold-27.bdf'
        }
        
        for name, filename in font_files.items():
            try:
                font_path = os.path.join(font_dir, filename)
                font = bitmap_font.load_font(font_path)
                # Skip fonts with invalid metrics (likely HTML files)
                if font.height == 0 or font.ascent == 0:
                    print(f"Skipping {name}: Invalid font metrics (height={font.height}, ascent={font.ascent})")
                    cls.invalid_fonts.append(name)
                else:
                    cls.fonts[name] = font
                    print(f"Loaded {name}: height={font.height}, ascent={font.ascent}")
            except Exception as e:
                print(f"Failed to load {name}: {e}")
                cls.invalid_fonts.append(name)
        
        # Character sets to test
        cls.uppercase_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        cls.numbers = '0123456789'
        cls.test_phrase = 'HELLO WORLD 123'
        
    def test_font_loading(self):
        """Test that all fonts loaded successfully."""
        # Report invalid fonts
        if self.invalid_fonts:
            print(f"\nWARNING: The following fonts are invalid (likely HTML files): {', '.join(self.invalid_fonts)}")
            print("Please download proper BDF files for these fonts.\n")
            
        # Test valid fonts
        self.assertGreater(len(self.fonts), 0, "No valid fonts loaded")
        
        for font_name, font in self.fonts.items():
            with self.subTest(font=font_name):
                self.assertIsNotNone(font, f"Font {font_name} failed to load")
                self.assertGreater(font.height, 0, f"Font {font_name} has invalid height")
                self.assertGreater(font.ascent, 0, f"Font {font_name} has invalid ascent")
                
    def test_font_metrics(self):
        """Test font metric properties."""
        expected_metrics = {
            'tom-thumb': {'height': 6, 'ascent': 5},
            '5x8': {'height': 5, 'ascent': 5},  # Actual metrics from the font
            # Large fonts are currently invalid HTML files
            # 'LeagueSpartan-16': {'min_height': 16, 'min_ascent': 12},
            # 'LibreBodoni-27': {'min_height': 27, 'min_ascent': 20}
        }
        
        for font_name, font in self.fonts.items():
            with self.subTest(font=font_name):
                if font_name in expected_metrics:
                    metrics = expected_metrics[font_name]
                    if 'height' in metrics:
                        self.assertEqual(font.height, metrics['height'], 
                                       f"{font_name} height mismatch")
                    elif 'min_height' in metrics:
                        self.assertGreaterEqual(font.height, metrics['min_height'],
                                              f"{font_name} height too small")
                    
                    if 'ascent' in metrics:
                        self.assertEqual(font.ascent, metrics['ascent'],
                                       f"{font_name} ascent mismatch")
                    elif 'min_ascent' in metrics:
                        self.assertGreaterEqual(font.ascent, metrics['min_ascent'],
                                              f"{font_name} ascent too small")
                                              
    def test_uppercase_letters(self):
        """Test all uppercase letters A-Z in each font."""
        for font_name, font in self.fonts.items():
            for char in self.uppercase_letters:
                with self.subTest(font=font_name, char=char):
                    # Get the glyph
                    glyph = font.get_glyph(char)
                    self.assertIsNotNone(glyph, f"No glyph for '{char}' in {font_name}")
                    
                    # Check glyph properties
                    self.assertIn('bitmap', glyph)
                    self.assertIn('width', glyph)
                    self.assertIn('height', glyph)
                    self.assertGreater(glyph['width'], 0, f"Invalid width for '{char}'")
                    self.assertGreater(glyph['height'], 0, f"Invalid height for '{char}'")
                    
                    # Test rendering in a label
                    label = Label(font, text=char, color=0xFFFFFF)
                    self.assertIsNotNone(label._bitmap, f"Label bitmap not created for '{char}'")
                    self.assertGreater(label.width, 0, f"Label width is 0 for '{char}'")
                    self.assertGreater(label.height, 0, f"Label height is 0 for '{char}'")
                    
    def test_numbers(self):
        """Test all numbers 0-9 in each font."""
        for font_name, font in self.fonts.items():
            for char in self.numbers:
                with self.subTest(font=font_name, char=char):
                    # Get the glyph
                    glyph = font.get_glyph(char)
                    self.assertIsNotNone(glyph, f"No glyph for '{char}' in {font_name}")
                    
                    # Check glyph properties
                    self.assertIn('bitmap', glyph)
                    self.assertGreater(glyph['width'], 0, f"Invalid width for '{char}'")
                    self.assertGreater(glyph['height'], 0, f"Invalid height for '{char}'")
                    
                    # Test rendering in a label
                    label = Label(font, text=char, color=0xFFFFFF)
                    self.assertIsNotNone(label._bitmap, f"Label bitmap not created for '{char}'")
                    
    def test_large_font_rendering(self):
        """Test rendering with large fonts on appropriate displays."""
        # Test LeagueSpartan-16 (medium-large font) if available
        if 'LeagueSpartan-16' not in self.fonts:
            self.skipTest("LeagueSpartan-16 font not available")
            
        font = self.fonts['LeagueSpartan-16']
        matrix = LEDMatrix(128, 32)  # Larger display for larger font
        display = Display(FourWire(matrix), width=128, height=32)
        
        # Test single character
        label = Label(font, text='A', color=0xFF0000)
        group = Group()
        group.append(label)
        display.show(group)
        display.refresh()
        
        # Check that something was rendered
        has_content = False
        for y in range(matrix.height):
            for x in range(matrix.width):
                if matrix.get_pixel(x, y) != (0, 0, 0):
                    has_content = True
                    break
            if has_content:
                break
        self.assertTrue(has_content, "Large font 'A' not rendered")
        
        # Test LibreBodoni-27 (extra large font) if available
        if 'LibreBodoni-27' not in self.fonts:
            self.skipTest("LibreBodoni-27 font not available")
            
        font = self.fonts['LibreBodoni-27']
        matrix = LEDMatrix(256, 64)  # Even larger display
        display = Display(FourWire(matrix), width=256, height=64)
        
        label = Label(font, text='B', color=0x00FF00)
        group = Group()
        group.append(label)
        display.show(group)
        display.refresh()
        
        # Check rendering
        has_content = False
        for y in range(matrix.height):
            for x in range(matrix.width):
                if matrix.get_pixel(x, y) != (0, 0, 0):
                    has_content = True
                    break
            if has_content:
                break
        self.assertTrue(has_content, "Extra large font 'B' not rendered")
        
    def test_font_scaling(self):
        """Test that fonts scale properly with label scale parameter."""
        for font_name, font in self.fonts.items():
            with self.subTest(font=font_name):
                # Create labels with different scales
                label1 = Label(font, text='X', color=0xFFFFFF, scale=1)
                label2 = Label(font, text='X', color=0xFFFFFF, scale=2)
                
                # Scale 2 should have double dimensions
                self.assertEqual(label2.width, label1.width * 2,
                               f"{font_name}: Scaled width incorrect")
                self.assertEqual(label2.height, label1.height * 2,
                               f"{font_name}: Scaled height incorrect")
                               
    def test_multiline_large_fonts(self):
        """Test multiline text with large fonts."""
        # Test with larger fonts that might overflow on small displays
        for font_name in ['LeagueSpartan-16', 'LibreBodoni-27']:
            font = self.fonts[font_name]
            with self.subTest(font=font_name):
                label = Label(font, text='HELLO\\nWORLD', color=0xFFFFFF)
                
                # Check that height is approximately 2x single line
                single_line = Label(font, text='HELLO', color=0xFFFFFF)
                expected_height = int(single_line.height * 2 * label.line_spacing)
                self.assertAlmostEqual(label.height, expected_height, delta=5,
                                     msg=f"{font_name}: Multiline height incorrect")
                                     
    def test_character_spacing(self):
        """Test that character spacing works correctly."""
        for font_name, font in self.fonts.items():
            with self.subTest(font=font_name):
                # Test string of characters
                text = 'ABC'
                label = Label(font, text=text, color=0xFFFFFF)
                
                # Width should be sum of character widths plus spacing
                total_width = 0
                for char in text:
                    glyph = font.get_glyph(char)
                    if glyph:
                        total_width += glyph.get('dx', glyph['width'])
                        
                # Allow some tolerance for padding
                self.assertLessEqual(abs(label.width - total_width), 2,
                                   f"{font_name}: Character spacing incorrect")
                                   
    def test_complete_alphabet_render(self):
        """Test rendering the complete alphabet in each font."""
        for font_name, font in self.fonts.items():
            with self.subTest(font=font_name):
                # Determine matrix size based on font
                if font_name in ['LibreBodoni-27']:
                    matrix_width, matrix_height = 512, 64
                elif font_name in ['LeagueSpartan-16']:
                    matrix_width, matrix_height = 256, 32
                else:
                    matrix_width, matrix_height = 128, 32
                    
                matrix = LEDMatrix(matrix_width, matrix_height)
                display = Display(FourWire(matrix), width=matrix_width, height=matrix_height)
                
                # Create label with full alphabet
                label = Label(font, text=self.uppercase_letters, color=0xFFFF00)
                group = Group()
                group.append(label)
                display.show(group)
                display.refresh()
                
                # Verify content was rendered
                pixel_count = 0
                for y in range(matrix.height):
                    for x in range(matrix.width):
                        if matrix.get_pixel(x, y) != (0, 0, 0):
                            pixel_count += 1
                            
                # Should have many pixels for full alphabet
                min_expected_pixels = len(self.uppercase_letters) * 5  # At least 5 pixels per char
                self.assertGreater(pixel_count, min_expected_pixels,
                                 f"{font_name}: Full alphabet not properly rendered")
                                 
    def test_glyph_bitmap_content(self):
        """Test that glyph bitmaps contain actual pixel data."""
        test_chars = 'AHIM089'  # Mix of different character shapes
        
        for font_name, font in self.fonts.items():
            for char in test_chars:
                with self.subTest(font=font_name, char=char):
                    glyph = font.get_glyph(char)
                    if glyph and 'bitmap' in glyph:
                        bitmap = glyph['bitmap']
                        
                        # Count non-zero pixels
                        pixel_count = 0
                        for y in range(bitmap.height):
                            for x in range(bitmap.width):
                                if bitmap[x, y] > 0:
                                    pixel_count += 1
                                    
                        # Each character should have at least some pixels
                        self.assertGreater(pixel_count, 0,
                                         f"{font_name}: Glyph '{char}' has no pixels")
                                         
                        # Verify reasonable pixel density (not all pixels, not too few)
                        total_pixels = bitmap.width * bitmap.height
                        density = pixel_count / total_pixels
                        self.assertGreater(density, 0.1,  # At least 10% pixels
                                         f"{font_name}: Glyph '{char}' too sparse")
                        self.assertLess(density, 0.95,     # Not more than 95% pixels
                                      f"{font_name}: Glyph '{char}' too dense")


if __name__ == '__main__':
    unittest.main()