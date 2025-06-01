#!/usr/bin/env python3
"""
Unit test with screenshot generation to analyze font positioning issues.
Creates side-by-side comparisons showing expected vs actual font rendering.
"""

import sys
import os
import pygame
import unittest

# Add PyLEDSimulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'PyLEDSimulator'))

from pyledsimulator.devices.matrixportal_s3 import MatrixPortalS3
from pyledsimulator import displayio
from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.terminalio import FONT as terminalio_FONT
from pyledsimulator.adafruit_bitmap_font import bitmap_font


class TestFontRendering(unittest.TestCase):
    """Test font rendering with visual comparison."""
    
    def setUp(self):
        """Set up test environment."""
        self.device = MatrixPortalS3(width=64, height=32)
        self.device.initialize()
        
        pygame.init()
        self.screen = pygame.display.set_mode((self.device.matrix.surface_width, 
                                              self.device.matrix.surface_height))
        
    def test_viii_font_scale_1(self):
        """Test viii font at scale 1."""
        print("\n=== Testing viii font scale 1 ===")
        
        # Clear display
        main_group = displayio.Group()
        self.device.display.root_group = main_group
        
        # Create test label
        label = Label(terminalio_FONT, text="Test", color=0xFFFFFF, scale=1)
        label.x = 5
        label.y = 5  # Try positioning at top
        main_group.append(label)
        
        # Print debug info
        print(f"Font: {label.font.name if hasattr(label.font, 'name') else 'Unknown'}")
        print(f"Font metrics: height={label.font.height}, ascent={label.font.ascent}, descent={label.font.descent}")
        print(f"Label: pos=({label.x}, {label.y}), size=({label.width}, {label.height})")
        
        # Render and save
        self.device.display.refresh()
        self.device.matrix.render()
        
        if hasattr(self.device.matrix, 'surface'):
            pygame.image.save(self.device.matrix.surface, "test_viii_scale1.png")
            
            # Analyze if pixels are visible
            pixel_array = pygame.surfarray.array3d(self.device.matrix.surface)
            import numpy as np
            non_black = np.any(pixel_array > 10, axis=2)
            has_pixels = np.any(non_black)
            
            print(f"Pixels rendered: {has_pixels}")
            if has_pixels:
                rows = np.any(non_black, axis=0)
                cols = np.any(non_black, axis=1)
                y_min, y_max = np.where(rows)[0][[0, -1]]
                x_min, x_max = np.where(cols)[0][[0, -1]]
                print(f"Rendered area: ({x_min}, {y_min}) to ({x_max}, {y_max})")
            
            self.assertTrue(has_pixels, "Scale 1 viii font should render visible pixels")
            
    def test_viii_font_scale_2_manual(self):
        """Test viii font at scale 2 by manually using scale 1 font."""
        print("\n=== Testing viii font scale 2 (manual) ===")
        
        # Clear display
        main_group = displayio.Group()
        self.device.display.root_group = main_group
        
        # Force use of viii font instead of auto-switching to Arial
        # Create label with scale=1 but manually manage the font
        label = Label(terminalio_FONT, text="Test", color=0xFF0000, scale=1)
        label.x = 5
        label.y = 5
        # The Group scale should handle the 2x scaling
        label.scale = 2
        main_group.append(label)
        
        print(f"Font: {label.font.name if hasattr(label.font, 'name') else 'Unknown'}")
        print(f"Font metrics: height={label.font.height}, ascent={label.font.ascent}, descent={label.font.descent}")
        print(f"Label: pos=({label.x}, {label.y}), size=({label.width}, {label.height}), scale={label.scale}")
        
        # Render and save
        self.device.display.refresh()
        self.device.matrix.render()
        
        if hasattr(self.device.matrix, 'surface'):
            pygame.image.save(self.device.matrix.surface, "test_viii_scale2_manual.png")
            
            # Analyze rendering
            pixel_array = pygame.surfarray.array3d(self.device.matrix.surface)
            import numpy as np
            non_black = np.any(pixel_array > 10, axis=2)
            has_pixels = np.any(non_black)
            
            print(f"Pixels rendered: {has_pixels}")
            if has_pixels:
                rows = np.any(non_black, axis=0)
                cols = np.any(non_black, axis=1)
                y_min, y_max = np.where(rows)[0][[0, -1]]
                x_min, x_max = np.where(cols)[0][[0, -1]]
                print(f"Rendered area: ({x_min}, {y_min}) to ({x_max}, {y_max})")
                
            self.assertTrue(has_pixels, "Manual scale 2 viii font should render visible pixels")
            
    def test_arial_font_positioning(self):
        """Test Arial_16 font positioning."""
        print("\n=== Testing Arial_16 font ===")
        
        try:
            arial_font = bitmap_font.load_font("PyLEDSimulator/fonts/Arial_16.bdf")
        except:
            self.skipTest("Arial_16.bdf not available")
            
        # Clear display
        main_group = displayio.Group()
        self.device.display.root_group = main_group
        
        # Create test label - try positioning higher up
        label = Label(arial_font, text="A", color=0x00FF00, scale=1)
        label.x = 5
        label.y = -10  # Try negative Y to see if that helps
        main_group.append(label)
        
        print(f"Font: {label.font.name if hasattr(label.font, 'name') else 'Unknown'}")
        print(f"Font metrics: height={label.font.height}, ascent={label.font.ascent}, descent={label.font.descent}")
        print(f"Label: pos=({label.x}, {label.y}), size=({label.width}, {label.height})")
        
        # Render and save
        self.device.display.refresh()
        self.device.matrix.render()
        
        if hasattr(self.device.matrix, 'surface'):
            pygame.image.save(self.device.matrix.surface, "test_arial_positioning.png")
            
            # Analyze rendering
            pixel_array = pygame.surfarray.array3d(self.device.matrix.surface)
            import numpy as np
            non_black = np.any(pixel_array > 10, axis=2)
            has_pixels = np.any(non_black)
            
            print(f"Pixels rendered: {has_pixels}")
            if has_pixels:
                rows = np.any(non_black, axis=0)
                cols = np.any(non_black, axis=1)
                y_min, y_max = np.where(rows)[0][[0, -1]]
                x_min, x_max = np.where(cols)[0][[0, -1]]
                print(f"Rendered area: ({x_min}, {y_min}) to ({x_max}, {y_max})")
                
    def tearDown(self):
        """Clean up."""
        pygame.time.wait(100)  # Brief pause between tests


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2, exit=False)
    
    print("\nTest completed! Check generated PNG files:")
    print("- test_viii_scale1.png")
    print("- test_viii_scale2_manual.png") 
    print("- test_arial_positioning.png")
    
    pygame.quit()