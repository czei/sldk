"""
Simulated LED Matrix display for development on desktop platforms.
Uses Pygame to render a visual representation of the LED matrix.
Copyright 2024 3DUPFitters LLC
"""
import pygame
import time
import sys
import os
import asyncio
from PIL import Image, ImageDraw, ImageFont
from src.ui.display_interface import DisplayInterface
from src.utils.error_handler import ErrorHandler


# Initialize logger
logger = ErrorHandler("error_log")


class SimulatedLEDMatrix(DisplayInterface):
    """
    A simulated LED Matrix display for development purposes
    """
    
    def __init__(self, width=64, height=32, led_size=10, spacing=2, bg_color=(0, 0, 0)):
        """
        Initialize the simulated display
        
        Args:
            width: Width of the matrix in LEDs
            height: Height of the matrix in LEDs
            led_size: Size of each LED in pixels
            spacing: Spacing between LEDs in pixels
            bg_color: Background color as RGB tuple
        """
        self.width = width
        self.height = height
        self.led_size = led_size
        self.spacing = spacing
        self.bg_color = bg_color
        self.window_width = width * (led_size + spacing)
        self.window_height = height * (led_size + spacing)
        
        # Initialize display attributes
        self.pixels = [[(0, 0, 0) for _ in range(width)] for _ in range(height)]
        self.text = ""
        self.text_color = (255, 255, 255)
        self.scroll_position = 0
        self.brightness = 1.0
        self.rotation = 0
        self.running = True
        self.screen = None
        self.font = None
        self.text_surface = None
        self.current_image = None
        
        # For scrolling animation
        self.scroll_timer = time.time()
        self.frame_delay = 0.04
        
        logger.info("Initialized Simulated LED Matrix")
    
    def initialize(self):
        """Initialize the Pygame window and components"""
        try:
            pygame.init()
            pygame.display.set_caption("LED Matrix Simulator")
            self.screen = pygame.display.set_mode((self.window_width, self.window_height))
            
            # Find a suitable font
            font_path = self._find_font()
            font_size = max(14, min(self.height // 2, 24))  # Reasonable size based on matrix height
            
            try:
                if font_path:
                    self.font = pygame.font.Font(font_path, font_size)
                else:
                    # Fall back to system font
                    self.font = pygame.font.SysFont("monospace", font_size)
            except Exception as e:
                logger.error(e, "Error loading font, falling back to default")
                self.font = pygame.font.SysFont("monospace", font_size)
                
            # Set up the event handling for window close
            pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])
                
            logger.info("Pygame initialized successfully")
            return True
            
        except Exception as e:
            logger.error(e, "Failed to initialize Pygame")
            return False
    
    def _find_font(self):
        """Find a suitable font for the simulator"""
        # Try to use the same font as the hardware if available
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "..", "fonts", "tom-thumb.bdf"),
            os.path.join(os.path.dirname(__file__), "..", "fonts", "Teeny-Tiny-Pixls-5.bdf"),
            "/System/Library/Fonts/Monaco.ttf",  # macOS
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",  # Linux
            "C:\\Windows\\Fonts\\consola.ttf"  # Windows
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.debug(f"Using font: {path}")
                return path
                
        return None
        
    def set_text(self, text, color=None):
        """
        Set the text to display
        
        Args:
            text: The text to display
            color: RGB color tuple (default: white)
        """
        self.text = text
        
        if color:
            if isinstance(color, int):
                # Convert hex to RGB tuple
                r = (color >> 16) & 0xFF
                g = (color >> 8) & 0xFF
                b = color & 0xFF
                self.text_color = (r, g, b)
            else:
                self.text_color = color
        
        if self.font and text:
            try:
                self.text_surface = self.font.render(text, True, self.text_color)
                self.scroll_position = self.window_width
            except Exception as e:
                logger.error(e, f"Error rendering text: {text}")
    
    def scroll(self, frame_delay=0.04):
        """Scroll the text across the display"""
        self.frame_delay = frame_delay
        # Actual scrolling happens in update() method
    
    def clear(self):
        """Clear the display"""
        self.pixels = [[(0, 0, 0) for _ in range(self.width)] for _ in range(self.height)]
        self.text = ""
        self.text_surface = None
        self.current_image = None
    
    def update(self):
        """Update the display state and render to screen"""
        # Check for quit events
        self._handle_events()
        
        if not self.screen:
            return False
            
        # Clear screen with background color
        self.screen.fill(self.bg_color)
        
        # Draw LED grid
        for y in range(self.height):
            for x in range(self.width):
                color = self._apply_brightness(self.pixels[y][x])
                rect = pygame.Rect(
                    x * (self.led_size + self.spacing),
                    y * (self.led_size + self.spacing),
                    self.led_size,
                    self.led_size
                )
                pygame.draw.rect(self.screen, color, rect)
        
        # Draw image if available
        if self.current_image:
            img_surface = pygame.surfarray.make_surface(self.current_image)
            self.screen.blit(img_surface, (0, 0))
        
        # Handle text scrolling
        if self.text_surface:
            current_time = time.time()
            if current_time - self.scroll_timer > self.frame_delay:
                self.scroll_timer = current_time
                self.scroll_position -= 1
                
                # Reset position when text scrolls off screen
                if self.scroll_position < -self.text_surface.get_width():
                    self.scroll_position = self.window_width
            
            # Draw text
            text_y = (self.window_height - self.text_surface.get_height()) // 2
            self.screen.blit(self.text_surface, (self.scroll_position, text_y))
        
        # Update the display
        pygame.display.flip()
        return True
    
    def show_image(self, image, x=0, y=0):
        """
        Display an image on the matrix
        
        Args:
            image: PIL Image object
            x: X position
            y: Y position
        """
        try:
            # If it's a PIL Image, convert to pygame surface
            if hasattr(image, 'mode') and image.mode:
                # Resize to fit matrix if needed
                width, height = image.size
                if width > self.width or height > self.height:
                    image = image.resize((self.width, self.height))
                
                # Convert PIL Image to pygame surface
                image_data = image.convert('RGB').tobytes()
                
                # Create a 3D array for the pixel data
                pixel_array = [[[0 for _ in range(3)] for _ in range(image.width)] for _ in range(image.height)]
                
                # Fill the array with pixel data
                for py in range(image.height):
                    for px in range(image.width):
                        r, g, b = image.getpixel((px, py))
                        self.pixels[y + py][x + px] = (r, g, b)
                
                # Store the image for rendering
                self.current_image = pygame.Surface((image.width, image.height))
                pygame.surfarray.pixels3d(self.current_image)[:] = pixel_array
                
        except Exception as e:
            logger.error(e, "Error displaying image")
    
    def set_brightness(self, brightness):
        """
        Set the display brightness
        
        Args:
            brightness: Float between 0.0 and 1.0
        """
        self.brightness = min(max(brightness, 0.0), 1.0)
    
    def set_rotation(self, rotation):
        """
        Set display rotation
        
        Args:
            rotation: Rotation angle in degrees (0, 90, 180, 270)
        """
        self.rotation = rotation
    
    def _handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    pygame.quit()
                    sys.exit()
    
    def _apply_brightness(self, color):
        """Apply brightness adjustment to a color"""
        r, g, b = color
        return (
            int(r * self.brightness),
            int(g * self.brightness),
            int(b * self.brightness)
        )
    
    async def run_async(self):
        """Run the display in an async loop"""
        while self.running:
            self.update()
            await asyncio.sleep(0.01)  # Small delay to prevent CPU hogging