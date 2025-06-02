# SPDX-FileCopyrightText: 2020 Jeff Epler for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# This example implements a simple two line scroller using
# Adafruit_CircuitPython_Display_Text. Each line has its own color
# and it is possible to modify the example to use other fonts and non-standard
# characters.

import adafruit_display_text.label
import asyncio
import board
import displayio
import framebufferio
import rgbmatrix
import terminalio
import adafruit_imageload
from adafruit_bitmap_font import bitmap_font

# If there was a display before (protomatter, LCD, or E-paper), release it so
# we can create ours
displayio.release_displays()

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
    doublebuffer=True)

# Associate the RGB matrix with a Display so that we can use displayio features
display = framebufferio.FramebufferDisplay(matrix_board, auto_refresh=False)

# font1 = bitmap_font.load_font("verdana-7pt.bdf")
font2 = bitmap_font.load_font("tom-thumb.bdf")

line1 = adafruit_display_text.label.Label(
    terminalio.FONT,
    color=0xff0000,
    text="Powered by")

line1.x = display.width
line1.x = 0
line1.y = 10

line2 = adafruit_display_text.label.Label(
    font2,
    color=0x0080ff,
    text="queue-times.com")

line2.x = 1
line2.y = 25

# Put each line of text into a Group, then show that group.
g = displayio.Group()
display.root_group = g

# tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
g.append(line1)
g.append(line2)
display.show(g)

while True:
    display.refresh(minimum_frames_per_second=0)








