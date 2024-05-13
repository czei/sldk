from unittest import TestCase

import adafruit_imageload
import displayio
import board
import adafruit_blinka
import adafruit_platformdetect
import src.image_processor


class TestImageProcessor(TestCase):
    def test_image_processing(self):

        image, palette = adafruit_imageload.load("images/4bit.bmp")
        tile_grid = displayio.TileGrid(image, pixel_shader=palette)
        group = displayio.Group()
        group.append(tile_grid)
        board.DISPLAY.root_group = group


        # orig_image = adafruit_imageload.load(
        #     "../src/images/OpeningLEDLogo.bmp")

        # bitmap = displayio.OnDiskBitmap("../src/images/OpeningLEDLogo.bmp")

        #PIN = board.D18
        #led = digitalio.DigitalInOut(PIN)
        #led.direction = digitalio.Direction.OUTPUT

        bitmap, palette = adafruit_imageload.load("../src/images/OpeningLEDLogo.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
        ip = src.image_processor.ImageProcessor(bitmap)
