"""
Simple Clock Example - A real-world use case for SimpleScrollApp.

This creates a scrolling clock display that shows time and date.
"""
import sys
import os

# Add framework to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cpyapp.apps import SimpleScrollApp
import time


def get_time_and_date():
    """Get current time and date as a formatted string."""
    current_time = time.localtime()
    
    # Format time
    hour = current_time.tm_hour
    minute = current_time.tm_min
    second = current_time.tm_sec
    
    # Format date
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    day_name = days[current_time.tm_wday]
    month_name = months[current_time.tm_mon - 1]
    day = current_time.tm_mday
    
    # Create display string
    time_str = f"{hour:02d}:{minute:02d}:{second:02d}"
    date_str = f"{day_name}, {month_name} {day}"
    
    return f"{time_str} - {date_str}"


def main():
    """Run the clock application."""
    print("Starting Simple Clock Display")
    print("Press Ctrl+C to stop")
    
    # Create clock app with info style (blue text)
    app = SimpleScrollApp(
        data_source=get_time_and_date,
        style="info"
    )
    
    # Update every second
    app.settings_manager.set('update_interval', 1)
    
    # Run the clock
    app.run()


if __name__ == "__main__":
    main()