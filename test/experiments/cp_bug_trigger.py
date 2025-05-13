#
# Attempt to trigger a CircuitPython bug when simultaneously
# reading from an HTTP source and scrolling on the LED display.
#
import supervisor
import board
import gc
import asyncio
import traceback
import wifi
import ssl
import socketpool
import displayio
import rgbmatrix
import framebufferio
import adafruit_requests
import adafruit_httpserver
from secrets import secrets
from adafruit_display_text.label import Label
import terminalio


class AsyncScrollingDisplay:
    def __init__(self, hardware):
        self.font = terminalio.FONT
        self.hardware = hardware

        # Configure generic scrolling message
        self.scrolling_message = "No Data"
        self.scrolling_label = Label(terminalio.FONT)
        self.scrolling_label.x = 0
        self.scrolling_label.y = 15
        self.scrolling_group = displayio.Group()
        self.scrolling_group.append(self.scrolling_label)
        self.scrolling_group.hidden = False
        self.hardware.root_group = self.scrolling_group

    async def show_scroll_message(self):
        self.hardware.refresh(minimum_frames_per_second=0)
        self.scrolling_label.text = self.scrolling_message
        self.scrolling_group.hidden = False

        while self.scroll_x(self.scrolling_label) is True:
            await asyncio.sleep(.04)

        self.scrolling_group.hidden = True

    def scroll_x(self, line):
        line.x = line.x - 1
        line_width = line.bounding_box[2]
        if line.x < -line_width:
            line.x = self.hardware.width
            return False
        return True

    class Board:
        def __init__(self):
            self.MTX_R1 = 0
            self.MTX_G1 = 0
            self.MTX_B1 = 0
            self.MTX_R2 = 0
            self.MTX_G2 = 0
            self.MTX_B2 = 0
            self.MTX_ADDRA = 0
            self.MTX_ADDRB = 0
            self.MTX_ADDRC = 0
            self.MTX_ADDRD = 0
            self.MTX_CLK = 0
            self.MTX_LAT = 0
            self.MTX_OE = 0


supervisor.runtime.autoreload = False

# Display Setup first in case any error messages
# Need to be displayed
displayio.release_displays()
DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 32
DISPLAY_ROTATION = 0
BIT_DEPTH = 4
AUTO_REFRESH = True

matrix = rgbmatrix.RGBMatrix(
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

# Associate the RGB matrix with a Display, so we can use displayio
display_hardware = framebufferio.FramebufferDisplay(
    matrix, auto_refresh=AUTO_REFRESH, rotation=DISPLAY_ROTATION)
display_hardware.refresh(minimum_frames_per_second=0)

wifi.radio.connect(secrets['ssid'], secrets['password'])

if wifi.radio.connected is False:
    print("Unable to connect to wifi")

# The messages class contains a list of function calls
# to the local Display class, which in turn uses the displayio Display
display = AsyncScrollingDisplay(display_hardware)

# Setup Global Sockets and Server
socket_pool = socketpool.SocketPool(wifi.radio)
http_requests = adafruit_requests.Session(socket_pool, ssl.create_default_context())
web_server = adafruit_httpserver.Server(socket_pool, "/static", debug=False)


async def run_display(local_display):
    while True:
        try:
            await local_display.show_scroll_message()
            await asyncio.sleep(0)  # let other tasks run
        except RuntimeError:
            traceback.print_exc()


def run_garbage_collector():
    # Commented out because it seems to hang the box
    # gc.collect()
    mem_free = gc.mem_free()
    print(f"Memory available: {mem_free}")
    return mem_free


async def update_ride_times(local_display):
    while True:
        try:
            run_garbage_collector()
            print("Calling API through http")
            local_response = http_requests.get("https://queue-times.com/parks/2/queue_times.json")
            # json_response = local_response.json()
            print("Received response from API")

            # Scroll the first 20 characters of the JSON response
            # Data parsing removed to simplify test code
            local_display.scrolling_message = str(local_response.content)
            print(f"Received data from API: {local_display.scrolling_message}")
            await asyncio.sleep(60)  # let other tasks run
        except OSError as error:
            print(str(error))
            traceback.print_exc()
        except RuntimeError as error:
            print(str(error))
            traceback.print_exc()


# Make sure there is data before the display starts
update_ride_times(display)


# Simultaneously display values while updating
# from theme park API
async def main():
    await asyncio.gather(
        run_display(display),
        update_ride_times(display)
    )


asyncio.run(main())
