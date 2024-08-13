# import src.themeparkwaits
# SPDX-FileCopyrightText: 2020 Jeff Epler for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# This example implements a simple two line scroller using
# Adafruit_CircuitPython_Display_Text. Each line has its own color
# and it is possible to modify the example to use other fonts and non-standard
# characters.

import sys
sys.path.append('/src/lib')

import asyncio
import board
import displayio
import framebufferio
import rgbmatrix
import terminalio
import adafruit_imageload

from src.theme_park_api import SettingsManager
from src.theme_park_display import AsyncScrollingDisplay

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
    tile=1,
    serpentine=False,
    doublebuffer=True)

# Associate the RGB matrix with a Display
display_hardware = framebufferio.FramebufferDisplay(
    matrix_board, auto_refresh=True, rotation=DISPLAY_ROTATION)
display_hardware.refresh(minimum_frames_per_second=0)
# Put each line of text into a Group, then show that group.
# g = displayio.Group()
# display_hardware.root_group = g

# Load settings from JSON file
settings = SettingsManager("../settings.json")
display = AsyncScrollingDisplay(display_hardware, settings)
orig_image, palette = adafruit_imageload.load(
    "src/images/OpeningLEDLogo.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
tile_grid = displayio.TileGrid(orig_image, pixel_shader=palette)
# g.append(tile_grid)


def show():
    while True:
        print("Show Centered")
        setup_text1 = f"Connect your phone to Wifi channel AJDDDDF, password \"password\"."
        setup_text2 = "  Then load page http://192.168.4.1"
        # run_setup_message(setup_text, 1)
        display.show_centered(setup_text1, setup_text2, 4)


asyncio.run(show())
