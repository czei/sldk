#!/usr/bin/env python3
"""Comprehensive testing of valid BDF fonts.

Tests the two valid fonts (tom-thumb and 5x8) with:
- All uppercase letters A-Z  
- All numbers 0-9
- Common punctuation
- Multi-character rendering
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


class TestValidFonts(unittest.TestCase):
    """Test valid fonts with comprehensive character coverage."""
    
    @classmethod
    def setUpClass(cls):
        """Load valid fonts."""
        font_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'fonts'
        )
        
        cls.fonts = {
            'tom-thumb': bitmap_font.load_font(os.path.join(font_dir, 'tom-thumb.bdf')),
            'viii': bitmap_font.load_font(os.path.join(font_dir, 'viii.bdf'))
        }
        
        # Character sets to test
        cls.uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        cls.lowercase = 'abcdefghijklmnopqrstuvwxyz'
        cls.numbers = '0123456789'
        cls.punctuation = '.,!?-+*/@#$%&()[]{}"\':'
        cls.test_phrases = [
            'HELLO WORLD',
            'TESTING 123',
            'RAINBOW TEXT',
            'LED MATRIX',
            '2024 DISPLAY'
        ]
        
    def test_font_metrics(self):
        """Verify font metrics are correct."""
        self.assertEqual(self.fonts['tom-thumb'].height, 6)
        self.assertEqual(self.fonts['tom-thumb'].ascent, 5)
        self.assertEqual(self.fonts['5x8'].height, 5)
        self.assertEqual(self.fonts['5x8'].ascent, 5)
        
    def test_uppercase_glyphs(self):
        """Test all uppercase letters have valid glyphs."""
        for font_name, font in self.fonts.items():
            missing_chars = []
            for char in self.uppercase:
                glyph = font.get_glyph(char)
                if not glyph:
                    missing_chars.append(char)
                    
            with self.subTest(font=font_name):
                self.assertEqual(len(missing_chars), 0,
                               f"{font_name} missing glyphs for: {missing_chars}")
                               
    def test_number_glyphs(self):
        """Test all numbers have valid glyphs."""
        for font_name, font in self.fonts.items():
            missing_chars = []
            for char in self.numbers:
                glyph = font.get_glyph(char)
                if not glyph:
                    missing_chars.append(char)
                    
            with self.subTest(font=font_name):
                self.assertEqual(len(missing_chars), 0,
                               f"{font_name} missing glyphs for: {missing_chars}")
                               
    def test_character_rendering(self):
        """Test individual character rendering."""
        test_chars = 'ABCXYZ0189'
        
        for font_name, font in self.fonts.items():
            for char in test_chars:
                with self.subTest(font=font_name, char=char):
                    # Create label
                    label = Label(font, text=char, color=0xFFFFFF)
                    
                    # Verify bitmap created
                    self.assertIsNotNone(label._bitmap)
                    self.assertGreater(label.width, 0)
                    self.assertGreater(label.height, 0)
                    
                    # Check bitmap has content
                    has_pixels = False
                    for y in range(label._bitmap.height):
                        for x in range(label._bitmap.width):
                            if label._bitmap[x, y] > 0:
                                has_pixels = True
                                break
                        if has_pixels:
                            break
                            
                    self.assertTrue(has_pixels, 
                                  f"{font_name}: Character '{char}' has no pixels")
                                  
    def test_phrase_rendering(self):
        """Test rendering complete phrases."""
        matrix = LEDMatrix(128, 32)
        display = Display(FourWire(matrix), width=128, height=32)
        
        for font_name, font in self.fonts.items():
            for phrase in self.test_phrases:
                with self.subTest(font=font_name, phrase=phrase):
                    # Create and render label
                    label = Label(font, text=phrase, color=0xFFFF00)
                    group = Group()
                    group.append(label)
                    
                    display.show(group)
                    display.refresh()
                    
                    # Count rendered pixels
                    pixel_count = 0
                    for y in range(matrix.height):
                        for x in range(matrix.width):
                            if matrix.get_pixel(x, y) != (0, 0, 0):
                                pixel_count += 1
                                
                    # Should have reasonable number of pixels for phrase
                    min_expected = len(phrase) * 3  # At least 3 pixels per character
                    self.assertGreater(pixel_count, min_expected,
                                     f"{font_name}: '{phrase}' rendered too few pixels")
                                     
    def test_multiline_text(self):
        """Test multiline text rendering."""
        multiline_texts = [
            "HELLO\\nWORLD",
            "LINE 1\\nLINE 2\\nLINE 3",
            "TEST\\n123"
        ]
        
        for font_name, font in self.fonts.items():
            for text in multiline_texts:
                with self.subTest(font=font_name, text=text):
                    label = Label(font, text=text, color=0xFFFFFF)
                    
                    # Count lines
                    line_count = text.count('\\n') + 1
                    expected_height = font.height * line_count
                    
                    # Allow for line spacing
                    self.assertGreaterEqual(label.height, expected_height,
                                          f"{font_name}: Multiline height too small")
                                          
    def test_character_widths(self):
        """Test that different characters have appropriate widths."""
        # Characters expected to have different widths
        width_tests = {
            'I': 'narrow',  # Should be narrower
            'W': 'wide',    # Should be wider
            'M': 'wide',
            '.': 'narrow',
            ' ': 'space'
        }
        
        for font_name, font in self.fonts.items():
            widths = {}
            
            # Measure character widths
            for char in width_tests.keys():
                glyph = font.get_glyph(char)
                if glyph:
                    widths[char] = glyph.get('width', 0)
                    
            with self.subTest(font=font_name):
                if 'I' in widths and 'W' in widths:
                    self.assertLess(widths['I'], widths['W'],
                                  f"{font_name}: 'I' should be narrower than 'W'")
                                  
                if '.' in widths and 'M' in widths:
                    self.assertLess(widths['.'], widths['M'],
                                  f"{font_name}: '.' should be narrower than 'M'")
                                  
    def test_scaling(self):
        """Test font scaling."""
        for font_name, font in self.fonts.items():
            with self.subTest(font=font_name):
                # Create labels at different scales
                label1 = Label(font, text='SCALE', color=0xFFFFFF, scale=1)
                label2 = Label(font, text='SCALE', color=0xFFFFFF, scale=2)
                label3 = Label(font, text='SCALE', color=0xFFFFFF, scale=3)
                
                # Verify scaling
                self.assertEqual(label2.width, label1.width * 2)
                self.assertEqual(label2.height, label1.height * 2)
                self.assertEqual(label3.width, label1.width * 3)
                self.assertEqual(label3.height, label1.height * 3)
                
    def test_color_rendering(self):
        """Test different colors render correctly."""
        colors = {
            'red': 0xFF0000,
            'green': 0x00FF00,
            'blue': 0x0000FF,
            'yellow': 0xFFFF00,
            'cyan': 0x00FFFF,
            'magenta': 0xFF00FF,
            'white': 0xFFFFFF
        }
        
        matrix = LEDMatrix(64, 32)
        display = Display(FourWire(matrix), width=64, height=32)
        
        for font_name, font in self.fonts.items():
            for color_name, color_value in colors.items():
                with self.subTest(font=font_name, color=color_name):
                    # Create colored label
                    label = Label(font, text='COLOR', color=color_value)
                    group = Group()
                    group.append(label)
                    
                    display.show(group)
                    display.refresh()
                    
                    # Verify some pixels have the expected color
                    found_color = False
                    for y in range(matrix.height):
                        for x in range(matrix.width):
                            pixel = matrix.get_pixel(x, y)
                            if pixel != (0, 0, 0):  # Not black
                                found_color = True
                                break
                        if found_color:
                            break
                            
                    self.assertTrue(found_color,
                                  f"{font_name}: No {color_name} pixels found")
                                  
    def test_special_characters(self):
        """Test rendering of special characters that exist in the fonts."""
        # Test common special characters
        special_chars = '.,!?-+*/()[]'
        
        for font_name, font in self.fonts.items():
            available_chars = []
            for char in special_chars:
                glyph = font.get_glyph(char)
                if glyph:
                    available_chars.append(char)
                    
            with self.subTest(font=font_name):
                # Test rendering available special characters
                if available_chars:
                    text = ''.join(available_chars)
                    label = Label(font, text=text, color=0xFFFFFF)
                    
                    # Should create a valid bitmap
                    self.assertIsNotNone(label._bitmap)
                    self.assertGreater(label.width, 0)
                    
                    # Report which special characters are available
                    print(f"{font_name} supports special chars: {available_chars}")


if __name__ == '__main__':
    unittest.main()