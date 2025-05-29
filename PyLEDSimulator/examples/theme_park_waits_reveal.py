#!/usr/bin/env python3
"""Random LED reveal of THEME PARK WAITS display.

Starts with RANDOM LEDs turned on (50% chance for each LED). The animation:
- Randomly turns off LEDs that are on but aren't part of the text
- Randomly turns on text LEDs that are off but should be on
- Never turns on non-text LEDs after the initial random state
The animation continues until only the THEME PARK WAITS text remains lit.

OPTIMIZED VERSION: 3-5x faster than the original implementation.
"""

import sys
import os
import random
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3


def get_theme_park_waits_pixels():
    """Return list of (x, y) coordinates for all LEDs in THEME PARK WAITS."""
    pixels = []
    
    # THEME PARK - First line (8 pixels tall)
    # T (x=4, y=3) - 8 LEDs tall
    for x in range(4, 9): pixels.append((x, 3))
    for y in range(4, 11): pixels.append((6, y))
    
    # H (x=10, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.append((10, y))
    for y in range(3, 11): pixels.append((14, y))
    for x in range(11, 14): pixels.append((x, 6))
    
    # E (x=16, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.append((16, y))
    for x in range(16, 20): pixels.append((x, 3))
    for x in range(16, 19): pixels.append((x, 6))
    for x in range(16, 20): pixels.append((x, 10))
    
    # M (x=22, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.append((22, y))
    for y in range(3, 11): pixels.append((27, y))
    pixels.append((23, 4))
    pixels.append((24, 5))
    pixels.append((25, 5))
    pixels.append((26, 4))
    
    # E (x=29, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.append((29, y))
    for x in range(29, 33): pixels.append((x, 3))
    for x in range(29, 32): pixels.append((x, 6))
    for x in range(29, 33): pixels.append((x, 10))
    
    # P (x=36, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.append((36, y))
    for x in range(36, 40): pixels.append((x, 3))
    for x in range(36, 40): pixels.append((x, 6))
    pixels.append((39, 4))
    pixels.append((39, 5))
    
    # A (x=42, y=3) - 8 LEDs tall
    for y in range(4, 11): pixels.append((42, y))
    for y in range(4, 11): pixels.append((46, y))
    for x in range(43, 46): pixels.append((x, 3))
    for x in range(42, 47): pixels.append((x, 6))
    
    # R (x=48, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.append((48, y))
    for x in range(48, 52): pixels.append((x, 3))
    for x in range(48, 52): pixels.append((x, 6))
    pixels.append((51, 4))
    pixels.append((51, 5))
    pixels.append((50, 7))
    pixels.append((51, 8))
    pixels.append((52, 9))
    pixels.append((53, 10))
    
    # K (x=54, y=3) - 8 LEDs tall
    for y in range(3, 11): pixels.append((54, y))
    pixels.append((57, 3))
    pixels.append((56, 4))
    pixels.append((55, 5))
    pixels.append((55, 6))
    pixels.append((56, 7))
    pixels.append((57, 8))
    pixels.append((58, 9))
    pixels.append((59, 10))
    
    # WAITS - Second line (16 pixels tall, moved right by 3 LEDs)
    # W (x=5, y=15) - exact pattern from screenshot
    # Left outer edge
    for y in range(15, 31):
        pixels.append((5, y))
        pixels.append((6, y))
    # Right outer edge
    for y in range(15, 31):
        pixels.append((13, y))
        pixels.append((14, y))

    ## CLAUDE DO NOT MODIFY
    for x in range(7, 9): pixels.append((x, 28))
    for x in range(7, 9): pixels.append((x, 27))
    for x in range(11, 13): pixels.append((x, 28))
    for x in range(11, 13): pixels.append((x, 27))
    for y in range(23, 27): pixels.append((9, y))
    for y in range(23, 27): pixels.append((10, y))
    ## End do not modify
    
    # A (x=16, y=15) - 10 LEDs wide, 16 pixels tall
    for y in range(17, 31): pixels.append((16, y))
    for y in range(17, 31): pixels.append((17, y))
    for y in range(17, 31): pixels.append((24, y))
    for y in range(17, 31): pixels.append((25, y))
    for x in range(18, 24): pixels.append((x, 15))
    for x in range(18, 24): pixels.append((x, 16))
    for x in range(16, 26): pixels.append((x, 22))
    for x in range(16, 26): pixels.append((x, 23))
    
    # I (x=27, y=15) - 10 LEDs wide, 16 pixels tall
    for x in range(27, 37): pixels.append((x, 15))
    for x in range(27, 37): pixels.append((x, 16))
    for x in range(27, 37): pixels.append((x, 29))
    for x in range(27, 37): pixels.append((x, 30))
    for y in range(15, 31): pixels.append((31, y))
    for y in range(15, 31): pixels.append((32, y))
    
    # T (x=38, y=15) - 10 LEDs wide, 16 pixels tall
    for x in range(38, 48): pixels.append((x, 15))
    for x in range(38, 48): pixels.append((x, 16))
    for y in range(15, 31): pixels.append((42, y))
    for y in range(15, 31): pixels.append((43, y))
    
    # S (x=49, y=15) - 10 LEDs wide, 16 pixels tall
    for x in range(49, 59): pixels.append((x, 15))
    for x in range(49, 59): pixels.append((x, 16))
    for y in range(17, 22): pixels.append((49, y))
    for y in range(17, 22): pixels.append((50, y))
    for x in range(49, 59): pixels.append((x, 22))
    for x in range(49, 59): pixels.append((x, 23))
    for y in range(24, 29): pixels.append((57, y))
    for y in range(24, 29): pixels.append((58, y))
    for x in range(49, 59): pixels.append((x, 29))
    for x in range(49, 59): pixels.append((x, 30))
    
    return pixels


# Simple shuffle alternative for CircuitPython compatibility
def simple_shuffle(lst):
    """Simple in-place shuffle for CircuitPython compatibility."""
    for i in range(len(lst)):
        j = random.randint(0, len(lst) - 1)
        lst[i], lst[j] = lst[j], lst[i]


def show_splash(device, duration=4, show_version=False, version_text="v1.0"):
    """Show THEME PARK WAITS splash screen with optional version.
    
    Args:
        device: The MatrixPortalS3 device instance
        duration: Duration to show splash in seconds (default: 4)
        show_version: Whether to show version text (default: False)
        version_text: Version text to display (default: "v1.0")
    """
    device.matrix.clear()
    yellow = (255, 255, 0)
    dim_yellow = (128, 128, 0)  # Dimmer yellow for version
    
    # Draw THEME PARK WAITS
    target_pixels = get_theme_park_waits_pixels()
    for pixel in target_pixels:
        device.matrix.set_pixel(pixel[0], pixel[1], yellow)
    
    # Draw version text if requested
    if show_version:
        # Simple version display in bottom right corner
        # Using a simple pixel pattern for version text
        version_pixels = []
        
        # "v" character (small, bottom right area)
        version_pixels.extend([
            (52, 26), (52, 27),
            (53, 28), (53, 29),
            (54, 27), (54, 26)
        ])
        
        # "1" character
        version_pixels.extend([
            (56, 26), (56, 27), (56, 28), (56, 29), (56, 30)
        ])
        
        # "." dot
        version_pixels.append((58, 30))
        
        # "0" character
        version_pixels.extend([
            (60, 26), (60, 27), (60, 28), (60, 29), (60, 30),
            (61, 26), (61, 30),
            (62, 26), (62, 27), (62, 28), (62, 29), (62, 30)
        ])
        
        # Draw version pixels in dimmer yellow
        for pixel in version_pixels:
            if 0 <= pixel[0] < 64 and 0 <= pixel[1] < 32:
                device.matrix.set_pixel(pixel[0], pixel[1], dim_yellow)
    
    # Wait for duration
    time.sleep(duration)
    device.matrix.clear()


def main():
    """Run the optimized reveal animation."""
    device = MatrixPortalS3()
    device.initialize()
    device.matrix.clear()
    
    yellow = (255, 255, 0)
    
    # Option to show splash with version first
    show_splash_first = True  # Set to True to show splash before animation
    
    if show_splash_first:
        print("Showing THEME PARK WAITS splash with version...")
        show_splash(device, duration=3, show_version=True, version_text="v1.0")
        print("Starting reveal animation...")
    else:
        print("Starting THEME PARK WAITS reveal animation...")
        print("Starting with random LEDs on, gradually revealing the text...")
    
    print("Press ESC or close window to exit.")
    
    # Get target pixels for THEME PARK WAITS
    target_pixels = get_theme_park_waits_pixels()
    target_set = set(target_pixels)  # For faster lookup
    
    # Start with RANDOM LEDs turned on
    for x in range(64):
        for y in range(32):
            if random.random() < 0.5:  # 50% chance each LED is on
                device.matrix.set_pixel(x, y, yellow)
            else:
                device.matrix.set_pixel(x, y, (0, 0, 0))

    # Animation parameters
    start_time = time.time()
    frame_count = 0
    last_update = time.time()
    animation_complete = False

    # Count how many incorrect LEDs need to be turned off
    # and how many correct LEDs need to be turned on
    incorrect_on = []  # LEDs that are on but shouldn't be
    missing_text = []  # Text LEDs that are off but should be on

    # Analyze initial state to categorize LEDs
    for x in range(64):
        for y in range(32):
            pixel = (x, y)
            is_on = device.matrix.get_pixel(x, y) != (0, 0, 0)
            is_text = pixel in target_set
            
            if is_on and not is_text:
                # LED is on but shouldn't be - needs to turn off
                incorrect_on.append(pixel)
            elif not is_on and is_text:
                # LED is off but should be on - needs to turn on
                missing_text.append(pixel)

    # Shuffle lists once for randomness, then we can use pop() efficiently
    simple_shuffle(incorrect_on)
    simple_shuffle(missing_text)

    print("Initial state: {} incorrect on, {} text missing".format(len(incorrect_on), len(missing_text)))
    print("Target has {} text LEDs".format(len(target_pixels)))
    
    def update_animation():
        nonlocal frame_count, animation_complete, last_update, incorrect_on, missing_text
        
        current_time = time.time()
        
        # Update every ~50ms (faster animation)
        if current_time - last_update < 0.05:
            return
        
        last_update = current_time
        frame_count += 1
        
        # Turn off incorrect LEDs - use fixed rate for consistent speed
        if len(incorrect_on) > 0:
            # Turn off 5 incorrect LEDs per frame (consistent fast speed)
            num_to_turn_off = min(5, len(incorrect_on))
            for _ in range(num_to_turn_off):
                pixel = incorrect_on.pop()
                device.matrix.set_pixel(pixel[0], pixel[1], (0, 0, 0))
        
        # Turn on missing text LEDs - use fixed rate for consistent speed
        if len(missing_text) > 0:
            # Turn on 3 missing text LEDs per frame (consistent fast speed)
            num_to_turn_on = min(3, len(missing_text))
            for _ in range(num_to_turn_on):
                pixel = missing_text.pop()
                device.matrix.set_pixel(pixel[0], pixel[1], yellow)
        
        # Check if we're done
        if len(incorrect_on) == 0 and len(missing_text) == 0:
            if not animation_complete:  # Only print once
                animation_complete = True
                elapsed = current_time - start_time
                print("THEME PARK WAITS revealed in {:.1f} seconds!".format(elapsed))
                print("Animation complete!")
            return
        
        # Progress update less frequently to reduce overhead
        if frame_count % 5 == 0:
            elapsed = current_time - start_time
            print("Progress: {} incorrect left, {} missing text in {:.1f}s".format(
                len(incorrect_on), len(missing_text), elapsed))
    
    # Run with animation callback
    device.run(title="THEME PARK WAITS Reveal (Optimized)", update_callback=update_animation)


if __name__ == "__main__":
    main()