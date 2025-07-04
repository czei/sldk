# Display Styles System

The styles system provides pre-configured styling options for LED matrix displays, making it easy to create beautiful, animated text displays with minimal code.

## Quick Start

```python
from cpyapp.apps import SimpleScrollApp

# Use a built-in style by name
app = SimpleScrollApp("Hello World!", style="rainbow")
app.run()

# Use a theme-specific style
app = SimpleScrollApp("Space Mountain: 45 min", style="theme_park")
app.run()

# Create a custom style
custom_style = {
    'text_color': '0xFF00FF',  # Magenta
    'scroll_speed': 0.04,
    'pulse_enabled': True
}
app = SimpleScrollApp("Custom!", style=custom_style)
app.run()
```

## Style Categories

### 1. Core Styles (`templates.py`)
Basic styles for common use cases:
- `default` - Standard white text
- `rainbow` - Colorful rainbow effect
- `alert` - Red pulsing for urgent messages
- `success` - Green for positive messages
- `info` - Blue for informational content
- `fast`/`slow` - Speed variations
- `static` - Non-scrolling display
- `neon` - Bright neon appearance
- `retro` - Green terminal style
- `elegant` - Soft, sophisticated look
- `warning` - Orange warning style
- `party` - Fun celebration effects
- `minimal` - Clean, simple style
- `high_contrast` - Maximum visibility

### 2. Theme Styles (`themes.py`)
Specialized styles for specific content types:
- `theme_park` - Optimized for park wait times
- `stock_ticker` - Financial data with color coding
- `weather` - Temperature-based colors
- `clock` - Time display formatting
- `sports_score` - Team colors and scores
- `news_ticker` - News headline formatting
- `transit` - Public transit arrivals
- `countdown` - Timer displays
- `calendar` - Event displays
- `crypto_ticker` - Cryptocurrency prices

### 3. Animation Styles (`animations.py`)
Visual effects and transitions:
- `smooth_scroll` - Eased scrolling
- `bouncy_scroll` - Bouncing effect
- `typewriter` - Character-by-character reveal
- `marquee` - Classic marquee
- `ticker` - News ticker style
- `crawl` - Star Wars text crawl
- `fade_transition` - Fade in/out
- `slide_transition` - Slide effects
- `reveal_transition` - Reveal animations
- `pulse_animation` - Pulsing brightness
- `rainbow_cycle` - Animated rainbow
- `breathing` - Gentle glow effect
- `sparkle` - Glitter effect
- `wave` - Wave motion
- `matrix_rain` - Matrix-style effect

### 4. Layout Styles (`layouts.py`)
Text positioning and arrangement:
- `single_line` - Standard scrolling
- `centered` - Center-aligned static
- `two_line` - Title and content
- `split_screen` - Side-by-side areas
- `ticker` - Bottom ticker layout
- `header_footer` - Fixed header/footer
- `grid` - Grid-based layout
- `vertical_scroll` - Vertical scrolling
- `side_by_side` - Comparison layout
- `full_screen` - Maximum text size
- `compact` - Minimal spacing
- `padded` - Comfortable margins
- `responsive` - Adapts to content

### 5. Color Schemes (`colors.py`)
Pre-defined color palettes:
- `neon`, `pastel`, `high_contrast`
- `dark_mode`, `retro_terminal`
- `ocean`, `sunset`, `forest`
- `cyberpunk`, `monochrome`, `rainbow`
- `accessibility` - Colorblind-friendly
- Seasonal: `winter`, `spring`, `summer`, `autumn`

## Advanced Usage

### Creating Custom Styles

```python
from cpyapp.styles import create_style, BaseStyle

# Method 1: Dictionary-based
custom = create_style({
    'text_color': '0xFF00FF',
    'scroll_speed': 0.04,
    'pulse_enabled': True,
    'brightness': 0.8
})

# Method 2: Extend BaseStyle
class MyStyle(BaseStyle):
    def __init__(self):
        super().__init__("my_style")
        self.update_properties({
            'text_color': '0x00FFFF',
            'scroll_speed': 0.045,
            'pulse_enabled': True
        })
```

### Combining Styles

```python
from cpyapp.styles import create_composite, merge_styles

# Composite style from multiple sources
style = create_composite(
    'rainbow',      # Base colors
    'fast',         # Speed
    'two_line',     # Layout
    brightness=0.9  # Custom property
)

# Merge styles
merged = merge_styles('alert', 'typewriter', 'centered')
```

### Applying Color Schemes

```python
from cpyapp.styles import get_style, apply_color_scheme

# Get a style and apply a color scheme
style = get_style('default')
apply_color_scheme(style, 'cyberpunk')
```

### Quick Style Helper

```python
from cpyapp.styles import quick_style

# Create a style with simple parameters
style = quick_style(
    color='red',
    speed='fast',
    effect='pulse',
    layout='centered'
)
```

## Style Properties

Common properties available in all styles:

### Text Properties
- `text_color` - Text color (hex or 'rainbow')
- `background_color` - Background color
- `font_scale` - Font size multiplier

### Animation Properties
- `scroll_speed` - Scroll speed (seconds per step)
- `scroll_delay` - Delay after scroll completes
- `scroll_direction` - Direction (left, right, up, down)
- `transition_effect` - Transition type
- `pulse_enabled` - Enable pulsing
- `rainbow_enabled` - Enable rainbow effect
- `breathe_enabled` - Enable breathing effect

### Layout Properties
- `text_align` - Horizontal alignment
- `vertical_align` - Vertical alignment
- `padding_x` - Horizontal padding
- `padding_y` - Vertical padding

### Display Properties
- `brightness` - Overall brightness (0.0-1.0)
- `brightness_scale` - Color brightness scale
- `message_delay` - Delay between messages
- `static_duration` - Duration for static messages

## Integration with Display System

The styles work seamlessly with the existing display system:

```python
# Styles automatically configure the display
app = SimpleScrollApp("Hello", style="neon")

# Access the style instance
style = app.style

# Modify style properties at runtime
style.set_property('brightness', 0.9)
style.set_property('pulse_speed', 2.0)

# Apply style to display components
style.apply_to_display(app.display)
style.apply_to_label(text_label)
```

## Creating Theme-Specific Apps

```python
# Theme park wait times app
class WaitTimesApp(SimpleScrollApp):
    def __init__(self, park_data):
        super().__init__(
            data_source=park_data,
            style="theme_park"  # Automatically uses optimized styling
        )

# Stock ticker app
class StockApp(SimpleScrollApp):
    def __init__(self, stock_api):
        super().__init__(
            data_source=stock_api,
            style="stock_ticker"  # Green/red for gains/losses
        )
```

## Best Practices

1. **Start Simple**: Use named styles first
2. **Theme Matching**: Use theme styles for specific content
3. **Readability**: Consider brightness and contrast
4. **Performance**: Some effects use more CPU
5. **Accessibility**: Use high contrast for visibility

## Style Development

To create new styles:

1. Extend `BaseStyle` class
2. Define default properties in `__init__`
3. Override methods for custom behavior
4. Add to appropriate category module
5. Register in the factory mappings

Example:
```python
class MyNewStyle(BaseStyle):
    def __init__(self):
        super().__init__("my_new_style")
        self.update_properties({
            'text_color': ColorUtils.colors["White"],
            'custom_property': 'value'
        })
    
    def custom_method(self):
        # Add custom behavior
        pass
```

The styles system makes it easy to create beautiful LED matrix displays while maintaining flexibility for advanced customization.