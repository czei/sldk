#!/usr/bin/env python3
"""Simple font tests to verify basic functionality."""

import unittest
import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pyledsimulator.adafruit_bitmap_font import bitmap_font
from pyledsimulator.adafruit_display_text.label import Label


class TestFontsSimple(unittest.TestCase):
    """Simple tests for font functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Load fonts."""
        font_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'fonts'
        )
        
        cls.tom_thumb = bitmap_font.load_font(os.path.join(font_dir, 'tom-thumb.bdf'))
        cls.font_viii = bitmap_font.load_font(os.path.join(font_dir, 'viii.bdf'))
        
    def test_alphabet_rendering(self):
        """Test rendering A-Z for each font."""
        fonts = [
            ('tom-thumb', self.tom_thumb),
            ('viii', self.font_viii)
        ]
        
        for font_name, font in fonts:
            print(f"\nTesting {font_name} font (height={font.height}, ascent={font.ascent})")
            
            # Test each letter
            for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                label = Label(font, text=char, color=0xFFFFFF)
                self.assertGreater(label.width, 0, f"{font_name}: {char} has no width")
                self.assertGreater(label.height, 0, f"{font_name}: {char} has no height")
                
                # Check that bitmap has content
                pixel_count = 0
                for y in range(label._bitmap.height):
                    for x in range(label._bitmap.width):
                        if label._bitmap[x, y] > 0:
                            pixel_count += 1
                            
                self.assertGreater(pixel_count, 0, f"{font_name}: {char} has no pixels")
                
    def test_numbers_rendering(self):
        """Test rendering 0-9 for each font."""
        fonts = [
            ('tom-thumb', self.tom_thumb),
            ('viii', self.font_viii)
        ]
        
        for font_name, font in fonts:
            # Test each number
            for char in '0123456789':
                label = Label(font, text=char, color=0xFFFFFF)
                self.assertGreater(label.width, 0, f"{font_name}: {char} has no width")
                
                # Check pixels
                pixel_count = 0
                for y in range(label._bitmap.height):
                    for x in range(label._bitmap.width):
                        if label._bitmap[x, y] > 0:
                            pixel_count += 1
                            
                self.assertGreater(pixel_count, 0, f"{font_name}: {char} has no pixels")
                
    def test_word_rendering(self):
        """Test rendering complete words."""
        test_words = ['HELLO', 'WORLD', 'LED', 'MATRIX', 'DISPLAY', 'TEST123']
        
        fonts = [
            ('tom-thumb', self.tom_thumb),
            ('viii', self.font_viii)
        ]
        
        for font_name, font in fonts:
            for word in test_words:
                label = Label(font, text=word, color=0xFFFFFF)
                
                # Width should be roughly proportional to word length
                min_width = len(word) * 2  # At least 2 pixels per character
                self.assertGreater(label.width, min_width, 
                                 f"{font_name}: '{word}' too narrow")
                
                # Check pixel density
                total_pixels = label._bitmap.width * label._bitmap.height
                pixel_count = 0
                for y in range(label._bitmap.height):
                    for x in range(label._bitmap.width):
                        if label._bitmap[x, y] > 0:
                            pixel_count += 1
                            
                # Should have reasonable pixel density
                density = pixel_count / total_pixels
                self.assertGreater(density, 0.1, 
                                 f"{font_name}: '{word}' too sparse ({density:.2f})")
                
    def test_multiline_proper(self):
        """Test multiline with actual newlines."""
        fonts = [
            ('tom-thumb', self.tom_thumb),
            ('viii', self.font_viii)
        ]
        
        for font_name, font in fonts:
            # Test with actual newline character
            text = "HELLO\nWORLD"
            label = Label(font, text=text, color=0xFFFFFF)
            
            # Height should be approximately 2x single line
            single_line = Label(font, text="HELLO", color=0xFFFFFF)
            self.assertGreater(label.height, single_line.height,
                             f"{font_name}: Multiline not taller than single")
            
            # Test 3 lines
            text3 = "LINE1\nLINE2\nLINE3"
            label3 = Label(font, text=text3, color=0xFFFFFF)
            self.assertGreater(label3.height, label.height,
                             f"{font_name}: 3 lines not taller than 2")
                             
    def test_scale_parameter(self):
        """Test the scale parameter works."""
        fonts = [
            ('tom-thumb', self.tom_thumb),
            ('viii', self.font_viii)
        ]
        
        for font_name, font in fonts:
            # Create base label
            base = Label(font, text="X", color=0xFFFFFF, scale=1)
            
            # Test scale 2
            scale2 = Label(font, text="X", color=0xFFFFFF, scale=2)
            
            # The bitmap should be larger, not the reported width/height
            # Check actual bitmap dimensions
            self.assertGreater(scale2._bitmap.width, base._bitmap.width,
                             f"{font_name}: Scale 2 bitmap not wider")
            self.assertGreater(scale2._bitmap.height, base._bitmap.height,
                             f"{font_name}: Scale 2 bitmap not taller")
                             
    def test_glyph_details(self):
        """Test and report glyph details."""
        print("\n=== Glyph Details ===")
        
        fonts = [
            ('tom-thumb', self.tom_thumb),
            ('viii', self.font_viii)
        ]
        
        test_chars = "ABCXYZ0189.,"
        
        for font_name, font in fonts:
            print(f"\n{font_name} font:")
            for char in test_chars:
                glyph = font.get_glyph(char)
                if glyph:
                    print(f"  '{char}': width={glyph.get('width', '?')}, "
                          f"height={glyph.get('height', '?')}, "
                          f"dx={glyph.get('dx', '?')}")
                else:
                    print(f"  '{char}': No glyph")


if __name__ == '__main__':
    unittest.main(verbose=2)