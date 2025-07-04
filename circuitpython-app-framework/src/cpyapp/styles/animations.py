"""
Animation styles for display effects.

This module provides various animation and transition effects
for text display including scrolling variations, color animations,
and text effects.

Copyright 2024 3DUPFitters LLC
"""
import math
import time
from .base import BaseStyle
from ..utils.colors import ColorUtils
from ..utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")


class AnimationMixin:
    """Mixin class providing animation utilities."""
    
    @staticmethod
    def ease_in_out(t):
        """
        Ease in-out interpolation function.
        
        Args:
            t: Time value from 0.0 to 1.0
            
        Returns:
            Interpolated value
        """
        return t * t * (3.0 - 2.0 * t)
    
    @staticmethod
    def bounce(t):
        """
        Bounce interpolation function.
        
        Args:
            t: Time value from 0.0 to 1.0
            
        Returns:
            Interpolated value with bounce
        """
        if t < 0.5:
            return 8 * t * t * t * t
        else:
            t = t - 1
            return 1 + 8 * t * t * t * t
            
    @staticmethod
    def sine_wave(t, frequency=1.0):
        """
        Sine wave function for smooth oscillations.
        
        Args:
            t: Time value
            frequency: Wave frequency
            
        Returns:
            Sine value between -1 and 1
        """
        return math.sin(2 * math.pi * frequency * t)


class SmoothScrollStyle(BaseStyle, AnimationMixin):
    """Smooth scrolling with easing."""
    
    def __init__(self):
        super().__init__("smooth_scroll")
        self.update_properties({
            'text_color': ColorUtils.colors["White"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.04,
            'scroll_easing': True,
            'easing_function': 'ease_in_out',
            'brightness': 0.5,
        })


class BouncyScrollStyle(BaseStyle, AnimationMixin):
    """Bouncy scrolling effect."""
    
    def __init__(self):
        super().__init__("bouncy_scroll")
        self.update_properties({
            'text_color': ColorUtils.colors["Yellow"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.05,
            'scroll_bounce': True,
            'bounce_height': 2,  # pixels
            'bounce_frequency': 2.0,
            'brightness': 0.6,
        })


class TypewriterStyle(BaseStyle):
    """Typewriter effect - reveals text character by character."""
    
    def __init__(self):
        super().__init__("typewriter")
        self.update_properties({
            'text_color': ColorUtils.colors["Green"],
            'background_color': ColorUtils.colors["Black"],
            'typewriter_speed': 0.1,  # seconds per character
            'typewriter_sound': False,  # Could trigger sound if available
            'cursor_visible': True,
            'cursor_blink': True,
            'brightness': 0.7,
        })


class MarqueeStyle(BaseStyle):
    """Classic marquee effect."""
    
    def __init__(self):
        super().__init__("marquee")
        self.update_properties({
            'text_color': ColorUtils.colors["White"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.03,
            'continuous_scroll': True,
            'gap_size': 20,  # pixels between text repeats
            'brightness': 0.5,
        })


class TickerStyle(BaseStyle):
    """News ticker style scrolling."""
    
    def __init__(self):
        super().__init__("ticker")
        self.update_properties({
            'text_color': ColorUtils.colors["White"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.04,
            'continuous_scroll': True,
            'separator': ' • ',
            'gap_size': 10,
            'brightness': 0.6,
        })


class CrawlStyle(BaseStyle):
    """Star Wars style text crawl."""
    
    def __init__(self):
        super().__init__("crawl")
        self.update_properties({
            'text_color': ColorUtils.colors["Yellow"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.08,  # Slower for dramatic effect
            'scroll_direction': 'up',
            'perspective_effect': True,  # If supported
            'fade_top': True,
            'brightness': 0.7,
        })


class FadeTransitionStyle(BaseStyle):
    """Fade in/out transitions."""
    
    def __init__(self):
        super().__init__("fade_transition")
        self.update_properties({
            'text_color': ColorUtils.colors["White"],
            'background_color': ColorUtils.colors["Black"],
            'transition_effect': 'fade',
            'fade_duration': 0.5,  # seconds
            'fade_steps': 10,
            'brightness': 0.5,
        })


class SlideTransitionStyle(BaseStyle):
    """Slide in/out transitions."""
    
    def __init__(self):
        super().__init__("slide_transition")
        self.update_properties({
            'text_color': ColorUtils.colors["White"],
            'background_color': ColorUtils.colors["Black"],
            'transition_effect': 'slide',
            'slide_direction': 'left',  # left, right, up, down
            'slide_duration': 0.3,
            'brightness': 0.5,
        })


class RevealTransitionStyle(BaseStyle):
    """Reveal effect transitions."""
    
    def __init__(self):
        super().__init__("reveal_transition")
        self.update_properties({
            'text_color': ColorUtils.colors["White"],
            'background_color': ColorUtils.colors["Black"],
            'transition_effect': 'reveal',
            'reveal_direction': 'left_to_right',
            'reveal_duration': 0.5,
            'brightness': 0.5,
        })


class PulseAnimationStyle(BaseStyle, AnimationMixin):
    """Pulsing brightness animation."""
    
    def __init__(self):
        super().__init__("pulse_animation")
        self.update_properties({
            'text_color': ColorUtils.colors["White"],
            'background_color': ColorUtils.colors["Black"],
            'pulse_enabled': True,
            'pulse_min_brightness': 0.3,
            'pulse_max_brightness': 1.0,
            'pulse_speed': 1.0,  # Hz
            'scroll_speed': 0.05,
        })
        
    def get_pulse_brightness(self, base_time=None):
        """
        Calculate current pulse brightness.
        
        Args:
            base_time: Base time for animation (None = current time)
            
        Returns:
            Brightness value between min and max
        """
        if base_time is None:
            base_time = time.monotonic()
            
        t = self.sine_wave(base_time, self.get_property('pulse_speed', 1.0))
        # Convert from [-1, 1] to [0, 1]
        t = (t + 1) / 2
        
        min_bright = self.get_property('pulse_min_brightness', 0.3)
        max_bright = self.get_property('pulse_max_brightness', 1.0)
        
        return min_bright + (max_bright - min_bright) * t


class RainbowCycleStyle(BaseStyle):
    """Rainbow color cycling animation."""
    
    def __init__(self):
        super().__init__("rainbow_cycle")
        self.update_properties({
            'text_color': 'rainbow',
            'background_color': ColorUtils.colors["Black"],
            'rainbow_enabled': True,
            'rainbow_speed': 1.0,  # Hz
            'rainbow_spread': 1.0,  # How spread out the rainbow is
            'scroll_speed': 0.05,
            'brightness': 0.7,
        })
        
    def get_rainbow_color(self, position=0, base_time=None):
        """
        Calculate rainbow color for a position.
        
        Args:
            position: Position in the text (0-1)
            base_time: Base time for animation
            
        Returns:
            Color as hex string
        """
        if base_time is None:
            base_time = time.monotonic()
            
        speed = self.get_property('rainbow_speed', 1.0)
        spread = self.get_property('rainbow_spread', 1.0)
        
        # Calculate hue based on position and time
        hue = (position * spread + base_time * speed) % 1.0
        
        # Convert HSV to RGB (simplified)
        # Hue is 0-1, full saturation and value
        r, g, b = self._hsv_to_rgb(hue, 1.0, 1.0)
        
        return ColorUtils.from_rgb(int(r * 255), int(g * 255), int(b * 255))
        
    def _hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB."""
        i = int(h * 6)
        f = h * 6 - i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        
        i = i % 6
        if i == 0:
            return v, t, p
        elif i == 1:
            return q, v, p
        elif i == 2:
            return p, v, t
        elif i == 3:
            return p, q, v
        elif i == 4:
            return t, p, v
        else:
            return v, p, q


class BreathingStyle(BaseStyle, AnimationMixin):
    """Breathing/glow effect."""
    
    def __init__(self):
        super().__init__("breathing")
        self.update_properties({
            'text_color': ColorUtils.colors["Blue"],
            'background_color': ColorUtils.colors["Black"],
            'breathe_enabled': True,
            'breathe_min_brightness': 0.2,
            'breathe_max_brightness': 0.8,
            'breathe_speed': 0.3,  # Hz (slower than pulse)
            'scroll_speed': 0.05,
        })


class SparkleStyle(BaseStyle):
    """Sparkle/glitter effect."""
    
    def __init__(self):
        super().__init__("sparkle")
        self.update_properties({
            'text_color': ColorUtils.colors["White"],
            'background_color': ColorUtils.colors["Black"],
            'sparkle_enabled': True,
            'sparkle_density': 0.1,  # Percentage of pixels
            'sparkle_duration': 0.1,  # seconds
            'sparkle_color': ColorUtils.colors["White"],
            'scroll_speed': 0.05,
            'brightness': 0.6,
        })


class WaveStyle(BaseStyle, AnimationMixin):
    """Wave motion effect."""
    
    def __init__(self):
        super().__init__("wave")
        self.update_properties({
            'text_color': ColorUtils.colors["Blue"],
            'background_color': ColorUtils.colors["Black"],
            'wave_enabled': True,
            'wave_amplitude': 3,  # pixels
            'wave_frequency': 0.5,  # Hz
            'wave_length': 20,  # pixels
            'scroll_speed': 0.04,
            'brightness': 0.6,
        })


class MatrixRainStyle(BaseStyle):
    """Matrix rain effect."""
    
    def __init__(self):
        super().__init__("matrix_rain")
        self.update_properties({
            'text_color': ColorUtils.colors["Green"],
            'background_color': ColorUtils.colors["Black"],
            'matrix_effect': True,
            'rain_speed': 0.1,
            'trail_length': 5,
            'character_set': 'binary',  # binary, katakana, custom
            'brightness': 0.7,
        })


# Dictionary mapping animation names to classes
ANIMATION_STYLES = {
    'smooth_scroll': SmoothScrollStyle,
    'bouncy_scroll': BouncyScrollStyle,
    'typewriter': TypewriterStyle,
    'marquee': MarqueeStyle,
    'ticker': TickerStyle,
    'crawl': CrawlStyle,
    'fade_transition': FadeTransitionStyle,
    'slide_transition': SlideTransitionStyle,
    'reveal_transition': RevealTransitionStyle,
    'pulse_animation': PulseAnimationStyle,
    'rainbow_cycle': RainbowCycleStyle,
    'breathing': BreathingStyle,
    'sparkle': SparkleStyle,
    'wave': WaveStyle,
    'matrix_rain': MatrixRainStyle,
}


def get_animation_style(name):
    """
    Get an animation style by name.
    
    Args:
        name: The animation name
        
    Returns:
        A style instance or None if not found
    """
    style_class = ANIMATION_STYLES.get(name)
    if style_class:
        return style_class()
    return None


def list_animation_styles():
    """
    List all available animation styles.
    
    Returns:
        List of animation names
    """
    return list(ANIMATION_STYLES.keys())