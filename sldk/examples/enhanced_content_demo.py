#!/usr/bin/env python3
"""Enhanced content demo - shows text with visual effects.

This demonstrates how content and effects work together.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sldk.display import UnifiedDisplay
from sldk.display.enhanced_content import (
    SparklingText, GlowingText, AnimatedBackground, RainbowText
)


async def create_display_with_window(title="SLDK Enhanced Content Demo"):
    """Create display and window for simulator.
    
    Args:
        title: The window title to display
        
    Returns:
        UnifiedDisplay instance with window created
    """
    display = UnifiedDisplay()
    await display.initialize()
    
    # Create window for simulator
    if hasattr(display, 'create_window'):
        await display.create_window(title)
    
    return display


async def demo_sparkling_text():
    """Demo: Text with sparkle effects."""
    print("\\n=== Sparkling Text Demo ===")
    print("HELLO text with sparkles")
    
    display = await create_display_with_window("SLDK Enhanced Content - Sparkling Text")
    
    # Create sparkling text
    content = SparklingText(
        text="HELLO",
        color=0x00FF00,  # Green text
        sparkle_color=0xFFFFFF,  # White sparkles
        sparkle_intensity=3
    )
    
    await content.start()
    
    # Run for 8 seconds
    for frame in range(80):  # 10 FPS * 8 seconds
        print(f"\\rFrame {frame + 1}/80", end="")
        
        await display.clear()
        await content.render(display)
        await display.show()
        await asyncio.sleep(0.1)
    
    print("\\nSparkling text demo complete!")
    await display.clear()
    await display.show()


async def demo_glowing_text():
    """Demo: Text with edge glow."""
    print("\\n=== Glowing Text Demo ===")
    print("Text with pulsing edge glow")
    
    display = await create_display_with_window("SLDK Enhanced Content - Glowing Text")
    
    # Create glowing text
    content = GlowingText(
        text="GLOW",
        text_color=0xFFFF00,  # Yellow text
        glow_color=0x00FFFF   # Cyan glow
    )
    
    await content.start()
    
    # Run for 8 seconds
    for frame in range(80):  # 10 FPS * 8 seconds
        print(f"\\rFrame {frame + 1}/80", end="")
        
        await display.clear()
        await content.render(display)
        await display.show()
        await asyncio.sleep(0.1)
    
    print("\\nGlowing text demo complete!")
    await display.clear()
    await display.show()


async def demo_animated_background():
    """Demo: Animated particle background."""
    print("\\n=== Animated Background Demo ===")
    print("Background with particle effects")
    
    display = await create_display_with_window("SLDK Enhanced Content - Animated Background")
    
    # Test different particle types
    particle_types = ["sparkle", "rain", "snow"]
    
    for particle_type in particle_types:
        print(f"\\nParticle type: {particle_type}")
        
        background_colors = {
            "sparkle": 0x000033,  # Dark blue
            "rain": 0x001144,     # Storm blue
            "snow": 0x333344      # Gray sky
        }
        
        content = AnimatedBackground(
            background_color=background_colors[particle_type],
            particle_type=particle_type,
            particle_intensity=2
        )
        
        await content.start()
        
        # Run for 6 seconds per type
        for frame in range(60):  # 10 FPS * 6 seconds
            print(f"\\rFrame {frame + 1}/60", end="")
            
            await display.clear()
            await content.render(display)
            await display.show()
            await asyncio.sleep(0.1)
        
        content.clear_effects()
    
    print("\\nAnimated background demo complete!")
    await display.clear()
    await display.show()


async def demo_rainbow_text():
    """Demo: Rainbow color cycling text."""
    print("\\n=== Rainbow Text Demo ===")
    print("Text that cycles through rainbow colors")
    
    display = await create_display_with_window("SLDK Enhanced Content - Rainbow Text")
    
    # Create rainbow text
    content = RainbowText(
        text="RAINBOW",
        cycle_speed=2.0  # 2x speed
    )
    
    await content.start()
    
    # Run for 8 seconds
    for frame in range(80):  # 10 FPS * 8 seconds
        print(f"\\rFrame {frame + 1}/80", end="")
        
        await display.clear()
        await content.render(display)
        await display.show()
        await asyncio.sleep(0.1)
    
    print("\\nRainbow text demo complete!")
    await display.clear()
    await display.show()


async def demo_performance_test():
    """Demo: Performance test with multiple effects."""
    print("\\n=== Performance Test ===")
    print("Multiple effects running simultaneously")
    
    display = await create_display_with_window("SLDK Enhanced Content - Performance Test")
    
    # Create multiple content types
    contents = [
        SparklingText("TEST", color=0xFF0000, sparkle_intensity=2),
        AnimatedBackground(background_color=0x000011, particle_type="sparkle", particle_intensity=1)
    ]
    
    for content in contents:
        await content.start()
    
    import time
    start_time = time.time()
    frame_count = 0
    
    # Run for 5 seconds while measuring performance
    while time.time() - start_time < 5.0:
        frame_start = time.time()
        
        await display.clear()
        
        # Render all content
        for content in contents:
            await content.render(display)
        
        await display.show()
        
        frame_time = time.time() - frame_start
        frame_count += 1
        
        print(f"\\rFrame {frame_count}, Frame time: {frame_time*1000:.1f}ms", end="")
        
        await asyncio.sleep(0.1)  # Target 10 FPS
    
    # Calculate performance stats
    total_time = time.time() - start_time
    avg_fps = frame_count / total_time
    
    print(f"\\nPerformance test complete!")
    print(f"Average FPS: {avg_fps:.1f}")
    print(f"Total frames: {frame_count}")
    print(f"Duration: {total_time:.1f}s")
    
    # Cleanup
    for content in contents:
        content.clear_effects()
    
    await display.clear()
    await display.show()


async def run_simple_demo_using_device():
    """Run a simple demo using the same pattern as animation_demo_simple.py."""
    print("SLDK Enhanced Content Demo")
    print("=" * 40)
    print("Simple text demo using direct device approach")
    print("Press ESC or close window to exit")
    print()
    
    # Import device directly like animation_demo_simple.py does
    from sldk.simulator.devices import MatrixPortalS3
    
    # Create device
    device = MatrixPortalS3()
    device.initialize()
    
    def update():
        """Update function called each frame."""
        # Clear to black
        device.matrix.fill(0x000000)
        
        # Draw simple text pattern "HELLO"
        # H
        for y in range(5, 15):
            device.matrix.set_pixel(5, y, 0xFF0000)   # Left bar
            device.matrix.set_pixel(10, y, 0xFF0000)  # Right bar
        device.matrix.set_pixel(7, 10, 0xFF0000)     # Middle bar
        device.matrix.set_pixel(8, 10, 0xFF0000)     # Middle bar
        
        # E  
        for y in range(5, 15):
            device.matrix.set_pixel(15, y, 0x00FF00)  # Left bar
        for x in range(15, 20):
            device.matrix.set_pixel(x, 5, 0x00FF00)   # Top bar
            device.matrix.set_pixel(x, 10, 0x00FF00)  # Middle bar
            device.matrix.set_pixel(x, 14, 0x00FF00)  # Bottom bar
        
        # L
        for y in range(5, 15):
            device.matrix.set_pixel(25, y, 0x0000FF)  # Left bar
        for x in range(25, 30):
            device.matrix.set_pixel(x, 14, 0x0000FF)  # Bottom bar
        
        # L
        for y in range(5, 15):
            device.matrix.set_pixel(35, y, 0xFFFF00)  # Left bar
        for x in range(35, 40):
            device.matrix.set_pixel(x, 14, 0xFFFF00)  # Bottom bar
        
        # O
        for y in range(6, 14):
            device.matrix.set_pixel(45, y, 0xFF00FF)  # Left bar
            device.matrix.set_pixel(50, y, 0xFF00FF)  # Right bar
        for x in range(46, 50):
            device.matrix.set_pixel(x, 5, 0xFF00FF)   # Top bar
            device.matrix.set_pixel(x, 14, 0xFF00FF)  # Bottom bar
        
        return True
    
    # Use device.run() like animation_demo_simple.py
    device.run(update_callback=update, title="SLDK Enhanced Content Demo")


def main():
    """Main entry point."""
    import asyncio
    asyncio.run(run_simple_demo_using_device())


if __name__ == "__main__":
    main()