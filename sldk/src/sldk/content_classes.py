"""Content system for SLDK.

Provides content classes that work with the display strategy and effects system.
These classes offer a higher-level interface for creating display content with
built-in support for effects.
"""

from typing import Dict, Any, Optional
from .display.strategy import DisplayItem, Priority


class BaseContent:
    """Base class for display content.
    
    Provides common functionality for creating DisplayItems with effects support.
    """
    
    def __init__(self, 
                 strategy_name: str,
                 data: Dict[str, Any],
                 priority: int = Priority.NORMAL,
                 duration: Optional[float] = None):
        """Initialize content.
        
        Args:
            strategy_name: Name of the strategy to use
            data: Data for the strategy
            priority: Display priority
            duration: Display duration in seconds
        """
        self.strategy_name = strategy_name
        self.data = data
        self.priority = priority
        self.duration = duration
        self.effects = []
    
    def with_effect(self, effect):
        """Add an effect to this content.
        
        Args:
            effect: Effect instance to add
            
        Returns:
            Self for method chaining
        """
        self.effects.append(effect)
        return self
    
    def with_effects(self, effects: list):
        """Add multiple effects to this content.
        
        Args:
            effects: List of Effect instances
            
        Returns:
            Self for method chaining
        """
        self.effects.extend(effects)
        return self
    
    def to_display_item(self) -> DisplayItem:
        """Convert this content to a DisplayItem.
        
        Returns:
            DisplayItem instance ready for queue
        """
        item = DisplayItem(
            strategy_name=self.strategy_name,
            data=self.data,
            priority=self.priority,
            duration=self.duration
        )
        
        # Add effects
        for effect in self.effects:
            item.add_effect(effect)
        
        return item


class TextContent(BaseContent):
    """Content class for static text display."""
    
    def __init__(self, 
                 text: str,
                 x: int = 0,
                 y: int = 10,
                 color: int = 0xFFFFFF,
                 font: str = None,
                 priority: int = Priority.NORMAL,
                 duration: Optional[float] = None):
        """Initialize text content.
        
        Args:
            text: Text to display
            x: X position
            y: Y position
            color: Text color (RGB hex)
            font: Font name
            priority: Display priority
            duration: Display duration
        """
        data = {
            'text': text,
            'x': x,
            'y': y,
            'color': color
        }
        if font:
            data['font'] = font
        
        super().__init__('static_text', data, priority, duration)
        self.text = text


class ScrollingTextContent(BaseContent):
    """Content class for scrolling text display."""
    
    def __init__(self, 
                 text: str,
                 y: int = 10,
                 color: int = 0xFFFFFF,
                 speed: float = 0.05,
                 priority: int = Priority.NORMAL,
                 duration: Optional[float] = None):
        """Initialize scrolling text content.
        
        Args:
            text: Text to scroll
            y: Y position
            color: Text color (RGB hex)
            speed: Scroll speed
            priority: Display priority
            duration: Display duration (auto-calculated if None)
        """
        data = {
            'text': text,
            'y': y,
            'color': color,
            'speed': speed
        }
        
        super().__init__('scrolling_text', data, priority, duration)
        self.text = text


class SplashContent(BaseContent):
    """Content class for splash screen display.
    
    This is essentially static text but semantically different,
    often used with reveal effects.
    """
    
    def __init__(self, 
                 text: str,
                 x: int = 0,
                 y: int = 10,
                 color: int = 0xFFFFFF,
                 font: str = None,
                 priority: int = Priority.HIGH,
                 duration: float = 4.0):
        """Initialize splash content.
        
        Args:
            text: Splash text to display
            x: X position
            y: Y position
            color: Text color (RGB hex)
            font: Font name
            priority: Display priority (default HIGH)
            duration: Display duration (default 4 seconds)
        """
        data = {
            'text': text,
            'x': x,
            'y': y,
            'color': color
        }
        if font:
            data['font'] = font
        
        super().__init__('static_text', data, priority, duration)
        self.text = text


class AlertContent(BaseContent):
    """Content class for alert messages."""
    
    def __init__(self, 
                 message: str,
                 color: int = 0xFF0000,  # Red by default
                 priority: int = Priority.URGENT,
                 duration: float = 3.0):
        """Initialize alert content.
        
        Args:
            message: Alert message
            color: Alert color (RGB hex, default red)
            priority: Display priority (default URGENT)
            duration: Display duration (default 3 seconds)
        """
        data = {
            'text': message,
            'x': 0,
            'y': 10,
            'color': color
        }
        
        super().__init__('static_text', data, priority, duration)
        self.message = message


class CustomContent(BaseContent):
    """Content class for custom strategies."""
    
    def __init__(self, 
                 strategy_name: str,
                 data: Dict[str, Any],
                 priority: int = Priority.NORMAL,
                 duration: Optional[float] = None):
        """Initialize custom content.
        
        Args:
            strategy_name: Name of the custom strategy
            data: Data for the strategy
            priority: Display priority
            duration: Display duration
        """
        super().__init__(strategy_name, data, priority, duration)


# Factory functions for convenience
def create_text(text: str, **kwargs) -> TextContent:
    """Create static text content.
    
    Args:
        text: Text to display
        **kwargs: Additional parameters for TextContent
        
    Returns:
        TextContent instance
    """
    return TextContent(text, **kwargs)


def create_scrolling_text(text: str, **kwargs) -> ScrollingTextContent:
    """Create scrolling text content.
    
    Args:
        text: Text to scroll
        **kwargs: Additional parameters for ScrollingTextContent
        
    Returns:
        ScrollingTextContent instance
    """
    return ScrollingTextContent(text, **kwargs)


def create_splash(text: str, **kwargs) -> SplashContent:
    """Create splash content.
    
    Args:
        text: Splash text
        **kwargs: Additional parameters for SplashContent
        
    Returns:
        SplashContent instance
    """
    return SplashContent(text, **kwargs)


def create_alert(message: str, **kwargs) -> AlertContent:
    """Create alert content.
    
    Args:
        message: Alert message
        **kwargs: Additional parameters for AlertContent
        
    Returns:
        AlertContent instance
    """
    return AlertContent(message, **kwargs)


# Example usage functions that demonstrate the desired API
def example_usage():
    """Example of how to use the content system with effects."""
    from .effects import RevealEffect, FadeInEffect, PulseEffect
    
    # Basic text content
    text = create_text("Hello World", duration=3.0)
    
    # Text with reveal effect (Option A pattern)
    splash = create_splash("THEME PARK WAITS").with_effect(RevealEffect(duration=2.0))
    
    # Scrolling text with fade in
    scrolling = create_scrolling_text("Welcome to the system").with_effect(
        FadeInEffect(duration=1.0)
    )
    
    # Alert with pulse effect
    alert = create_alert("System Update").with_effect(
        PulseEffect(duration=2.0, pulses=3)
    )
    
    # Multiple effects
    fancy_splash = create_splash("LOADING...").with_effects([
        FadeInEffect(duration=1.0),
        PulseEffect(duration=2.0, pulses=2)
    ])
    
    # Convert to DisplayItems for queue
    display_items = [
        text.to_display_item(),
        splash.to_display_item(),
        scrolling.to_display_item(),
        alert.to_display_item(),
        fancy_splash.to_display_item()
    ]
    
    return display_items