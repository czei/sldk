#!/usr/bin/env python3
"""Recreation of THEME PARK WAITS LED display from screenshot.

This program recreates the exact pixel pattern from the LED display
showing "THEME PARK" on the first line and "WAITS" on the second line
in yellow/amber color.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyledsimulator.devices import MatrixPortalS3
from pyledsimulator.core import rgb888_to_rgb565


def draw_letter_T(matrix, x_offset, y_offset):
    """Draw the letter T at specified offset."""
    # Top horizontal line
    for x in range(5):
        matrix.set_pixel(x_offset + x, y_offset, (255, 255, 0))
    # Vertical line
    for y in range(1, 7):
        matrix.set_pixel(x_offset + 2, y_offset + y, (255, 255, 0))


def draw_letter_H(matrix, x_offset, y_offset):
    """Draw the letter H at specified offset."""
    # Left vertical
    for y in range(7):
        matrix.set_pixel(x_offset, y_offset + y, (255, 255, 0))
    # Right vertical
    for y in range(7):
        matrix.set_pixel(x_offset + 4, y_offset + y, (255, 255, 0))
    # Middle horizontal
    for x in range(1, 4):
        matrix.set_pixel(x_offset + x, y_offset + 3, (255, 255, 0))


def draw_letter_E(matrix, x_offset, y_offset):
    """Draw the letter E at specified offset."""
    # Left vertical
    for y in range(7):
        matrix.set_pixel(x_offset, y_offset + y, (255, 255, 0))
    # Top horizontal
    for x in range(5):
        matrix.set_pixel(x_offset + x, y_offset, (255, 255, 0))
    # Middle horizontal
    for x in range(4):
        matrix.set_pixel(x_offset + x, y_offset + 3, (255, 255, 0))
    # Bottom horizontal
    for x in range(5):
        matrix.set_pixel(x_offset + x, y_offset + 6, (255, 255, 0))


def draw_letter_M(matrix, x_offset, y_offset):
    """Draw the letter M at specified offset."""
    # Left vertical
    for y in range(7):
        matrix.set_pixel(x_offset, y_offset + y, (255, 255, 0))
    # Right vertical
    for y in range(7):
        matrix.set_pixel(x_offset + 4, y_offset + y, (255, 255, 0))
    # Left diagonal
    matrix.set_pixel(x_offset + 1, y_offset + 1, (255, 255, 0))
    matrix.set_pixel(x_offset + 2, y_offset + 2, (255, 255, 0))
    # Right diagonal
    matrix.set_pixel(x_offset + 3, y_offset + 1, (255, 255, 0))


def draw_letter_P(matrix, x_offset, y_offset):
    """Draw the letter P at specified offset."""
    # Left vertical
    for y in range(7):
        matrix.set_pixel(x_offset, y_offset + y, (255, 255, 0))
    # Top horizontal
    for x in range(4):
        matrix.set_pixel(x_offset + x, y_offset, (255, 255, 0))
    # Middle horizontal
    for x in range(4):
        matrix.set_pixel(x_offset + x, y_offset + 3, (255, 255, 0))
    # Right vertical (top part)
    for y in range(1, 3):
        matrix.set_pixel(x_offset + 3, y_offset + y, (255, 255, 0))


def draw_letter_A(matrix, x_offset, y_offset):
    """Draw the letter A at specified offset."""
    # Left vertical
    for y in range(1, 7):
        matrix.set_pixel(x_offset, y_offset + y, (255, 255, 0))
    # Right vertical
    for y in range(1, 7):
        matrix.set_pixel(x_offset + 4, y_offset + y, (255, 255, 0))
    # Top horizontal
    for x in range(1, 4):
        matrix.set_pixel(x_offset + x, y_offset, (255, 255, 0))
    # Middle horizontal
    for x in range(5):
        matrix.set_pixel(x_offset + x, y_offset + 3, (255, 255, 0))


def draw_letter_R(matrix, x_offset, y_offset):
    """Draw the letter R at specified offset."""
    # Left vertical
    for y in range(7):
        matrix.set_pixel(x_offset, y_offset + y, (255, 255, 0))
    # Top horizontal
    for x in range(4):
        matrix.set_pixel(x_offset + x, y_offset, (255, 255, 0))
    # Middle horizontal
    for x in range(4):
        matrix.set_pixel(x_offset + x, y_offset + 3, (255, 255, 0))
    # Right vertical (top part)
    for y in range(1, 3):
        matrix.set_pixel(x_offset + 3, y_offset + y, (255, 255, 0))
    # Diagonal leg
    matrix.set_pixel(x_offset + 2, y_offset + 4, (255, 255, 0))
    matrix.set_pixel(x_offset + 3, y_offset + 5, (255, 255, 0))
    matrix.set_pixel(x_offset + 4, y_offset + 6, (255, 255, 0))


def draw_letter_K(matrix, x_offset, y_offset):
    """Draw the letter K at specified offset."""
    # Left vertical
    for y in range(7):
        matrix.set_pixel(x_offset, y_offset + y, (255, 255, 0))
    # Upper diagonal
    matrix.set_pixel(x_offset + 3, y_offset, (255, 255, 0))
    matrix.set_pixel(x_offset + 2, y_offset + 1, (255, 255, 0))
    matrix.set_pixel(x_offset + 1, y_offset + 2, (255, 255, 0))
    matrix.set_pixel(x_offset + 1, y_offset + 3, (255, 255, 0))
    # Lower diagonal
    matrix.set_pixel(x_offset + 1, y_offset + 4, (255, 255, 0))
    matrix.set_pixel(x_offset + 2, y_offset + 5, (255, 255, 0))
    matrix.set_pixel(x_offset + 3, y_offset + 6, (255, 255, 0))


def draw_letter_W(matrix, x_offset, y_offset):
    """Draw the letter W at specified offset."""
    # Left vertical
    for y in range(7):
        matrix.set_pixel(x_offset, y_offset + y, (255, 255, 0))
    # Middle vertical
    for y in range(7):
        matrix.set_pixel(x_offset + 2, y_offset + y, (255, 255, 0))
    # Right vertical
    for y in range(7):
        matrix.set_pixel(x_offset + 4, y_offset + y, (255, 255, 0))
    # Bottom connections
    matrix.set_pixel(x_offset + 1, y_offset + 5, (255, 255, 0))
    matrix.set_pixel(x_offset + 3, y_offset + 5, (255, 255, 0))


def draw_letter_I(matrix, x_offset, y_offset):
    """Draw the letter I at specified offset."""
    # Top horizontal
    for x in range(5):
        matrix.set_pixel(x_offset + x, y_offset, (255, 255, 0))
    # Vertical line
    for y in range(1, 6):
        matrix.set_pixel(x_offset + 2, y_offset + y, (255, 255, 0))
    # Bottom horizontal
    for x in range(5):
        matrix.set_pixel(x_offset + x, y_offset + 6, (255, 255, 0))


def draw_letter_S(matrix, x_offset, y_offset):
    """Draw the letter S at specified offset."""
    # Top horizontal
    for x in range(1, 5):
        matrix.set_pixel(x_offset + x, y_offset, (255, 255, 0))
    # Top left
    matrix.set_pixel(x_offset, y_offset + 1, (255, 255, 0))
    matrix.set_pixel(x_offset, y_offset + 2, (255, 255, 0))
    # Middle horizontal
    for x in range(1, 4):
        matrix.set_pixel(x_offset + x, y_offset + 3, (255, 255, 0))
    # Bottom right
    matrix.set_pixel(x_offset + 4, y_offset + 4, (255, 255, 0))
    matrix.set_pixel(x_offset + 4, y_offset + 5, (255, 255, 0))
    # Bottom horizontal
    for x in range(5):
        matrix.set_pixel(x_offset + x, y_offset + 6, (255, 255, 0))


def main():
    """Run the THEME PARK WAITS display."""
    # Create and initialize device
    print("Creating THEME PARK WAITS display...")
    device = MatrixPortalS3()
    device.initialize()
    
    # Clear the display
    device.matrix.clear()
    
    # Draw "THEME PARK" on first line (y=2)
    y_line1 = 2
    
    # T
    draw_letter_T(device.matrix, 1, y_line1)
    # H
    draw_letter_H(device.matrix, 7, y_line1)
    # E
    draw_letter_E(device.matrix, 13, y_line1)
    # M
    draw_letter_M(device.matrix, 19, y_line1)
    # E
    draw_letter_E(device.matrix, 25, y_line1)
    
    # Space
    
    # P
    draw_letter_P(device.matrix, 33, y_line1)
    # A
    draw_letter_A(device.matrix, 39, y_line1)
    # R
    draw_letter_R(device.matrix, 45, y_line1)
    # K
    draw_letter_K(device.matrix, 51, y_line1)
    
    # Draw "WAITS" on second line (y=12)
    y_line2 = 12
    
    # Center "WAITS" horizontally
    x_offset_line2 = 15
    
    # W
    draw_letter_W(device.matrix, x_offset_line2, y_line2)
    # A
    draw_letter_A(device.matrix, x_offset_line2 + 6, y_line2)
    # I
    draw_letter_I(device.matrix, x_offset_line2 + 12, y_line2)
    # T
    draw_letter_T(device.matrix, x_offset_line2 + 18, y_line2)
    # S
    draw_letter_S(device.matrix, x_offset_line2 + 24, y_line2)
    
    # Run the simulation
    print("Displaying THEME PARK WAITS... Press ESC or close window to exit.")
    
    # Simple animation - make the display blink occasionally
    frame_count = 0
    
    def update():
        """Update function for animation."""
        nonlocal frame_count
        
        # Every 120 frames (2 seconds at 60fps), briefly dim the display
        if frame_count % 120 == 0:
            device.matrix.set_brightness(0.7)
        elif frame_count % 120 == 5:
            device.matrix.set_brightness(1.0)
            
        frame_count += 1
    
    device.run(update_callback=update, title="THEME PARK WAITS Display")


if __name__ == "__main__":
    main()