import board
import displayio
import framebufferio
import rgbmatrix


displayio.release_displays()

DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 32
DISPLAY_ROTATION = 0
BIT_DEPTH = 4
matrix_board = rgbmatrix.RGBMatrix(
    width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT, bit_depth=BIT_DEPTH,
    rgb_pins=[
        board.MTX_R1,
        board.MTX_G1,
        board.MTX_B1,
        board.MTX_R2,
        board.MTX_G2,
        board.MTX_B2],
    addr_pins=[board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC, board.MTX_ADDRD],
    clock_pin=board.MTX_CLK,
    latch_pin=board.MTX_LAT,
    output_enable_pin=board.MTX_OE,
    serpentine=False,
    doublebuffer=True)


# Associate the RGB matrix with a Display so that we can use displayio features
display = framebufferio.FramebufferDisplay(matrix_board, auto_refresh=False)

# Create a bitmap with two colors
bitmap = displayio.Bitmap(display.width, display.height, 2)

# Create a two color palette
palette = displayio.Palette(2)
palette[0] = 0x000000
palette[1] = 0xffffff

# Create a TileGrid to render the bitmap on the display
tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)

g = displayio.Group()
display.root_group = g
g.append(tile_grid)

# Draw a frame around the image
FRAME_COLOR = 1
for x in range(DISPLAY_WIDTH):
    bitmap[x, 0] = FRAME_COLOR
for x in range(DISPLAY_WIDTH):
    bitmap[x, DISPLAY_HEIGHT-1] = FRAME_COLOR
for y in range(DISPLAY_HEIGHT):
    bitmap[0, y] = FRAME_COLOR
for y in range(DISPLAY_HEIGHT):
    bitmap[DISPLAY_WIDTH-1, y] = FRAME_COLOR

for x in range(0, DISPLAY_WIDTH):
    for y in range(0, DISPLAY_HEIGHT):
        bitmap[x, y] = FRAME_COLOR

display.show(g)

while True:
    display.refresh()
    pass







