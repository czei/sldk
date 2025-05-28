#!/usr/bin/env python3
"""Basic test script to verify PyLEDSimulator functionality."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pyledsimulator.devices import MatrixPortalS3
from pyledsimulator.displayio import Group
from pyledsimulator.adafruit_display_text import Label
from pyledsimulator.terminalio import FONT


def test_basic_functionality():
    """Test basic LED simulator functionality."""
    print("Testing PyLEDSimulator basic functionality...")
    
    try:
        # Create device
        print("1. Creating MatrixPortalS3 device...")
        device = MatrixPortalS3()
        print("   ✓ Device created")
        
        # Initialize device
        print("2. Initializing device...")
        device.initialize()
        print("   ✓ Device initialized")
        
        # Create display elements
        print("3. Creating display elements...")
        main_group = Group()
        
        label = Label(
            font=FONT,
            text="TEST OK",
            color=0x00FF00,  # Green
            x=10,
            y=16
        )
        main_group.append(label)
        print("   ✓ Display elements created")
        
        # Show on display
        print("4. Showing content on display...")
        device.show(main_group)
        print("   ✓ Content shown")
        
        # Test single frame render
        print("5. Testing single frame render...")
        device.run_once()
        print("   ✓ Frame rendered")
        
        print("\n✅ All basic tests passed!")
        print("\nTo run interactive examples, try:")
        print("  python examples/matrixportal_s3_example.py")
        print("  python examples/scrolling_text_example.py")
        print("  python examples/rainbow_text.py")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    return True


if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)