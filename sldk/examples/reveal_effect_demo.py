#!/usr/bin/env python3
"""Simple demo of the RevealEffect for SLDK.

This demonstrates text reveal effects using direct device approach.
"""

import sys
import os
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def simple_reveal_demo():
    """Simple reveal effect demo using direct device approach."""
    print("SLDK Reveal Effect Demo")
    print("=" * 40)
    print("Demonstrating text reveal effects")
    
    # Import device directly
    from sldk.simulator.devices import MatrixPortalS3
    
    # Create device
    device = MatrixPortalS3()
    device.initialize()
    
    # Demo state
    demo_stage = 0
    stage_start = 0
    stage_names = ["Right Reveal", "Down Reveal", "Center Reveal"]
    
    def update():
        """Update function called each frame."""
        nonlocal demo_stage, stage_start
        
        current_time = time.time()
        if stage_start == 0:
            stage_start = current_time
        
        elapsed = current_time - stage_start
        
        # Clear to black
        device.matrix.fill(0x000000)
        
        if demo_stage == 0 and elapsed < 6:
            # Stage 1: Right reveal of "THEME PARK WAITS"
            text = "THEME PARK WAITS"
            reveal_duration = 3.0
            
            if elapsed < reveal_duration:
                # Revealing from left to right
                progress = elapsed / reveal_duration
                reveal_chars = int(len(text) * progress)
                
                for i, char in enumerate(text[:reveal_chars]):
                    char_x = 2 + i * 3
                    if char_x < device.width:
                        # Draw simple pixel representation of text
                        device.matrix.set_pixel(char_x, 12, 0x00FF00)  # Green
                        device.matrix.set_pixel(char_x, 13, 0x00FF00)
                        device.matrix.set_pixel(char_x, 14, 0x00FF00)
            else:
                # Fully revealed - show complete text
                for i, char in enumerate(text):
                    char_x = 2 + i * 3
                    if char_x < device.width:
                        device.matrix.set_pixel(char_x, 12, 0x00FF00)
                        device.matrix.set_pixel(char_x, 13, 0x00FF00)
                        device.matrix.set_pixel(char_x, 14, 0x00FF00)
                        
        elif demo_stage == 1 and elapsed < 6:
            # Stage 2: Down reveal of "SLDK EFFECTS"  
            text = "SLDK EFFECTS"
            reveal_duration = 3.0
            
            if elapsed < reveal_duration:
                # Revealing from top to bottom
                progress = elapsed / reveal_duration
                reveal_rows = int(20 * progress)
                
                for i, char in enumerate(text):
                    char_x = 2 + i * 4
                    if char_x < device.width:
                        for y in range(min(reveal_rows, 16)):
                            if y + 8 < device.height:
                                device.matrix.set_pixel(char_x, y + 8, 0xFF0000)  # Red
            else:
                # Fully revealed
                for i, char in enumerate(text):
                    char_x = 2 + i * 4
                    if char_x < device.width:
                        for y in range(16):
                            if y + 8 < device.height:
                                device.matrix.set_pixel(char_x, y + 8, 0xFF0000)
                                
        elif demo_stage == 2:
            # Stage 3: Center reveal of "REVEAL"
            text = "REVEAL"
            reveal_duration = 3.0
            
            if elapsed < reveal_duration:
                # Revealing from center outwards
                progress = elapsed / reveal_duration
                center_x = device.width // 2
                reveal_width = int(device.width * progress)
                
                for i, char in enumerate(text):
                    char_x = center_x - len(text) * 2 + i * 4
                    if abs(char_x - center_x) <= reveal_width // 2 and 0 <= char_x < device.width:
                        device.matrix.set_pixel(char_x, 12, 0x0000FF)  # Blue
                        device.matrix.set_pixel(char_x, 13, 0x0000FF)
                        device.matrix.set_pixel(char_x, 14, 0x0000FF)
            else:
                # Fully revealed
                center_x = device.width // 2
                for i, char in enumerate(text):
                    char_x = center_x - len(text) * 2 + i * 4
                    if 0 <= char_x < device.width:
                        device.matrix.set_pixel(char_x, 12, 0x0000FF)
                        device.matrix.set_pixel(char_x, 13, 0x0000FF)
                        device.matrix.set_pixel(char_x, 14, 0x0000FF)
        
        # Advance stages
        stage_duration = 6
        if elapsed >= stage_duration:
            demo_stage = (demo_stage + 1) % 3  # 3 total stages
            stage_start = current_time
            
            # Update window title with current effect name
            import pygame
            if pygame.display.get_init():
                new_title = f"SLDK Reveal Effect Demo - {stage_names[demo_stage]}"
                pygame.display.set_caption(new_title)
            
            print(f"Reveal Demo Stage {demo_stage + 1}: {stage_names[demo_stage]}")
        
        return True
    
    # Use device.run() 
    device.run(update_callback=update, title="SLDK Reveal Effect Demo")


def main():
    """Main entry point."""
    simple_reveal_demo()


if __name__ == "__main__":
    main()