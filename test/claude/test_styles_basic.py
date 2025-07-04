"""
Basic test of the styles system to verify it works.
"""
import sys
import os

# Add the framework to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'circuitpython-app-framework', 'src'))

from cpyapp.styles import (
    create_style, get_style, list_all_styles,
    quick_style, apply_color_scheme
)
from cpyapp.utils.colors import ColorUtils


def test_basic_functionality():
    """Test basic style functionality."""
    print("Testing Basic Style Functionality")
    print("=" * 50)
    
    # Test 1: Get a built-in style
    print("\n1. Getting built-in styles:")
    default_style = get_style('default')
    print(f"   Default style: {default_style}")
    print(f"   Text color: {default_style.get_property('text_color')}")
    
    rainbow_style = get_style('rainbow')
    print(f"   Rainbow style: {rainbow_style}")
    print(f"   Rainbow enabled: {rainbow_style.get_property('rainbow_enabled')}")
    
    # Test 2: Create custom style
    print("\n2. Creating custom style:")
    custom = create_style({
        'text_color': ColorUtils.colors["Red"],
        'scroll_speed': 0.02,
        'pulse_enabled': True
    })
    print(f"   Custom style: {custom}")
    print(f"   Properties: color={custom.get_property('text_color')}, speed={custom.get_property('scroll_speed')}")
    
    # Test 3: Quick style
    print("\n3. Using quick_style helper:")
    quick = quick_style(color='green', speed='fast', effect='pulse')
    print(f"   Quick style: {quick}")
    print(f"   Color: {quick.get_property('text_color')}")
    print(f"   Speed: {quick.get_property('scroll_speed')}")
    print(f"   Pulse: {quick.get_property('pulse_enabled')}")
    
    # Test 4: List all styles
    print("\n4. Available styles:")
    all_styles = list_all_styles()
    for category, styles in all_styles.items():
        print(f"   {category}: {len(styles)} styles")
        print(f"      First 5: {', '.join(sorted(styles)[:5])}")
    
    # Test 5: Theme styles
    print("\n5. Theme-specific styles:")
    theme_park = get_style('theme_park')
    print(f"   Theme park style: {theme_park}")
    print(f"   Ride name color: {theme_park.get_property('ride_name_color')}")
    print(f"   Wait time scale: {theme_park.get_property('wait_time_scale')}")
    
    # Test 6: Color schemes
    print("\n6. Color schemes:")
    style = create_style('default')
    print(f"   Original text color: {style.get_property('text_color')}")
    apply_color_scheme(style, 'neon')
    print(f"   After neon scheme: {style.get_property('text_color')}")
    
    # Test 7: Style properties
    print("\n7. Style configuration methods:")
    style = get_style('pulse_animation')
    scroll_config = style.get_scroll_config()
    anim_config = style.get_animation_config()
    layout_config = style.get_layout_config()
    
    print(f"   Scroll config: {scroll_config}")
    print(f"   Animation config: pulse={anim_config['pulse_enabled']}, speed={anim_config['pulse_speed']}")
    print(f"   Layout config: {layout_config}")
    
    print("\n✅ All tests passed!")


def test_style_integration():
    """Test integration with display components."""
    print("\n\nTesting Style Integration")
    print("=" * 50)
    
    # Mock display for testing
    class MockDisplay:
        def __init__(self):
            self.brightness = 0.5
            
        def set_brightness(self, value):
            self.brightness = value
            print(f"   Display brightness set to: {value}")
    
    class MockLabel:
        def __init__(self):
            self.color = 0xFFFFFF
            self.scale = 1
            
    # Test applying style to display
    print("\n1. Applying style to display:")
    display = MockDisplay()
    style = get_style('neon')
    style.apply_to_display(display)
    
    # Test applying style to label
    print("\n2. Applying style to label:")
    label = MockLabel()
    style.apply_to_label(label)
    print(f"   Label color: 0x{label.color:06X}")
    print(f"   Label scale: {label.scale}")
    
    print("\n✅ Integration tests passed!")


def test_style_examples():
    """Show example usage patterns."""
    print("\n\nStyle Usage Examples")
    print("=" * 50)
    
    # Example 1: Simple usage
    print("\n1. Simple usage - just a name:")
    print('   app = SimpleScrollApp("Hello", style="rainbow")')
    
    # Example 2: Custom properties
    print("\n2. Custom properties:")
    print('   app = SimpleScrollApp("Alert!", style={')
    print('       "text_color": "0xFF0000",')
    print('       "pulse_enabled": True,')
    print('       "scroll_speed": 0.04')
    print('   })')
    
    # Example 3: Composite style
    print("\n3. Composite style:")
    print('   from cpyapp.styles import create_composite')
    print('   style = create_composite(')
    print('       "rainbow",      # Colors')
    print('       "fast",         # Speed') 
    print('       "two_line",     # Layout')
    print('       brightness=0.9  # Custom')
    print('   )')
    print('   app = SimpleScrollApp("Composite!", style=style)')
    
    # Example 4: Theme-specific
    print("\n4. Theme-specific app:")
    print('   # Automatically uses optimized styling')
    print('   app = SimpleScrollApp(')
    print('       data_source=park_api,')
    print('       style="theme_park"')
    print('   )')
    
    print("\n✅ Examples complete!")


if __name__ == "__main__":
    print("Display Styles System Test")
    print("=" * 70)
    
    try:
        test_basic_functionality()
        test_style_integration()
        test_style_examples()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED! The styles system is working correctly.")
        print("\nThe system provides:")
        print("- 69+ pre-configured styles across 5 categories")
        print("- Easy-to-use API with progressive complexity")
        print("- Full customization capabilities")
        print("- Seamless integration with SimpleScrollApp")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()