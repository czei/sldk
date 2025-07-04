"""
Core style templates for common display patterns.

This module provides pre-configured styles for common use cases
like default scrolling, alerts, success messages, and more.

Copyright 2024 3DUPFitters LLC
"""
from .base import BaseStyle
from ..utils.colors import ColorUtils


class DefaultStyle(BaseStyle):
    """Standard scrolling text with default colors."""
    
    def __init__(self):
        super().__init__("default")
        self.update_properties({
            'text_color': ColorUtils.colors["White"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.05,
            'brightness': 0.5,
        })


class RainbowStyle(BaseStyle):
    """Colorful scrolling with rainbow effects."""
    
    def __init__(self):
        super().__init__("rainbow")
        self.update_properties({
            'text_color': 'rainbow',
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.05,
            'rainbow_enabled': True,
            'color_cycle_enabled': True,
            'color_cycle_speed': 2.0,
            'brightness': 0.7,
        })


class AlertStyle(BaseStyle):
    """Red/urgent styling for important messages."""
    
    def __init__(self):
        super().__init__("alert")
        self.update_properties({
            'text_color': ColorUtils.colors["Red"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.04,  # Slightly faster
            'pulse_enabled': True,
            'pulse_speed': 2.0,
            'brightness': 0.8,
        })


class SuccessStyle(BaseStyle):
    """Green styling for positive messages."""
    
    def __init__(self):
        super().__init__("success")
        self.update_properties({
            'text_color': ColorUtils.colors["Green"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.05,
            'brightness': 0.6,
        })


class InfoStyle(BaseStyle):
    """Blue styling for informational content."""
    
    def __init__(self):
        super().__init__("info")
        self.update_properties({
            'text_color': ColorUtils.colors["Blue"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.05,
            'brightness': 0.6,
        })


class FastStyle(BaseStyle):
    """Fast scrolling speed variation."""
    
    def __init__(self):
        super().__init__("fast")
        self.update_properties({
            'text_color': ColorUtils.colors["White"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.03,
            'scroll_delay': 1,
            'brightness': 0.5,
        })


class SlowStyle(BaseStyle):
    """Slow scrolling speed variation."""
    
    def __init__(self):
        super().__init__("slow")
        self.update_properties({
            'text_color': ColorUtils.colors["White"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.08,
            'scroll_delay': 3,
            'brightness': 0.5,
        })


class StaticStyle(BaseStyle):
    """Non-scrolling display option."""
    
    def __init__(self):
        super().__init__("static")
        self.update_properties({
            'text_color': ColorUtils.colors["White"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0,  # No scrolling
            'static_duration': 5,
            'text_align': 'center',
            'brightness': 0.5,
        })


class NeonStyle(BaseStyle):
    """Bright neon-like appearance."""
    
    def __init__(self):
        super().__init__("neon")
        self.update_properties({
            'text_color': ColorUtils.colors["Pink"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.05,
            'brightness': 1.0,  # Full brightness
            'pulse_enabled': True,
            'pulse_speed': 0.5,
        })


class RetroStyle(BaseStyle):
    """Retro computing terminal style."""
    
    def __init__(self):
        super().__init__("retro")
        self.update_properties({
            'text_color': ColorUtils.colors["Green"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.06,
            'brightness': 0.7,
            'transition_effect': 'typewriter',
        })


class ElegantStyle(BaseStyle):
    """Elegant style with soft colors."""
    
    def __init__(self):
        super().__init__("elegant")
        self.update_properties({
            'text_color': ColorUtils.colors["Old Lace"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.06,
            'brightness': 0.4,
            'transition_effect': 'fade',
            'transition_speed': 0.2,
        })


class WarningStyle(BaseStyle):
    """Orange/yellow warning style."""
    
    def __init__(self):
        super().__init__("warning")
        self.update_properties({
            'text_color': ColorUtils.colors["Orange"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.045,
            'brightness': 0.7,
            'pulse_enabled': True,
            'pulse_speed': 1.0,
        })


class PartyStyle(BaseStyle):
    """Fun party/celebration style."""
    
    def __init__(self):
        super().__init__("party")
        self.update_properties({
            'text_color': 'rainbow',
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.04,
            'rainbow_enabled': True,
            'sparkle_enabled': True,
            'color_cycle_enabled': True,
            'color_cycle_speed': 3.0,
            'brightness': 0.8,
        })


class MinimalStyle(BaseStyle):
    """Minimal, clean style."""
    
    def __init__(self):
        super().__init__("minimal")
        self.update_properties({
            'text_color': ColorUtils.colors["White"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.05,
            'brightness': 0.3,
            'text_align': 'center',
        })


class HighContrastStyle(BaseStyle):
    """High contrast for visibility."""
    
    def __init__(self):
        super().__init__("high_contrast")
        self.update_properties({
            'text_color': ColorUtils.colors["White"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.05,
            'brightness': 1.0,
            'font_scale': 1,
        })


# Dictionary mapping style names to classes
CORE_STYLES = {
    'default': DefaultStyle,
    'rainbow': RainbowStyle,
    'alert': AlertStyle,
    'success': SuccessStyle,
    'info': InfoStyle,
    'fast': FastStyle,
    'slow': SlowStyle,
    'static': StaticStyle,
    'neon': NeonStyle,
    'retro': RetroStyle,
    'elegant': ElegantStyle,
    'warning': WarningStyle,
    'party': PartyStyle,
    'minimal': MinimalStyle,
    'high_contrast': HighContrastStyle,
}


def get_core_style(name):
    """
    Get a core style by name.
    
    Args:
        name: The style name
        
    Returns:
        A style instance or None if not found
    """
    style_class = CORE_STYLES.get(name)
    if style_class:
        return style_class()
    return None


def list_core_styles():
    """
    List all available core styles.
    
    Returns:
        List of style names
    """
    return list(CORE_STYLES.keys())