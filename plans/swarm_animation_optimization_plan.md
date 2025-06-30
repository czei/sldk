# Swarm Animation Hardware Acceleration Implementation Plan

## Overview
This document provides a detailed implementation plan for converting the `theme_park_waits_swarm.py` animation from pixel-by-pixel software rendering to hardware-accelerated displayio/rgbmatrix rendering for CircuitPython on the MatrixPortal S3.

## Current Performance Issues
1. **Pixel-by-pixel rendering**: ~700+ individual `set_pixel()` calls per frame
2. **Per-frame color calculations**: HSV→RGB conversions for every pixel/bird
3. **No hardware acceleration**: PyLEDSimulator doesn't expose displayio/rgbmatrix
4. **Memory inefficiency**: Individual bird objects with floating-point positions

## Target Architecture
- Use `displayio.Bitmap` for layered rendering
- Pre-computed `displayio.Palette` for color management
- Hardware-accelerated `rgbmatrix` with DMA support
- Efficient bitmap updates with minimal CPU usage

## Implementation Phases

### Phase 1: Basic Hardware-Accelerated Framework (Priority: CRITICAL)

#### 1.1 Create New Hardware-Optimized File
**File**: `src/animations/swarm_animation_hw.py`

**Initial Structure**:
```python
import board
import displayio
import rgbmatrix
import framebufferio
import time
import math
import random

class SwarmAnimationHW:
    def __init__(self):
        # Display dimensions
        self.width = 64
        self.height = 32
        
        # Animation state
        self.frame_count = 0
        self.start_time = time.monotonic()
        
        # Initialize hardware display
        self._init_display()
        
        # Initialize bitmaps and palettes
        self._init_graphics()
        
        # Get target pixels for THEME PARK WAITS
        self.target_pixels = self._get_theme_park_waits_pixels()
        self.captured_pixels = set()
        
        # Bird flock management
        self.max_birds = 64  # Hardware-friendly limit
        self.birds = []
```

#### 1.2 Hardware Display Initialization
```python
def _init_display(self):
    """Initialize rgbmatrix hardware."""
    self.matrix = rgbmatrix.RGBMatrix(
        width=self.width,
        height=self.height,
        bit_depth=4,  # 16 colors
        rgb_pins=[
            board.MTX_R1, board.MTX_G1, board.MTX_B1,
            board.MTX_R2, board.MTX_G2, board.MTX_B2
        ],
        addr_pins=[
            board.MTX_ADDRA, board.MTX_ADDRB,
            board.MTX_ADDRC, board.MTX_ADDRD
        ],
        clock_pin=board.MTX_CLK,
        latch_pin=board.MTX_LAT,
        output_enable_pin=board.MTX_OE,
        doublebuffer=True  # Enable double buffering
    )
    
    self.display = framebufferio.FramebufferDisplay(
        self.matrix,
        auto_refresh=False  # Manual refresh for control
    )
```

#### 1.3 Graphics Resources Initialization
```python
def _init_graphics(self):
    """Initialize bitmaps and palettes."""
    # Text layer with 16 colors
    self.text_bitmap = displayio.Bitmap(self.width, self.height, 16)
    self.text_palette = displayio.Palette(16)
    
    # Bird layer with 8 colors
    self.bird_bitmap = displayio.Bitmap(self.width, self.height, 8)
    self.bird_palette = displayio.Palette(8)
    
    # Initialize palettes
    self._init_rainbow_palette(self.text_palette, 16)
    self._init_rainbow_palette(self.bird_palette, 8)
    
    # Create TileGrids
    self.text_tilegrid = displayio.TileGrid(
        self.text_bitmap,
        pixel_shader=self.text_palette
    )
    self.bird_tilegrid = displayio.TileGrid(
        self.bird_bitmap,
        pixel_shader=self.bird_palette
    )
    
    # Create display group
    self.root_group = displayio.Group()
    self.root_group.append(self.text_tilegrid)
    self.root_group.append(self.bird_tilegrid)
    
    # Set as display root
    self.display.root_group = self.root_group

def _init_rainbow_palette(self, palette, num_colors):
    """Initialize a rainbow gradient palette."""
    # Reserve index 0 for transparent/black
    palette[0] = 0x000000
    
    for i in range(1, num_colors):
        hue = (i - 1) / (num_colors - 1)
        r, g, b = self._hsv_to_rgb(hue, 1.0, 1.0)
        palette[i] = (r << 16) | (g << 8) | b
```

### Phase 2: Optimized Animation Logic (Priority: HIGH)

#### 2.1 Efficient Bird Class
```python
class Bird:
    """Lightweight bird for hardware rendering."""
    __slots__ = ['x', 'y', 'vx', 'vy', 'color_index']
    
    def __init__(self, x, y, vx, vy):
        # Use integer positions scaled by 256 for sub-pixel precision
        self.x = int(x * 256)
        self.y = int(y * 256)
        self.vx = int(vx * 256)
        self.vy = int(vy * 256)
        self.color_index = random.randint(1, 7)
    
    def update(self):
        """Update bird position."""
        self.x += self.vx
        self.y += self.vy
    
    def get_pixel_pos(self):
        """Get integer pixel position."""
        return (self.x >> 8, self.y >> 8)
    
    def is_on_screen(self, width, height):
        """Check if bird is visible."""
        px = self.x >> 8
        py = self.y >> 8
        return 0 <= px < width and 0 <= py < height
```

#### 2.2 Optimized Update Loop
```python
def update_frame(self):
    """Update one frame of animation."""
    self.frame_count += 1
    elapsed = time.monotonic() - self.start_time
    
    # Update birds
    self._update_birds()
    
    # Spawn new birds if needed
    if len(self.birds) < self.max_birds and len(self.captured_pixels) < len(self.target_pixels):
        self._spawn_birds()
    
    # Clear bitmaps
    self.text_bitmap.fill(0)
    self.bird_bitmap.fill(0)
    
    # Render captured text with animated colors
    self._render_text(elapsed)
    
    # Render birds
    self._render_birds()
    
    # Animate palettes
    if self.frame_count % 4 == 0:  # Rotate colors every 4 frames
        self._rotate_palette(self.text_palette)
        self._rotate_palette(self.bird_palette)
    
    # Refresh display
    self.display.refresh()

def _render_text(self, elapsed):
    """Render captured text pixels with spatial color variation."""
    for pixel in self.captured_pixels:
        x, y = pixel
        # Create wave effect across display
        color_offset = (x + y * 2 + int(elapsed * 10)) % 15
        self.text_bitmap[x, y] = color_offset + 1

def _render_birds(self):
    """Render birds to bitmap."""
    for bird in self.birds:
        if bird.is_on_screen(self.width, self.height):
            x, y = bird.get_pixel_pos()
            self.bird_bitmap[x, y] = bird.color_index
```

### Phase 3: Color Animation System (Priority: HIGH)

#### 3.1 Efficient Palette Animation
```python
def _rotate_palette(self, palette):
    """Rotate palette colors for animation."""
    if len(palette) <= 1:
        return
    
    # Save last color (skip index 0 which is transparent)
    temp = palette[len(palette) - 1]
    
    # Shift colors forward
    for i in range(len(palette) - 1, 1, -1):
        palette[i] = palette[i - 1]
    
    palette[1] = temp

def _pulse_palette(self, palette, phase):
    """Pulse brightness of palette colors."""
    for i in range(1, len(palette)):
        # Get base color
        base_color = palette[i]
        r = (base_color >> 16) & 0xFF
        g = (base_color >> 8) & 0xFF
        b = base_color & 0xFF
        
        # Apply sine wave brightness
        brightness = 0.7 + 0.3 * math.sin(phase + i * 0.5)
        r = int(r * brightness)
        g = int(g * brightness)
        b = int(b * brightness)
        
        palette[i] = (r << 16) | (g << 8) | b
```

#### 3.2 Pre-computed Color Tables
```python
# At module level, pre-compute color lookup tables
HSV_TO_RGB_LUT = []
for h in range(256):
    hue = h / 256.0
    r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
    HSV_TO_RGB_LUT.append((r << 16) | (g << 8) | b)

# Fast color lookup
def get_rainbow_color(index):
    """Get rainbow color from pre-computed table."""
    return HSV_TO_RGB_LUT[index & 0xFF]
```

### Phase 4: Memory Optimization (Priority: MEDIUM)

#### 4.1 Object Pooling for Birds
```python
class BirdPool:
    """Object pool to reduce allocations."""
    def __init__(self, size=128):
        self.pool = [Bird(0, 0, 0, 0) for _ in range(size)]
        self.active_count = 0
    
    def spawn(self, x, y, vx, vy):
        """Get bird from pool."""
        if self.active_count < len(self.pool):
            bird = self.pool[self.active_count]
            bird.x = int(x * 256)
            bird.y = int(y * 256)
            bird.vx = int(vx * 256)
            bird.vy = int(vy * 256)
            bird.color_index = (self.active_count % 7) + 1
            self.active_count += 1
            return bird
        return None
    
    def remove(self, index):
        """Return bird to pool."""
        if 0 <= index < self.active_count:
            # Swap with last active bird
            self.pool[index], self.pool[self.active_count - 1] = \
                self.pool[self.active_count - 1], self.pool[index]
            self.active_count -= 1
```

#### 4.2 Spatial Optimization for Target Detection
```python
def _check_bird_captures(self):
    """Efficiently check if birds hit target pixels."""
    # Create spatial hash for remaining targets
    target_hash = {}
    for pixel in (self.target_pixels - self.captured_pixels):
        key = (pixel[0] >> 2, pixel[1] >> 2)  # 4x4 grid cells
        if key not in target_hash:
            target_hash[key] = []
        target_hash[key].append(pixel)
    
    # Check birds against spatial hash
    for bird in self.birds[:self.bird_pool.active_count]:
        if bird.is_on_screen(self.width, self.height):
            x, y = bird.get_pixel_pos()
            key = (x >> 2, y >> 2)
            
            # Check current and adjacent cells
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    check_key = (key[0] + dx, key[1] + dy)
                    if check_key in target_hash:
                        for target in target_hash[check_key]:
                            if target == (x, y) and target not in self.captured_pixels:
                                self.captured_pixels.add(target)
                                return  # One capture per frame
```

### Phase 5: Integration and Testing (Priority: HIGH)

#### 5.1 Main Animation Loop
```python
def run_animation():
    """Main animation loop."""
    animation = SwarmAnimationHW()
    
    # Performance tracking
    frame_times = []
    last_report = time.monotonic()
    
    print("Starting hardware-accelerated swarm animation...")
    print(f"Target: {len(animation.target_pixels)} pixels")
    
    while len(animation.captured_pixels) < len(animation.target_pixels):
        frame_start = time.monotonic()
        
        # Update animation
        animation.update_frame()
        
        # Track performance
        frame_time = time.monotonic() - frame_start
        frame_times.append(frame_time)
        
        # Report stats every second
        if time.monotonic() - last_report > 1.0:
            avg_frame_time = sum(frame_times) / len(frame_times)
            fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
            
            print(f"FPS: {fps:.1f}, Captured: {len(animation.captured_pixels)}/{len(animation.target_pixels)}")
            
            frame_times = []
            last_report = time.monotonic()
    
    print("Animation complete!")
    
    # Show completed text for 2 seconds
    end_time = time.monotonic() + 2.0
    while time.monotonic() < end_time:
        animation.update_frame()
```

#### 5.2 CircuitPython Entry Point
```python
# code.py or main entry point
import gc
import supervisor

# Force garbage collection before animation
gc.collect()

# Disable auto-reload during animation
supervisor.runtime.autoreload = False

try:
    from src.animations.swarm_animation_hw import run_animation
    run_animation()
except Exception as e:
    print(f"Animation error: {e}")
    import traceback
    traceback.print_exception(e)
finally:
    # Re-enable auto-reload
    supervisor.runtime.autoreload = True
```

## Testing Strategy

### Performance Benchmarks
1. **Target FPS**: 30+ FPS with full animation
2. **Memory usage**: < 50% of available RAM
3. **CPU usage**: < 70% during animation

### Test Cases
1. **Basic rendering**: Verify bitmaps display correctly
2. **Color animation**: Confirm smooth palette rotation
3. **Bird movement**: Check collision detection with targets
4. **Memory stability**: Run for extended periods without crashes
5. **Edge cases**: Test with 0 birds, max birds, rapid spawning

### Debugging Tools
```python
# Add debug overlay
def _draw_debug_info(self):
    """Draw performance stats on display."""
    if self.frame_count % 30 == 0:  # Every second at 30 FPS
        print(f"Birds: {self.bird_pool.active_count}, "
              f"Captured: {len(self.captured_pixels)}, "
              f"Frame: {self.frame_count}")
```

## Migration Path

1. **Week 1**: Implement Phase 1-2 (basic framework)
2. **Week 2**: Add Phase 3-4 (optimizations)
3. **Week 3**: Testing and performance tuning
4. **Week 4**: Documentation and deployment

## Success Metrics
- Animation runs at 30+ FPS consistently
- Memory usage remains stable
- Visual quality matches or exceeds original
- Code is maintainable and well-documented

## Notes for Implementation
- Start with minimal features and add complexity gradually
- Test on actual hardware frequently
- Profile memory usage with `gc.mem_info()`
- Use `supervisor.ticks_ms()` for precise timing
- Consider adding configuration for different display sizes