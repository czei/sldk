# Theme Park Waits
# View information about ride wait times at any theme park
#

import asyncio
import mdns
import time
import board
import wifi
import microcontroller
import ssl
import socketpool
import displayio
import rgbmatrix
import framebufferio
import adafruit_requests
from theme_park_api import set_system_clock
import adafruit_httpserver
from adafruit_datetime import datetime

from adafruit_httpserver import (
    Server,
    REQUEST_HANDLED_RESPONSE_SENT,
    Request,
    FileResponse,
)

import supervisor

supervisor.runtime.autoreload = False


def wifi_setup():
    # Get Wifi credentials
    try:
        from secrets import secrets
    except ImportError:
        print("WiFi secrets are kept in secrets.py, please add them there!")
        raise
    wifi.radio.connect(secrets["ssid"], secrets["password"])
    while wifi.radio.connected is False:
        print("Not connected to Wifi")
        time.sleep(1)
    ssid = secrets["ssid"]
    print(f"Connected to Wifi: {ssid} at {wifi.radio.ipv4_address}")

# Putting the mdns server in a function causes an error
def mdns_setup():
    mdns_server = mdns.Server(wifi.radio)
    mdns_server.hostname = "themeparkwaits"
    mdns_server.advertise_service(service_type="_http", protocol="_tcp", port=80)


# Setup Networking and WIFI
wifi_setup()
mdns_setup()

# Setup Global Sockets and Server
# socket_pool = socketpool.SocketPool(wifi.radio)
web_server = adafruit_httpserver.Server(socketpool.SocketPool(wifi.radio), "/", debug=True)

# Display Setup
# displayio.release_displays()
DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 32
DISPLAY_ROTATION = 0
BIT_DEPTH = 3
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


# Set device time from the internet
http_requests = adafruit_requests.Session(socketpool.SocketPool(wifi.radio), ssl.create_default_context())
set_system_clock(http_requests)

# Associate the RGB matrix with a Display so we can use displayio
# display_hardware = framebufferio.FramebufferDisplay(
#    matrix, auto_refresh=AUTO_REFRESH, rotation=DISPLAY_ROTATION)


@web_server.route("/")
def base(request: Request):

    response = "<h1>My Web Page</h1>"
    d = datetime.now()
    response += f"<p>The date is {d}</p>"
    return adafruit_httpserver.Response(request, response, content_type="text/html")


def start_web_server(wserver):
    print("starting server..")
    # startup the server
    try:
        wserver.start(str(wifi.radio.ipv4_address))
        print("Listening on http://%s:80" % wifi.radio.ipv4_address)
    except OSError:
        time.sleep(5)
        print("restarting..")
        microcontroller.reset()


start_web_server(web_server)


async def run_web_server():
    while True:
        try:
            # Process any waiting requests
            pool_result = web_server.poll()

            if pool_result == REQUEST_HANDLED_RESPONSE_SENT:
                # Do something only after handling a request
                pass

            await asyncio.sleep(0)

        # If you want you can stop the server by calling server.stop() anywhere in your code
        except OSError as error:
            print(error)
            continue


asyncio.run(run_web_server())

