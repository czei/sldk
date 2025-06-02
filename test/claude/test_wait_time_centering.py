#!/usr/bin/env python3
"""
Test script to verify wait time centering calculations
"""

def test_centering_calculation():
    """Test the centering calculation with different wait time lengths"""
    
    # Simulate display width (MatrixPortal S3 is 64 pixels wide)
    display_width = 64
    
    # Simulate character width (terminalio.FONT is typically 6 pixels wide)
    char_width = 6
    
    # Test different wait times
    test_cases = [
        ("5", 1),      # 1 digit
        ("15", 2),     # 2 digits
        ("105", 3),    # 3 digits
        ("120", 3),    # 3 digits
        ("240", 3),    # 3 digits
    ]
    
    print("Testing wait time centering calculations:")
    print(f"Display width: {display_width} pixels")
    print(f"Character width: {char_width} pixels per character")
    print(f"Scale factor: 2 (double size)")
    print("-" * 60)
    
    for wait_time, num_chars in test_cases:
        # Calculate label width (with scale=2)
        base_width = num_chars * char_width
        scaled_width = base_width * 2  # scale=2
        
        # Calculate padding for centering
        padding = int((display_width - scaled_width) / 2)
        padding = max(0, padding)
        
        print(f"Wait time: '{wait_time}' ({num_chars} chars)")
        print(f"  Base width: {base_width} pixels")
        print(f"  Scaled width: {scaled_width} pixels")
        print(f"  Padding (x position): {padding} pixels")
        print(f"  Right edge at: {padding + scaled_width} pixels")
        
        # Check if it fits
        if padding + scaled_width > display_width:
            print(f"  WARNING: Text extends beyond display! ({padding + scaled_width} > {display_width})")
        else:
            print(f"  ✓ Fits within display")
        print()
    
    print("\nNote: The actual bounding box width may vary slightly depending on")
    print("the font metrics, but this gives a good approximation.")

if __name__ == "__main__":
    test_centering_calculation()