"""
Theme-specific styles for specialized applications.

This module provides styles optimized for specific types of content
like theme park wait times, stock tickers, weather, and clocks.

Copyright 2024 3DUPFitters LLC
"""
from .base import BaseStyle
from ..utils.colors import ColorUtils


class ThemeParkStyle(BaseStyle):
    """Styling optimized for park wait times with ride names/times."""
    
    def __init__(self):
        super().__init__("theme_park")
        self.update_properties({
            # Ride name in blue
            'ride_name_color': ColorUtils.colors["Blue"],
            # Wait time in off-white
            'ride_wait_time_color': ColorUtils.colors["Old Lace"],
            # Default text in yellow
            'text_color': ColorUtils.colors["Yellow"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.04,
            'brightness': 0.5,
            'brightness_scale': 0.5,
            # Layout for ride info
            'ride_name_y': 7,
            'wait_time_y': 22,
            'wait_time_scale': 2,  # Larger wait times
            # Message delays
            'ride_display_duration': 3,
            'message_delay': 2,
        })


class StockTickerStyle(BaseStyle):
    """Financial data styling with gains/losses colors."""
    
    def __init__(self):
        super().__init__("stock_ticker")
        self.update_properties({
            # Gains in green
            'gain_color': ColorUtils.colors["Green"],
            # Losses in red
            'loss_color': ColorUtils.colors["Red"],
            # Neutral in white
            'neutral_color': ColorUtils.colors["White"],
            # Symbol names in blue
            'symbol_color': ColorUtils.colors["Blue"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.03,  # Fast ticker speed
            'brightness': 0.6,
            # Continuous scroll
            'scroll_delay': 0,
            'continuous_scroll': True,
            # Formatting
            'show_percent_change': True,
            'show_arrows': True,  # ↑ ↓ indicators
        })


class WeatherStyle(BaseStyle):
    """Weather-specific styling with temperature/condition formatting."""
    
    def __init__(self):
        super().__init__("weather")
        self.update_properties({
            # Temperature colors
            'hot_color': ColorUtils.colors["Red"],      # > 85°F
            'warm_color': ColorUtils.colors["Orange"],  # 70-85°F
            'mild_color': ColorUtils.colors["Yellow"],  # 50-70°F
            'cool_color': ColorUtils.colors["Blue"],    # 32-50°F
            'cold_color': ColorUtils.colors["Purple"],  # < 32°F
            # Condition colors
            'sunny_color': ColorUtils.colors["Yellow"],
            'cloudy_color': ColorUtils.colors["White"],
            'rain_color': ColorUtils.colors["Blue"],
            'snow_color': ColorUtils.colors["White"],
            'storm_color': ColorUtils.colors["Purple"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.05,
            'brightness': 0.6,
            # Display options
            'show_conditions': True,
            'show_high_low': True,
            'temperature_unit': 'F',  # F or C
            'static_duration': 4,
        })


class ClockStyle(BaseStyle):
    """Time display styling with different formats."""
    
    def __init__(self):
        super().__init__("clock")
        self.update_properties({
            'text_color': ColorUtils.colors["White"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0,  # Static display
            'brightness': 0.5,
            'text_align': 'center',
            'font_scale': 2,  # Larger text
            # Clock format options
            'time_format': '12h',  # 12h or 24h
            'show_seconds': True,
            'show_date': False,
            'date_format': 'short',  # short, long, custom
            'blink_colon': True,
            'blink_speed': 1.0,
        })


class SportsScoreStyle(BaseStyle):
    """Sports score display styling."""
    
    def __init__(self):
        super().__init__("sports_score")
        self.update_properties({
            # Team colors
            'home_team_color': ColorUtils.colors["Blue"],
            'away_team_color': ColorUtils.colors["Red"],
            'score_color': ColorUtils.colors["White"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.04,
            'brightness': 0.7,
            # Score display
            'show_period': True,
            'show_time_remaining': True,
            'highlight_leading_team': True,
            'pulse_on_score_change': True,
            'pulse_speed': 3.0,
        })


class NewsTickerStyle(BaseStyle):
    """News ticker styling."""
    
    def __init__(self):
        super().__init__("news_ticker")
        self.update_properties({
            'text_color': ColorUtils.colors["White"],
            'headline_color': ColorUtils.colors["Yellow"],
            'breaking_color': ColorUtils.colors["Red"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.04,
            'brightness': 0.6,
            'continuous_scroll': True,
            'scroll_delay': 0,
            # News formatting
            'show_source': True,
            'show_timestamp': True,
            'separator': ' • ',
            'breaking_prefix': 'BREAKING: ',
        })


class TransitStyle(BaseStyle):
    """Public transit arrival times styling."""
    
    def __init__(self):
        super().__init__("transit")
        self.update_properties({
            # Line colors (can be customized per transit system)
            'line_color': ColorUtils.colors["Blue"],
            'arrival_color': ColorUtils.colors["Yellow"],
            'delayed_color': ColorUtils.colors["Red"],
            'on_time_color': ColorUtils.colors["Green"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.05,
            'brightness': 0.6,
            # Display format
            'show_line_name': True,
            'show_destination': True,
            'show_platform': False,
            'time_format': 'minutes',  # minutes, absolute
            'alert_when_close': True,
            'alert_threshold': 3,  # minutes
        })


class CountdownStyle(BaseStyle):
    """Countdown timer styling."""
    
    def __init__(self):
        super().__init__("countdown")
        self.update_properties({
            'text_color': ColorUtils.colors["White"],
            'urgent_color': ColorUtils.colors["Red"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0,  # Static
            'brightness': 0.7,
            'text_align': 'center',
            'font_scale': 2,
            # Countdown options
            'show_days': True,
            'show_hours': True,
            'show_minutes': True,
            'show_seconds': True,
            'urgent_threshold': 60,  # seconds
            'pulse_when_urgent': True,
            'pulse_speed': 2.0,
        })


class CalendarStyle(BaseStyle):
    """Calendar/event display styling."""
    
    def __init__(self):
        super().__init__("calendar")
        self.update_properties({
            'event_color': ColorUtils.colors["Yellow"],
            'date_color': ColorUtils.colors["Blue"],
            'time_color': ColorUtils.colors["White"],
            'today_color': ColorUtils.colors["Green"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.05,
            'brightness': 0.5,
            # Calendar display
            'show_date': True,
            'show_time': True,
            'show_location': False,
            'date_format': 'short',
            'time_format': '12h',
            'days_ahead': 7,
        })


class CryptoTickerStyle(BaseStyle):
    """Cryptocurrency ticker styling."""
    
    def __init__(self):
        super().__init__("crypto_ticker")
        self.update_properties({
            # Similar to stock ticker but with crypto-specific colors
            'bitcoin_color': ColorUtils.colors["Orange"],
            'ethereum_color': ColorUtils.colors["Purple"],
            'gain_color': ColorUtils.colors["Green"],
            'loss_color': ColorUtils.colors["Red"],
            'symbol_color': ColorUtils.colors["Blue"],
            'background_color': ColorUtils.colors["Black"],
            'scroll_speed': 0.03,
            'brightness': 0.7,
            'continuous_scroll': True,
            # Crypto formatting
            'show_market_cap': False,
            'show_24h_change': True,
            'decimal_places': 2,
            'show_sparkline': False,
        })


# Dictionary mapping theme names to classes
THEME_STYLES = {
    'theme_park': ThemeParkStyle,
    'stock_ticker': StockTickerStyle,
    'weather': WeatherStyle,
    'clock': ClockStyle,
    'sports_score': SportsScoreStyle,
    'news_ticker': NewsTickerStyle,
    'transit': TransitStyle,
    'countdown': CountdownStyle,
    'calendar': CalendarStyle,
    'crypto_ticker': CryptoTickerStyle,
}


def get_theme_style(name):
    """
    Get a theme style by name.
    
    Args:
        name: The theme name
        
    Returns:
        A style instance or None if not found
    """
    style_class = THEME_STYLES.get(name)
    if style_class:
        return style_class()
    return None


def list_theme_styles():
    """
    List all available theme styles.
    
    Returns:
        List of theme names
    """
    return list(THEME_STYLES.keys())