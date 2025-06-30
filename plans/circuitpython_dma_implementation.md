# CircuitPython DMA Implementation Details

## DisplayIO Library Components Using DMA

### 1. **RGBMatrix** (Primary DMA User)
```python
# In CircuitPython, when using RGB LED matrices:
import rgbmatrix
matrix = rgbmatrix.RGBMatrix(
    width=64, height=32,
    bit_depth=6,
    rgb_pins=[board.R0, board.G0, board.B0, board.R1, board.G1, board.B1],
    addr_pins=[board.A, board.B, board.C, board.D],
    clock_pin=board.CLK, latch_pin=board.LAT, output_enable_pin=board.OE
)
```
- **DMA Usage**: Continuously transfers framebuffer to LED matrix pins
- **ESP32-S3 Feature**: Uses I2S peripheral in parallel mode with DMA
- **Implementation**: `shared-module/rgbmatrix/RGBMatrix.c`

### 2. **Display.refresh()** 
```python
display.refresh()  # Triggers DMA transfer of framebuffer
```
- **DMA Usage**: Transfers displayio bitmap data to display hardware
- **Automatic**: When `auto_refresh=True`, DMA runs continuously
- **Implementation**: `shared-module/displayio/Display.c`

### 3. **FourWire** (SPI Displays)
```python
spi = busio.SPI(board.SCK, board.MOSI)
display_bus = displayio.FourWire(spi, command=board.DC, chip_select=board.CS)
```
- **DMA Usage**: ESP32-S3 SPI peripheral uses DMA for large transfers
- **Triggered by**: Bitmap blits and display updates
- **Implementation**: `ports/espressif/common-hal/displayio/ParallelBus.c`

### 4. **ParallelBus** (Parallel Displays)
```python
display_bus = displayio.ParallelBus(
    data_pins=[...],  # 8 or 16 data pins
    command=board.DC,
    chip_select=board.CS,
    write=board.WR,
    read=board.RD
)
```
- **DMA Usage**: ESP32-S3 LCD peripheral with DMA
- **Efficiency**: Transfers entire framebuffers without CPU
- **Implementation**: `ports/espressif/common-hal/paralleldisplay/ParallelBus.c`

## How DMA Works in DisplayIO

### 1. **Bitmap to Framebuffer**
```python
# When you do this:
bitmap = displayio.Bitmap(320, 240, 65536)
tilegrid = displayio.TileGrid(bitmap, pixel_shader=palette)
group.append(tilegrid)
display.show(group)

# Internally CircuitPython:
# 1. Renders group to framebuffer (CPU)
# 2. Sets up DMA descriptor chain
# 3. Starts DMA transfer (hardware)
# 4. CPU is free while transfer happens
```

### 2. **ESP32-S3 Specific Implementation**

The ESP32-S3 has several DMA-capable peripherals used by CircuitPython:

- **I2S DMA**: Used for RGBMatrix (LED panels)
  - Up to 40MHz pixel clock
  - Parallel output to multiple pins
  - Double-buffering for tear-free updates

- **SPI DMA**: Used for SPI displays
  - Up to 80MHz SPI clock
  - Automatic CS (chip select) handling
  - Linked-list DMA descriptors

- **LCD/CAM DMA**: Used for parallel displays
  - 8/16-bit parallel interface
  - RGB565/RGB888 support
  - Hardware color format conversion

### 3. **MatrixPortal S3 Specific**

For the MatrixPortal S3, the chain is:
```
displayio.Bitmap → displayio rendering → RGBMatrix framebuffer → I2S DMA → LED Matrix pins
```

## Code Example: Verifying DMA Usage

```python
import displayio
import rgbmatrix
import board
import time

# This uses DMA internally
display = board.DISPLAY  # On MatrixPortal S3

# Create large bitmap - would be slow without DMA
bitmap = displayio.Bitmap(64, 32, 256)
palette = displayio.Palette(256)

# Fill with data
for i in range(256):
    palette[i] = i << 16 | i << 8 | i  # Grayscale

# This triggers DMA setup
tilegrid = displayio.TileGrid(bitmap, pixel_shader=palette)
group = displayio.Group()
group.append(tilegrid)
display.show(group)

# Animation loop - CPU usage stays low due to DMA
while True:
    # Shift all pixels - CPU work
    for y in range(32):
        for x in range(63):
            bitmap[x, y] = bitmap[x + 1, y]
    
    # This triggers DMA transfer of entire framebuffer
    # CPU is free during the actual LED update
    display.refresh()  # Or automatic if auto_refresh=True
    
    time.sleep(0.01)
```

## Performance Metrics

### Without DMA (Theoretical)
- 64×32 display = 2048 pixels
- 3 bytes per pixel (RGB) = 6144 bytes
- At 30 FPS = 184,320 bytes/second
- CPU bit-banging at 10 cycles/byte = 1.8M cycles/second
- **Result**: 100% CPU usage on slow microcontroller

### With DMA (Actual)
- DMA setup: ~100 CPU cycles
- DMA transfer: 0 CPU cycles (happens in background)
- **Result**: <5% CPU usage for display updates

## Key CircuitPython Files

For ESP32-S3 MatrixPortal:
- `ports/espressif/common-hal/rgbmatrix/RGBMatrix.c` - DMA setup for LED matrix
- `ports/espressif/esp-idf/components/driver/i2s.c` - I2S DMA driver
- `shared-module/displayio/Display.c` - Display refresh logic
- `shared-module/rgbmatrix/RGBMatrix.c` - Matrix refresh coordination

## Summary

DMA in CircuitPython is implemented at the hardware abstraction layer (HAL) level. When you use displayio with compatible hardware like the ESP32-S3, you automatically get DMA benefits without explicit API calls. The key is using displayio's bitmap/group/display model rather than pixel-by-pixel updates.