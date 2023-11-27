# SPDX-FileCopyrightText: 2020 John Park for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# Scoreboard matrix display
# uses AdafruitIO to set scores and team names for a scoreboard
# Perfect for cornhole, ping pong, and other games

# Web server library
import biplane
import asyncio
import mdns
import time
import board
import wifi
import ssl
import socketpool
import adafruit_requests
import displayio
import rgbmatrix
import framebufferio

from theme_park_api import get_theme_parks_from_json
from theme_park_api import get_park_name_from_id
from theme_park_api import ThemePark
from theme_park_api import Vacation
from theme_park_api import AsyncScrollingDisplay
from theme_park_api import MessageQueue
from theme_park_api import get_park_url_from_id
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
        time.sleep(2)
    ssid = secrets["ssid"]
    print(f"Connected to Wifi: {ssid} at {wifi.radio.ipv4_address}")


def mdns_setup():
    mdns_server = mdns.Server(wifi.radio)
    mdns_server.hostname = "themeparkwaits"
    mdns_server.advertise_service(service_type="_http", protocol="_tcp", port=80)
    print(f"IP address is {mdns.RemoteService}")


# Setup WIFI
wifi_setup()

# Setup Global Sockets and Server
http_requests = adafruit_requests.Session(
    socketpool.SocketPool(wifi.radio), ssl.create_default_context())
web_server = biplane.Server()

# Display Setup
displayio.release_displays()
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

# Associate the RGB matrix with a Display so we can use displayio
display_hardware = framebufferio.FramebufferDisplay(
    matrix, auto_refresh=AUTO_REFRESH, rotation=DISPLAY_ROTATION)

# The messages class contains a list of function calls
# to the local Display class, which in turn uses the displayio Display
SCROLL_DELAY = 4
messages = MessageQueue(AsyncScrollingDisplay(display_hardware), SCROLL_DELAY)

# Params for the next vacation, if set
vacation = Vacation()

# The current selected park, empty at first
park = ThemePark()


# get List of theme parks to choose from
def populate_park_list():
    print("Getting master list of theme parks")
    url = "https://queue-times.com/parks.json"
    response = http_requests.get(url)
    json_response = response.json()
    return sorted(get_theme_parks_from_json(json_response))

# A list of all ~150 supported parks
park_list = populate_park_list()

# Get a list of rides to populate the currently selected ride
async def populate_ride_list(parks, park_id):
    url = get_park_url_from_id(parks, park_id)
    print(f"Configuring park {park_id} from {url}")
    response = http_requests.get(url)
    await asyncio.sleep(0)
    park.name = get_park_name_from_id(parks, park_id)
    await asyncio.sleep(0)
    park.set_rides(response.json())

async def update_live_wait_time():
    if park.id <= 0:
        return
    url = get_park_url_from_id(park_list, park.id)
    print(f"Park URL: {url}")
    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())
    await asyncio.sleep(0)
    response = requests.get(url)
    await asyncio.sleep(0)
    json_response = response.json()
    park.update(json_response)


def main_page(park_id):
    print("Generating main web GUI")
    page = "<link rel=\"stylesheet\" href=\"style.css\">"
    page += "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
    page += "</head>"
    page += "<body style=\"background-color:white;\">"

    page += "<div class=\"navbar\">"
    page += "<a href=\"/\">Theme Park Wait Times</a>"
    page += "</div>"

    page += "<br>"
    page += "<h2>Choose a Park</h2>"
    page += "<div>"
    page += "<form action=\"/action\">"
    page += "<p>"
    page += "<select name=\"park-names\" id=\"park-id\">\n"
    for park in park_list:
        park_name = ThemePark.remove_non_ascii(park[0])
        if park[1] == park_id:
            page += f"<option value=\"{park[1]}\" selected>{park_name}</option>\n"
        else:
            page += f"<option value=\"{park[1]}\">{park_name}</option>\n"
    page += "</select>"
    page += "</p>"

    page += "<p>"
    page += "<label for=\"Name\"></label>"
    page += "</p>"
    page += "<p>"
    page += "<input type=\"submit\">"
    page += "</p>"
    page += "</form>"
    page += "</div>"

    page += "<h2>Configure Next Visit</h2>"
    page += "<div>"
    page += "<form action=\"/vacation\">"
    page += "<p>"
    page += "<label for=\"Name\">Park:</label>"
    page += "<input type=\"text\" id=\"Name\" name=\"Name\">"
    page += "</p>"
    page += "<p>"
    page += "<label for=\"Year\">Year:</label>"
    page += "<input type=\"text\" id=\"Year\" name=\"Year\">"
    page += "</p>"
    page += "<p>"
    page += "<label for=\"Month\">Month:</label>"
    page += "<input type=\"text\" id=\"Month\" name=\"Month\">"
    page += "</p>"
    page += "<p>"
    page += "<label for=\"Day\">Day:</label>"
    page += "<input type=\"text\" id=\"Day\" name=\"Day\">"
    page += "</p>"
    page += "<p>"
    page += "</p>"

    page += "<p>"
    page += "<label for=\"Submit\"></label>"
    page += "<input type=\"submit\">"
    page += "</p>"
    page += "</form>"
    page += "</div>"
    return page


@web_server.route("/style.css", "GET")
def main(query_parameters, headers, body):
    f = open("style.css")
    data = f.read()
    f.close()
    return biplane.Response(data, content_type="text/html")


@web_server.route("/", "GET")
def main(query_parameters, headers, body):
    page = main_page(-1)
    response = biplane.Response(page, content_type="text/html")
    return response


@web_server.route("/action", "GET")
def main(query_parameters, headers, body):
    new_park_id = int(query_parameters.split("=")[1])
    new_park_name = get_park_name_from_id(park_list, new_park_id)
    park.change_parks(new_park_name, new_park_id)
    print(f"Selecting park {new_park_name}:{new_park_id}")
    page = main_page(new_park_id)
    return biplane.Response(page, content_type="text/html")


@web_server.route("/vacation", "GET")
def main(query_parameters, headers, body):
    print(f"Vacation Form sent parameters: {query_parameters}")
    vacation.parse(query_parameters)
    page = main_page(park.id)
    return biplane.Response(page, content_type="text/html")


async def run_server():
    for _ in web_server.circuitpython_start_wifi_ap(
            "FBI Surveillance Van 112", "9196190607", "themeparkwaits"):
        await asyncio.sleep(0)  # let other tasks run


async def run_display():
    while True:
        display_hardware.refresh(minimum_frames_per_second=0)
        if park.new_flag is True:
            await asyncio.create_task(update_live_wait_time())
            await asyncio.create_task(messages.add_rides(park))

        await asyncio.create_task(messages.show())
        # await asyncio.sleep(4)  # let other tasks run


async def update_ride_times():
    """
    If the user has selected a park, update the ride values ever so often.
    :return:
    """
    while True:
        try:
            await asyncio.sleep(300)
            if len(park.rides) > 0:
                await asyncio.create_task(update_live_wait_time())
                await asyncio.create_task(messages.add_rides(park))

        except RuntimeError:
            print("Runtime error getting wait times")


mdns_setup()

# run both coroutines at the same time
asyncio.run(asyncio.gather(run_display(), run_server(), update_ride_times()))

