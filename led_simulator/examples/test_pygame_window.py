#!/usr/bin/env python3
"""Test if pygame window is working properly."""

import pygame
import sys
import time

def test_pygame():
    """Test basic pygame functionality."""
    print("Testing pygame window creation...")
    
    # Initialize pygame
    pygame.init()
    
    # Create a simple window
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Test Window - Should Be Visible")
    
    # Colors
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    WHITE = (255, 255, 255)
    
    clock = pygame.time.Clock()
    frame_count = 0
    
    print("Window created! You should see a colorful test window.")
    print("Window will close automatically after 5 seconds.")
    
    running = True
    start_time = time.time()
    
    while running and (time.time() - start_time < 5.0):
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Clear screen
        screen.fill(BLACK)
        
        # Draw some test patterns
        # Colored squares that change position
        offset = (frame_count // 10) % 100
        
        pygame.draw.rect(screen, RED, (100 + offset, 100, 50, 50))
        pygame.draw.rect(screen, GREEN, (200 + offset, 150, 50, 50))
        pygame.draw.rect(screen, BLUE, (300 + offset, 200, 50, 50))
        
        # Draw text
        font = pygame.font.Font(None, 36)
        text = font.render(f"Frame: {frame_count}", True, WHITE)
        screen.blit(text, (50, 50))
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
        frame_count += 1
    
    pygame.quit()
    print("Test complete. Did you see the colorful window with moving squares?")

if __name__ == "__main__":
    test_pygame()