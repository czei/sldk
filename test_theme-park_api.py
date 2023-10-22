from unittest import TestCase
from urllib.request import urlopen, Request
from theme_park_api import get_park_url
from theme_park_api import ThemePark
from theme_park_api import ThemeParkRide
from theme_park_api import get_theme_parks_from_json
from theme_park_api import DisplayMode
import json
import time


class Test(TestCase):
    def test_get_theme_parks_from_json(self):
        f = open('theme-park-list.json')
        data = json.load(f)
        f.close()
        park_list = get_theme_parks_from_json(data)
        self.assertTrue(len(park_list) > 0)

        found_magic_kingdom = False
        for park_json in park_list:
            if park_json[0] == "Disney Magic Kingdom":
                found_magic_kingdom = True
        self.assertTrue(found_magic_kingdom is True)

        found_universal = False
        for park_json in park_list:
            if park_json[0] == "Universal Studios At Universal Orlando":
                found_universal = True
        self.assertTrue(found_universal is True)

    def test_get_theme_parks_from_json_http(self):
        url1 = "https://queue-times.com/parks.json"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3"}
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

        park = ThemePark("Magic Kingdom", data)
        self.assertTrue(park.get_num_rides() > 0)

        ride_found = False
        wait_time = 0
        is_open = False
        ride_id = 0
        for ride in park.rides:
            if ride.name == "Haunted Mansion":
                ride_found = True
                ride_id = ride.id
                wait_time = ride.wait_time
                is_open = ride.is_open
        self.assertTrue(ride_found)
        self.assertTrue(wait_time == 15)
        self.assertTrue(is_open is True)
        self.assertTrue(ride_id == 140)

        is_open = True
        ride_id = 0
        ride_found = False
        wait_time = 1000
        for ride in park.rides:
            if ride.name == "Liberty Square Riverboat":
                ride_found = True
                ride_id = ride.id
                wait_time = ride.wait_time
                is_open = ride.is_open
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

        park = ThemePark('Park Name', park_json)
        wait_time = park.get_wait_time('Haunted Mansion')
        self.assertTrue(wait_time == 15)
        is_open = park.is_ride_open('Haunted Mansion')
        self.assertTrue(is_open is True)

        wait_time = park.get_wait_time('Liberty Square Riverboat')
        self.assertTrue(wait_time == 0)
        is_open = park.is_ride_open('Liberty Square Riverboat')
        self.assertTrue(is_open is False)

        f = open('universal.json')
        park_json = json.load(f)
        f.close()
        self.assertTrue(len(park_json) > 0)

        universal_park = ThemePark('Universal', park_json)

        wait_time = universal_park.get_wait_time('Revenge of the Mummy™')
        self.assertTrue(wait_time == 20)

        wait_time = universal_park.get_wait_time('Illumination\'s Villain-Con Minion Blast')
        self.assertTrue(wait_time == 40)

        wait_time = universal_park.get_wait_time('Despicable Me Minion Mayhem™')
        self.assertTrue(wait_time == 55)

    def test_get_ride_class(self):
        f = open('magic-kingdom.json')
        data = json.load(f)
        f.close()
        park_class_instance = ThemePark('Magic Kingdom', data)
        self.assertTrue(park_class_instance.get_num_rides() > 0)
        ride_name = park_class_instance.get_current_ride_name()
        self.assertTrue(ride_name == "A Pirate's Adventure ~ Treasures of the Seven Seas")
        ride_name = park_class_instance.get_next_ride_name()
        self.assertTrue(ride_name == "Jungle Cruise")
        self.assertTrue(park_class_instance.get_current_ride_time() == 5)

    def test_display_mode(self):
        mode = DisplayMode(2)
        self.assertTrue(mode.get_current_mode() == "Scrolling")
        mode.increment_mode()
        self.assertTrue(mode.get_current_mode() == "Wait")
        mode.increment_mode()
        self.assertTrue(mode.get_current_mode() == "Scrolling")

        self.assertTrue(mode.time_to_switch_mode() is False)
        time.sleep(5)
        self.assertTrue(mode.time_to_switch_mode() is True)
