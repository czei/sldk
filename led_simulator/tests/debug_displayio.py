#!/usr/bin/env python3
"""Debug displayio rendering issues."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3
from pyledsimulator.displayio import Group, Bitmap, Palette, TileGrid


def test_displayio_rendering():
    """Debug displayio rendering."""
    print("Creating device...")
    device = MatrixPortalS3(width=8, height=8)
    device.initialize()
    
    print("\nCreating bitmap...")
    bitmap = Bitmap(4, 4, 2)
    print(f"Bitmap size: {bitmap.width}x{bitmap.height}")
    
    # Set some pixels
    bitmap[0, 0] = 1
    bitmap[1, 1] = 1
    bitmap[2, 2] = 1
    bitmap[3, 3] = 1
    
    print("\nCreating palette...")
    palette = Palette(2)
    palette[0] = 0x000000  # Black
    palette[1] = 0xFF0000  # Red
    print(f"Palette[0] = {palette[0]:06X}")
    print(f"Palette[1] = {palette[1]:06X}")
    
    print("\nCreating tilegrid...")
    tilegrid = TileGrid(bitmap, pixel_shader=palette)
    print(f"TileGrid size: {tilegrid.pixel_width}x{tilegrid.pixel_height}")
    
    print("\nShowing on display...")
    device.display.show(tilegrid)
    
    print("\nChecking display state...")
    print(f"Display root_group: {device.display.root_group}")
    print(f"Display size: {device.display.width}x{device.display.height}")
    
    print("\nRefreshing display...")
    device.display.refresh()
    
    print("\nChecking matrix state...")
    matrix = device.display.get_matrix()
    print(f"Matrix size: {matrix.width}x{matrix.height}")
    
    # Check if pixels were set
    print("\nChecking pixels on matrix:")
    for y in range(4):
        for x in range(4):
            color = matrix.get_pixel(x, y)
            if color != (0, 0, 0):
                print(f"  Pixel ({x},{y}) = {color}")
                
    # Try setting a pixel directly to verify matrix works
    print("\nSetting test pixel directly...")
    matrix.set_pixel(6, 6, (0, 255, 0))
    test_color = matrix.get_pixel(6, 6)
    print(f"Test pixel (6,6) = {test_color}")
    
    # Render and check surface
    print("\nRendering matrix...")
    matrix.render()
    surface = matrix.get_surface()
    print(f"Surface size: {surface.get_size()}")


if __name__ == "__main__":
    test_displayio_rendering()