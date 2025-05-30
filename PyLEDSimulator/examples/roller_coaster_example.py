#!/usr/bin/env python3
"""
Roller coaster animation example for PyLEDSimulator
This example shows how to use the sprite-based roller coaster animation
"""
import asyncio
import sys
import os

# Add project root to path for importing
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, project_root)

from src.ui.display_factory import create_display
from src.config.settings_manager import SettingsManager
from src.ui.roller_coaster_animation import show_roller_coaster_animation


async def main():
    """
    Run the roller coaster animation demo
    
    This demonstrates:
    - Sprite-based cart animation (1/3 display height)
    - Physics-based speed changes (slower uphill, faster downhill)
    - Smooth track following with interpolation
    - Optimized for CircuitPython sprite performance
    """
    print("Roller Coaster Animation Demo")
    print("=" * 40)
    print("Features:")
    print("- Cart size: ~1/3 of display height")
    print("- Sprite-based for CircuitPython optimization")
    print("- Physics-based speed variation")
    print("- Smooth track interpolation")
    print("- Press ESC or close window to exit early")
    print("=" * 40)
    
    # Create settings manager
    settings_manager = SettingsManager("settings.json")
    
    # Create display (will auto-detect simulator vs hardware)
    display = create_display({'settings_manager': settings_manager})
    
    # Initialize display
    if hasattr(display, 'initialize'):
        if not display.initialize():
            print("Failed to initialize display")
            return
    
    # Start display async loop for simulator
    if hasattr(display, 'run_async'):
        display_task = asyncio.create_task(display.run_async())
    
    try:
        # Run animation for 15 seconds
        print("Starting animation...")
        await show_roller_coaster_animation(display, duration=15)
        print("Animation complete!")
        
    except KeyboardInterrupt:
        print("\nAnimation interrupted by user")
    except Exception as e:
        print(f"Error running animation: {e}")
        import traceback
        traceback.print_exc()
    
    # Cleanup
    if hasattr(display, 'running'):
        display.running = False
    
    print("Demo finished!")


if __name__ == "__main__":
    asyncio.run(main())