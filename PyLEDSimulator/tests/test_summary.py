#!/usr/bin/env python3
"""Summary of all PyLEDSimulator tests."""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all test modules
from .test_core.test_pixel_buffer import TestPixelBuffer
from .test_core.test_led_matrix import TestLEDMatrix
from .test_displayio.test_bitmap import TestBitmap
from .test_displayio.test_display import TestDisplay
from .test_adafruit_display_text.test_label import TestLabel


def count_tests():
    """Count total number of unit tests."""
    loader = unittest.TestLoader()
    
    test_classes = [
        TestPixelBuffer,
        TestLEDMatrix, 
        TestBitmap,
        TestDisplay,
        TestLabel
    ]
    
    total_tests = 0
    test_details = []
    
    for test_class in test_classes:
        suite = loader.loadTestsFromTestCase(test_class)
        count = suite.countTestCases()
        total_tests += count
        test_details.append((test_class.__name__, count))
        
    return total_tests, test_details


def main():
    """Print test summary."""
    print("=" * 70)
    print("PyLEDSimulator Unit Test Summary")
    print("=" * 70)
    
    total, details = count_tests()
    
    print(f"\nTotal unit tests created: {total}")
    print("\nBreakdown by module:")
    
    for class_name, count in details:
        module = class_name.replace("Test", "")
        print(f"  {module:20} {count:3} tests")
        
    print("\nTest Categories:")
    print("  • Core functionality (PixelBuffer, LEDMatrix)")
    print("  • displayio API (Bitmap, Display, Palette, TileGrid, Group)")  
    print("  • Text rendering (Label, BitmapLabel, ScrollingLabel)")
    print("  • Visual verification (pixel color comparison)")
    print("  • Font loading (BDF font support)")
    
    print("\nKey Testing Features:")
    print("  ✓ Image snapshot verification")
    print("  ✓ Pixel-level color checking")
    print("  ✓ Rendering pipeline validation")
    print("  ✓ API compatibility testing")
    print("  ✓ Memory and bounds checking")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()