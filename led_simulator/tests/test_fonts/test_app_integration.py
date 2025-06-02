#!/usr/bin/env python3
"""Test that the main app works with the character spacing improvements."""

import sys
import os

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from pyledsimulator.devices.matrixportal_s3 import MatrixPortalS3
from pyledsimulator import displayio
from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.terminalio import FONT as terminalio_FONT


def test_app_integration():
    """Test that the PyLEDSimulator can create labels with proper spacing."""
    
    print("=== APP INTEGRATION TEST ===")
    
    # Create device
    device = MatrixPortalS3(width=64, height=32)
    device.initialize()
    
    # Create main group
    main_group = displayio.Group()
    device.display.root_group = main_group
    
    # Create a label with improved spacing (similar to what the theme park app would use)
    label = Label(
        terminalio_FONT, 
        text="Pirates: 45 min", 
        color=0x00FF00, 
        character_spacing=1,  # Use the improved spacing
        x=2, 
        y=10
    )
    
    print(f"Created label: '{label.text}'")
    print(f"Label dimensions: {label.width} x {label.height}")
    print(f"Character spacing: {label.character_spacing}")
    
    main_group.append(label)
    
    # Test that we can refresh the display without errors
    try:
        device.display.refresh()
        print("✓ Display refresh successful")
    except Exception as e:
        print(f"✗ Display refresh failed: {e}")
        return False
    
    # Test that we can render without errors
    try:
        device.matrix.render()
        print("✓ Matrix render successful")
    except Exception as e:
        print(f"✗ Matrix render failed: {e}")
        return False
    
    print("✓ App integration test passed!")
    return True


if __name__ == "__main__":
    test_app_integration()