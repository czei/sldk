# Theme Park Waits
# View information about ride wait times at any theme park
#
import rtc
import biplane
import asyncio
import mdns
import time
import board
import wifi
import ssl
import socketpool
import displayio
import rgbmatrix
import framebufferio
import adafruit_requests
import adafruit_datetime
import adafruit_matrixportal.matrix
from adafruit_datetime import datetime, date, time

from theme_park_api import get_theme_parks_from_json
from theme_park_api import set_system_clock
from theme_park_api import get_park_name_from_id
from theme_park_api import ThemePark
from theme_park_api import Vacation
from theme_park_api import AsyncScrollingDisplay
from theme_park_api import MessageQueue
from theme_park_api import get_park_url_from_id
from theme_park_api import populate_park_list

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


def mdns_setup():
    mdns_server = mdns.Server(wifi.radio)
    mdns_server.hostname = "themeparkwaits"
    mdns_server.advertise_service(service_type="_http", protocol="_tcp", port=80)


# Setup Networking and WIFI
wifi_setup()
mdns_setup()

# Setup Global Sockets and Server
socket_pool = socketpool.SocketPool(wifi.radio)
http_requests = adafruit_requests.Session(socket_pool, ssl.create_default_context())
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



# Get a list of rides to populate the currently selected ride
async def populate_ride_list(parks, park_id):
    url = get_park_url_from_id(parks, park_id)
    print(f"Configuring park {park_id} from {url}")
    response = http_requests.get(url)
    await asyncio.sleep(0)
    current_park.name = get_park_name_from_id(parks, park_id)
    await asyncio.sleep(0)
    current_park.set_rides(response.json())

async def update_live_wait_time():
    if current_park.id <= 0:
        return
    url = get_park_url_from_id(park_list, current_park.id)
    print(f"Park URL: {url}")
    # pool = socketpool.SocketPool(wifi.radio)
    # requests = adafruit_requests.Session(pool, ssl.create_default_context())
    response = http_requests.get(url)
    await asyncio.sleep(0)
    json_response = response.json()
    await asyncio.sleep(0)
    current_park.update(json_response)
    await asyncio.sleep(0)


# Set device time from the internet
set_system_clock(http_requests)

# Associate the RGB matrix with a Display so we can use displayio
display_hardware = framebufferio.FramebufferDisplay(
    matrix, auto_refresh=AUTO_REFRESH, rotation=DISPLAY_ROTATION)

# The current selected park, empty at first
# A list of all ~150 supported parks
park_list = populate_park_list(http_requests)
current_park = ThemePark()

# The messages class contains a list of function calls
# to the local Display class, which in turn uses the displayio Display
SCROLL_DELAY = 4
messages = MessageQueue(AsyncScrollingDisplay(display_hardware), SCROLL_DELAY)

# Params for the next vacation, if set
vacation_date = Vacation()


def main_page():
    page = "<link rel=\"stylesheet\" href=\"style.css\">"
    page += "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
    page += "</head>"
    page += "<body style=\"background-color:white;\">"

    page += "<div class=\"navbar\">"
    page += "<a href=\"#home\">Theme Park Wait Times</a>"
    page += "</div>"

    page += "<br>"
    page += "<h2>Choose a Park</h2>"
    page += "<div>"
    page += "<form action=\"/\" method=\"GET\">"
    page += "<p><select name=\"park-id\" id=\"park-id\">\n"
    for park in park_list:
        park_name = ThemePark.remove_non_ascii(park[0])
        if park[1] == current_park.id:
            page += f"<option value=\"{park[1]}\" selected>{park_name}</option>\n"
        else:
            page += f"<option value=\"{park[1]}\">{park_name}</option>\n"
    page += "</select></p>"

    page += "<p><label for=\"Name\"></label></p>"
#    page += "<p><input type=\"submit\"></p>"
#   page += "</form>"
    page += "</div>"

    page += "<h2>Configure Next Visit</h2>"
    page += "<div>"
    page += "<p>"
    page += "<label for=\"Name\">Park:</label>"
    page += f"<input type=\"text\" name=\"Name\" style=\"text-align: left;\" value=\"{vacation_date.name}\">"
    page += "</p>"

    page += "<p>"
    page += "<label for=\"Date\">Date:</label>"
    page += "<select id=\"Year\" name=\"Year\">"
    year_now = datetime.now().year
    for year in range(year_now, 2044):
        if vacation_date.is_set() is True and year == vacation_date.year:
            page += f"<option value=\"{year}\" selected>{year}</option>\n"
        else:
            page += f"<option value=\"{year}\">{year}</option>\n"
    page += "</select>"
    # page += "</p>"

    # page += "<p>"
    # page += "<label for=\"Month\">Month:</label>"
    page += "<select id=\"Month\" name=\"Month\">"
    for month in range(1,13):
        if vacation_date.is_set() is True and month == vacation_date.month:
            page += f"<option value=\"{month}\" selected>{month}</option>\n"
        else:
            page += f"<option value=\"{month}\">{month}</option>\n"
    page += "</select>"
    # page += "</p>"

    # page += "<p>"
    # page += "<label for=\"Day\">Day:</label>"
    page += "<select id=\"Day\" name=\"Day\">"
    for day in range(1,32):
        if vacation_date.is_set() is True and day == vacation_date.day:
            page += f"<option value=\"{day}\" selected>{day}</option>\n"
        else:
            page += f"<option value=\"{day}\">{day}</option>\n"
    page += "</select>"
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

    if len(query_parameters) > 0:
        params = query_parameters.split("&")
        vacation_date.parse(query_parameters)
        current_park.parse(query_parameters, park_list)

        # The user may not have set a new flag, but this
        # triggers the messages to reload.
        messages.regenerate_flag = True

    return biplane.Response(main_page(), content_type="text/html")


async def run_server():
    for _ in web_server.circuitpython_start_wifi_ap("Test", "Param2", "Param3"):
       await asyncio.sleep(0)  # let other tasks run
    # with socket_pool.socket() as server_socket:
    # print("http server yielding")
    #    await web_server.start(server_socket, ('0.0.0.0', 80), 3)
    #    await asyncio.sleep(0)

messages.regenerate_flag = True
current_park.id = 7

async def run_display():
    while True:
        display_hardware.refresh(minimum_frames_per_second=0)
        if messages.regenerate_flag is True:
            await asyncio.create_task(update_live_wait_time())
            await asyncio.create_task(messages.add_rides(current_park,vacation_date))

        # await asyncio.create_task(messages.show())
        # Messages.show() uses create_task in its calls
        await messages.show()
        await asyncio.sleep(1)  # let other tasks run


async def update_ride_times():
    """
    If the user has selected a park, update the ride values ever so often.
    :return:
    """
    while True:
        try:
            await asyncio.sleep(300)
            if len(current_park.rides) > 0:
                await asyncio.create_task(update_live_wait_time())
                await asyncio.create_task(messages.add_rides(current_park, vacation_date))

        except RuntimeError:
            print("Runtime error getting wait times")



# run both coroutines at the same time
asyncio.run(asyncio.gather(run_display(), run_server(), update_ride_times()))
# asyncio.run(asyncio.gather(run_display()))
