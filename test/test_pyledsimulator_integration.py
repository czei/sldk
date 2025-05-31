#!/usr/bin/env python3
"""
Test script to verify PyLEDSimulator integration with Theme Park Waits app
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_pyledsimulator():
    """Test the PyLEDSimulator display integration"""
    print("Testing PyLEDSimulator integration...")
    
    # Import the display factory
    from src.ui.display_factory import create_display
    from src.config.settings_manager import SettingsManager
    
    # Create a settings manager
    settings_manager = SettingsManager("settings.json")
    
    # Create display with PyLEDSimulator
    config = {'settings_manager': settings_manager}
    display = create_display(config)
    
    print(f"Created display: {type(display).__name__}")
    
    # Initialize the display
    if display.initialize():
        print("Display initialized successfully!")
        
        # Test basic display functions
        print("\nTesting splash screen...")
        await display.show_splash(duration=3)
        
        print("\nTesting ride name display...")
        await display.show_ride_name("Space Mountain")
        await asyncio.sleep(2)
        
        print("\nTesting wait time display...")
        await display.show_ride_wait_time("45")
        await asyncio.sleep(2)
        
        print("\nTesting 3-digit wait time...")
        await display.show_ride_wait_time("120")
        await asyncio.sleep(2)
        
        print("\nTesting closed ride...")
        await display.show_ride_closed("Closed")
        await asyncio.sleep(2)
        
        print("\nTesting scrolling message...")
        await display.show_scroll_message("Welcome to Theme Park Waits!")
        
        print("\nAll tests completed!")
        
    else:
        print("Failed to initialize display")
        
    # Keep the window open for a bit
    print("\nKeeping display open for 5 seconds...")
    await asyncio.sleep(5)

if __name__ == "__main__":
    # Set dev mode flag
    if '--dev' not in sys.argv:
        sys.argv.append('--dev')
    
    # Run the test
    asyncio.run(test_pyledsimulator())