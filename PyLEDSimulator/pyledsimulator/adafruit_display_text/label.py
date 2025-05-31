"""Text label implementation for displayio."""

from ..displayio import Group, Bitmap, Palette, TileGrid
from ..core.color_utils import rgb888_to_rgb565
from ..terminalio.font_scaler import get_font_for_scale


class Label(Group):
    """A label displaying a string of text.
    
    Compatible with CircuitPython's adafruit_display_text.label.Label API.
    """
    
    def __init__(self, font, *, text="", color=0xFFFFFF, background_color=None,
                 line_spacing=1.25, background_tight=False, padding_top=0,
                 padding_bottom=0, padding_left=0, padding_right=0,
                 anchor_point=None, anchored_position=None, scale=1,
                 base_alignment=False, tab_replacement=(4, " "), label_direction="LTR",
                 **kwargs):
        """Initialize Label.
        
        Args:
            font: Font to use for text
            text: Initial text to display
            color: Text color (RGB565 or RGB888)
            background_color: Background color (None for transparent)
            line_spacing: Line spacing multiplier
            background_tight: Whether background fits text tightly
            padding_top: Top padding in pixels
            padding_bottom: Bottom padding in pixels
            padding_left: Left padding in pixels
            padding_right: Right padding in pixels
            anchor_point: Anchor point as (x, y) normalized values
            anchored_position: Position for anchor point
            scale: Scale factor for text
            base_alignment: Whether to align text baselines
            tab_replacement: Tuple of (spaces, character) for tab replacement
            label_direction: Text direction ("LTR" or "RTL")
            **kwargs: Additional keyword arguments
        """
        super().__init__(scale=scale, **kwargs)
        
        # If using terminalio.FONT, automatically select font based on scale
        try:
            from ..terminalio import FONT as DEFAULT_FONT
            if font is DEFAULT_FONT:
                self.font = get_font_for_scale(scale)
            else:
                self.font = font
        except ImportError:
            # If terminalio is not available, just use the provided font
            self.font = font
        self._text = ""
        self._color = color if isinstance(color, int) else rgb888_to_rgb565(*color)
        self._background_color = background_color
        self.line_spacing = line_spacing
        self.background_tight = background_tight
        self.padding_top = padding_top
        self.padding_bottom = padding_bottom
        self.padding_left = padding_left
        self.padding_right = padding_right
        self._anchor_point = anchor_point
        self._anchored_position = anchored_position
        self.base_alignment = base_alignment
        self.tab_replacement = tab_replacement
        self.label_direction = label_direction
        
        # Internal display objects
        self._bitmap = None
        self._palette = None
        self._tilegrid = None
        
        # Set initial text
        if text:
            self.text = text
            
    @property
    def text(self):
        """Get the current text."""
        return self._text
        
    @text.setter
    def text(self, new_text):
        """Set the text to display.
        
        Args:
            new_text: New text string
        """
        if new_text == self._text:
            return
            
        self._text = str(new_text)
        self._update_text()
        
    @property
    def color(self):
        """Get the text color."""
        return self._color
        
    @color.setter
    def color(self, new_color):
        """Set the text color.
        
        Args:
            new_color: New color value
        """
        self._color = new_color if isinstance(new_color, int) else rgb888_to_rgb565(*new_color)
        if self._palette:
            self._palette[1] = self._color
            
    @property
    def background_color(self):
        """Get the background color."""
        return self._background_color
        
    @background_color.setter
    def background_color(self, new_color):
        """Set the background color.
        
        Args:
            new_color: New color value or None for transparent
        """
        self._background_color = new_color
        if self._palette and new_color is not None:
            if isinstance(new_color, int):
                self._palette[0] = new_color
            else:
                self._palette[0] = rgb888_to_rgb565(*new_color)
        self._update_text()
        
    @property
    def anchor_point(self):
        """Get the anchor point."""
        return self._anchor_point
        
    @anchor_point.setter
    def anchor_point(self, new_anchor):
        """Set the anchor point.
        
        Args:
            new_anchor: (x, y) tuple with normalized coordinates (0.0-1.0)
        """
        self._anchor_point = new_anchor
        self._update_position()
        
    @property
    def anchored_position(self):
        """Get the anchored position."""
        return self._anchored_position
        
    @anchored_position.setter
    def anchored_position(self, new_position):
        """Set the anchored position.
        
        Args:
            new_position: (x, y) position for the anchor point
        """
        self._anchored_position = new_position
        self._update_position()
        
    def _update_text(self):
        """Update the text bitmap and display objects."""
        # Replace tabs
        display_text = self._text
        if '\t' in display_text:
            tab_spaces, tab_char = self.tab_replacement
            display_text = display_text.replace('\t', tab_char * tab_spaces)
            
        # Calculate text dimensions
        lines = display_text.split('\n')
        max_width = 0
        total_height = 0
        
        for i, line in enumerate(lines):
            line_width = 0
            line_height = 0
            
            for char in line:
                glyph = self.font.get_glyph(char)
                if glyph:
                    line_width += glyph['dx']
                    line_height = max(line_height, glyph['height'])
                    
            max_width = max(max_width, line_width)
            if i == 0:
                total_height = self.font.height  # Use font height, not glyph height
            else:
                total_height += int(self.font.height * self.line_spacing)
                
        # Add padding
        bitmap_width = max_width + self.padding_left + self.padding_right
        bitmap_height = total_height + self.padding_top + self.padding_bottom
        
        # Ensure minimum size
        bitmap_width = max(1, bitmap_width)
        bitmap_height = max(1, bitmap_height)
        
        # Create new bitmap and palette
        self._bitmap = Bitmap(bitmap_width, bitmap_height, 2)
        self._palette = Palette(2)
        
        # Set colors
        if self._background_color is None:
            self._palette.make_transparent(0)
        else:
            self._palette[0] = self._background_color
        self._palette[1] = self._color
        
        # Fill background
        if self._background_color is not None:
            self._bitmap.fill(0)
            
        # Render text
        y_offset = self.padding_top
        
        for line_num, line in enumerate(lines):
            x_offset = self.padding_left
            
            # Handle RTL text direction
            if self.label_direction == "RTL":
                line = line[::-1]
                
            for char in line:
                glyph = self.font.get_glyph(char)
                if not glyph:
                    continue
                    
                # Get glyph bitmap
                glyph_bitmap = glyph['bitmap']
                glyph_x_offset = glyph.get('x_offset', 0)
                glyph_y_offset = glyph.get('y_offset', 0)
                
                # Calculate position
                draw_x = x_offset + glyph_x_offset
                draw_y = y_offset + glyph_y_offset
                
                # Copy glyph pixels to main bitmap
                for gy in range(glyph_bitmap.height):
                    for gx in range(glyph_bitmap.width):
                        if glyph_bitmap[gx, gy] > 0:
                            bx = draw_x + gx
                            by = draw_y + gy
                            if 0 <= bx < bitmap_width and 0 <= by < bitmap_height:
                                self._bitmap[bx, by] = 1
                                
                x_offset += glyph['dx']
                
            # Move to next line
            if line_num < len(lines) - 1:
                y_offset += int(self.font.height * self.line_spacing)
                
        # Update or create tilegrid
        if self._tilegrid:
            self.remove(self._tilegrid)
            
        self._tilegrid = TileGrid(self._bitmap, pixel_shader=self._palette)
        self.append(self._tilegrid)
        
        # Update position if anchored
        self._update_position()
        
    def _update_position(self):
        """Update position based on anchor point."""
        if self._anchor_point and self._anchored_position and self._bitmap:
            anchor_x, anchor_y = self._anchor_point
            pos_x, pos_y = self._anchored_position
            
            # Calculate actual position
            self.x = int(pos_x - self._bitmap.width * anchor_x)
            self.y = int(pos_y - self._bitmap.height * anchor_y)
            
    @property
    def bounding_box(self):
        """Get the bounding box of the label.
        
        Returns:
            Tuple of (x, y, width, height)
        """
        if self._bitmap:
            return (self.x, self.y, self._bitmap.width, self._bitmap.height)
        return (self.x, self.y, 0, 0)
        
    @property
    def width(self):
        """Get the width of the label."""
        return self._bitmap.width if self._bitmap else 0
        
    @property
    def height(self):
        """Get the height of the label."""
        return self._bitmap.height if self._bitmap else 0