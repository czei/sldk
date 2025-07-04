"""
Display Styles Demo - Showcases the new styles system.

This demonstrates all the different style categories and how to use them
with the SimpleScrollApp and the display framework.
"""
import sys
import os

# Add framework to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cpyapp.apps import SimpleScrollApp
from cpyapp.styles import (
    create_style, get_style, list_all_styles, merge_styles,
    create_composite, quick_style, apply_color_scheme
)


def demo_core_styles():
    """Demonstrate core style templates."""
    print("\n=== CORE STYLES DEMO ===")
    
    core_styles = [
        'default', 'rainbow', 'alert', 'success', 'info',
        'fast', 'slow', 'static', 'neon', 'retro',
        'elegant', 'warning', 'party', 'minimal', 'high_contrast'
    ]
    
    for style_name in core_styles:
        print(f"\n{style_name.upper()} Style:")
        app = SimpleScrollApp(f"Testing {style_name} style!", style=style_name)
        # app.run()  # Uncomment to see it in action


def demo_theme_styles():
    """Demonstrate theme-specific styles."""
    print("\n=== THEME STYLES DEMO ===")
    
    # Theme park style
    print("\nTheme Park Style:")
    app = SimpleScrollApp("Space Mountain: 45 min", style="theme_park")
    
    # Stock ticker style
    print("\nStock Ticker Style:")
    app = SimpleScrollApp("AAPL: $185.92 (+2.15%)", style="stock_ticker")
    
    # Weather style
    print("\nWeather Style:")
    app = SimpleScrollApp("Orlando: 78°F Sunny", style="weather")
    
    # Clock style
    print("\nClock Style:")
    app = SimpleScrollApp("12:45:30", style="clock")
    
    # News ticker style
    print("\nNews Ticker Style:")
    app = SimpleScrollApp("BREAKING: New LED features released!", style="news_ticker")


def demo_animation_styles():
    """Demonstrate animation styles."""
    print("\n=== ANIMATION STYLES DEMO ===")
    
    animations = [
        'smooth_scroll', 'bouncy_scroll', 'typewriter', 'marquee',
        'ticker', 'crawl', 'fade_transition', 'slide_transition',
        'pulse_animation', 'rainbow_cycle', 'breathing', 'sparkle',
        'wave', 'matrix_rain'
    ]
    
    for anim in animations:
        print(f"\n{anim.upper()} Animation:")
        app = SimpleScrollApp(f"Testing {anim}!", style=anim)


def demo_layout_styles():
    """Demonstrate layout styles."""
    print("\n=== LAYOUT STYLES DEMO ===")
    
    layouts = [
        'single_line', 'centered', 'two_line', 'split_screen',
        'ticker', 'header_footer', 'grid', 'vertical_scroll',
        'side_by_side', 'full_screen', 'compact', 'padded', 'responsive'
    ]
    
    for layout in layouts:
        print(f"\n{layout.upper()} Layout:")
        app = SimpleScrollApp(f"Layout: {layout}", style=layout)


def demo_color_schemes():
    """Demonstrate color schemes."""
    print("\n=== COLOR SCHEMES DEMO ===")
    
    schemes = [
        'neon', 'pastel', 'high_contrast', 'dark_mode', 'retro_terminal',
        'ocean', 'sunset', 'forest', 'cyberpunk', 'monochrome',
        'rainbow', 'accessibility', 'winter', 'spring', 'summer', 'autumn'
    ]
    
    for scheme in schemes:
        print(f"\n{scheme.upper()} Color Scheme:")
        # Create a base style and apply color scheme
        style = create_style('default')
        apply_color_scheme(style, scheme)
        app = SimpleScrollApp(f"Color scheme: {scheme}", style=style)


def demo_custom_styles():
    """Demonstrate custom style creation."""
    print("\n=== CUSTOM STYLES DEMO ===")
    
    # Custom style from dictionary
    print("\nCustom Dictionary Style:")
    custom1 = {
        'text_color': '0xFF00FF',  # Magenta
        'scroll_speed': 0.04,
        'pulse_enabled': True,
        'brightness': 0.8
    }
    app = SimpleScrollApp("Custom magenta pulse!", style=custom1)
    
    # Quick style helper
    print("\nQuick Style Helper:")
    quick = quick_style(color='red', speed='fast', effect='breathe')
    app = SimpleScrollApp("Quick style creation!", style=quick)
    
    # Composite style
    print("\nComposite Style:")
    composite = create_composite(
        'rainbow',      # Base rainbow colors
        'fast',         # Fast scrolling
        'two_line',     # Two line layout
        brightness=0.9  # Custom brightness
    )
    app = SimpleScrollApp("Composite style!", style=composite)
    
    # Merged styles
    print("\nMerged Styles:")
    merged = merge_styles(
        'alert',        # Red color
        'typewriter',   # Typewriter effect
        'centered'      # Centered layout
    )
    app = SimpleScrollApp("ALERT!", style=merged)


def demo_style_combinations():
    """Demonstrate combining different style aspects."""
    print("\n=== STYLE COMBINATIONS DEMO ===")
    
    # Theme park with animations
    print("\nTheme Park + Pulse:")
    style1 = create_composite('theme_park', 'pulse_animation')
    app = SimpleScrollApp("Pirates: 20 min", style=style1)
    
    # Stock ticker with color scheme
    print("\nStock Ticker + Cyberpunk Colors:")
    style2 = create_style('stock_ticker')
    apply_color_scheme(style2, 'cyberpunk')
    app = SimpleScrollApp("BTC: $45,231 (+5.2%)", style=style2)
    
    # Weather with special effects
    print("\nWeather + Breathing Effect:")
    style3 = create_composite('weather', 'breathing', scroll_speed=0.06)
    app = SimpleScrollApp("72°F Partly Cloudy", style=style3)
    
    # Clock with neon colors
    print("\nClock + Neon Style:")
    style4 = create_composite('clock', 'neon')
    app = SimpleScrollApp("15:30", style=style4)


def demo_progressive_usage():
    """Show how styles grow with user expertise."""
    print("\n=== PROGRESSIVE USAGE DEMO ===")
    
    # Beginner - just use a name
    print("\nBeginner - Named style:")
    app1 = SimpleScrollApp("Hello World!", style="rainbow")
    
    # Intermediate - use theme styles
    print("\nIntermediate - Theme style:")
    app2 = SimpleScrollApp("AAPL: $185", style="stock_ticker")
    
    # Advanced - create custom composite
    print("\nAdvanced - Custom composite:")
    my_style = create_composite(
        'elegant',                    # Base elegant style
        'ocean',                      # Ocean color scheme
        'fade_transition',            # Fade transitions
        scroll_speed=0.04,            # Custom speed
        pulse_enabled=True,           # Add pulse
        pulse_speed=0.5               # Slow pulse
    )
    app3 = SimpleScrollApp("Advanced styling!", style=my_style)
    
    # Expert - full control
    print("\nExpert - Full control:")
    from cpyapp.styles.base import BaseStyle
    
    class MyCustomStyle(BaseStyle):
        def __init__(self):
            super().__init__("my_custom")
            self.update_properties({
                'text_color': '0x00FFFF',
                'background_color': '0x000033',
                'scroll_speed': 0.045,
                'rainbow_enabled': False,
                'pulse_enabled': True,
                'pulse_min_brightness': 0.4,
                'pulse_max_brightness': 1.0,
                'pulse_speed': 0.8,
                'transition_effect': 'slide',
                'text_align': 'center',
            })
    
    app4 = SimpleScrollApp("Expert mode!", style=MyCustomStyle())


def list_available_styles():
    """List all available styles."""
    print("\n=== AVAILABLE STYLES ===")
    
    all_styles = list_all_styles()
    
    for category, styles in all_styles.items():
        print(f"\n{category.upper()} ({len(styles)} styles):")
        for style in sorted(styles):
            print(f"  - {style}")


if __name__ == "__main__":
    print("Display Styles Demonstration")
    print("=" * 50)
    
    # List all available styles
    list_available_styles()
    
    # Run all demos
    demo_core_styles()
    demo_theme_styles()
    demo_animation_styles()
    demo_layout_styles()
    demo_color_schemes()
    demo_custom_styles()
    demo_style_combinations()
    demo_progressive_usage()
    
    print("\n\nDemo complete! The styles system provides:")
    print("- 15 core styles (default, rainbow, alert, etc.)")
    print("- 10 theme-specific styles (theme_park, stock_ticker, etc.)")
    print("- 15 animation styles (smooth_scroll, pulse, breathing, etc.)")
    print("- 13 layout styles (centered, two_line, grid, etc.)")
    print("- 16 color schemes (neon, ocean, cyberpunk, seasons, etc.)")
    print("- Style factory for easy creation and merging")
    print("- Progressive API from beginner to expert")
    print("\nUncomment app.run() lines to see styles in action!")