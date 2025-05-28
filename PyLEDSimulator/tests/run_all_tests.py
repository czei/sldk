#!/usr/bin/env python3
"""Run all unit tests for PyLEDSimulator."""

import sys
import os
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all test modules
from test_core.test_pixel_buffer import TestPixelBuffer
from test_core.test_led_matrix import TestLEDMatrix
from test_displayio.test_bitmap import TestBitmap
from test_displayio.test_display import TestDisplay
from test_adafruit_display_text.test_label import TestLabel

def run_all_tests():
    """Run all unit tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    test_classes = [
        TestPixelBuffer,
        TestLEDMatrix,
        TestBitmap,
        TestDisplay,
        TestLabel
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)