#!/usr/bin/env python3
"""
Visual font analysis test - generates screenshots for analysis and comparison with BDF font files.
"""

import sys
import os
import pygame
import numpy as np

# Add PyLEDSimulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'PyLEDSimulator'))

from pyledsimulator.devices.matrixportal_s3 import MatrixPortalS3
from pyledsimulator import displayio
from pyledsimulator.adafruit_display_text.label import Label
from pyledsimulator.terminalio import FONT as terminalio_FONT
from pyledsimulator.adafruit_bitmap_font import bitmap_font


class FontVisualAnalyzer:
    """Analyze font rendering and generate visual comparisons."""
    
    def __init__(self):
        self.device = MatrixPortalS3(width=64, height=32)
        self.device.initialize()
        
        # Initialize pygame for screenshots
        pygame.init()
        self.screen = pygame.display.set_mode((self.device.matrix.surface_width, 
                                              self.device.matrix.surface_height))
        pygame.display.set_caption("Font Visual Analysis")
        
    def test_single_character(self, font, char, scale=1, filename_prefix=""):
        """Test rendering of a single character and save screenshot."""
        print(f"Testing character '{char}' with {filename_prefix} font at scale {scale}")
        
        # Clear display
        self.device.display.root_group = displayio.Group()
        main_group = displayio.Group()
        self.device.display.root_group = main_group
        
        # Create label with the character
        label = Label(font, text=char, color=0xFFFFFF, scale=scale)
        label.x = 10
        label.y = 16
        main_group.append(label)
        
        # Get font information
        glyph = font.get_glyph(char)
        if glyph:
            print(f"  Glyph info: width={glyph['width']}, height={glyph['height']}")
            print(f"  Glyph offset: x_offset={glyph['x_offset']}, y_offset={glyph['y_offset']}")
        print(f"  Font info: height={font.height}, ascent={font.ascent}, descent={font.descent}")
        print(f"  Label info: width={label.width}, height={label.height}")
        print(f"  Label position: x={label.x}, y={label.y}")
        
        # Render and save screenshot
        self.device.display.refresh()
        self.device.matrix.render()
        
        if hasattr(self.device.matrix, 'surface'):
            # Save screenshot
            filename = f"font_test_{filename_prefix}_scale{scale}_{char}_analysis.png"
            pygame.image.save(self.device.matrix.surface, filename)
            print(f"  Screenshot saved: {filename}")
            
            # Analyze pixel data
            self._analyze_pixel_data(self.device.matrix.surface, char, filename_prefix, scale)
            
        return glyph
        
    def _analyze_pixel_data(self, surface, char, font_name, scale):
        """Analyze the pixel data of rendered character."""
        # Convert surface to array for analysis
        pixel_array = pygame.surfarray.array3d(surface)
        
        # Find non-black pixels (rendered character)
        non_black = np.any(pixel_array > 10, axis=2)
        
        if np.any(non_black):
            # Find bounding box of rendered character
            rows = np.any(non_black, axis=0)
            cols = np.any(non_black, axis=1)
            
            if np.any(rows) and np.any(cols):
                y_min, y_max = np.where(rows)[0][[0, -1]]
                x_min, x_max = np.where(cols)[0][[0, -1]]
                
                rendered_width = x_max - x_min + 1
                rendered_height = y_max - y_min + 1
                
                print(f"  Rendered bounding box: ({x_min}, {y_min}) to ({x_max}, {y_max})")
                print(f"  Rendered size: {rendered_width}x{rendered_height} pixels")
                print(f"  Character top at y={y_min}, bottom at y={y_max}")
                
                # Check if character is visible
                if rendered_height < 2:
                    print(f"  ⚠️  WARNING: Character too small! Only {rendered_height} pixels tall")
                if y_min > surface.get_height() - 5:
                    print(f"  ⚠️  WARNING: Character positioned too low, may be cut off")
                if y_max < 5:
                    print(f"  ⚠️  WARNING: Character positioned too high")
            else:
                print("  ❌ ERROR: No visible pixels found for character!")
        else:
            print("  ❌ ERROR: Character not rendered - no non-black pixels found!")
            
    def test_font_comparison(self):
        """Test multiple fonts and scales for comparison."""
        print("=" * 60)
        print("FONT VISUAL ANALYSIS REPORT")
        print("=" * 60)
        
        # Load fonts
        fonts_to_test = [
            ("viii", terminalio_FONT),
            ("tom-thumb", self._load_font_safe("PyLEDSimulator/fonts/tom-thumb.bdf")),
            ("Arial_16", self._load_font_safe("PyLEDSimulator/fonts/Arial_16.bdf"))
        ]
        
        test_chars = ['A', 'g', 'M', '1']
        scales = [1, 2]
        
        for font_name, font in fonts_to_test:
            if font is None:
                print(f"\n❌ Skipping {font_name} - font not loaded")
                continue
                
            print(f"\n{'='*40}")
            print(f"TESTING FONT: {font_name}")
            print(f"{'='*40}")
            
            for scale in scales:
                print(f"\n--- Scale {scale} ---")
                for char in test_chars:
                    self.test_single_character(font, char, scale, font_name)
                    pygame.time.wait(100)  # Small delay
                    
    def _load_font_safe(self, path):
        """Safely load a font file."""
        try:
            return bitmap_font.load_font(path)
        except Exception as e:
            print(f"Failed to load font {path}: {e}")
            return None
            
    def analyze_bdf_file(self, bdf_path, char='A'):
        """Analyze a BDF font file directly to understand expected character dimensions."""
        print(f"\n{'='*40}")
        print(f"ANALYZING BDF FILE: {bdf_path}")
        print(f"{'='*40}")
        
        try:
            with open(bdf_path, 'r', encoding='latin-1') as f:
                lines = f.readlines()
                
            # Parse BDF metadata
            font_info = {}
            char_info = {}
            in_char = False
            current_char = None
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('FONTBOUNDINGBOX'):
                    parts = line.split()
                    if len(parts) >= 5:
                        font_info['bbox_width'] = int(parts[1])
                        font_info['bbox_height'] = int(parts[2])
                        font_info['bbox_x_offset'] = int(parts[3])
                        font_info['bbox_y_offset'] = int(parts[4])
                elif line.startswith('FONT_ASCENT'):
                    font_info['ascent'] = int(line.split()[1])
                elif line.startswith('FONT_DESCENT'):
                    font_info['descent'] = int(line.split()[1])
                elif line.startswith('STARTCHAR'):
                    current_char = line.split()[1] if len(line.split()) > 1 else None
                elif line.startswith('ENCODING'):
                    encoding = int(line.split()[1])
                    if encoding == ord(char):
                        in_char = True
                        char_info['encoding'] = encoding
                elif in_char and line.startswith('BBX'):
                    parts = line.split()
                    if len(parts) >= 5:
                        char_info['width'] = int(parts[1])
                        char_info['height'] = int(parts[2])
                        char_info['x_offset'] = int(parts[3])
                        char_info['y_offset'] = int(parts[4])
                elif in_char and line.startswith('ENDCHAR'):
                    break
                    
            print("Font metadata:")
            for key, value in font_info.items():
                print(f"  {key}: {value}")
                
            print(f"\nCharacter '{char}' metadata:")
            for key, value in char_info.items():
                print(f"  {key}: {value}")
                
            # Calculate expected positioning
            if 'ascent' in font_info and 'y_offset' in char_info:
                expected_baseline_y = font_info['ascent']
                char_top = expected_baseline_y + char_info['y_offset']
                char_bottom = char_top + char_info['height']
                print(f"\nExpected positioning (if baseline at y={expected_baseline_y}):")
                print(f"  Character top should be at y={char_top}")
                print(f"  Character bottom should be at y={char_bottom}")
                print(f"  Character should be {char_info['height']} pixels tall")
                
        except Exception as e:
            print(f"Error analyzing BDF file: {e}")
            
    def run_full_analysis(self):
        """Run complete font analysis."""
        # Analyze BDF files first
        bdf_files = [
            "PyLEDSimulator/fonts/viii.bdf",
            "PyLEDSimulator/fonts/tom-thumb.bdf", 
            "PyLEDSimulator/fonts/Arial_16.bdf"
        ]
        
        for bdf_path in bdf_files:
            if os.path.exists(bdf_path):
                self.analyze_bdf_file(bdf_path, 'A')
            else:
                print(f"BDF file not found: {bdf_path}")
                
        # Test font rendering
        self.test_font_comparison()
        
        print(f"\n{'='*60}")
        print("ANALYSIS COMPLETE")
        print("Screenshots saved for visual inspection.")
        print("Check the generated PNG files to compare with expected font metrics.")
        print(f"{'='*60}")


def main():
    """Run the font visual analysis."""
    analyzer = FontVisualAnalyzer()
    analyzer.run_full_analysis()
    
    # Keep window open briefly for manual inspection
    print("\nPress any key to close...")
    pygame.time.wait(2000)
    pygame.quit()


if __name__ == "__main__":
    main()