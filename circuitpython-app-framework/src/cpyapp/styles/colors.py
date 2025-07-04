"""
Color schemes and palettes for display styles.

This module provides pre-defined color palettes and schemes
for various visual themes and accessibility options.

Copyright 2024 3DUPFitters LLC
"""
from ..utils.colors import ColorUtils


class ColorScheme:
    """Base class for color schemes."""
    
    def __init__(self, name, colors):
        """
        Initialize a color scheme.
        
        Args:
            name: Scheme name
            colors: Dictionary of color roles and values
        """
        self.name = name
        self.colors = colors
        
    def get_color(self, role, default=None):
        """
        Get a color by its role.
        
        Args:
            role: Color role (e.g., 'primary', 'text', 'background')
            default: Default color if role not found
            
        Returns:
            Color value as hex string
        """
        return self.colors.get(role, default or ColorUtils.colors["White"])
        
    def to_style_dict(self):
        """
        Convert scheme to style properties dictionary.
        
        Returns:
            Dictionary with style color properties
        """
        style_dict = {}
        
        # Map common roles to style properties
        role_mapping = {
            'text': 'text_color',
            'background': 'background_color',
            'primary': 'text_color',
            'secondary': 'secondary_color',
            'accent': 'accent_color',
            'success': 'success_color',
            'warning': 'warning_color',
            'error': 'error_color',
            'info': 'info_color',
        }
        
        for role, value in self.colors.items():
            if role in role_mapping:
                style_dict[role_mapping[role]] = value
                
        return style_dict


# Pre-defined color schemes
class NeonScheme(ColorScheme):
    """Bright neon colors on black."""
    
    def __init__(self):
        super().__init__("neon", {
            'text': ColorUtils.colors["Pink"],
            'background': ColorUtils.colors["Black"],
            'primary': ColorUtils.colors["Pink"],
            'secondary': ColorUtils.colors["Blue"],
            'accent': ColorUtils.colors["Yellow"],
            'success': ColorUtils.colors["Green"],
            'warning': ColorUtils.colors["Orange"],
            'error': ColorUtils.colors["Red"],
        })


class PastelScheme(ColorScheme):
    """Soft pastel colors."""
    
    def __init__(self):
        super().__init__("pastel", {
            'text': "0xFFB6C1",  # Light Pink
            'background': "0x1C1C1C",  # Dark Gray
            'primary': "0xFFB6C1",  # Light Pink
            'secondary': "0xADD8E6",  # Light Blue
            'accent': "0xFFFFB6",  # Light Yellow
            'success': "0x90EE90",  # Light Green
            'warning': "0xFFDAB9",  # Peach
            'error': "0xFF6B6B",  # Light Red
        })


class HighContrastScheme(ColorScheme):
    """Maximum contrast for visibility."""
    
    def __init__(self):
        super().__init__("high_contrast", {
            'text': ColorUtils.colors["White"],
            'background': ColorUtils.colors["Black"],
            'primary': ColorUtils.colors["White"],
            'secondary': ColorUtils.colors["Yellow"],
            'accent': ColorUtils.colors["Green"],
            'success': ColorUtils.colors["Green"],
            'warning': ColorUtils.colors["Yellow"],
            'error': ColorUtils.colors["Red"],
        })


class DarkModeScheme(ColorScheme):
    """Dark mode with muted colors."""
    
    def __init__(self):
        super().__init__("dark_mode", {
            'text': "0xE0E0E0",  # Light Gray
            'background': ColorUtils.colors["Black"],
            'primary': "0xE0E0E0",
            'secondary': "0x808080",  # Medium Gray
            'accent': "0x4A90E2",  # Muted Blue
            'success': "0x4CAF50",  # Muted Green
            'warning': "0xFFA726",  # Muted Orange
            'error': "0xEF5350",  # Muted Red
        })


class RetroTerminalScheme(ColorScheme):
    """Classic green terminal look."""
    
    def __init__(self):
        super().__init__("retro_terminal", {
            'text': ColorUtils.colors["Green"],
            'background': ColorUtils.colors["Black"],
            'primary': ColorUtils.colors["Green"],
            'secondary': "0x00AA00",  # Darker Green
            'accent': "0x00FF00",  # Bright Green
            'success': ColorUtils.colors["Green"],
            'warning': ColorUtils.colors["Yellow"],
            'error': ColorUtils.colors["Red"],
        })


class OceanScheme(ColorScheme):
    """Ocean-inspired blues and greens."""
    
    def __init__(self):
        super().__init__("ocean", {
            'text': "0x00CED1",  # Dark Turquoise
            'background': "0x001F3F",  # Navy
            'primary': "0x00CED1",
            'secondary': "0x20B2AA",  # Light Sea Green
            'accent': "0x40E0D0",  # Turquoise
            'success': "0x3CB371",  # Medium Sea Green
            'warning': "0xFFD700",  # Gold
            'error': "0xFF6347",  # Tomato
        })


class SunsetScheme(ColorScheme):
    """Warm sunset colors."""
    
    def __init__(self):
        super().__init__("sunset", {
            'text': ColorUtils.colors["Orange"],
            'background': "0x1A0033",  # Deep Purple
            'primary': ColorUtils.colors["Orange"],
            'secondary': "0xFF6B6B",  # Coral
            'accent': ColorUtils.colors["Yellow"],
            'success': "0x98D8C8",  # Mint
            'warning': ColorUtils.colors["Yellow"],
            'error': ColorUtils.colors["Red"],
        })


class ForestScheme(ColorScheme):
    """Natural forest greens and browns."""
    
    def __init__(self):
        super().__init__("forest", {
            'text': "0x90EE90",  # Light Green
            'background': "0x0F2F0F",  # Dark Forest Green
            'primary': "0x228B22",  # Forest Green
            'secondary': "0x8B4513",  # Saddle Brown
            'accent': "0xFFFF00",  # Yellow
            'success': ColorUtils.colors["Green"],
            'warning': ColorUtils.colors["Orange"],
            'error': "0x8B0000",  # Dark Red
        })


class CyberpunkScheme(ColorScheme):
    """Cyberpunk aesthetic with pink and cyan."""
    
    def __init__(self):
        super().__init__("cyberpunk", {
            'text': "0x00FFFF",  # Cyan
            'background': ColorUtils.colors["Black"],
            'primary': "0x00FFFF",  # Cyan
            'secondary': "0xFF1493",  # Deep Pink
            'accent': "0xFFFF00",  # Yellow
            'success': "0x00FF00",  # Lime
            'warning': "0xFFA500",  # Orange
            'error': "0xFF0080",  # Magenta
        })


class MonochromeScheme(ColorScheme):
    """Black and white only."""
    
    def __init__(self):
        super().__init__("monochrome", {
            'text': ColorUtils.colors["White"],
            'background': ColorUtils.colors["Black"],
            'primary': ColorUtils.colors["White"],
            'secondary': "0x808080",  # Gray
            'accent': ColorUtils.colors["White"],
            'success': ColorUtils.colors["White"],
            'warning': ColorUtils.colors["White"],
            'error': ColorUtils.colors["White"],
        })


class RainbowScheme(ColorScheme):
    """All colors of the rainbow."""
    
    def __init__(self):
        super().__init__("rainbow", {
            'text': 'rainbow',  # Special marker
            'background': ColorUtils.colors["Black"],
            'primary': ColorUtils.colors["Red"],
            'secondary': ColorUtils.colors["Orange"],
            'accent': ColorUtils.colors["Yellow"],
            'success': ColorUtils.colors["Green"],
            'warning': ColorUtils.colors["Blue"],
            'error': ColorUtils.colors["Purple"],
        })


class AccessibilityScheme(ColorScheme):
    """Colors optimized for color blindness."""
    
    def __init__(self):
        super().__init__("accessibility", {
            'text': ColorUtils.colors["White"],
            'background': ColorUtils.colors["Black"],
            'primary': "0x0173B2",  # Blue (distinguishable)
            'secondary': "0xDE8F05",  # Orange (distinguishable)
            'accent': "0x029E73",  # Green (distinguishable)
            'success': "0x029E73",
            'warning': "0xDE8F05",
            'error': "0xCC3311",  # Red (distinguishable)
        })


# Seasonal schemes
class WinterScheme(ColorScheme):
    """Cool winter colors."""
    
    def __init__(self):
        super().__init__("winter", {
            'text': "0xB0E0E6",  # Powder Blue
            'background': "0x191970",  # Midnight Blue
            'primary': ColorUtils.colors["White"],
            'secondary': "0x87CEEB",  # Sky Blue
            'accent': "0xC0C0C0",  # Silver
            'success': "0x98FB98",  # Pale Green
            'warning': "0xFFE4B5",  # Moccasin
            'error': "0xDC143C",  # Crimson
        })


class SpringScheme(ColorScheme):
    """Fresh spring colors."""
    
    def __init__(self):
        super().__init__("spring", {
            'text': "0x98FB98",  # Pale Green
            'background': "0x2F4F2F",  # Dark Slate Gray
            'primary': "0x00FF7F",  # Spring Green
            'secondary': "0xFFB6C1",  # Light Pink
            'accent': ColorUtils.colors["Yellow"],
            'success': ColorUtils.colors["Green"],
            'warning': "0xFFDAB9",  # Peach Puff
            'error': "0xFF69B4",  # Hot Pink
        })


class SummerScheme(ColorScheme):
    """Bright summer colors."""
    
    def __init__(self):
        super().__init__("summer", {
            'text': ColorUtils.colors["Yellow"],
            'background': "0x00008B",  # Dark Blue
            'primary': "0xFFD700",  # Gold
            'secondary': "0xFF8C00",  # Dark Orange
            'accent': "0x00CED1",  # Dark Turquoise
            'success': "0x32CD32",  # Lime Green
            'warning': ColorUtils.colors["Orange"],
            'error': "0xFF4500",  # Orange Red
        })


class AutumnScheme(ColorScheme):
    """Warm autumn colors."""
    
    def __init__(self):
        super().__init__("autumn", {
            'text': "0xD2691E",  # Chocolate
            'background': "0x8B4513",  # Saddle Brown
            'primary': "0xFF8C00",  # Dark Orange
            'secondary': "0xB22222",  # Fire Brick
            'accent': "0xFFD700",  # Gold
            'success': "0x6B8E23",  # Olive Drab
            'warning': ColorUtils.colors["Yellow"],
            'error': "0x8B0000",  # Dark Red
        })


# Dictionary of all schemes
COLOR_SCHEMES = {
    'neon': NeonScheme,
    'pastel': PastelScheme,
    'high_contrast': HighContrastScheme,
    'dark_mode': DarkModeScheme,
    'retro_terminal': RetroTerminalScheme,
    'ocean': OceanScheme,
    'sunset': SunsetScheme,
    'forest': ForestScheme,
    'cyberpunk': CyberpunkScheme,
    'monochrome': MonochromeScheme,
    'rainbow': RainbowScheme,
    'accessibility': AccessibilityScheme,
    'winter': WinterScheme,
    'spring': SpringScheme,
    'summer': SummerScheme,
    'autumn': AutumnScheme,
}


def get_color_scheme(name):
    """
    Get a color scheme by name.
    
    Args:
        name: Scheme name
        
    Returns:
        ColorScheme instance or None
    """
    scheme_class = COLOR_SCHEMES.get(name)
    if scheme_class:
        return scheme_class()
    return None


def list_color_schemes():
    """
    List all available color schemes.
    
    Returns:
        List of scheme names
    """
    return list(COLOR_SCHEMES.keys())


def apply_color_scheme(style, scheme_name):
    """
    Apply a color scheme to a style.
    
    Args:
        style: BaseStyle instance to modify
        scheme_name: Name of color scheme to apply
        
    Returns:
        The modified style
    """
    scheme = get_color_scheme(scheme_name)
    if scheme:
        style.update_properties(scheme.to_style_dict())
    return style