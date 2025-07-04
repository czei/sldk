"""
Display style templates for SimpleScrollApp framework.

This package provides pre-configured styling options for different
types of content and visual effects, making it easy to create
beautiful LED matrix displays.

Copyright 2024 3DUPFitters LLC
"""

# Base style class
from .base import BaseStyle

# Core style templates
from .templates import (
    DefaultStyle, RainbowStyle, AlertStyle, SuccessStyle, InfoStyle,
    FastStyle, SlowStyle, StaticStyle, NeonStyle, RetroStyle,
    ElegantStyle, WarningStyle, PartyStyle, MinimalStyle, HighContrastStyle,
    get_core_style, list_core_styles, CORE_STYLES
)

# Theme-specific styles
from .themes import (
    ThemeParkStyle, StockTickerStyle, WeatherStyle, ClockStyle,
    SportsScoreStyle, NewsTickerStyle, TransitStyle, CountdownStyle,
    CalendarStyle, CryptoTickerStyle,
    get_theme_style, list_theme_styles, THEME_STYLES
)

# Animation styles
from .animations import (
    SmoothScrollStyle, BouncyScrollStyle, TypewriterStyle, MarqueeStyle,
    TickerStyle, CrawlStyle, FadeTransitionStyle, SlideTransitionStyle,
    RevealTransitionStyle, PulseAnimationStyle, RainbowCycleStyle,
    BreathingStyle, SparkleStyle, WaveStyle, MatrixRainStyle,
    get_animation_style, list_animation_styles, ANIMATION_STYLES
)

# Layout management
from .layouts import (
    SingleLineLayout, CenteredLayout, TwoLineLayout, SplitScreenLayout,
    TickerLayout, HeaderFooterLayout, GridLayout, VerticalScrollLayout,
    SideBySideLayout, FullScreenLayout, CompactLayout, PaddedLayout,
    ResponsiveLayout, LayoutCalculator,
    get_layout_style, list_layout_styles, LAYOUT_STYLES
)

# Style factory
from .factory import (
    StyleFactory, create_style, get_style, list_styles,
    merge_styles, create_composite
)

# Color schemes
from .colors import (
    ColorScheme, NeonScheme, PastelScheme, HighContrastScheme,
    DarkModeScheme, RetroTerminalScheme, OceanScheme, SunsetScheme,
    ForestScheme, CyberpunkScheme, MonochromeScheme, RainbowScheme,
    AccessibilityScheme, WinterScheme, SpringScheme, SummerScheme,
    AutumnScheme, get_color_scheme, list_color_schemes, apply_color_scheme,
    COLOR_SCHEMES
)

# Convenience function to get any style by name
def get_style_by_name(name):
    """
    Get any style by name, searching all categories.
    
    Args:
        name: Style name
        
    Returns:
        Style instance or default style
    """
    return get_style(name)


# List all available styles across all categories
def list_all_styles():
    """
    List all available styles across all categories.
    
    Returns:
        Dictionary with categories and their styles
    """
    return list_styles()


# Create a style from simple parameters
def quick_style(color=None, speed=None, effect=None, layout=None):
    """
    Create a quick style from simple parameters.
    
    Args:
        color: Color name or hex value for text
        speed: 'fast', 'normal', 'slow', or float value
        effect: Effect name like 'pulse', 'rainbow', 'breathe'
        layout: Layout name like 'centered', 'two_line'
        
    Returns:
        A configured style instance
        
    Example:
        style = quick_style(color='red', speed='fast', effect='pulse')
    """
    # Start with default
    style = create_style('default')
    
    # Apply color
    if color:
        if color.lower() in ['red', 'green', 'blue', 'yellow', 'white', 'pink', 'orange', 'purple']:
            from ..utils.colors import ColorUtils
            style.set_property('text_color', ColorUtils.colors.get(color.title(), ColorUtils.colors["White"]))
        elif color.startswith('0x') or color.startswith('#'):
            style.set_property('text_color', color)
            
    # Apply speed
    if speed:
        if speed == 'fast':
            style.set_property('scroll_speed', 0.03)
        elif speed == 'slow':
            style.set_property('scroll_speed', 0.08)
        elif speed == 'normal':
            style.set_property('scroll_speed', 0.05)
        elif isinstance(speed, (int, float)):
            style.set_property('scroll_speed', speed)
            
    # Apply effect
    if effect:
        if effect == 'pulse':
            style.set_property('pulse_enabled', True)
        elif effect == 'rainbow':
            style.set_property('rainbow_enabled', True)
            style.set_property('text_color', 'rainbow')
        elif effect == 'breathe':
            style.set_property('breathe_enabled', True)
        elif effect == 'sparkle':
            style.set_property('sparkle_enabled', True)
            
    # Apply layout
    if layout:
        layout_style = get_layout_style(layout)
        if layout_style:
            style.merge(layout_style)
            
    return style


__all__ = [
    # Base
    'BaseStyle',
    
    # Factory functions
    'create_style',
    'get_style',
    'get_style_by_name',
    'list_styles',
    'list_all_styles',
    'merge_styles',
    'create_composite',
    'quick_style',
    
    # Core styles
    'DefaultStyle', 'RainbowStyle', 'AlertStyle', 'SuccessStyle', 'InfoStyle',
    'FastStyle', 'SlowStyle', 'StaticStyle', 'NeonStyle', 'RetroStyle',
    'ElegantStyle', 'WarningStyle', 'PartyStyle', 'MinimalStyle', 'HighContrastStyle',
    
    # Theme styles
    'ThemeParkStyle', 'StockTickerStyle', 'WeatherStyle', 'ClockStyle',
    'SportsScoreStyle', 'NewsTickerStyle', 'TransitStyle', 'CountdownStyle',
    'CalendarStyle', 'CryptoTickerStyle',
    
    # Animation styles
    'SmoothScrollStyle', 'BouncyScrollStyle', 'TypewriterStyle', 'MarqueeStyle',
    'TickerStyle', 'CrawlStyle', 'FadeTransitionStyle', 'SlideTransitionStyle',
    'RevealTransitionStyle', 'PulseAnimationStyle', 'RainbowCycleStyle',
    'BreathingStyle', 'SparkleStyle', 'WaveStyle', 'MatrixRainStyle',
    
    # Layout styles
    'SingleLineLayout', 'CenteredLayout', 'TwoLineLayout', 'SplitScreenLayout',
    'TickerLayout', 'HeaderFooterLayout', 'GridLayout', 'VerticalScrollLayout',
    'SideBySideLayout', 'FullScreenLayout', 'CompactLayout', 'PaddedLayout',
    'ResponsiveLayout', 'LayoutCalculator',
    
    # Color schemes
    'ColorScheme', 'get_color_scheme', 'list_color_schemes', 'apply_color_scheme',
    
    # Style factory
    'StyleFactory',
]