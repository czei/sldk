from unittest import TestCase
from urllib.request import urlopen, Request

from theme_park_api import get_park_url_from_name
from theme_park_api import ThemePark
from theme_park_api import get_theme_parks_from_json
from theme_park_api import Vacation
from theme_park_api import get_park_location_from_id
import json
import datetime
from adafruit_datetime import datetime, time
from theme_park_api import SettingsManager
try:
    import rtc
except ModuleNotFoundError:
    # Mocking the unavailable modules in non-embedded environments
    # You can add more according to your needs, these are just placeholders
    class rtc:
        class RTC:
            def __init__(self):
                self.datetime = datetime()

"""
This file ensures everything is in place to run PyTest based unit tests against
the adafruit_radio module. It works by using Python's mock library to add
MagicMock objects to sys.modules for the modules which are not available to
standard Python because they're CircuitPython only modules.

Such mocking happens as soon as this conftest.py file is imported (so the
mocked modules exist in sys.modules before the module to be tested is
imported), and immediately before each test function is evaluated (so changes
to state remain isolated between tests).
"""
import sys
from unittest.mock import MagicMock, Mock

# Add fully qualified namespace paths to things that are imported, but which
# should be mocked away. For instance, modules which are available in
# CircuitPython but not standard Python.
MOCK_MODULES = [
    "adafruit_ble.BLERadio",
    "adafruit_ble.advertising.adafruit.AdafruitRadio",
    "adafruit_matrixportal.matrixportal",
]


def mock_imported_modules():
    """
    Mocks away the modules named in MOCK_MODULES, so the module under test
    can be imported with modules which may not be available.
    """
    module_paths = set()
    for m in MOCK_MODULES:
        namespaces = m.split(".")
        ns = []
        for n in namespaces:
            ns.append(n)
            module_paths.add(".".join(ns))
    for m_path in module_paths:
        sys.modules[m_path] = MagicMock()


def pytest_runtest_setup(item):
    """
    Called immediately before any test function is called.

    Recreates afresh the mocked away modules so state between tests remains
    isolated.
    """
    mock_imported_modules()


# Initial mocking needed to stop ImportError when importing module under test.
mock_imported_modules()


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

        park = ThemePark(data, "Disney Magic Kingdom", 6)
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
                is_open = ride.open_flag
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
                is_open = ride.open_flag
        self.assertTrue(ride_found)
        self.assertTrue(wait_time == 0)
        self.assertTrue(is_open is False)
        self.assertTrue(ride_id == 1187)

    def test_get_park_url_from_name(self):
        f = open('theme-park-list.json')
        data = json.load(f)
        f.close()
        park_list = get_theme_parks_from_json(data)
        url = get_park_url_from_name(park_list, 'Disney Magic Kingdom')
        self.assertTrue(url == "https://queue-times.com/parks/6/queue_times.json")

    def test_get_wait_time(self):
        f = open('magic-kingdom.json')
        park_json = json.load(f)
        f.close()
        self.assertTrue(len(park_json) > 0)

        park = ThemePark(park_json, 'Park Name')
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

        universal_park = ThemePark(park_json, "Universal")

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
        park_class_instance = ThemePark(data, 'Disney Magic Kingdom', 6)
        self.assertTrue(park_class_instance.get_num_rides() > 0)
        ride_name = park_class_instance.get_current_ride_name()
        self.assertTrue(ride_name == "A Pirate's Adventure ~ Treasures of the Seven Seas")
        ride_name = park_class_instance.get_next_ride_name()
        self.assertTrue(ride_name == "Jungle Cruise")
        self.assertTrue(park_class_instance.get_current_ride_time() == 5)

    def test_theme_park_class(self):
        park = ThemePark()
        self.assertTrue(type(park) is ThemePark)

    def test_get_park_location_from_id(self):
        url1 = "https://queue-times.com/parks.json"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3"}
        req = Request(url=url1, headers=headers)
        response = urlopen(req).read()
        data = json.loads(response)
        park_list = get_theme_parks_from_json(data)

        location = get_park_location_from_id(park_list, 6)
        print(f"Location of park id 6 is {location}: {location[0]}, {location[1]}")
        self.assertTrue(len(park_list) > 0)
        self.assertTrue(location[0] == "28.417663")
        self.assertTrue(location[1] == "-81.581212")

    def test_vacation(self):
        params = "Name=Wdw&Year=2024&Month=1&Day=2"
        vac = Vacation()
        self.assertTrue(vac.is_set() is False)
        vac.parse(params)
        self.assertTrue(vac.name == "Wdw")
        self.assertTrue(vac.year == 2024)
        self.assertTrue(vac.month == 1)
        self.assertTrue(vac.day == 2)
        self.assertTrue(vac.is_set() is True)

        # This only works running on MatrixPortal board
        # rtc.RTC().datetime = (2023, 1, 2, 0, 1, 34, 0, 0, 0)
        # today = datetime.now()
        self.assertTrue(vac.get_days_until() >= 0)

    def test_park_param_parsing(self):
        str_params = "park-id=7&Name=WDW&Year=2027&Month=1&Day=4&skip_closed=on"
        park = ThemePark()

        f = open('theme-park-list.json')
        data = json.load(f)
        f.close()
        park_list = get_theme_parks_from_json(data)
        self.assertTrue(len(park_list) > 0)

        park.parse(str_params, park_list)
        self.assertTrue(park.id == 7)
        self.assertTrue(park.name == "Disney Hollywood Studios")
        self.assertTrue(park.skip_closed == "True")

    def test_set_system_clock(self):
        # Only works running on actual board
        # set_system_clock()
        # self.assertTrue(rtc.RTC().datetime == (2023, 1, 1, 0, 1, 34, 0, 0, 0))

        time_data = {'timezone': 'America/New_York', 'utc_datetime': '2023-12-04T15:16:28.262657+00:00',
                     'raw_offset': -18000, 'client_ip': '74.124.189.239', 'dst_from': None, 'unixtime': 1701702988,
                     'utc_offset': '-05:00', 'datetime': '2023-12-04T10:16:28.262657-05:00', 'week_number': 49,
                     'abbreviation': 'EST', 'day_of_year': 338, 'day_of_week': 1, 'dst': False, 'dst_offset': 0,
                     'dst_until': None}

        print(f"Datetime is {time_data["datetime"]}")
        date_string = time_data["datetime"]
        date_elements = date_string.split("T")
        date = date_elements[0].split("-")
        ltime = date_elements[1].split(".")
        offset = ltime[1]
        ltime = ltime[0].split(":")

        # Pass elements to datetime constructor
        datetime_object = datetime(
            int(date[0]),
            int(date[1]),
            int(date[2]),
            int(ltime[0]),
            int(ltime[1]),
            int(ltime[2])
        )

        print(f"The new datetime is {datetime_object}")
        self.assertTrue(datetime_object.year == 2023)
        self.assertTrue(datetime_object.day == 4)
        self.assertTrue(datetime_object.month == 12)

    def test_settings_manager(self):
        manager = SettingsManager("settings.json")
        manager.load_settings()

        self.assertTrue(manager.settings["display_closed_rides"] is True)
        self.assertTrue(manager.settings["current_park_id"] == 6)
        self.assertTrue(manager.settings["current_park_name"] == "Disney Magic Kingdom")
        manager.settings["display_closed_rides"] = False
        self.assertTrue(manager.settings["display_closed_rides"] is False)

        manager.settings["new_param"] = 12
        self.assertTrue(manager.settings["new_param"] == 12)

        manager.save_settings()
        manager1 = SettingsManager("settings.json")
        self.assertTrue(manager1.settings["display_closed_rides"] is False)
        self.assertTrue(manager1.settings["new_param"] == 12)
        manager.settings["display_closed_rides"] = True
        manager.save_settings()

        ride = ThemePark()
        self.assertTrue(ride.id == 0)
        self.assertTrue(ride.name != "Disney Magic Kingdom")
        self.assertTrue(ride.skip_closed is False)
        self.assertTrue(ride.skip_meet is False)
        ride.load_settings(manager)
        self.assertTrue(ride.id == 6)
        self.assertTrue(ride.name == "Disney Magic Kingdom")
        self.assertTrue(ride.skip_closed is True)
        self.assertTrue(ride.skip_meet is True)

        scroll_speed = manager.get_scroll_speed()
        self.assertTrue(scroll_speed == 0.4)
        manager.settings["scroll_speed"] = "Fast"
        scroll_speed = manager.get_scroll_speed()
        self.assertTrue(scroll_speed == 0.2)
        manager.settings["scroll_speed"] = "Slow"
        scroll_speed = manager.get_scroll_speed()
        self.assertTrue(scroll_speed == 0.6)



    def test_closed_park(self):
        f = open('closed-park.json')
        data = json.load(f)
        f.close()

        tokyo_disneyland = ThemePark(data, "Tokyo Disneyland", 274)
        self.assertTrue(tokyo_disneyland.is_open is False)
        self.assertTrue(len(tokyo_disneyland.rides) > 10)

        f = open('magic-kingdom.json')
        data = json.load(f)
        f.close()

        magic_kingdom = ThemePark(data, "Disney Magic Kingdom", 6)
        self.assertTrue(len(magic_kingdom.rides) > 10)
        self.assertTrue(magic_kingdom.is_open is True)
