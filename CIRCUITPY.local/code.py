# Theme Park Waits
# View information about ride wait times at any theme park
#
# import biplane
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
import adafruit_httpserver
from adafruit_datetime import datetime, time

from adafruit_httpserver import (
    Server,
    REQUEST_HANDLED_RESPONSE_SENT,
    Request,
    FileResponse,
)

from theme_park_api import set_system_clock
from theme_park_api import get_park_name_from_id
from theme_park_api import ThemePark
from theme_park_api import Vacation
from theme_park_api import AsyncScrollingDisplay
from theme_park_api import MessageQueue
from theme_park_api import get_park_url_from_id
from theme_park_api import populate_park_list
from theme_park_api import SettingsManager

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

# Setup Networking and WI-FI
wifi_setup()

# def mdns_setup():
# Putting mdns in function causes it to stop working
mdns_server = mdns.Server(wifi.radio)
mdns_server.hostname = "themeparkwaits"
mdns_server.advertise_service(service_type="_http", protocol="_tcp", port=80)

# mdns_setup()

# Setup Global Sockets and Server
socket_pool = socketpool.SocketPool(wifi.radio)
http_requests = adafruit_requests.Session(socket_pool, ssl.create_default_context())
web_server = adafruit_httpserver.Server(socket_pool, "/static", debug=True)

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
async def update_live_wait_time():
    url = get_park_url_from_id(park_list, current_park.id)
    print(f"Park URL: {url}")
    if current_park.id <= 0:
        return
    response = http_requests.get(url)
    json_response = response.json()
    current_park.update(json_response)


# Set device time from the internet
set_system_clock(http_requests)

# Associate the RGB matrix with a Display so we can use displayio
display_hardware = framebufferio.FramebufferDisplay(
    matrix, auto_refresh=AUTO_REFRESH, rotation=DISPLAY_ROTATION)

# The current selected park, empty at first
# A list of all ~150 supported parks
park_list = populate_park_list(http_requests)
current_park = ThemePark()

# Params for the next vacation, if set
vacation_date = Vacation()

# Load settings from JSON file
settings = SettingsManager("settings.json")
current_park.load_settings(settings)
vacation_date.load_settings(settings)

# The messages class contains a list of function calls
# to the local Display class, which in turn uses the displayio Display
display = AsyncScrollingDisplay(display_hardware)
display.set_colors(settings)
SCROLL_DELAY = 4
messages = MessageQueue(display, SCROLL_DELAY)


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
    for month in range(1, 13):
        if vacation_date.is_set() is True and month == vacation_date.month:
            page += f"<option value=\"{month}\" selected>{month}</option>\n"
        else:
            page += f"<option value=\"{month}\">{month}</option>\n"
    page += "</select>"
    # page += "</p>"

    # page += "<p>"
    # page += "<label for=\"Day\">Day:</label>"
    page += "<select id=\"Day\" name=\"Day\">"
    for day in range(1, 32):
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


@web_server.route("/style.css")
def base(request: Request):
    f = open("style.css")
    data = f.read()
    f.close()
    return adafruit_httpserver.Response(request, data, content_type="text/html")


@web_server.route("/")
# def main(query_parameters, headers, body):
def base(request: Request):
    if len(request.query_params) > 0:
        vacation_date.parse(str(request.query_params))
        current_park.parse(str(request.query_params), park_list)
        current_park.store_settings(settings)

        if vacation_date.is_set() is True:
            vacation_date.store_settings(settings)

        # This # triggers the messages to reload with new info.
        messages.regenerate_flag = True

        # Save the settings to disk
        settings.save_settings()

    return adafruit_httpserver.Response(request, main_page(), content_type="text/html")


def start_web_server(wserver):
    print("starting server..")
    # startup the server
    try:
        wserver.start(str(wifi.radio.ipv4_address))
        print("Listening on http://%s:80" % wifi.radio.ipv4_address)
    except OSError:
        time.sleep(5)
        print("restarting device..")
        microcontroller.reset()


start_web_server(web_server)


async def run_web_server(wserver):
    while True:
        try:
            # Process any waiting requests
            pool_result = wserver.poll()
            await asyncio.sleep(.2)
            if pool_result == REQUEST_HANDLED_RESPONSE_SENT:
                # Do something only after handling a request
                pass

        # If you want you can stop the server by calling server.stop() anywhere in your code
        except OSError as error:
            print(error)
            continue


async def run_display():
    while True:
        display_hardware.refresh(minimum_frames_per_second=0)
        if messages.regenerate_flag is True and current_park.is_valid() is True:
            await update_live_wait_time()
            await messages.add_rides(current_park, vacation_date)
            messages.regenerate_flag = False

        # Messages.show() uses create_task in its calls
        # await asyncio.create_task(messages.show())
        await messages.show()
        await asyncio.sleep(0)  # let other tasks run


async def update_ride_times():
    """
    If the user has selected a park, update the ride values ever so often.
    :return:
    """
    while True:
        try:
            await asyncio.sleep(300)
            if len(current_park.rides) > 0:
                await update_live_wait_time()
                await messages.add_rides(current_park, vacation_date)

        except RuntimeError:
            print("Runtime error getting wait times")


# Gives unknown host error
asyncio.run(asyncio.gather(
    run_display(),
    run_web_server(),
    update_ride_times(),
))
#    update_ride_times())
# Tried by itself, mDNS works
# asyncio.run(run_display())

# Gives unknown host error
# asyncio.run(run_web_server())
