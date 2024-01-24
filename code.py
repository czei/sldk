# Theme Park Waits
# View information about ride wait times at any theme park
# Copyright 2024 3DUPFitters LLC
#
import asyncio
import mdns
import time
import traceback
import wifi
import microcontroller
import ssl
import socketpool
import displayio
import rgbmatrix
import framebufferio
import adafruit_requests
import adafruit_httpserver
from adafruit_datetime import datetime

from adafruit_httpserver import (
    Status,
    REQUEST_HANDLED_RESPONSE_SENT,
    Request,
    Response,
    Headers,
    GET,
    POST
)
from adafruit_matrixportal.matrixportal import MatrixPortal

from theme_park_api import set_system_clock, ColorUtils, MatrixPortalDisplay
from theme_park_api import get_park_name_from_id
from theme_park_api import ThemePark
from theme_park_api import Vacation
from theme_park_api import AsyncScrollingDisplay
from theme_park_api import MessageQueue
from theme_park_api import get_park_url_from_id
from theme_park_api import populate_park_list
from theme_park_api import SettingsManager
from theme_park_api import load_credentials

try:
    import board
except (ModuleNotFoundError, NotImplementedError):
    # Mocking the unavailable modules in non-embedded environments
    # You can add more according to your needs, these are just placeholders

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

try:
    import wifimgr
except (ModuleNotFoundError, NotImplementedError):
    wifimgr.get_connection.return_value = None

# We don't want autoreload during development, but it
# may be useful in the field to recover after an unanticipated
# error.
import supervisor

supervisor.runtime.autoreload = False

# Display Setup first in case any error messages
# Need to be displayed
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
display_hardware.refresh(minimum_frames_per_second=0)

# Load settings from JSON file
current_park = ThemePark()
settings = SettingsManager("settings.json")
current_park.load_settings(settings)

# Params for the next vacation, if set
vacation_date = Vacation()
vacation_date.load_settings(settings)


#
# Scroll the user instructions on how to configure the wifi
# when it fails to connect.  This could be the first time,
# or if they change their wifi password, or move the box
# to a new location.
#
def run_setup_message():
    print("Starting Wifi Configure message")
    setup_text = f"Connect your phone to Wifi channel {wifimgr.AP_SSID}, password \"{wifimgr.AP_PASSWORD}\"."
    setup_text += "  Then load page http://192.168.4.1"
    local_portal = MatrixPortal(status_neopixel=board.NEOPIXEL, debug=True)
    local_display = MatrixPortalDisplay(local_portal, settings)
    try:
        local_display.sync_show_scroll_message(setup_text)
        time.sleep(1)
        now = datetime.now()
        print(f"The current time:  {now.hour}:{now.minute}")

    except RuntimeError:
        traceback.print_exc()


# Setup WI-FI Password
ssid, password = load_credentials()
try:
    wifi.radio.connect(ssid, password)
except (RuntimeError, ConnectionError, ValueError):
    run_setup_message()
    while wifi.radio.connected is not True:
        try:
            ssid = ""
            password = ""
            if wifimgr.get_connection() is not None:
                wifi.radio.connect(ssid, password)
                print("Resetting Wifi after setup")
                import microcontroller
                microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
                microcontroller.reset()

        except (RuntimeError, ConnectionError, ValueError):
            print("Something went seriously wrong connecting to Wifi")
            import microcontroller
            microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
            microcontroller.reset()

print(f"Connected to Wifi: {ssid} at {wifi.radio.ipv4_address}")

# The messages class contains a list of function calls
# to the local Display class, which in turn uses the displayio Display
display = AsyncScrollingDisplay(display_hardware, settings)
display.set_colors(settings)
SCROLL_DELAY = 4
messages = MessageQueue(display, SCROLL_DELAY, regen_flag=True)

# Setup Global Sockets and Server
socket_pool = socketpool.SocketPool(wifi.radio)
http_requests = adafruit_requests.Session(socket_pool, ssl.create_default_context())
web_server = adafruit_httpserver.Server(socket_pool, "/static", debug=False)

# Configure DNS so that users can configure at http://themeparkwaits.local
mdns_server = mdns.Server(wifi.radio)
mdns_server.hostname = "themeparkwaits"
mdns_server.advertise_service(service_type="_http", protocol="_tcp", port=80)


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
    print(f"Updating Park from URL: {url}")
    response = http_requests.get(url)
    json_response = response.json()
    current_park.update(json_response)


# The current selected park, empty at first
# A list of all ~150 supported parks
park_list = populate_park_list(http_requests)


def generate_header():
    page = "<link rel=\"stylesheet\" href=\"style.css\">"
    page += "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
    page += "</head>"
    page += "<body style=\"background-color:white;\">"

    page += "<div class=\"navbar\">"
    page += "<a href=\"/\">Theme Park Wait Times</a>\n"
    page += "<div class=\"settings\">"
    page += "<a href=\"/settings.html\" class=\"settings\">&#x2699;</a>\n"
    page += "</div>"
    page += "</div>"
    return page


def generate_main_page():
    page = generate_header()
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
    page += "</div>"

    # page += "<div style=\"display: flex; align-items: center;\">"
    page += "<div class=\"myCheckbox\">\n"
    if settings.settings["skip_meet"] is True:
        page += "<label><input class=\"myCheckbox\" type=\"checkbox\" id=\"skip_meet\" name=\"skip_meet\" Checked>Skip Character Meets</label>\n"
    else:
        page += "<label><input class=\"myCheckbox\" type=\"checkbox\" id=\"skip_meet\" name=\"skip_meet\">Skip Character Meets</label>\n"
    page += "</div>\n"

    page += "<div class=\"myCheckbox\">\n"
    print(f"skip_closed is {settings.settings["skip_closed"]}")
    if settings.settings["skip_closed"] is True:
        page += "<label><input type=\"checkbox\" id=\"skip_closed\" name=\"skip_closed\" Checked>Skip Closed Rides</label>"
    else:
        page += "<label><input type=\"checkbox\" id=\"skip_closed\" name=\"skip_closed\">Skip Closed Rides</label>"
    # page += "<label for=\"skip_closed\">Skip Closed Rides</label>\n"
    page += "</div>\n"

    page += "<h2>Configure Vacation</h2>"
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

    page += "<select id=\"Month\" name=\"Month\">"
    for month in range(1, 13):
        if vacation_date.is_set() is True and month == vacation_date.month:
            page += f"<option value=\"{month}\" selected>{month}</option>\n"
        else:
            page += f"<option value=\"{month}\">{month}</option>\n"
    page += "</select>"

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
    page += "<body>"
    return page


@web_server.route("/style.css")
def base(request: Request):
    f = open("style.css")
    data = f.read()
    f.close()
    return adafruit_httpserver.Response(request, data, content_type="text/html")


@web_server.route("/settings.html", [GET, POST])
def base(request: Request):
    # Parse new settings
    if request.method == POST:
        for name, value in request.form_data.items():
            settings.settings[name] = value
        display.set_colors(settings)
        try:
            # Save the settings to disk
            settings.save_settings()
        except OSError:
            print("Unable to save settings, drive is read only.")

    page = generate_header()
    page += "<h2>Settings</h2>"
    page += "<div>"
    page += "<form action=\"/settings.html\" method=\"POST\">"

    for color_setting_name, color_value in settings.settings.items():
        if "color" in color_setting_name:
            page += "<p>"
            page += f"<label for=\"Name\">{SettingsManager.get_pretty_name(color_setting_name)}</label>"
            page += ColorUtils.html_color_chooser(color_setting_name, hex_num_str=color_value)
            page += "</p>"

    page += "<p>"
    page += f"<label for=\"Name\">Scroll Speed</label>"
    page += "<select name=\"scroll_speed\" id=\"scroll_speed\">"
    for speed in ["Slow", "Medium", "Fast"]:
        if speed == settings.settings.get("scroll_speed"):
            page += f"<option value=\"{speed}\" selected>{speed}</option>\n"
        else:
            page += f"<option value=\"{speed}\">{speed}</option>\n"
        page += "</p>"
    page += "</select>"

    page += "<p>"
    page += "<label for=\"Submit\"></label>"
    page += "<input type=\"submit\">"
    page += "</p>"
    page += "</form>"
    page += "</div>"
    page += "<body>"

    return adafruit_httpserver.Response(request, page, content_type="text/html")


@web_server.route("/", [GET])
def base(request: Request):
    if len(request.query_params) > 0:
        vacation_date.parse(str(request.query_params))
        current_park.parse(str(request.query_params), park_list)
        current_park.store_settings(settings)

        if vacation_date.is_set() is True:
            vacation_date.store_settings(settings)

        # This # triggers the messages to reload with new info.
        messages.regenerate_flag = True

        try:
            # Save the settings to disk
            settings.save_settings()
        except OSError:
            print("Unable to save settings, drive is read only.")

        request.query_params = ({})
        head = Headers({"Location": "/"})
        response = Response(request, "", headers=head, status=Status(302, "Moved temporarily"),
                            content_type="text/html")
        return response

    return adafruit_httpserver.Response(request, generate_main_page(), content_type="text/html")


def start_web_server(wserver):
    print("starting server..")
    # startup the server
    try:
        wserver.start(str(wifi.radio.ipv4_address), 80)
        print("Listening on http://%s:80" % wifi.radio.ipv4_address)
    except OSError:
        time.sleep(5)
        print("restarting device..")
        microcontroller.reset()


start_web_server(web_server)


async def run_web_server():
    while True:
        try:
            # Process any waiting requests
            pool_result = web_server.poll()
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
        try:
            print(f"Messages regen_flag is {messages.regenerate_flag}")
            print(f"Park valid flag is {current_park.is_valid()}")
            if messages.regenerate_flag is True and current_park.is_valid() is True:
                await update_live_wait_time()
                await messages.add_rides(current_park, vacation_date)
                messages.regenerate_flag = False

            await messages.show()
            await asyncio.sleep(0)  # let other tasks run

            now = datetime.now()
            print(f"The current time:  {now.hour}:{now.minute}")

        except RuntimeError:
            traceback.print_exc()


async def update_ride_times():
    """
    If the user has selected a park, update the ride values ever so often.
    :return:
    """
    while True:
        try:
            if current_park.is_open is True:
                await asyncio.sleep(300)
            else:
                await asyncio.sleep(3600)

            if len(current_park.rides) > 0:
                await update_live_wait_time()
                await messages.add_rides(current_park, vacation_date)

        except RuntimeError:
            traceback.print_exc()


# Set device time from the internet
set_system_clock(http_requests)

asyncio.run(asyncio.gather(
    run_display(),
    run_web_server(),
    update_ride_times()
))
