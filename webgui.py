import json

from rainbowio import colorwheel

import biplane
from theme_park_api import populate_park_list




def remove_non_ascii(orig_str):
    new_str = ""
    for c in orig_str:
        if ord(c) < 128:
            new_str += c
    return new_str

class ColorPicker:
    def __init__(self):
        self.index = 0

    def get_next_color(self):
        self.index = (self.index + 1) % 256
        color = colorwheel(self.index)
        print(f"color = {color}")
        return color



