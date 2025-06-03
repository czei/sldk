#!/usr/bin/env python3
"""Animation demo for SLDK.

Demonstrates custom animation content.
"""

import sys
import os
import math

# Add parent directory to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import asyncio
    import time
    get_time = time.time
except ImportError:
    # CircuitPython
    import asyncio
    import time
    get_time = lambda: time.monotonic()

from sldk.app import SLDKApp
from sldk.display import DisplayContent, ScrollingText


class BouncingBall(DisplayContent):
    """A bouncing ball animation."""
    
    def __init__(self, color=0xFFFFFF, radius=2, speed=50):
        """Initialize bouncing ball.
        
        Args:
            color: Ball color
            radius: Ball radius in pixels
            speed: Speed of movement
        """
        super().__init__(duration=10)  # 10 second animation
        self.color = color
        self.radius = radius
        self.speed = speed
        
        # Position and velocity
        self.x = radius
        self.y = radius
        self.vx = speed / 10.0
        self.vy = speed / 15.0
        
        self._last_update = None
        
    async def render(self, display):
        """Render the bouncing ball."""
        # Update position
        now = get_time()
        if self._last_update is not None:
            dt = now - self._last_update
            
            # Update position
            self.x += self.vx * dt
            self.y += self.vy * dt
            
            # Bounce off walls
            if self.x - self.radius <= 0 or self.x + self.radius >= display.width:
                self.vx = -self.vx
                self.x = max(self.radius, min(display.width - self.radius, self.x))
                
            if self.y - self.radius <= 0 or self.y + self.radius >= display.height:
                self.vy = -self.vy
                self.y = max(self.radius, min(display.height - self.radius, self.y))
        
        self._last_update = now
        
        # Draw the ball
        cx = int(self.x)
        cy = int(self.y)
        
        # Simple circle drawing
        for y in range(max(0, cy - self.radius), min(display.height, cy + self.radius + 1)):
            for x in range(max(0, cx - self.radius), min(display.width, cx + self.radius + 1)):
                # Check if pixel is inside circle
                dx = x - cx
                dy = y - cy
                if dx * dx + dy * dy <= self.radius * self.radius:
                    await display.set_pixel(x, y, self.color)


class RainbowWave(DisplayContent):
    """A rainbow wave effect."""
    
    def __init__(self, duration=15):
        """Initialize rainbow wave."""
        super().__init__(duration=duration)
        self.offset = 0
        
    async def render(self, display):
        """Render rainbow wave."""
        # Create rainbow wave effect
        for y in range(display.height):
            for x in range(display.width):
                # Calculate hue based on position and time
                hue = (x * 10 + y * 5 + self.offset) % 360
                
                # Convert HSV to RGB (simplified)
                h = hue / 60.0
                c = 1.0
                x_val = c * (1 - abs(h % 2 - 1))
                
                if h < 1:
                    r, g, b = c, x_val, 0
                elif h < 2:
                    r, g, b = x_val, c, 0
                elif h < 3:
                    r, g, b = 0, c, x_val
                elif h < 4:
                    r, g, b = 0, x_val, c
                elif h < 5:
                    r, g, b = x_val, 0, c
                else:
                    r, g, b = c, 0, x_val
                
                # Convert to 24-bit color
                color = (int(r * 255) << 16) | (int(g * 255) << 8) | int(b * 255)
                
                # Apply wave effect
                wave = math.sin((x + self.offset / 10.0) * 0.2) * 0.5 + 0.5
                color = (
                    (int(((color >> 16) & 0xFF) * wave) << 16) |
                    (int(((color >> 8) & 0xFF) * wave) << 8) |
                    int((color & 0xFF) * wave)
                )
                
                await display.set_pixel(x, y, color)
        
        # Move the wave
        self.offset += 1


class AnimationDemoApp(SLDKApp):
    """Animation demonstration application."""
    
    def __init__(self):
        super().__init__(enable_web=False)
        
    async def setup(self):
        """Set up animations."""
        print("Animation demo starting...")
        
        # Add various animations
        self.content_queue.add(ScrollingText(
            "SLDK Animation Demo",
            y=12,
            color=0xFFFF00,
            speed=0.03
        ))
        
        self.content_queue.add(BouncingBall(
            color=0xFF0000,  # Red
            radius=3,
            speed=40
        ))
        
        self.content_queue.add(BouncingBall(
            color=0x00FF00,  # Green
            radius=2,
            speed=60
        ))
        
        self.content_queue.add(RainbowWave(duration=10))
        
        self.content_queue.add(ScrollingText(
            "Thanks for watching!",
            y=12,
            color=0x00FFFF,
            speed=0.04
        ))


def simple_animation_demo():
    """Simple animation demo using direct device approach."""
    print("Animation demo starting...")
    
    # Import device directly
    from sldk.simulator.devices import MatrixPortalS3
    import time
    import math
    
    # Create device
    device = MatrixPortalS3()
    device.initialize()
    
    # Animation state
    demo_stage = 0
    stage_start = 0
    ball_x, ball_y = 10.0, 10.0
    ball_vx, ball_vy = 15.0, 12.0
    
    def update():
        """Update function called each frame."""
        nonlocal demo_stage, stage_start, ball_x, ball_y, ball_vx, ball_vy
        
        current_time = time.time()
        if stage_start == 0:
            stage_start = current_time
        
        elapsed = current_time - stage_start
        
        # Clear to black
        device.matrix.fill(0x000000)
        
        if demo_stage == 0 and elapsed < 5:
            # Stage 1: Scrolling "SLDK Animation Demo" text
            scroll_text = "SLDK ANIMATION DEMO"
            x_offset = int(device.width - elapsed * 15) % (len(scroll_text) * 4 + device.width)
            
            for i, char in enumerate(scroll_text):
                char_x = x_offset + i * 4
                if 0 <= char_x < device.width:
                    device.matrix.set_pixel(char_x, 12, 0xFFFF00)  # Yellow
                    device.matrix.set_pixel(char_x, 13, 0xFFFF00)
                    
        elif demo_stage == 1 and elapsed < 8:
            # Stage 2: Bouncing ball animation
            dt = 0.1  # Fixed timestep
            
            # Update ball position
            ball_x += ball_vx * dt
            ball_y += ball_vy * dt
            
            # Bounce off walls
            if ball_x <= 2 or ball_x >= device.width - 2:
                ball_vx = -ball_vx
                ball_x = max(2, min(device.width - 2, ball_x))
            if ball_y <= 2 or ball_y >= device.height - 2:
                ball_vy = -ball_vy
                ball_y = max(2, min(device.height - 2, ball_y))
            
            # Draw bouncing ball
            cx, cy = int(ball_x), int(ball_y)
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    px, py = cx + dx, cy + dy
                    if 0 <= px < device.width and 0 <= py < device.height:
                        if dx*dx + dy*dy <= 4:
                            device.matrix.set_pixel(px, py, 0xFF0000)  # Red ball
                            
        elif demo_stage == 2 and elapsed < 8:
            # Stage 3: Rainbow wave effect
            offset = int(elapsed * 30)
            for y in range(device.height):
                for x in range(device.width):
                    hue = (x * 8 + y * 4 + offset) % 360
                    # Simple color mapping
                    if hue < 60:
                        color = 0xFF0000  # Red
                    elif hue < 120:
                        color = 0xFFFF00  # Yellow
                    elif hue < 180:
                        color = 0x00FF00  # Green
                    elif hue < 240:
                        color = 0x00FFFF  # Cyan
                    elif hue < 300:
                        color = 0x0000FF  # Blue
                    else:
                        color = 0xFF00FF  # Magenta
                    device.matrix.set_pixel(x, y, color)
                    
        elif demo_stage == 3:
            # Stage 4: Scrolling "Thanks for watching!" text
            scroll_text = "THANKS FOR WATCHING!"
            x_offset = int(device.width - (elapsed - 24) * 12) % (len(scroll_text) * 4 + device.width)
            
            for i, char in enumerate(scroll_text):
                char_x = x_offset + i * 4
                if 0 <= char_x < device.width:
                    device.matrix.set_pixel(char_x, 16, 0x00FFFF)  # Cyan
                    device.matrix.set_pixel(char_x, 17, 0x00FFFF)
        
        # Advance stages
        stage_duration = [5, 8, 8, 5][demo_stage]
        if elapsed >= stage_duration:
            demo_stage = (demo_stage + 1) % 4
            stage_start = current_time
            if demo_stage == 1:  # Reset ball position for bouncing stage
                ball_x, ball_y = 10.0, 10.0
                ball_vx, ball_vy = 15.0, 12.0
        
        return True
    
    # Use device.run() 
    device.run(update_callback=update, title="SLDK Animation Demo")


def main():
    """Main entry point."""
    simple_animation_demo()


if __name__ == "__main__":
    main()