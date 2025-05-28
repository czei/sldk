#!/usr/bin/env python3
"""Test Label rendering specifically."""

import unittest
import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3
from pyledsimulator.adafruit_display_text import Label
from pyledsimulator.terminalio import FONT
from pyledsimulator.displayio import Group


class TestLabelRendering(unittest.TestCase):
    """Test Label rendering functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Initialize pygame once for all tests."""
        pygame.init()
        
    def setUp(self):
        """Set up test fixtures."""
        self.device = MatrixPortalS3(width=32, height=16)  # Smaller for testing
        self.device.initialize()
        
    def count_non_black_pixels(self):
        """Count pixels that aren't black."""
        matrix = self.device.display.get_matrix()
        count = 0
        for y in range(matrix.height):
            for x in range(matrix.width):
                if matrix.get_pixel(x, y) != (0, 0, 0):
                    count += 1
        return count
        
    def test_label_creation(self):
        """Test that labels can be created."""
        label = Label(
            font=FONT,
            text="Hi",
            color=0xFF0000,
            x=5,
            y=8
        )
        
        self.assertEqual(label.text, "Hi")
        self.assertEqual(label.x, 5)
        self.assertEqual(label.y, 8)
        self.assertIsNotNone(label._bitmap)
        self.assertIsNotNone(label._tilegrid)
        
    def test_label_bitmap_creation(self):
        """Test that labels create internal bitmaps correctly."""
        label = Label(
            font=FONT,
            text="TEST",
            color=0x00FF00
        )
        
        # Check that label has a bitmap
        self.assertIsNotNone(label._bitmap)
        print(f"Label bitmap size: {label._bitmap.width}x{label._bitmap.height}")
        
        # Check that bitmap has some non-zero pixels
        has_content = False
        for y in range(label._bitmap.height):
            for x in range(label._bitmap.width):
                if label._bitmap[x, y] > 0:
                    has_content = True
                    print(f"Found content at bitmap pixel ({x},{y}) = {label._bitmap[x, y]}")
                    break
            if has_content:
                break
                
        self.assertTrue(has_content, "Label bitmap has no content")
        
    def test_label_font_glyphs(self):
        """Test that font provides glyph data."""
        # Test the font directly
        glyph = FONT.get_glyph('A')
        self.assertIsNotNone(glyph, "Font should provide glyph for 'A'")
        
        print(f"Glyph 'A' info: {glyph}")
        if glyph:
            self.assertIn('bitmap', glyph)
            self.assertIn('width', glyph)
            self.assertIn('height', glyph)
            self.assertIn('dx', glyph)
            
    def test_single_label_display(self):
        """Test displaying a single label."""
        label = Label(
            font=FONT,
            text="A",
            color=0xFFFF00,  # Yellow
            x=10,
            y=8
        )
        
        # Show the label
        self.device.display.show(label)
        self.device.display.refresh()
        
        # Check if anything was rendered
        matrix = self.device.display.get_matrix()
        matrix.render()
        
        non_black = self.count_non_black_pixels()
        print(f"Non-black pixels after rendering single 'A': {non_black}")
        
        # For debugging, print what's actually in the matrix
        for y in range(min(10, matrix.height)):
            for x in range(min(20, matrix.width)):
                color = matrix.get_pixel(x, y)
                if color != (0, 0, 0):
                    print(f"Matrix pixel ({x},{y}) = {color}")
                    
        # We expect at least some pixels for the letter 'A'
        self.assertGreater(non_black, 0, "Letter 'A' should render some pixels")
        
    def test_label_group_rendering(self):
        """Test labels in a group."""
        group = Group()
        
        # Add a simple label
        label = Label(
            font=FONT,
            text="X",
            color=0xFF0000,  # Red
            x=5,
            y=8
        )
        group.append(label)
        
        # Show the group
        self.device.display.show(group)
        self.device.display.refresh()
        
        non_black = self.count_non_black_pixels()
        print(f"Non-black pixels after rendering 'X' in group: {non_black}")
        
        self.assertGreater(non_black, 0, "Letter 'X' in group should render pixels")
        
    def test_rainbow_text_setup(self):
        """Test the rainbow text example setup without animation."""
        main_group = Group()
        
        # Create labels like in rainbow_text.py
        text = "RAINBOW"
        labels = []
        
        for i, char in enumerate(text):
            label = Label(
                font=FONT,
                text=char,
                color=0xFFFFFF,  # White
                x=2 + i * 9,
                y=8
            )
            labels.append(label)
            main_group.append(label)
            
        # Show the group
        self.device.display.show(main_group)
        self.device.display.refresh()
        
        non_black = self.count_non_black_pixels()
        print(f"Non-black pixels after rendering 'RAINBOW': {non_black}")
        
        # Should have pixels for 7 characters
        self.assertGreater(non_black, 10, "RAINBOW text should render many pixels")


if __name__ == '__main__':
    unittest.main(verbosity=2)