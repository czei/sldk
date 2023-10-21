# SPDX-FileCopyrightText: 2020 John Park for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# Scoreboard matrix display
# uses AdafruitIO to set scores and team names for a scoreboard
# Perfect for cornhole, ping pong, and other games

import re
import board
import time
import terminalio
import wifi
import ssl
import socketpool
import adafruit_requests
import displayio
from rainbowio import colorwheel
from theme_park_api import get_theme_parks_from_json
from theme_park_api import Rides
from theme_park_api import ParkUpdateTimer

from theme_park_api import get_park_url
from adafruit_matrixportal.matrixportal import MatrixPortal

# get List of theme parks to choose from
def populate_park_list():
    url = "https://queue-times.com/parks.json"
    wifi.radio.connect(secrets["ssid"], secrets["password"])
    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())
    response = requests.get(url)
    json_response = response.json()
    return get_theme_parks_from_json(json_response)

def populate_ride_list(park_list, park_name):
    url = get_park_url(park_list, park_name)
    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())
    response = requests.get(url)
    rides = Rides(response.json())
    return rides


# Get WIFI credentials
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# init global variables
ansion_wait = 5
park_list = populate_park_list()
UPDATE_DELAY = 4
SCROLL_DELAY = 0.03
displayio.release_displays()
display_wait = False

# --- Display setup ---
matrixportal = MatrixPortal(status_neopixel=board.NEOPIXEL, debug=False)

# RED_COLOR = 0xAA0000
# RED_COLOR = 0x993333
RED_COLOR = 0xCC3333
BLUE_COLOR = 0x0000AA
BLACK_COLOR = 0x000000

# Red Score
# matrixportal.add_text(
#     text_font=terminalio.FONT,
#     text_position=(2, int(matrixportal.graphics.display.height * 0.75) - 3),
#     text_color=RED_COLOR,
#     scrolling=False,
#     text_scale=1,
# )

# Ride Wait Time
WAIT_TIME = 0
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(23, int(matrixportal.graphics.display.height * 0.75) - 2),
    text_color=BLUE_COLOR,
    scrolling=False,
    text_scale=2,
)

# Ride Name
RIDE_NAME = 1
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(0, int(matrixportal.graphics.display.height * 0.25)+10),
    text_color=RED_COLOR,
    scrolling=True,
    text_scale=.5,
)

# Standby
STANDBY = 2
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=((int((matrixportal.graphics.display.width-7*6) / 2)+2), 6),
    text_color=BLUE_COLOR,
)

# Static 'Connecting' Text
# matrixportal.add_text(
#     text_font=terminalio.FONT,
#    text_position=(59, 0),
# )

def show_connecting(show):
    if show:
        matrixportal.set_text(".", 4)
    else:
        matrixportal.set_text(" ", 4)


def update_live_wait_time(park_name):
    url = get_park_url(park_list, park_name)
    print(f"Park URL: {url}")
    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())
    response = requests.get(url)
    json_response = response.json()
    rides.update(json_response)

def process_ride_name(ride_name):
    return re.sub(r'\s' , '\n', ride_name)


def show_ride_wait_time(ride_wait_time) :
    matrixportal.set_text("", RIDE_NAME)
    matrixportal.set_text(ride_wait_time, WAIT_TIME)
    matrixportal.set_text("Standby", STANDBY)


def show_ride_name(ride_name) :
    matrixportal.set_text("", STANDBY)
    matrixportal.set_text("", WAIT_TIME)
    matrixportal.set_text(ride_name, RIDE_NAME)

class ColorPicker:
    def __init__(self):
        self.index = 0

    def get_next_color(self):
        self.index = (self.index + 1) % 256
        color = colorwheel(self.index)
        print(f"color = {color}")
        return color

# Setup Ride Data
PARK_NAME = "Hollywood Studios"
rides = populate_ride_list(park_list, PARK_NAME)
# show_ride_name(rides.get_current_ride_name())
park_update_timer = ParkUpdateTimer(300)

while True:
    try:
        ride_name = rides.get_current_ride_name()
        print(f"Displaying Ride: {ride_name}")
        show_ride_name(ride_name)
        matrixportal.scroll_text()

        show_ride_wait_time(rides.get_current_ride_time())
        rides.increment_counter()
        time.sleep(4)

        # Time to contact website to get latest wait times
        if park_update_timer.time_to_do_something() is True:
            update_live_wait_time(PARK_NAME)

    except RuntimeError:
        print("Runtime error getting wait times")

