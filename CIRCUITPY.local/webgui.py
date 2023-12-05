import json
import biplane
from theme_park_api import populate_park_list




def remove_non_ascii(orig_str):
    new_str = ""
    for c in orig_str:
        if ord(c) < 128:
            new_str += c
    return new_str



