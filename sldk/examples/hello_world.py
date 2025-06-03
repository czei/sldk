#!/usr/bin/env python3
"""Hello World example for SLDK.

Demonstrates basic text display and scrolling.
"""

import sys
import os

# Add parent directory to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import asyncio
except ImportError:
    # CircuitPython
    import asyncio

from sldk.app import SLDKApp
from sldk.display import ScrollingText, StaticText


class HelloWorldApp(SLDKApp):
    """Simple Hello World application showcasing SLDK's built-in features."""
    
    def __init__(self):
        # Disable web server for this simple example
        super().__init__(enable_web=False, update_interval=10)
    
    async def create_display(self):
        """Create display instance that actually shows a window."""
        try:
            # Use SimulatorDisplay which we know creates a visible window
            from sldk.display.simulator import SimulatorDisplay
            display = SimulatorDisplay(width=64, height=32)
            
            # Create window explicitly
            await display.create_window("SLDK Hello World Demo")
            
            return display
        except ImportError:
            # Fallback to unified display
            return await super().create_display()
        
    async def setup(self):
        """Initialize the application with automatic text rendering and scrolling."""
        print("Setting up Hello World demo...")
        print("✓ Using SLDK's built-in StaticText for font rendering")
        print("✓ Using SLDK's built-in ScrollingText for automatic scrolling")
        
        # Repeat the demo several times for better visibility
        for cycle in range(5):  # Repeat 5 times
            print(f"Adding demo cycle {cycle + 1}/5")
            
            # Show static "Hello" text using SLDK's font rendering
            self.content_queue.add(StaticText(
                f"Hello {cycle + 1}", 
                x=15, y=12,
                color=0xFF0000,  # Red
                duration=4  # Longer duration
            ))
            
            # Show static "World!" text using SLDK's font rendering
            self.content_queue.add(StaticText(
                f"World! {cycle + 1}",
                x=10, y=12,
                color=0x00FF00,  # Green
                duration=4  # Longer duration
            ))
            
            # Add some colorful static text variations
            colors = [0xFF0080, 0x8000FF, 0x00FF80, 0xFF8000, 0x80FF00]
            self.content_queue.add(StaticText(
                f"SLDK!",
                x=18, y=12,
                color=colors[cycle],
                duration=3
            ))
        
        # Demonstrate SLDK's automatic scrolling - no manual pixel manipulation needed!
        for i in range(3):  # Multiple scrolling messages
            self.content_queue.add(ScrollingText(
                f"Welcome to SLDK - Scrolling LED Dev Kit! This is message {i+1} scrolling automatically using the built-in ScrollingText class.",
                y=12,
                color=0x0080FF,  # Blue
                speed=0.025  # Slightly faster scrolling
            ))
            
        # Add a final long-duration message to keep window open
        self.content_queue.add(StaticText(
            "Demo Complete",
            x=5, y=12,
            color=0xFFFFFF,  # White
            duration=10  # Keep visible for 10 seconds
        ))
        
    async def update_data(self):
        """Update data periodically."""
        # Keep adding content to prevent the app from exiting
        import time
        
        # Add a new message every 30 seconds to keep the demo running
        colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0xFF00FF, 0x00FFFF]
        color = colors[int(time.time()) % len(colors)]
        
        self.content_queue.add(StaticText(
            f"Time: {int(time.time()) % 100}",
            x=10, y=20,
            color=color,
            duration=5
        ))


def _fallback_demo():
    """Fallback demo for CircuitPython compatibility."""
    print("CircuitPython fallback demo")
    print("This would use CircuitPython's displayio for text rendering")
    # In a real CircuitPython environment, this would use displayio and bitmap_label
    # For now, just show the concept
    

def simple_hello_world_with_sldk_features():
    """Hello world demo using proper SLDK display interface with real text rendering."""
    print("SLDK Hello World Demo")
    print("=" * 40)
    print("This demo showcases SLDK's built-in features:")
    print("• Real font rendering with StaticText and ScrollingText")
    print("• Automatic text positioning and color")
    print("• Clean API using SLDK content classes!")
    print()
    
    try:
        # Use the proper SLDK App framework to showcase real library usage
        import asyncio
        app = HelloWorldApp()
        asyncio.run(app.run())
    except Exception as e:
        print(f"Error running SLDK app: {e}")
        print("Falling back to basic demo...")
        _fallback_demo()


def main():
    """Main entry point."""
    simple_hello_world_with_sldk_features()


if __name__ == "__main__":
    main()