#!/usr/bin/env python3
"""Force display test with explicit pygame initialization."""

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
import sys
import time

print("Initializing pygame display...")

# Force pygame to initialize
pygame.init()
pygame.display.init()

# Create window
print("Creating window...")
screen = pygame.display.set_mode((640, 320))
pygame.display.set_caption("SLDK Test Display")

# Make sure window is visible
pygame.event.pump()
pygame.display.update()

print("Window should be visible now!")
print("Look for a window titled 'SLDK Test Display'")

# Fill with pattern
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
frame = 0

try:
    clock = pygame.time.Clock()
    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
                
        # Change color
        color = colors[frame % len(colors)]
        screen.fill(color)
        
        # Draw text
        if pygame.font:
            font = pygame.font.Font(None, 36)
            text = font.render(f"Frame: {frame}", True, (255, 255, 255))
            screen.blit(text, (10, 10))
        
        pygame.display.flip()
        clock.tick(4)  # 4 FPS for visible changes
        
        frame += 1
        if frame % 4 == 0:
            color_name = ["RED", "GREEN", "BLUE", "YELLOW"][((frame-1) % len(colors))]
            print(f"Frame {frame}: Screen is {color_name}")
            
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    pygame.quit()