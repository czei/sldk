#!/usr/bin/env python3
"""Random LED reveal of THEME PARK WAITS display.

Starts with random yellow LEDs switching on/off. When a yellow LED appears
in the correct position for the THEME PARK WAITS text, it stays on permanently.
When an LED turns off and it's not part of the text, it stays off permanently.
The animation continues until all text LEDs are revealed.
"""

import sys
import os
import random
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3


def get_theme_park_waits_pixels():
    """Return set of (x, y) coordinates for all LEDs in THEME PARK WAITS."""
    pixels = set()
    
    # THEME PARK - First line (8 pixels tall)
    # T (x=4, y=3) - 8 LEDs tall
    for x in range(4, 9): pixels.add((x, 3))
    for y in range(4, 11): pixels.add((6, y))
    
    # H (x=10, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.add((10, y))
    for y in range(3, 11): pixels.add((14, y))
    for x in range(11, 14): pixels.add((x, 6))
    
    # E (x=16, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.add((16, y))
    for x in range(16, 20): pixels.add((x, 3))
    for x in range(16, 19): pixels.add((x, 6))
    for x in range(16, 20): pixels.add((x, 10))
    
    # M (x=22, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.add((22, y))
    for y in range(3, 11): pixels.add((27, y))
    pixels.add((23, 4))
    pixels.add((24, 5))
    pixels.add((25, 5))
    pixels.add((26, 4))
    
    # E (x=29, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.add((29, y))
    for x in range(29, 33): pixels.add((x, 3))
    for x in range(29, 32): pixels.add((x, 6))
    for x in range(29, 33): pixels.add((x, 10))
    
    # P (x=36, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.add((36, y))
    for x in range(36, 40): pixels.add((x, 3))
    for x in range(36, 40): pixels.add((x, 6))
    pixels.add((39, 4))
    pixels.add((39, 5))
    
    # A (x=42, y=3) - 8 LEDs tall
    for y in range(4, 11): pixels.add((42, y))
    for y in range(4, 11): pixels.add((46, y))
    for x in range(43, 46): pixels.add((x, 3))
    for x in range(42, 47): pixels.add((x, 6))
    
    # R (x=48, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.add((48, y))
    for x in range(48, 52): pixels.add((x, 3))
    for x in range(48, 52): pixels.add((x, 6))
    pixels.add((51, 4))
    pixels.add((51, 5))
    pixels.add((50, 7))
    pixels.add((51, 8))
    pixels.add((52, 9))
    pixels.add((53, 10))
    
    # K (x=54, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.add((54, y))
    pixels.add((57, 3))
    pixels.add((56, 4))
    pixels.add((55, 5))
    pixels.add((55, 6))
    pixels.add((56, 7))
    pixels.add((57, 8))
    pixels.add((58, 9))
    pixels.add((59, 10))
    
    # WAITS - Second line (16 pixels tall, moved right by 3 LEDs)
    # W (x=5, y=15) - exact pattern from screenshot
    # Left outer edge
    for y in range(15, 31):
        pixels.add((5, y))
        pixels.add((6, y))
    # Right outer edge
    for y in range(15, 31):
        pixels.add((13, y))
        pixels.add((14, y))
    # Inner left diagonal
    for y in range(15, 23): pixels.add((8, y))
    for y in range(23, 31): pixels.add((9, y))
    # Inner right diagonal
    for y in range(15, 23): pixels.add((11, y))
    for y in range(23, 31): pixels.add((10, y))
    
    # A (x=16, y=15) - 10 LEDs wide, 16 pixels tall
    for y in range(17, 31): pixels.add((16, y))
    for y in range(17, 31): pixels.add((17, y))
    for y in range(17, 31): pixels.add((24, y))
    for y in range(17, 31): pixels.add((25, y))
    for x in range(18, 24): pixels.add((x, 15))
    for x in range(18, 24): pixels.add((x, 16))
    for x in range(16, 26): pixels.add((x, 22))
    for x in range(16, 26): pixels.add((x, 23))
    
    # I (x=27, y=15) - 10 LEDs wide, 16 pixels tall
    for x in range(27, 37): pixels.add((x, 15))
    for x in range(27, 37): pixels.add((x, 16))
    for x in range(27, 37): pixels.add((x, 29))
    for x in range(27, 37): pixels.add((x, 30))
    for y in range(15, 31): pixels.add((31, y))
    for y in range(15, 31): pixels.add((32, y))
    
    # T (x=38, y=15) - 10 LEDs wide, 16 pixels tall
    for x in range(38, 48): pixels.add((x, 15))
    for x in range(38, 48): pixels.add((x, 16))
    for y in range(15, 31): pixels.add((42, y))
    for y in range(15, 31): pixels.add((43, y))
    
    # S (x=49, y=15) - 10 LEDs wide, 16 pixels tall
    for x in range(49, 59): pixels.add((x, 15))
    for x in range(49, 59): pixels.add((x, 16))
    for y in range(17, 22): pixels.add((49, y))
    for y in range(17, 22): pixels.add((50, y))
    for x in range(49, 59): pixels.add((x, 22))
    for x in range(49, 59): pixels.add((x, 23))
    for y in range(24, 29): pixels.add((57, y))
    for y in range(24, 29): pixels.add((58, y))
    for x in range(49, 59): pixels.add((x, 29))
    for x in range(49, 59): pixels.add((x, 30))
    
    return pixels


def main():
    """Run the reveal animation."""
    device = MatrixPortalS3()
    device.initialize()
    device.matrix.clear()
    
    yellow = (255, 255, 0)
    off = (0, 0, 0)
    
    # Get target pixels for THEME PARK WAITS
    target_pixels = get_theme_park_waits_pixels()
    
    # Track which target pixels have been "locked" (will stay on permanently)
    locked_pixels = set()
    # Track which non-target pixels have been "killed" (will stay off permanently)
    killed_pixels = set()
    
    print("Starting reveal animation... Watch the text appear!")
    print("Press ESC or close window to exit.")
    
    # Animation state
    start_time = time.time()
    frame_count = 0
    animation_complete = False
    
    # Animation parameters for 6-8 second duration
    total_frames = 80  # 8 seconds at ~100ms per frame
    last_update = time.time()
    
    def update_animation():
        nonlocal frame_count, animation_complete, last_update
        
        current_time = time.time()
        # Update every ~100ms
        if current_time - last_update < 0.1:
            return
        last_update = current_time
        
        if animation_complete or len(locked_pixels) >= len(target_pixels) or frame_count >= total_frames:
            animation_complete = True
            return
            
        frame_count += 1
        
        # Store previous frame state to detect what turned off
        previous_pixels = set()
        for x in range(64):
            for y in range(32):
                if device.matrix.get_pixel(x, y) != (0, 0, 0):  # Was on in previous frame
                    previous_pixels.add((x, y))
        
        # Generate completely new random pattern each frame
        device.matrix.clear()
        new_pixels = set()
        for x in range(64):
            for y in range(32):
                # Locked pixels always stay on
                if (x, y) in locked_pixels:
                    new_pixels.add((x, y))
                    device.matrix.set_pixel(x, y, yellow)
                # Killed pixels always stay off
                elif (x, y) in killed_pixels:
                    continue  # Stay off
                # All other pixels have random chance to be on
                elif random.random() < 0.35:
                    new_pixels.add((x, y))
                    device.matrix.set_pixel(x, y, yellow)
        
        # Check for non-target pixels that turned off - they should stay off forever
        for pixel in previous_pixels:
            if pixel not in new_pixels and pixel not in target_pixels and pixel not in locked_pixels:
                killed_pixels.add(pixel)
                print(f"Killed pixel {pixel} (now {len(killed_pixels)} killed)")
        
        # Check if any target pixels should get locked this frame
        # Target pixels that are currently ON should be locked immediately (no random chance)
        for pixel in target_pixels:
            if pixel not in locked_pixels and pixel in new_pixels:
                # Lock this pixel permanently - it's a target pixel that's currently on
                locked_pixels.add(pixel)
                print(f"Locked pixel {pixel} ({len(locked_pixels)}/{len(target_pixels)})")
        
        # No need for lock probability - target pixels lock immediately when they appear
        
        # Show progress every 10 frames
        if frame_count % 10 == 0:
            elapsed = time.time() - start_time
            print(f"Progress: {len(locked_pixels)}/{len(target_pixels)} pixels locked in {elapsed:.1f}s")
        
        if len(locked_pixels) >= len(target_pixels):
            elapsed = time.time() - start_time
            print(f"THEME PARK WAITS fully revealed in {elapsed:.1f} seconds!")
            print("Animation complete!")
            animation_complete = True
    
    # Run with animation callback
    device.run(title="THEME PARK WAITS Reveal", update_callback=update_animation)


if __name__ == "__main__":
    main()