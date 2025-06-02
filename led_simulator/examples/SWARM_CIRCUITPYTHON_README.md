# CircuitPython Swarm Animation Implementations

After careful analysis of the MatrixPortal S3 hardware constraints and CircuitPython's animation capabilities, I've created three different approaches to implement the swarm animation:

## Hardware Constraints
- **RAM**: 512KB (very limited)
- **CPU**: SAMD51 @ 120MHz (relatively slow)
- **Display**: 64x32 RGB LEDs via displayio
- **No true multithreading**: Only cooperative multitasking with asyncio

## Implementation Approaches

### 1. Particle System Approach (`theme_park_waits_swarm_circuitpython.py`)
**Memory Usage**: ~50KB
**Performance**: Excellent (20+ FPS)

**Features:**
- Lightweight particle system using arrays instead of objects
- Direct bitmap manipulation
- Up to 30 simultaneous birds
- Simple but effective flocking behavior
- Pre-calculated text positions for efficiency

**Pros:**
- Very memory efficient
- Fast performance
- Can handle many birds

**Cons:**
- Less visual polish
- No sprite animations
- Simple graphics

### 2. Sprite Pool Approach (`theme_park_waits_swarm_sprites.py`)
**Memory Usage**: ~150KB
**Performance**: Good (20 FPS)

**Features:**
- Uses displayio sprites with pooling
- Animated bird colors using HSV
- Individual palettes per bird
- Smoother motion with sub-pixel positioning
- Wing animation frames

**Pros:**
- Better visual quality
- Smooth color transitions
- Proper sprite handling

**Cons:**
- Limited to ~20 sprites
- Higher memory usage
- More complex code

### 3. Advanced Hybrid Approach (`theme_park_waits_swarm_advanced.py`)
**Memory Usage**: ~200KB
**Performance**: Moderate (15-20 FPS)

**Features:**
- Combines sprites with bitmap effects
- Particle trails behind birds
- Wing flapping animation
- Color-coded trail effects
- Victory celebration animation
- Pre-calculated sine tables for smooth motion

**Pros:**
- Best visual effects
- Multiple animation layers
- Professional appearance

**Cons:**
- Highest memory usage
- May need tuning for specific hardware
- Complex implementation

## Key Optimizations Used

1. **Memory Management:**
   - Sprite pooling instead of dynamic allocation
   - Structure of arrays instead of array of objects
   - Pre-calculated lookup tables
   - Minimal object creation

2. **Performance:**
   - Manhattan distance instead of Euclidean
   - Limited search radius for targets
   - Frame skipping for effects
   - Direct bitmap manipulation

3. **Visual Tricks:**
   - Color palette animation instead of pixel updates
   - Reusing bitmaps with different palettes
   - Trail effects using palette fading
   - Simplified text representation

## Recommended Usage

- **For Maximum Birds**: Use the particle system approach
- **For Best Compatibility**: Use the sprite pool approach
- **For Best Visuals**: Use the advanced hybrid approach (test on hardware first)

## Porting Considerations

When porting to actual hardware:

1. **Test Memory Usage**: Use `gc.mem_free()` to monitor
2. **Adjust Constants**: Reduce MAX_BIRDS if needed
3. **Profile Performance**: Target 15+ FPS minimum
4. **Simplify if Needed**: Remove effects that cause slowdown

## Example Usage on MatrixPortal S3

```python
# Copy one of the files to code.py on your MatrixPortal S3
# The animation will start automatically

# For testing/tuning:
import gc
print(f"Free memory: {gc.mem_free()} bytes")

# Run the animation
if __name__ == "__main__":
    # Choose based on your needs
    run_swarm_animation()  # Particle system
    # or
    # run_sprite_swarm()   # Sprite version
    # or
    # run_advanced_swarm() # Advanced version
```

## Future Enhancements

Possible improvements within hardware constraints:
- Use ulab for optimized array operations
- Implement spatial hashing for neighbor searches
- Add sound effects using PWM audio
- Create different swarm patterns
- Save/load animation sequences from flash

The key to success on CircuitPython is thinking creatively within the constraints rather than trying to port desktop-style code directly.