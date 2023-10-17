# SPDX-FileCopyrightText: 2020 John Park for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# Scoreboard matrix display
# uses AdafruitIO to set scores and team names for a scoreboard
# Perfect for cornhole, ping pong, and other games

import time
import board
import terminalio
import wifi
import ssl
import socketpool
import adafruit_requests
import adafruit_display_text.label
import displayio
import framebufferio
import rgbmatrix
from theme_park_api import get_theme_parks_from_json
from theme_park_api import get_rides_from_json
from theme_park_api import get_park_url
from adafruit_matrixportal.matrixportal import MatrixPortal
from rainbowio import colorwheel


# get List of theme parks to choose from
def populate_park_list():
    url = "https://queue-times.com/parks.json"
    wifi.radio.connect(secrets["ssid"], secrets["password"])
    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())
    response = requests.get(url)
    json_response = response.json()
    return get_theme_parks_from_json(json_response)

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
displayio.release_displays()

# --- Display setup ---
matrixportal = MatrixPortal(status_neopixel=board.NEOPIXEL, debug=False)

# RED_COLOR = 0xAA0000
# RED_COLOR = 0x993333
RED_COLOR = 0xCC3333
BLUE_COLOR = 0x0000AA

# Red Score
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(2, int(matrixportal.graphics.display.height * 0.75) - 3),
    text_color=RED_COLOR,
    text_scale=1,
)

# Blue Score
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(25, int(matrixportal.graphics.display.height * 0.75) - 2),
    text_color=BLUE_COLOR,
    text_scale=2,
)

# Red Team name
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(2, int(matrixportal.graphics.display.height * 0.25) - 2),
    text_color=RED_COLOR,
    text_scale=.5,
)

# Blue Team name
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(20, int(matrixportal.graphics.display.height * 0.25)),
    text_color=BLUE_COLOR,
)

# Static 'Connecting' Text
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(59, 0),
)

matrixportal.set_text_color(RED_COLOR, 0)
matrixportal.set_text_color(BLUE_COLOR, 1)

def show_connecting(show):
    if show:
        matrixportal.set_text(".", 4)
    else:
        matrixportal.set_text(" ", 4)

def customize_team_names():
    matrixportal.set_text("Mansion", 0)
    matrixportal.set_text("Haunted", 2)
    matrixportal.set_text("Standby", 3)


def get_wait_time(park_name, ride_name):
    url = get_park_url(park_list, park_name)
    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())
    response = requests.get(url)
    json_response = response.json()
    ride_list = get_rides_from_json(json_response)
    for ride in ride_list:
        if ride[0] == ride_name:
            return ride[2]

def update_scores():
    try:
        matrixportal.set_text(get_wait_time('Disney Magic Kingdom', 'Haunted Mansion'), 1)
    except RuntimeError:
        print("Error updating wait time")

class ColorPicker:
    def __init__(self):
        self.index = 0

    def get_next_color(self):
        self.index = (self.index + 1) % 256
        color = colorwheel(self.index)
        print(f"color = {color}")
        return color

customize_team_names()
update_scores()
last_update = time.monotonic()

picker = ColorPicker()

while True:
    # Set the red score text
    if time.monotonic() > last_update + UPDATE_DELAY:
        matrixportal.set_text_color(picker.get_next_color(), 0)
        # matrixportal.set_text_color(picker.get_next_color(), 1)
        matrixportal.set_text_color(picker.get_next_color(), 2)
        # matrixportal.set_text_color(picker.get_next_color(), 3)
        update_scores()
        last_update = time.monotonic()
