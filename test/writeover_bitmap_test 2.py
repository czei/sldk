# SPDX-FileCopyrightText: 2020 Jeff Epler for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# This example implements a simple two line scroller using
# Adafruit_CircuitPython_Display_Text. Each line has its own color
# and it is possible to modify the example to use other fonts and non-standard
# characters.

import adafruit_display_text.label
import board
import asyncio
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

DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 32
DISPLAY_ROTATION = 0
BIT_DEPTH = 3
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
display = framebufferio.FramebufferDisplay(matrix_board, auto_refresh=True)

# Put each line of text into a Group, then show that group.
g = displayio.Group()
display.root_group = g

image, palette = adafruit_imageload.load(
    "src/OpeningLEDLogo.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)



# Create a TileGrid to render the bitmap on the display
tile_grid = displayio.TileGrid(image, pixel_shader=palette)
g.append(tile_grid)
display.show(g)
display.refresh(minimum_frames_per_second=0)

# Draw a frame around the image
FRAME_COLOR = 25024
for x in range(DISPLAY_WIDTH):
    image[x, 0] = FRAME_COLOR
for x in range(DISPLAY_WIDTH):
    image[x, DISPLAY_HEIGHT-1] = FRAME_COLOR
for y in range(DISPLAY_HEIGHT):
    image[0, y] = FRAME_COLOR
for y in range(DISPLAY_HEIGHT):
    image[DISPLAY_WIDTH-1, y] = FRAME_COLOR

def draw_on_image(image_local):
    x = 0
    y = 0

    while True:
        x += 1
        if x > DISPLAY_WIDTH-1:
            x = 0
            y += 1
        if y > DISPLAY_HEIGHT-1:
            y = 0
        image_local[x, y] = FRAME_COLOR
        #  await asyncio.sleep(0)


while True:

    for x in range(DISPLAY_WIDTH-1):
        for y in range(DISPLAY_HEIGHT):
            image[x, y] = FRAME_COLOR
            display.refresh(minimum_frames_per_second=0)
            time.sleep(1)







