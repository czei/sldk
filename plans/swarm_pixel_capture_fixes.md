# Swarm Animation Pixel Capture Fixes

## Issue
The optimized swarm animation was not capturing all pixels of the THEME PARK WAITS text, leaving gaps in the letters.

## Root Causes
1. **Birds were deactivating after capturing a single pixel** - This meant each bird could only light up one LED before disappearing
2. **Single-point collision detection** - Birds were only checking their exact center position
3. **Large bird sprites** - The 3x3 cross pattern made precise pixel capture difficult
4. **Insufficient bird spawning** - Not enough birds to cover all 507 target pixels

## Fixes Applied

### 1. Continuous Bird Flight
- Removed `self.active = False` after pixel capture
- Birds now continue flying and can capture multiple pixels
- This dramatically increases capture efficiency

### 2. Area-Based Capture
- Changed from single-point to area-based capture
- Birds now check a 3x3 area around their position
- Captures pixels at fractional positions (e.g., bird at 5.4, 3.4 can capture pixels at 5,3 and 6,4)

### 3. Visual Improvements
- Reduced bird sprite to single pixel (center only) for cleaner appearance
- Maintained 3x3 sprite size for compatibility but only center pixel is visible

### 4. Increased Bird Density
- MAX_BIRDS: 100 → 200
- SPAWN_INTERVAL: 0.5s → 0.1s
- Spawn count: 5 → 20 birds per wave
- Active threshold: 50% → 90% of max birds

### 5. Enhanced Attraction
- Increased attraction range from 30 to 50 pixels
- Stronger attraction forces (0.6 near, 0.4 medium, 0.2 far)
- Better sampling of missing pixel clusters (10 → 20 samples)

### 6. Text Bitmap Management
- Explicit initialization of text bitmap to all black
- Immediate update of captured pixels in text bitmap
- Check to avoid overwriting already-set pixels

## Result
The animation now successfully captures all 507 pixels of THEME PARK WAITS text with:
- More natural bird movement (birds don't disappear after one capture)
- Complete text coverage without gaps
- Smooth rainbow wave animation on completed text
- Better visual appearance with single-pixel birds

## Performance Impact
- Negligible on hardware due to DMA-based rendering
- Slightly higher CPU usage in simulator due to more active birds
- Still maintains 30 FPS target refresh rate