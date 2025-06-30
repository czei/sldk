#!/usr/bin/env python3
"""Test SLDK imports"""

import sys
import os

# Add SLDK to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sldk', 'src'))

try:
    import sldk.simulator.displayio as displayio
    print("✓ displayio imported successfully")
    
    from sldk.simulator.devices import MatrixPortalS3
    print("✓ MatrixPortalS3 imported successfully")
    
    # Test creating a device
    device = MatrixPortalS3()
    print("✓ MatrixPortalS3 device created")
    
    # Test displayio components
    bitmap = displayio.Bitmap(10, 10, 2)
    print("✓ Bitmap created")
    
    palette = displayio.Palette(2)
    print("✓ Palette created")
    
    group = displayio.Group()
    print("✓ Group created")
    
    print("\n✅ All SLDK imports working!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()