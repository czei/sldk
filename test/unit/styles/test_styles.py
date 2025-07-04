"""
Unit tests for the display styles system.
"""
import pytest
from unittest.mock import MagicMock, patch

# Import the styles modules
from cpyapp.styles import (
    BaseStyle, create_style, get_style, list_all_styles,
    merge_styles, create_composite, quick_style,
    DefaultStyle, RainbowStyle, ThemeParkStyle,
    get_color_scheme, apply_color_scheme
)
from cpyapp.utils.colors import ColorUtils


class TestBaseStyle:
    """Test the BaseStyle class."""
    
    def test_init(self):
        """Test base style initialization."""
        style = BaseStyle("test_style")
        assert style.name == "test_style"
        assert style.get_property('text_color') == ColorUtils.colors["White"]
        assert style.get_property('background_color') == ColorUtils.colors["Black"]
        assert style.get_property('scroll_speed') == 0.05
        
    def test_get_set_property(self):
        """Test getting and setting properties."""
        style = BaseStyle()
        
        # Set property
        style.set_property('custom_prop', 'value')
        assert style.get_property('custom_prop') == 'value'
        
        # Get with default
        assert style.get_property('nonexistent', 'default') == 'default'
        
    def test_update_properties(self):
        """Test updating multiple properties."""
        style = BaseStyle()
        style.update_properties({
            'text_color': ColorUtils.colors["Red"],
            'scroll_speed': 0.03,
            'custom': True
        })
        
        assert style.get_property('text_color') == ColorUtils.colors["Red"]
        assert style.get_property('scroll_speed') == 0.03
        assert style.get_property('custom') is True
        
    def test_get_color(self):
        """Test color retrieval with brightness."""
        style = BaseStyle()
        style.set_property('text_color', ColorUtils.colors["White"])
        style.set_property('brightness_scale', 0.5)
        
        # Should scale the color
        color = style.get_color('text_color')
        assert color == ColorUtils.scale_color(ColorUtils.colors["White"], 0.5)
        
        # Rainbow should pass through
        style.set_property('text_color', 'rainbow')
        assert style.get_color('text_color') == 'rainbow'
        
    def test_to_dict_from_dict(self):
        """Test serialization."""
        style = BaseStyle()
        style.set_property('custom', 'value')
        
        # To dict
        data = style.to_dict()
        assert 'custom' in data
        assert data['custom'] == 'value'
        
        # From dict
        new_style = BaseStyle()
        new_style.from_dict(data)
        assert new_style.get_property('custom') == 'value'
        
    def test_clone(self):
        """Test style cloning."""
        style = BaseStyle("original")
        style.set_property('custom', 'value')
        
        cloned = style.clone()
        assert cloned.name == "original_copy"
        assert cloned.get_property('custom') == 'value'
        
        # Modifying clone shouldn't affect original
        cloned.set_property('custom', 'new_value')
        assert style.get_property('custom') == 'value'
        
    def test_merge(self):
        """Test style merging."""
        style1 = BaseStyle()
        style1.set_property('prop1', 'value1')
        style1.set_property('shared', 'original')
        
        style2 = BaseStyle()
        style2.set_property('prop2', 'value2')
        style2.set_property('shared', 'override')
        
        # Merge style2 into style1
        style1.merge(style2)
        
        assert style1.get_property('prop1') == 'value1'
        assert style1.get_property('prop2') == 'value2'
        assert style1.get_property('shared') == 'override'
        
        # Merge from dict
        style1.merge({'prop3': 'value3'})
        assert style1.get_property('prop3') == 'value3'


class TestStyleFactory:
    """Test the style factory functions."""
    
    def test_get_style(self):
        """Test getting styles by name."""
        # Core style
        style = get_style('default')
        assert isinstance(style, DefaultStyle)
        
        # Theme style
        style = get_style('theme_park')
        assert isinstance(style, ThemeParkStyle)
        
        # Unknown style returns default
        style = get_style('nonexistent')
        assert isinstance(style, DefaultStyle)
        
    def test_create_style_string(self):
        """Test creating style from string."""
        style = create_style('rainbow')
        assert isinstance(style, RainbowStyle)
        assert style.get_property('rainbow_enabled') is True
        
    def test_create_style_dict(self):
        """Test creating style from dictionary."""
        style = create_style({
            'text_color': ColorUtils.colors["Red"],
            'scroll_speed': 0.02
        })
        assert isinstance(style, BaseStyle)
        assert style.get_property('text_color') == ColorUtils.colors["Red"]
        assert style.get_property('scroll_speed') == 0.02
        
    def test_create_style_instance(self):
        """Test passing existing style instance."""
        original = DefaultStyle()
        style = create_style(original)
        assert style is original
        
    def test_create_style_none(self):
        """Test None returns default."""
        style = create_style(None)
        assert isinstance(style, DefaultStyle)
        
    def test_merge_styles(self):
        """Test merging multiple styles."""
        merged = merge_styles('alert', 'fast', {'brightness': 0.9})
        
        # Should have alert color
        assert merged.get_property('text_color') == ColorUtils.colors["Red"]
        # Should have fast speed
        assert merged.get_property('scroll_speed') == 0.03
        # Should have custom brightness
        assert merged.get_property('brightness') == 0.9
        
    def test_create_composite(self):
        """Test creating composite styles."""
        composite = create_composite(
            'rainbow',
            'fast',
            'centered',
            brightness=0.8,
            custom_prop='test'
        )
        
        assert composite.get_property('rainbow_enabled') is True
        assert composite.get_property('scroll_speed') == 0.03
        assert composite.get_property('text_align') == 'center'
        assert composite.get_property('brightness') == 0.8
        assert composite.get_property('custom_prop') == 'test'
        
    def test_list_all_styles(self):
        """Test listing all styles."""
        all_styles = list_all_styles()
        
        assert 'core' in all_styles
        assert 'theme' in all_styles
        assert 'animation' in all_styles
        assert 'layout' in all_styles
        
        assert 'default' in all_styles['core']
        assert 'theme_park' in all_styles['theme']
        assert 'pulse_animation' in all_styles['animation']
        assert 'centered' in all_styles['layout']


class TestQuickStyle:
    """Test the quick_style helper."""
    
    def test_quick_style_color(self):
        """Test quick style with color."""
        style = quick_style(color='red')
        assert style.get_property('text_color') == ColorUtils.colors["Red"]
        
        # Hex color
        style = quick_style(color='0xFF00FF')
        assert style.get_property('text_color') == '0xFF00FF'
        
    def test_quick_style_speed(self):
        """Test quick style with speed."""
        style = quick_style(speed='fast')
        assert style.get_property('scroll_speed') == 0.03
        
        style = quick_style(speed='slow')
        assert style.get_property('scroll_speed') == 0.08
        
        style = quick_style(speed=0.02)
        assert style.get_property('scroll_speed') == 0.02
        
    def test_quick_style_effect(self):
        """Test quick style with effect."""
        style = quick_style(effect='pulse')
        assert style.get_property('pulse_enabled') is True
        
        style = quick_style(effect='rainbow')
        assert style.get_property('rainbow_enabled') is True
        assert style.get_property('text_color') == 'rainbow'
        
    def test_quick_style_layout(self):
        """Test quick style with layout."""
        style = quick_style(layout='centered')
        assert style.get_property('text_align') == 'center'
        
    def test_quick_style_combined(self):
        """Test quick style with all parameters."""
        style = quick_style(
            color='green',
            speed='fast',
            effect='breathe',
            layout='two_line'
        )
        
        assert style.get_property('text_color') == ColorUtils.colors["Green"]
        assert style.get_property('scroll_speed') == 0.03
        assert style.get_property('breathe_enabled') is True
        assert style.get_property('layout_type') == 'two_line'


class TestColorSchemes:
    """Test color scheme functionality."""
    
    def test_get_color_scheme(self):
        """Test getting color schemes."""
        scheme = get_color_scheme('neon')
        assert scheme is not None
        assert scheme.name == 'neon'
        assert 'text' in scheme.colors
        
    def test_apply_color_scheme(self):
        """Test applying color scheme to style."""
        style = BaseStyle()
        apply_color_scheme(style, 'cyberpunk')
        
        # Should have cyberpunk colors
        text_color = style.get_property('text_color')
        assert text_color == "0x00FFFF"  # Cyan
        
    def test_color_scheme_to_style_dict(self):
        """Test converting scheme to style properties."""
        scheme = get_color_scheme('ocean')
        style_dict = scheme.to_style_dict()
        
        assert 'text_color' in style_dict
        assert 'background_color' in style_dict


class TestSpecificStyles:
    """Test specific style implementations."""
    
    def test_theme_park_style(self):
        """Test theme park style properties."""
        style = ThemeParkStyle()
        
        assert style.get_property('ride_name_color') == ColorUtils.colors["Blue"]
        assert style.get_property('ride_wait_time_color') == ColorUtils.colors["Old Lace"]
        assert style.get_property('wait_time_scale') == 2
        
    def test_rainbow_style(self):
        """Test rainbow style properties."""
        style = RainbowStyle()
        
        assert style.get_property('text_color') == 'rainbow'
        assert style.get_property('rainbow_enabled') is True
        assert style.get_property('color_cycle_enabled') is True
        
    def test_animation_style_methods(self):
        """Test animation style special methods."""
        from cpyapp.styles.animations import PulseAnimationStyle
        
        style = PulseAnimationStyle()
        
        # Test pulse brightness calculation
        brightness = style.get_pulse_brightness(0)  # Time 0
        assert 0.3 <= brightness <= 1.0
        
    def test_layout_calculator(self):
        """Test layout calculator utilities."""
        from cpyapp.styles.layouts import LayoutCalculator
        
        # Center horizontally
        x = LayoutCalculator.center_horizontally(20, 64)
        assert x == 22  # (64 - 20) / 2
        
        # Align text
        x = LayoutCalculator.align_text(20, 64, 'right')
        assert x == 44  # 64 - 20
        
        # Grid position
        x, y = LayoutCalculator.calculate_grid_position(1, 2, 20, 10, 2)
        assert x == 46  # col 2 * (20 + 2) + 2
        assert y == 24  # row 1 * (10 + 2) + 2 + 10


def test_integration_with_simple_scroll_app():
    """Test integration with SimpleScrollApp."""
    from cpyapp.apps import SimpleScrollApp
    
    # Mock the display and other components
    with patch('cpyapp.apps.simple.create_display') as mock_display, \
         patch('cpyapp.apps.simple.HttpClient'), \
         patch('cpyapp.apps.simple.create_data_source'):
        
        # Test with string style
        app = SimpleScrollApp("Test", style="rainbow")
        assert hasattr(app, 'style')
        assert app.style.get_property('rainbow_enabled') is True
        
        # Test with custom style
        custom = {
            'text_color': '0xFF00FF',
            'scroll_speed': 0.02
        }
        app = SimpleScrollApp("Test", style=custom)
        assert app.style.get_property('text_color') == '0xFF00FF'
        
        # Test with style instance
        style_obj = ThemeParkStyle()
        app = SimpleScrollApp("Test", style=style_obj)
        assert app.style is style_obj