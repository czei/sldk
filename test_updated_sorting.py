#!/usr/bin/env python3
"""Test the updated sorting logic to ensure it works with existing tests."""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from unittest.mock import MagicMock, AsyncMock
from src.ui.message_queue import MessageQueue
from src.models.theme_park_ride import ThemeParkRide
from src.models.theme_park import ThemePark


def create_test_setup():
    """Create test setup similar to the existing unit tests."""
    # Create mock display
    mock_display = MagicMock()
    mock_display.show_scroll_message = AsyncMock()
    mock_display.show_ride_wait_time = AsyncMock()
    mock_display.show_ride_closed = AsyncMock()
    mock_display.show_ride_name = AsyncMock()
    
    # Create mock settings manager
    mock_settings_manager = MagicMock()
    mock_display.settings_manager = mock_settings_manager
    
    # Create message queue
    message_queue = MessageQueue(mock_display, delay_param=0)
    
    # Create test rides (same as existing tests)
    rides = [
        ThemeParkRide("Space Mountain", 1, 60, True),
        ThemeParkRide("Big Thunder Mountain", 2, 30, True),
        ThemeParkRide("Pirates of the Caribbean", 3, 15, True),
        ThemeParkRide("Haunted Mansion", 4, 45, True),
        ThemeParkRide("Matterhorn", 5, 0, False),  # Closed ride
        ThemeParkRide("Meet Mickey", 6, 20, True),  # Meet & greet
    ]
    
    # Create test park
    park = MagicMock(spec=ThemePark)
    park.id = 1
    park.name = "Test Park"
    park.rides = rides
    park.is_open = True
    
    return message_queue, rides, park


def test_sort_rides_max_wait_fixed():
    """Test sorting by longest wait time first with the fix."""
    message_queue, rides, park = create_test_setup()
    
    rides_with_parks = [(ride, park) for ride in rides]
    sorted_rides = message_queue._sort_rides(rides_with_parks, "max_wait")
    
    # Extract wait times using the NEW logic (open_flag instead of is_open())
    wait_times = [ride[0].wait_time if ride[0].open_flag else 0 for ride in sorted_rides]
    expected_times = [60, 45, 30, 20, 15, 0]  # Descending order
    
    print("Max Wait Test:")
    print(f"Expected: {expected_times}")
    print(f"Actual:   {wait_times}")
    
    assert wait_times == expected_times, f"Max wait sorting failed: got {wait_times}, expected {expected_times}"
    print("✅ Max wait sorting test passed")


def test_sort_rides_min_wait_fixed():
    """Test sorting by shortest wait time first with the fix."""
    message_queue, rides, park = create_test_setup()
    
    rides_with_parks = [(ride, park) for ride in rides]
    sorted_rides = message_queue._sort_rides(rides_with_parks, "min_wait")
    
    # Extract wait times using the NEW logic (open_flag instead of is_open())
    wait_times = [ride[0].wait_time if ride[0].open_flag else 0 for ride in sorted_rides]
    expected_times = [0, 15, 20, 30, 45, 60]  # Ascending order
    
    print("Min Wait Test:")
    print(f"Expected: {expected_times}")
    print(f"Actual:   {wait_times}")
    
    assert wait_times == expected_times, f"Min wait sorting failed: got {wait_times}, expected {expected_times}"
    print("✅ Min wait sorting test passed")


def test_zero_wait_open_rides():
    """Test that open rides with 0-minute waits are sorted correctly."""
    message_queue, _, _ = create_test_setup()
    
    # Create specific test rides including 0-minute wait open rides
    test_rides = [
        ThemeParkRide("High Wait Ride", 1, 60, True),      # 60 min, open
        ThemeParkRide("Zero Wait Ride 1", 2, 0, True),     # 0 min, open (walk-on)
        ThemeParkRide("Medium Wait Ride", 3, 30, True),    # 30 min, open
        ThemeParkRide("Zero Wait Ride 2", 4, 0, True),     # 0 min, open (walk-on)
        ThemeParkRide("Closed Ride", 5, 0, False),         # 0 min, closed
    ]
    
    park = MagicMock()
    park.name = "Test Park"
    
    rides_with_parks = [(ride, park) for ride in test_rides]
    
    # Test max_wait sorting
    sorted_rides = message_queue._sort_rides(rides_with_parks, "max_wait")
    
    # The order should be: High Wait (60), Medium Wait (30), Zero Wait 1 (0), Zero Wait 2 (0), Closed (0)
    # But the zero wait open rides should come before the closed ride
    sorted_names = [ride[0].name for ride in sorted_rides]
    
    print("Zero Wait Rides Test:")
    print("Sorted order:")
    for i, (ride, _) in enumerate(sorted_rides):
        status = "OPEN" if ride.open_flag else "CLOSED"
        print(f"  {i+1}. {ride.name}: {ride.wait_time} min ({status})")
    
    # First should be highest wait time
    assert sorted_rides[0][0].name == "High Wait Ride"
    assert sorted_rides[1][0].name == "Medium Wait Ride"
    
    # Open rides with 0 wait should come before closed rides
    closed_ride_idx = None
    zero_wait_open_indices = []
    
    for i, (ride, _) in enumerate(sorted_rides):
        if ride.name == "Closed Ride":
            closed_ride_idx = i
        elif ride.wait_time == 0 and ride.open_flag:
            zero_wait_open_indices.append(i)
    
    # All open rides with 0 wait should come before the closed ride
    for idx in zero_wait_open_indices:
        assert idx < closed_ride_idx, f"Open ride with 0 wait at index {idx} should come before closed ride at index {closed_ride_idx}"
    
    print("✅ Zero wait open rides are correctly sorted before closed rides")


if __name__ == "__main__":
    print("🧪 Testing Updated Sorting Logic")
    print("=" * 50)
    
    try:
        test_sort_rides_max_wait_fixed()
        test_sort_rides_min_wait_fixed()
        test_zero_wait_open_rides()
        
        print("\n🎉 All tests passed! The sorting fix is working correctly.")
        print("✅ The fix properly handles:")
        print("   - Regular wait time sorting")
        print("   - Open rides with 0-minute waits")
        print("   - Closed rides")
        print("   - Maintains compatibility with existing test expectations")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise