"""
Layout management for display arrangements.

This module provides various layout options for text positioning,
alignment, and multi-line displays.

Copyright 2024 3DUPFitters LLC
"""
from .base import BaseStyle
from ..utils.colors import ColorUtils


class SingleLineLayout(BaseStyle):
    """Standard single line scrolling layout."""
    
    def __init__(self):
        super().__init__("single_line")
        self.update_properties({
            'layout_type': 'single_line',
            'text_y_position': 15,  # Centered vertically on 32px display
            'text_align': 'left',
            'scroll_enabled': True,
        })


class CenteredLayout(BaseStyle):
    """Centered static text layout."""
    
    def __init__(self):
        super().__init__("centered")
        self.update_properties({
            'layout_type': 'centered',
            'text_align': 'center',
            'vertical_align': 'center',
            'scroll_enabled': False,
            'auto_scale': True,  # Scale font to fit
        })


class TwoLineLayout(BaseStyle):
    """Two line layout for title and content."""
    
    def __init__(self):
        super().__init__("two_line")
        self.update_properties({
            'layout_type': 'two_line',
            'line1_y': 10,
            'line2_y': 22,
            'line1_color': ColorUtils.colors["Yellow"],
            'line2_color': ColorUtils.colors["White"],
            'line1_scale': 1,
            'line2_scale': 1,
            'line1_align': 'left',
            'line2_align': 'left',
            'scroll_line1': False,
            'scroll_line2': True,
        })


class SplitScreenLayout(BaseStyle):
    """Split screen with two independent areas."""
    
    def __init__(self):
        super().__init__("split_screen")
        self.update_properties({
            'layout_type': 'split_screen',
            'split_position': 32,  # X position of split
            'left_color': ColorUtils.colors["Blue"],
            'right_color': ColorUtils.colors["Green"],
            'left_align': 'center',
            'right_align': 'center',
            'scroll_left': False,
            'scroll_right': False,
        })


class TickerLayout(BaseStyle):
    """Bottom ticker with static top content."""
    
    def __init__(self):
        super().__init__("ticker_layout")
        self.update_properties({
            'layout_type': 'ticker',
            'main_y': 12,
            'ticker_y': 28,
            'main_color': ColorUtils.colors["White"],
            'ticker_color': ColorUtils.colors["Yellow"],
            'main_scale': 2,
            'ticker_scale': 1,
            'ticker_speed': 0.03,
            'ticker_continuous': True,
        })


class HeaderFooterLayout(BaseStyle):
    """Header and footer with scrolling middle."""
    
    def __init__(self):
        super().__init__("header_footer")
        self.update_properties({
            'layout_type': 'header_footer',
            'header_y': 6,
            'content_y': 16,
            'footer_y': 28,
            'header_color': ColorUtils.colors["Blue"],
            'content_color': ColorUtils.colors["White"],
            'footer_color': ColorUtils.colors["Blue"],
            'header_static': True,
            'footer_static': True,
            'content_scroll': True,
        })


class GridLayout(BaseStyle):
    """Grid-based layout for structured data."""
    
    def __init__(self):
        super().__init__("grid")
        self.update_properties({
            'layout_type': 'grid',
            'rows': 2,
            'columns': 2,
            'cell_width': 32,
            'cell_height': 16,
            'grid_color': ColorUtils.colors["White"],
            'show_borders': False,
            'cell_padding': 1,
        })


class VerticalScrollLayout(BaseStyle):
    """Vertical scrolling for long text."""
    
    def __init__(self):
        super().__init__("vertical_scroll")
        self.update_properties({
            'layout_type': 'vertical_scroll',
            'scroll_direction': 'up',
            'line_height': 8,
            'scroll_speed': 0.08,
            'pause_on_line': True,
            'pause_duration': 2,
        })


class SideBySideLayout(BaseStyle):
    """Side by side comparison layout."""
    
    def __init__(self):
        super().__init__("side_by_side")
        self.update_properties({
            'layout_type': 'side_by_side',
            'left_width': 32,
            'right_width': 32,
            'left_color': ColorUtils.colors["Green"],
            'right_color': ColorUtils.colors["Red"],
            'center_divider': True,
            'divider_color': ColorUtils.colors["White"],
        })


class FullScreenLayout(BaseStyle):
    """Full screen with maximum text size."""
    
    def __init__(self):
        super().__init__("full_screen")
        self.update_properties({
            'layout_type': 'full_screen',
            'auto_scale': True,
            'max_scale': 4,
            'center_horizontal': True,
            'center_vertical': True,
            'fill_screen': True,
        })


class CompactLayout(BaseStyle):
    """Compact layout with minimal spacing."""
    
    def __init__(self):
        super().__init__("compact")
        self.update_properties({
            'layout_type': 'compact',
            'line_spacing': 6,
            'character_spacing': -1,  # Tighter spacing
            'margin_top': 0,
            'margin_bottom': 0,
            'margin_left': 0,
            'margin_right': 0,
        })


class PaddedLayout(BaseStyle):
    """Layout with comfortable padding."""
    
    def __init__(self):
        super().__init__("padded")
        self.update_properties({
            'layout_type': 'padded',
            'padding_top': 4,
            'padding_bottom': 4,
            'padding_left': 4,
            'padding_right': 4,
            'content_align': 'center',
        })


class ResponsiveLayout(BaseStyle):
    """Layout that adapts to content."""
    
    def __init__(self):
        super().__init__("responsive")
        self.update_properties({
            'layout_type': 'responsive',
            'auto_layout': True,
            'prefer_static': True,  # Static if fits, scroll if not
            'min_font_scale': 1,
            'max_font_scale': 3,
            'break_words': False,
            'hyphenate': False,
        })


# Layout positioning utilities
class LayoutCalculator:
    """Utilities for calculating layout positions."""
    
    @staticmethod
    def center_horizontally(text_width, display_width):
        """Calculate X position to center text horizontally."""
        return max(0, (display_width - text_width) // 2)
        
    @staticmethod
    def center_vertically(text_height, display_height):
        """Calculate Y position to center text vertically."""
        # Account for baseline positioning
        return (display_height + text_height) // 2
        
    @staticmethod
    def align_text(text_width, display_width, alignment='left'):
        """
        Calculate X position based on alignment.
        
        Args:
            text_width: Width of the text
            display_width: Width of the display
            alignment: 'left', 'center', or 'right'
            
        Returns:
            X position
        """
        if alignment == 'center':
            return LayoutCalculator.center_horizontally(text_width, display_width)
        elif alignment == 'right':
            return max(0, display_width - text_width)
        else:  # left
            return 0
            
    @staticmethod
    def calculate_grid_position(row, col, cell_width, cell_height, padding=0):
        """
        Calculate position for grid cell.
        
        Args:
            row: Row index (0-based)
            col: Column index (0-based)
            cell_width: Width of each cell
            cell_height: Height of each cell
            padding: Padding between cells
            
        Returns:
            Tuple of (x, y) position
        """
        x = col * (cell_width + padding) + padding
        y = row * (cell_height + padding) + padding + cell_height  # Baseline
        return x, y


# Dictionary mapping layout names to classes
LAYOUT_STYLES = {
    'single_line': SingleLineLayout,
    'centered': CenteredLayout,
    'two_line': TwoLineLayout,
    'split_screen': SplitScreenLayout,
    'ticker': TickerLayout,
    'header_footer': HeaderFooterLayout,
    'grid': GridLayout,
    'vertical_scroll': VerticalScrollLayout,
    'side_by_side': SideBySideLayout,
    'full_screen': FullScreenLayout,
    'compact': CompactLayout,
    'padded': PaddedLayout,
    'responsive': ResponsiveLayout,
}


def get_layout_style(name):
    """
    Get a layout style by name.
    
    Args:
        name: The layout name
        
    Returns:
        A style instance or None if not found
    """
    style_class = LAYOUT_STYLES.get(name)
    if style_class:
        return style_class()
    return None


def list_layout_styles():
    """
    List all available layout styles.
    
    Returns:
        List of layout names
    """
    return list(LAYOUT_STYLES.keys())