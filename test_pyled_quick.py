#!/usr/bin/env python3
"""Quick test of PyLEDSimulator integration"""
import asyncio
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def quick_test():
    """Quick test that exits after showing splash"""
    # Import after adding to path
    from src.ui.display_factory import create_display
    from src.config.settings_manager import SettingsManager
    
    print("Creating display...")
    settings = SettingsManager("settings.json")
    display = create_display({'settings_manager': settings})
    
    if display.initialize():
        print("Display initialized!")
        
        # Start the display loop
        display_task = asyncio.create_task(display.run_async())
        
        # Show splash for 2 seconds
        print("Showing splash...")
        await display.show_splash(duration=2)
        
        # Show a message
        print("Showing message...")
        await display.show_scroll_message("PyLEDSimulator Works!")
        
        print("Test complete!")
        
        # Cancel the display task
        display_task.cancel()
        try:
            await display_task
        except asyncio.CancelledError:
            pass
    else:
        print("Failed to initialize display")

if __name__ == "__main__":
    # Set dev mode
    sys.argv.append('--dev')
    
    # Run the test
    asyncio.run(quick_test())