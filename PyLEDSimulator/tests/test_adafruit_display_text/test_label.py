"""Unit tests for Label class."""

import unittest
from pyledsimulator.adafruit_display_text import Label
from pyledsimulator.adafruit_bitmap_font import load_font
from pyledsimulator.core.color_utils import rgb888_to_rgb565


class TestLabel(unittest.TestCase):
    """Test cases for Label functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use a mock font for testing
        self.mock_font = MockFont()
        
    def test_initialization(self):
        """Test Label initialization."""
        label = Label(
            font=self.mock_font,
            text="Hello",
            color=0xFF0000,
            x=10,
            y=20
        )
        
        self.assertEqual(label.text, "Hello")
        self.assertEqual(label.color, 0xFF0000)
        self.assertEqual(label.x, 10)
        self.assertEqual(label.y, 20)
        self.assertIsNone(label.background_color)
        
    def test_text_property(self):
        """Test text property setter/getter."""
        label = Label(font=self.mock_font)
        
        # Set text
        label.text = "Test"
        self.assertEqual(label.text, "Test")
        
        # Change text
        label.text = "Changed"
        self.assertEqual(label.text, "Changed")
        
        # Set to non-string
        label.text = 123
        self.assertEqual(label.text, "123")
        
    def test_color_property(self):
        """Test color property."""
        label = Label(font=self.mock_font, text="Color")
        
        # Set RGB565 color
        label.color = 0x07E0  # Green
        self.assertEqual(label.color, 0x07E0)
        
        # Set with tuple (should convert to RGB565)
        label.color = (255, 0, 0)  # Red
        expected = rgb888_to_rgb565(255, 0, 0)
        self.assertEqual(label.color, expected)
        
    def test_background_color(self):
        """Test background color property."""
        label = Label(font=self.mock_font, text="BG")
        
        # Initially None
        self.assertIsNone(label.background_color)
        
        # Set background
        label.background_color = 0x001F  # Blue
        self.assertEqual(label.background_color, 0x001F)
        
        # Clear background
        label.background_color = None
        self.assertIsNone(label.background_color)
        
    def test_padding(self):
        """Test padding properties."""
        label = Label(
            font=self.mock_font,
            text="Pad",
            padding_top=5,
            padding_bottom=10,
            padding_left=3,
            padding_right=7
        )
        
        self.assertEqual(label.padding_top, 5)
        self.assertEqual(label.padding_bottom, 10)
        self.assertEqual(label.padding_left, 3)
        self.assertEqual(label.padding_right, 7)
        
    def test_anchor_point(self):
        """Test anchor point functionality."""
        label = Label(font=self.mock_font, text="Anchor")
        
        # Set anchor point
        label.anchor_point = (0.5, 0.5)  # Center
        self.assertEqual(label.anchor_point, (0.5, 0.5))
        
        # Set anchored position
        label.anchored_position = (50, 50)
        self.assertEqual(label.anchored_position, (50, 50))
        
    def test_tab_replacement(self):
        """Test tab replacement in text."""
        label = Label(
            font=self.mock_font,
            text="A\tB",
            tab_replacement=(4, " ")
        )
        
        # Tab should be replaced with 4 spaces in rendering
        # (actual replacement happens during _update_text)
        self.assertEqual(label.tab_replacement, (4, " "))
        
    def test_multiline_text(self):
        """Test multiline text support."""
        label = Label(
            font=self.mock_font,
            text="Line1\nLine2\nLine3",
            line_spacing=1.5
        )
        
        self.assertEqual(label.text, "Line1\nLine2\nLine3")
        self.assertEqual(label.line_spacing, 1.5)
        
    def test_label_direction(self):
        """Test label direction (LTR/RTL)."""
        label = Label(
            font=self.mock_font,
            text="RTL",
            label_direction="RTL"
        )
        
        self.assertEqual(label.label_direction, "RTL")
        
    def test_scale(self):
        """Test label scaling."""
        label = Label(
            font=self.mock_font,
            text="Big",
            scale=2
        )
        
        self.assertEqual(label.scale, 2)
        
    def test_bounding_box(self):
        """Test bounding box calculation."""
        label = Label(
            font=self.mock_font,
            text="Box",
            x=10,
            y=20
        )
        
        # Bounding box should include position
        bbox = label.bounding_box
        self.assertEqual(bbox[0], 10)  # x
        self.assertEqual(bbox[1], 20)  # y
        # Width and height depend on font rendering
        
    def test_width_height_properties(self):
        """Test width and height properties."""
        label = Label(font=self.mock_font, text="Size")
        
        # These depend on actual bitmap size after rendering
        # Just verify they return integers
        self.assertIsInstance(label.width, int)
        self.assertIsInstance(label.height, int)


class MockFont:
    """Mock font for testing."""
    
    def __init__(self):
        self.height = 8
        self.ascent = 7
        self.descent = 1
        
    def get_glyph(self, char):
        """Return mock glyph data."""
        # Simple mock - each character is 5x7 pixels
        return {
            'bitmap': MockBitmap(5, 7),
            'width': 5,
            'height': 7,
            'dx': 6,  # Advance width
            'dy': 0,
            'x_offset': 0,
            'y_offset': 0
        }


class MockBitmap:
    """Mock bitmap for glyphs."""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
    def __getitem__(self, index):
        # Return 1 for "on" pixels in a simple pattern
        x, y = index
        return 1 if (x + y) % 2 == 0 else 0


if __name__ == '__main__':
    unittest.main()