#!/usr/bin/env python3
"""Quick font positioning test."""

import sys
import os
import pygame

# Add PyLEDSimulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'PyLEDSimulator'))

from pyledsimulator.devices.matrixportal_s3 import MatrixPortalS3
from pyledsimulator import displayio
from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.terminalio import FONT as terminalio_FONT

def test_quick():
    # Create device
    device = MatrixPortalS3(width=64, height=32)
    device.initialize()
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((device.matrix.surface_width, device.matrix.surface_height))
    
    # Create label
    main_group = displayio.Group()
    device.display.root_group = main_group
    
    # Test scale 1
    label1 = Label(terminalio_FONT, text="A", color=0xFFFFFF, scale=1)
    label1.x = 5
    label1.y = 10
    main_group.append(label1)
    
    # Test scale 2  
    label2 = Label(terminalio_FONT, text="B", color=0xFF0000, scale=2)
    label2.x = 15
    label2.y = 10
    main_group.append(label2)
    
    print(f"Font height: {terminalio_FONT.height}, ascent: {terminalio_FONT.ascent}, descent: {terminalio_FONT.descent}")
    print(f"Label1 (scale 1): position=({label1.x}, {label1.y}), size=({label1.width}, {label1.height})")
    print(f"Label2 (scale 2): position=({label2.x}, {label2.y}), size=({label2.width}, {label2.height})")
    
    # Render
    device.display.refresh()
    device.matrix.render()
    
    if hasattr(device.matrix, 'surface'):
        screen.blit(device.matrix.surface, (0, 0))
        pygame.display.flip()
        pygame.image.save(device.matrix.surface, "font_positioning_test.png")
        print("Screenshot saved: font_positioning_test.png")
        
        # Quick pixel analysis
        pixel_array = pygame.surfarray.array3d(device.matrix.surface)
        import numpy as np
        non_black = np.any(pixel_array > 10, axis=2)
        
        if np.any(non_black):
            rows = np.any(non_black, axis=0)
            cols = np.any(non_black, axis=1)
            
            if np.any(rows) and np.any(cols):
                y_min, y_max = np.where(rows)[0][[0, -1]]
                x_min, x_max = np.where(cols)[0][[0, -1]]
                print(f"Characters rendered from ({x_min}, {y_min}) to ({x_max}, {y_max})")
                print(f"Height: {y_max - y_min + 1} pixels")
                
                if y_min < device.matrix.surface_height // 2:
                    print("✓ Characters appear in upper half of display - positioning looks better!")
                else:
                    print("⚠️ Characters still positioned too low")
            else:
                print("❌ No characters visible")
        else:
            print("❌ No characters rendered")
    
    pygame.time.wait(2000)
    pygame.quit()

if __name__ == "__main__":
    test_quick()