# SPDX-FileCopyrightText: 2020 John Park for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# Scoreboard matrix display
# uses AdafruitIO to set scores and team names for a scoreboard
# Perfect for cornhole, ping pong, and other games

import re
import time
import board
import terminalio
import wifi
import ssl
import socketpool
import adafruit_requests
import displayio
from rainbowio import colorwheel
from theme_park_api import get_theme_parks_from_json
from theme_park_api import Rides

from theme_park_api import get_park_url
from theme_park_api import get_wait_time
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
    scrolling=False,
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

def customize_team_names():
    # matrixportal.set_text("Mansion", 0)
    matrixportal.set_text("5", 0)
    matrixportal.set_text("Haunted\nMansion", 1)
    matrixportal.set_text("Standby", 2)


def get_live_wait_time(park_name, ride_name):
    url = get_park_url(park_list, park_name)
    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())
    response = requests.get(url)
    json_response = response.json()
    return get_wait_time(json_response, ride_name)

def process_ride_name(ride_name):
    return re.sub(r'\s' , '\n', ride_name)

def update_scores(park_name, ride_name):
    # matrixportal.set_text_color(BLACK_COLOR)
    if display_wait is False :
        matrixportal.set_text("", STANDBY)
        matrixportal.set_text("", WAIT_TIME)
        matrixportal.set_text(process_ride_name(ride_name), RIDE_NAME)
    else:
        wait_time = get_live_wait_time(park_name, ride_name)
        matrixportal.set_text("", RIDE_NAME)
        matrixportal.set_text(wait_time, WAIT_TIME)
        matrixportal.set_text("Standby", STANDBY)


class ColorPicker:
    def __init__(self):
        self.index = 0

    def get_next_color(self):
        self.index = (self.index + 1) % 256
        color = colorwheel(self.index)
        print(f"color = {color}")
        return color

# customize_team_names()
# update_scores()
last_update = time.monotonic()
rides = populate_ride_list(park_list, 'Disney Magic Kingdom')


while True:
    current_ride_index = 0
    if time.monotonic() > last_update + UPDATE_DELAY:
        display_wait = not display_wait
        ride_name = rides.get_current_ride_name()
        print(f"Current Ride: {ride_name}")
        update_scores('Disney Magic Kingdom', ride_name)
        last_update = time.monotonic()
        if display_wait is True:
            rides.increment_counter()
