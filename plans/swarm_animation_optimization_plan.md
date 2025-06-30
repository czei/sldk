# Swarm Animation Hardware Acceleration Plan

## Performance Analysis

### Current Implementation Issues
The swarm animation in `theme_park_waits_swarm.py` has severe performance bottlenecks:

1. **Pixel-by-pixel rendering**: Makes thousands of individual `set_pixel()` calls per frame
   - Line 744: `device.matrix.set_pixel(pixel[0], pixel[1], text_color)` for captured text
   - Line 752: `device.matrix.set_pixel(bird_x, bird_y, bird_color)` for each bird
   - With ~500 captured pixels + 100-500 birds = 600-1000 set_pixel calls per frame

2. **No hardware acceleration**: Not using displayio/rgbmatrix DMA capabilities
3. **Blocking updates**: Each pixel update blocks the CPU
4. **Memory inefficiency**: Creating new color tuples every frame

### Hardware Capabilities
The MatrixPortal S3 (ESP32-S3) supports:
- DMA (Direct Memory Access) for display updates
- Hardware-accelerated bitmap rendering
- Double buffering for smooth animation
- Efficient palette-based color management

## Optimization Strategy

### 1. Bitmap-Based Rendering
Replace pixel-by-pixel updates with bitmap operations:
```python
# Create bitmaps for different layers
background_bitmap = displayio.Bitmap(64, 32, 16)  # 16 colors
birds_bitmap = displayio.Bitmap(64, 32, 16)
text_bitmap = displayio.Bitmap(64, 32, 16)

# Use TileGrid for hardware-accelerated rendering
background_grid = displayio.TileGrid(background_bitmap, pixel_shader=palette)
```

### 2. Pre-computed Color Palettes
Instead of calculating colors every frame:
```python
# Pre-compute rainbow palette
rainbow_palette = displayio.Palette(16)
for i in range(16):
    hue = i / 16.0
    rainbow_palette[i] = hsv_to_rgb888(hue, 1.0, 1.0)
```

### 3. Sprite Pooling for Birds
Use displayio sprites with object pooling:
```python
# Create sprite pool
bird_sprites = displayio.Group(max_size=MAX_BIRDS)
for i in range(MAX_BIRDS):
    bird_bitmap = displayio.Bitmap(3, 3, 1)
    bird_sprite = displayio.TileGrid(bird_bitmap, pixel_shader=bird_palette, x=-10, y=-10)
    bird_sprites.append(bird_sprite)
```

### 4. Efficient Text Rendering
Pre-render text patterns into bitmap:
```python
# Pre-calculate text pixels once
TEXT_PIXELS = get_theme_park_waits_pixels()
# Store in bitmap for fast lookup
text_mask = displayio.Bitmap(64, 32, 2)  # 0=empty, 1=text
for x, y in TEXT_PIXELS:
    text_mask[x, y] = 1
```

### 5. Frame Buffer Management
Use double buffering with displayio Groups:
```python
# Layer management
main_group = displayio.Group()
main_group.append(background_layer)
main_group.append(text_layer)
main_group.append(birds_layer)
display.show(main_group)
```

## Implementation Plan

### Phase 1: Core Structure
1. Convert to displayio-based architecture
2. Implement bitmap layers
3. Create color palette system

### Phase 2: Bird System
1. Implement sprite pool
2. Convert bird movement to sprite updates
3. Add efficient collision detection

### Phase 3: Text Animation
1. Pre-render text patterns
2. Implement wave-based color animation
3. Use palette cycling for rainbow effects

### Phase 4: Optimization
1. Memory pooling for objects
2. Frame rate limiting
3. Batch updates

## Expected Performance Improvements
- **Current**: ~10 FPS with 500+ objects
- **Optimized**: 30-60 FPS with hardware acceleration
- **Memory**: 50% reduction through object pooling
- **CPU**: 80% reduction through DMA transfers

## Memory Budget
```
Bitmaps: 64x32x2 bytes x 3 layers = 12KB
Palettes: 16 colors x 3 bytes x 3 = 144 bytes
Sprites: 3x3x1 byte x 100 = 900 bytes
Total: ~13KB (well within ESP32-S3's 512KB RAM)
```

## Code Architecture
```python
class HardwareSwarmAnimation:
    def __init__(self):
        self.display = board.DISPLAY
        self.main_group = displayio.Group()
        self.setup_layers()
        self.setup_palettes()
        self.setup_sprites()
        
    def setup_layers(self):
        # Create bitmap layers
        pass
        
    def update(self):
        # Update only changed elements
        # Let hardware handle rendering
        pass
```

This approach leverages the ESP32-S3's hardware capabilities for smooth, efficient animation.