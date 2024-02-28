# SPDX-FileCopyrightText: 2020 Jeff Epler for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# This example implements a simple two line scroller using
# Adafruit_CircuitPython_Display_Text. Each line has its own color
# and it is possible to modify the example to use other fonts and non-standard
# characters.

import adafruit_display_text.label
import board
import displayio
import framebufferio
import rgbmatrix
import terminalio
import adafruit_imageload
from src.pixeldust import PixelDust
import time

# If there was a display before (protomatter, LCD, or E-paper), release it so
# we can create ours
displayio.release_displays()

def convert_3bit_bitmap_to_6bit(bitmap_3_bit, palette):
    # 3-bit max value is 8 and 6-bit max value is 64
    scale_factor = 262144 / 64   # 2 to the 18th power = 262,144
    scale_factor = 1

    # Calculate new width and height
    width = bitmap_3_bit.width
    height = bitmap_3_bit.height

    # Create 6-bit bitmap with same dimensions
    bitmap_6_bit = displayio.Bitmap(width, height, 262144)

    # Copy and scale pixel values from 3-bit to 6-bit bitmap
    for y in range(height):
        for x in range(width):
            old_value = bitmap_3_bit[x, y]
            new_value = round(old_value * scale_factor)
            # print(f"Old Value = {old_value} New = {new_value}")
            bitmap_6_bit[x, y] = new_value

    return bitmap_6_bit

# This next call creates the RGB Matrix object itself. It has the given width
# and height. bit_depth can range from 1 to 6; higher numbers allow more color
# shades to be displayed, but increase memory usage and slow down your Python
# code. If you just want to show primary colors plus black and white, use 1.
# Otherwise, try 3, 4 and 5 to see which effect you like best.
#
# These lines are for the Feather M4 Express. If you're using a different board,
# check the guide to find the pins and wiring diagrams for your board.
# If you have a matrix with a different width or height, change that too.
# If you have a 16x32 display, try with just a single line of text.
DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 32
DISPLAY_ROTATION = 0
BIT_DEPTH = 6
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
    tile=1,
    serpentine=False,
    doublebuffer=False)


# Associate the RGB matrix with a Display so that we can use displayio features
display = framebufferio.FramebufferDisplay(matrix_board, auto_refresh=False)

# Create two lines of text to scroll. Besides changing the text, you can also
# customize the color and font (using Adafruit_CircuitPython_Bitmap_Font).
# To keep this demo simple, we just used the built-in font.
# The Y coordinates of the two lines were chosen so that they looked good
# but if you change the font you might find that other values work better.
line1 = adafruit_display_text.label.Label(
    terminalio.FONT,
    color=0xff0000,
    text="THEME PARK")
line1.x = display.width
line1.x = 3
line1.y = 5

line2 = adafruit_display_text.label.Label(
    terminalio.FONT,
    color=0x0080ff,
    text="WAITS",
    scale=2)

line2.x = 3
line2.y = 20

# Put each line of text into a Group, then show that group.
g = displayio.Group()
display.root_group = g

orig_image, palette = adafruit_imageload.load(
    "src/OpeningLEDLogo1.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)

print(f"The size of the pallette is {len(palette)}")

image = convert_3bit_bitmap_to_6bit(orig_image, palette)

# Create a TileGrid to render the bitmap on the display
tile_grid = displayio.TileGrid(image, pixel_shader=palette)

# tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
# g.append(tile_grid)
g.append(line1)
g.append(line2)
display.show(g)
display.refresh(minimum_frames_per_second=0)

FRAME_COLOR = 25024

for x in range(DISPLAY_WIDTH):
    image[x, 0] = FRAME_COLOR
for x in range(DISPLAY_WIDTH):
    image[x, DISPLAY_HEIGHT-1] = FRAME_COLOR
for y in range(DISPLAY_HEIGHT):
    image[0, y] = FRAME_COLOR
for y in range(DISPLAY_HEIGHT):
    image[DISPLAY_WIDTH-1, y] = FRAME_COLOR

elasticity = .1
dust = PixelDust(DISPLAY_WIDTH, DISPLAY_HEIGHT, elasticity)

acceleration = [0.0, 100.0, 0.0]
dust.init_grains(image)
print(f"Created {dust.num_grains} grains")


x = 0
y = 0
while True:

    display.refresh(minimum_frames_per_second=0)
    display.show(g)

    # dust.iterate(acceleration)
    # print(f"Image value at {x}:{y} is {image[x, y]}")
    # image[int(x), int(y)] = 6
    # image[int(x), int(y)] = FRAME_COLOR
    x += 1
    if x > DISPLAY_WIDTH-1:
        x = 0
        y += 1
    if y > DISPLAY_HEIGHT-1:
        y = 0

    # time.sleep(.1)
    # for i in range(dust.num_grains):
    #    pos_x, pos_y = dust.get_position(i)
    #    print(f"Grain pos = [{pos_x}, {pos_y}]")
    # if pos_x < DISPLAY_WIDTH and pos_y < DISPLAY_HEIGHT:
    # image[int(pos_x), int(pos_y)] = 25024






