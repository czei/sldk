from unittest import TestCase
from theme_park_api import get_theme_parks_from_json
from urllib.request import urlopen, Request

from theme_park_api import get_rides_from_json
from theme_park_api import get_park_url
from theme_park_api import get_wait_time

import json


class Test(TestCase):
    def test_get_theme_parks_from_json(self):
        f = open('theme-park-list.json')
        data = json.load(f)
        f.close()
        park_list = get_theme_parks_from_json(data)
        self.assertTrue(len(park_list) > 0)

        found_magic_kingdom = False
        for park in park_list:
            if park[0] == "Disney Magic Kingdom":
                found_magic_kingdom = True
        self.assertTrue(found_magic_kingdom is True)

    def test_get_theme_parks_from_json_http(self):
        url1 = "https://queue-times.com/parks.json"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3"}
        req = Request(url=url1, headers=headers)
        response = urlopen(req).read()
        data = json.loads(response)

        park_list = get_theme_parks_from_json(data)
        self.assertTrue(len(park_list) > 0)

        found_magic_kingdom = False
        for park in park_list:
            if park[0] == "Disney Magic Kingdom":
                found_magic_kingdom = True
        self.assertTrue(found_magic_kingdom is True)

    def test_get_rides_from_json(self):
        f = open('magic-kingdom.json')
        data = json.load(f)
        f.close()
        ride_list = get_rides_from_json(data)
        self.assertTrue(len(ride_list) > 0)

        ride_found = False
        wait_time = 0
        is_open = False
        ride_id = 0
        for ride in ride_list:
            if ride[0] == "Haunted Mansion":
                ride_found = True
                ride_id = ride[1]
                wait_time = ride[2]
                is_open = ride[3]
        self.assertTrue(ride_found)
        self.assertTrue(wait_time == 15)
        self.assertTrue(is_open is True)
        self.assertTrue(ride_id == 140)

        is_open = True
        ride_id = 0
        ride_found = False
        wait_time = 1000
        for ride in ride_list:
            if ride[0] == "Liberty Square Riverboat":
                ride_found = True
                ride_id = ride[1]
                wait_time = ride[2]
                is_open = ride[3]
        self.assertTrue(ride_found)
        self.assertTrue(wait_time == 0)
        self.assertTrue(is_open is False)
        self.assertTrue(ride_id == 1187)


    def test_get_park_url(self):
        f = open('theme-park-list.json')
        data = json.load(f)
        f.close()
        park_list = get_theme_parks_from_json(data)
        url = get_park_url(park_list, 'Disney Magic Kingdom')
        self.assertTrue(url == "https://queue-times.com/parks/6/queue_times.json")

    def test_get_wait_time(self):
        f = open('magic-kingdom.json')
        park_json = json.load(f)
        f.close()
        self.assertTrue(len(park_json) > 0)

        wait_time = get_wait_time(park_json, 'Haunted Mansion')
        self.assertTrue(wait_time == 15)

        wait_time = get_wait_time(park_json, 'Liberty Square Riverboat')
        self.assertTrue(wait_time == "Closed")
