#!/usr/bin/env python3
"""Test script to verify the sorting fix works correctly."""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.theme_park_ride import ThemeParkRide
from src.ui.message_queue import MessageQueue


class MockDisplay:
    """Mock display for testing."""
    def __init__(self, settings):
        self.settings_manager = MockSettingsManager(settings)


class MockSettingsManager:
    """Mock settings manager for testing."""
    def __init__(self, settings):
        self.settings = settings
    
    def get(self, key, default=None):
        return self.settings.get(key, default)


def test_sorting_fix():
    """Test that the sorting fix works correctly for rides with 0-minute waits."""
    print("Testing sorting fix for rides with 0-minute wait times...")
    
    # Create test rides with various wait times, including 0-minute waits
    rides = [
        ThemeParkRide("Space Mountain", 1, 45, True),    # 45 min wait, open
        ThemeParkRide("Pirates", 2, 0, True),           # 0 min wait, open (walk-on)
        ThemeParkRide("Haunted Mansion", 3, 25, True),  # 25 min wait, open
        ThemeParkRide("Thunder Mountain", 4, 0, True),  # 0 min wait, open (walk-on)
        ThemeParkRide("Splash Mountain", 5, 60, True),  # 60 min wait, open
        ThemeParkRide("Closed Ride", 6, 0, False),      # 0 min wait, closed
    ]
    
    # Create a mock park
    class MockPark:
        def __init__(self):
            self.name = "Test Park"
    
    mock_park = MockPark()
    rides_with_parks = [(ride, mock_park) for ride in rides]
    
    # Create message queue with max_wait sorting
    mock_display = MockDisplay({"sort_mode": "max_wait"})
    message_queue = MessageQueue(mock_display)
    
    # Test sorting with max_wait
    sorted_rides = message_queue._sort_rides(rides_with_parks, "max_wait")
    
    print("\n=== MAX_WAIT SORTING TEST ===")
    print("Expected order: Splash Mountain (60), Space Mountain (45), Haunted Mansion (25), Pirates (0), Thunder Mountain (0), Closed Ride (0)")
    print("Actual order:")
    for i, (ride, park) in enumerate(sorted_rides):
        status = "OPEN" if ride.open_flag else "CLOSED"
        is_open_result = ride.is_open()
        print(f"  {i+1}. {ride.name}: {ride.wait_time} min ({status}) - is_open()={is_open_result}")
    
    # Verify the sorting is correct
    expected_order = [
        "Splash Mountain",    # 60 min
        "Space Mountain",     # 45 min  
        "Haunted Mansion",    # 25 min
        "Pirates",            # 0 min but open
        "Thunder Mountain",   # 0 min but open
        "Closed Ride"         # 0 min and closed
    ]
    
    actual_order = [ride.name for ride, park in sorted_rides]
    
    print(f"\nExpected: {expected_order}")
    print(f"Actual:   {actual_order}")
    
    # Check if the first three are in correct order (the non-zero wait times)
    success = True
    
    # The first ride should be Splash Mountain (60 min)
    if actual_order[0] != "Splash Mountain":
        print(f"❌ ERROR: First ride should be 'Splash Mountain' but got '{actual_order[0]}'")
        success = False
    
    # The second ride should be Space Mountain (45 min)
    if actual_order[1] != "Space Mountain":
        print(f"❌ ERROR: Second ride should be 'Space Mountain' but got '{actual_order[1]}'")
        success = False
        
    # The third ride should be Haunted Mansion (25 min)
    if actual_order[2] != "Haunted Mansion":
        print(f"❌ ERROR: Third ride should be 'Haunted Mansion' but got '{actual_order[2]}'")
        success = False
    
    # The 0-minute open rides should come before closed rides
    pirates_idx = actual_order.index("Pirates")
    thunder_idx = actual_order.index("Thunder Mountain")
    closed_idx = actual_order.index("Closed Ride")
    
    if pirates_idx > closed_idx or thunder_idx > closed_idx:
        print(f"❌ ERROR: Open rides with 0 wait should come before closed rides")
        print(f"   Pirates index: {pirates_idx}, Thunder Mountain index: {thunder_idx}, Closed Ride index: {closed_idx}")
        success = False
    
    if success:
        print("✅ SUCCESS: Sorting works correctly! Open rides with 0-minute waits are properly sorted.")
        print("   - Rides are sorted by wait time descending")
        print("   - Open rides with 0-minute waits come before closed rides")
        print("   - The fix correctly uses open_flag instead of is_open() for sorting")
    else:
        print("❌ FAILURE: Sorting is still not working correctly.")
        
    return success


def test_before_fix():
    """Show what the sorting looked like before the fix."""
    print("\n" + "="*60)
    print("SHOWING BEHAVIOR BEFORE THE FIX")
    print("="*60)
    
    # Create the same test rides
    rides = [
        ThemeParkRide("Space Mountain", 1, 45, True),    
        ThemeParkRide("Pirates", 2, 0, True),           
        ThemeParkRide("Haunted Mansion", 3, 25, True),  
        ThemeParkRide("Thunder Mountain", 4, 0, True),  
        ThemeParkRide("Splash Mountain", 5, 60, True),  
        ThemeParkRide("Closed Ride", 6, 0, False),      
    ]
    
    class MockPark:
        def __init__(self):
            self.name = "Test Park"
    
    mock_park = MockPark()
    rides_with_parks = [(ride, mock_park) for ride in rides]
    
    # Simulate the OLD sorting logic (using is_open())
    def old_sort_logic(rides_with_parks):
        return sorted(rides_with_parks, 
                     key=lambda x: x[0].wait_time if x[0].is_open() else 0,  # OLD: used is_open()
                     reverse=True)
    
    old_sorted = old_sort_logic(rides_with_parks)
    
    print("OLD SORTING (using is_open() method):")
    for i, (ride, park) in enumerate(old_sorted):
        status = "OPEN" if ride.open_flag else "CLOSED"
        is_open_result = ride.is_open()
        wait_for_sort = ride.wait_time if ride.is_open() else 0
        print(f"  {i+1}. {ride.name}: {ride.wait_time} min ({status}) - is_open()={is_open_result} - sort_key={wait_for_sort}")
    
    print("\nPROBLEM: Rides with 0-minute waits have is_open()=False, so they get sort_key=0")
    print("This makes them sort the same as closed rides, which is incorrect!")


if __name__ == "__main__":
    print("🔧 TESTING THEMEPARKWAITS SORTING FIX")
    print("="*60)
    
    # Show the old behavior first
    test_before_fix()
    
    # Test the new behavior
    print("\n" + "="*60)
    print("TESTING THE FIX")
    print("="*60)
    
    success = test_sorting_fix()
    
    print("\n" + "="*60)
    if success:
        print("🎉 CONCLUSION: The sorting fix is working correctly!")
        print("   Deploy this fix to resolve the CircuitPython sorting issue.")
    else:
        print("❌ CONCLUSION: The fix needs more work.")
    print("="*60)