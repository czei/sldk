"""
Color utilities for handling color conversions and manipulations.
Copyright 2024 3DUPFitters LLC
"""


class ColorUtils:
    """Utilities for handling colors and conversions"""
    
    # Color definitions as a class variable
    colors = {
        "Red": "0xff0000",
        "Green": "0x00ff00",
        "Blue": "0x0000ff",
        "White": "0xffffff",
        "Black": "0x000000",
        "Purple": "0x800080",
        "Yellow": "0xffff00",
        "Orange": "0xffa500",
        "Pink": "0xffc0cb",
        "Old Lace": "0xfdf5e6"
    }

    @staticmethod
    def to_rgb(color_hex):
        """
        Convert a hex color string to an RGB tuple
        
        Args:
            color_hex: A hexadecimal color string (e.g., "0xRRGGBB")
            
        Returns:
            A tuple of (red, green, blue) values, each 0-255
        """
        color_int = int(color_hex, 16)
        r = (color_int >> 16) & 0xFF
        g = (color_int >> 8) & 0xFF
        b = color_int & 0xFF
        return r, g, b

    @staticmethod
    def from_rgb(r, g, b):
        """
        Convert RGB values to a hex color string
        
        Args:
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)
            
        Returns:
            A hexadecimal color string (e.g., "0xRRGGBB")
        """
        return f"0x{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def scale_color(color_hex, scale_factor):
        """
        Scale a color's brightness by a factor
        
        Args:
            color_hex: A hexadecimal color string (e.g., "0xRRGGBB")
            scale_factor: Factor to scale brightness by (0.0-1.0)
            
        Returns:
            A new hexadecimal color string with adjusted brightness
        """
        if color_hex == "0x000000":
            return color_hex
            
        r, g, b = ColorUtils.to_rgb(color_hex)
        r = int(r * scale_factor)
        g = int(g * scale_factor)
        b = int(b * scale_factor)
        
        # Ensure values stay within valid range
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        
        return ColorUtils.from_rgb(r, g, b)