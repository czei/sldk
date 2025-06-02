#!/usr/bin/env python3
"""Simple test to verify character spacing is working."""

import sys
import os

# Add PyLEDSimulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.terminalio import FONT as terminalio_FONT


def test_label_properties():
    """Test that the Label class has the new character_spacing property."""
    font = terminalio_FONT
    
    print("=== SIMPLE SPACING TEST ===")
    
    # Test default spacing
    label1 = Label(font, text="hello")
    print(f"Default character_spacing: {label1.character_spacing}")
    print(f"Label dimensions: {label1.width} x {label1.height}")
    
    # Test custom spacing
    label2 = Label(font, text="hello", character_spacing=2)
    print(f"Custom character_spacing: {label2.character_spacing}")
    print(f"Label dimensions: {label2.width} x {label2.height}")
    
    # Test that custom spacing makes labels wider
    width_diff = label2.width - label1.width
    print(f"Width difference (should be positive): {width_diff}")
    
    if width_diff > 0:
        print("✓ Character spacing is working correctly!")
    else:
        print("✗ Character spacing may not be working")


if __name__ == "__main__":
    test_label_properties()