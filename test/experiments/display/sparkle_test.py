# SPDX-FileCopyrightText: 2020 Jeff Epler for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# This example implements a simple two line scroller using
# Adafruit_CircuitPython_Display_Text. Each line has its own color
# and it is possible to modify the example to use other fonts and non-standard
# characters.

import time

import adafruit_imageload
import board
import displayio
import framebufferio
import rgbmatrix
from src.theme_park_api import ColorUtils
from ulab import numpy as np

FRAME_COLOR = 25024

# If there was a display before (protomatter, LCD, or E-paper), release it so
# we can create ours
displayio.release_displays()

def pad_hex(num):
    hex_val = hex(num)[2:]  # remove '0x'
    # return hex_val.zfill(6)
    length = len(hex_val)
    for i in range(0, 6 - length):
        hex_val = "0" + hex_val
    return hex_val


def matrix_multiply(matrix, bitmap):
    # Make sure inputs are numpy arrays
    np_matrix = np.array(matrix)
    np_bitmap = np.zeros((bitmap.width, bitmap.height), dtype=np.uint8)

    for y in range(bitmap.height-1):
        for x in range(bitmap.width-1):
            np_bitmap[x][y] = bitmap[x, y]
    # np_imagebuffer = np.array(bitmap)
    # Perform matrix multiplication, if the sizes are compatible
    result = np.dot(np_matrix, np_bitmap)
    return result.tolist()

def init_matrix():
    matrix = [[0, 0, 0, 0, 0] for _ in range(5)]

    # Now, let's assign individual values one by one
    matrix[0][0] = 0.25
    matrix[0][1] = 0.25
    matrix[0][2] = 0.25
    matrix[0][3] = 0.25
    matrix[0][4] = 0.25

    matrix[1][0] = 0.25
    matrix[1][1] = 0.5
    matrix[1][2] = 0.5
    matrix[1][3] = 0.5
    matrix[1][4] = 0.25

    matrix[2][0] = 0.25
    matrix[2][1] = 0.5
    matrix[2][2] = 1.0
    matrix[2][3] = 0.5
    matrix[2][4] = 0.25

    matrix[3][0] = 0.25
    matrix[3][1] = 0.5
    matrix[3][2] = 0.5
    matrix[3][3] = 0.5
    matrix[3][4] = 0.25

    matrix[4][0] = 0.25
    matrix[4][1] = 0.25
    matrix[4][2] = 0.25
    matrix[4][3] = 0.25
    matrix[4][4] = 0.25

    return matrix


def fix_color(bitmap_3_bit):

    # Calculate new width and height
    width = bitmap_3_bit.width
    height = bitmap_3_bit.height

    # Create 4-bit bitmap with same dimensions
    bitmap_4_bit = displayio.Bitmap(width, height, 65536)

    # Copy and scale pixel values from 3-bit to 6-bit bitmap
    for y in range(height):
        for x in range(width):
            old_value = bitmap_3_bit[x, y]
            # print(f"Old Value = {old_value}")
            new_value = old_value
            if old_value > 50000:
                new_value = FRAME_COLOR
                if y > 12:
                    new_value = int(FRAME_COLOR / 2)
                else:
                    new_value = FRAME_COLOR

            if old_value < 50000:
                new_value = 0


            # print(f"Hex = {new_value}")
            # new_value = ColorUtils.hex_str_to_number(ColorUtils.scale_color(hex_value, scale_factor))
            # new_value = round(old_value * scale_factor)
            #print(f"Old Value = {old_value} Scaled = {new_value}")
            bitmap_4_bit[x, y] = new_value

    return bitmap_4_bit


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
    doublebuffer=False)



# Associate the RGB matrix with a Display so that we can use displayio features
display = framebufferio.FramebufferDisplay(matrix_board, auto_refresh=False)

# Put each line of text into a Group, then show that group.
g = displayio.Group()
display.root_group = g

orig_image, palette = adafruit_imageload.load(
    "src/images/OpeningLEDLogo.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)

image = fix_color(orig_image)

matrix = init_matrix()
mod_image = matrix_multiply(matrix, image)

# Create a TileGrid to render the bitmap on the display
tile_grid = displayio.TileGrid(mod_image, pixel_shader=palette)

# tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
g.append(tile_grid)
# display.show(g)  # Removed for 9.0 beta port
display.refresh(minimum_frames_per_second=0)


time.sleep(4)

x = 0
y = 2
while True:
    display.refresh(minimum_frames_per_second=0)



