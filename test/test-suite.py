import asyncio
import os
import tempfile
from unittest import TestCase
from unittest.mock import patch, MagicMock
from urllib.request import urlopen, Request
import ssl
import json
from adafruit_datetime import datetime
from adafruit_datetime import date

# Import refactored modules
from src.async_http_request import async_read_url
from src.utils.color_utils import ColorUtils
from src.utils.url_utils import url_decode, load_credentials
from src.models.theme_park import ThemePark
from src.models.theme_park_list import ThemeParkList
from src.models.vacation import Vacation
from src.config.settings_manager import SettingsManager
from src.utils.error_handler import ErrorHandler

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
from unittest.mock import MagicMock

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
    def __init__(self, methodName: str):
        super().__init__(methodName)
        self.header = ""
        self.body = b""

    def test_get_theme_parks_from_json(self):
        f = open('theme-park-list.json')
        data = json.load(f)
        f.close()

        park_list = ThemeParkList(data)
        self.assertTrue(len(park_list.park_list) > 0)

        found_magic_kingdom = False
        for park in park_list.park_list:
            if park.name == "Disney Magic Kingdom":
                found_magic_kingdom = True
        self.assertTrue(found_magic_kingdom is True)

        found_universal = False
        for park in park_list.park_list:
            if park.name == "Universal Studios At Universal Orlando":
                found_universal = True
        self.assertTrue(found_universal is True)

    def test_get_theme_parks_from_json_http(self):
        url1 = "https://queue-times.com/parks.json"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3"}
        req = Request(url=url1, headers=headers)

        # Create an SSL context object with SSLv23 method
        sslContext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)

        response = urlopen(req,context=sslContext).read()
        data = json.loads(response)

        park_list = ThemeParkList(data)
        self.assertTrue(len(park_list.park_list) > 0)
        found_magic_kingdom = False
        for park in park_list.park_list:
            if park.name == "Disney Magic Kingdom":
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
        park_list = ThemeParkList(data)
        url = park_list.get_park_url_from_name('Disney Magic Kingdom')
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

        f = open('epcot-test-data.json')
        park_json = json.load(f)
        f.close()
        self.assertTrue(len(park_json) > 0)

        # Test the new Meet and Greet at EPCOT
        epcot = ThemePark(park_json, "EPCOT")
        wait_time = epcot.get_wait_time('Meet Beloved Disney Pals at Mickey Friends')
        self.assertTrue(wait_time == 35)

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

        # Create an SSL context object with SSLv23 method
        sslContext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)

        req = Request(url=url1, headers=headers)
        response = urlopen(req, context=sslContext).read()
        data = json.loads(response)
        park_list = ThemeParkList(data)

        location = park_list.get_park_location_from_id(6)
        print(f"Location of park id 6 is {location}: {location[0]}, {location[1]}")
        self.assertTrue(len(park_list.park_list) > 0)
        self.assertTrue(location[0] == "28.417663")
        self.assertTrue(location[1] == "-81.581212")

    def test_vacation(self):
        params = "Name=Orlando+Vacation&Year=2044&Month=1&Day=2"
        vac = Vacation()
        self.assertTrue(vac.is_set() is False)
        vac.parse(params)
        self.assertTrue(vac.name == "Orlando Vacation")
        self.assertTrue(vac.year == 2044)
        self.assertTrue(vac.month == 1)
        self.assertTrue(vac.day == 2)
        self.assertTrue(vac.is_set() is True)

        # This only works running on MatrixPortal board
        # rtc.RTC().datetime = (2023, 1, 2, 0, 1, 34, 0, 0, 0)
        # today = datetime.now()
        self.assertTrue(vac.get_days_until() >= 0)

    def test_park_param_parsing(self):
        str_params = "park-id=7&Name=WDW&Year=2027&Month=1&Day=4&skip_closed=on"

        f = open('theme-park-list.json')
        data = json.load(f)
        f.close()
        park_list = ThemeParkList(data)
        self.assertTrue(len(park_list.park_list) > 0)

        park_list.parse(str_params)
        self.assertTrue(park_list.current_park.id == 7)
        self.assertTrue(park_list.current_park.name == "Disney Hollywood Studios")
        self.assertTrue(park_list.skip_closed is True)

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

        self.assertTrue(manager.settings["skip_closed"] is True)
        self.assertTrue(manager.settings["skip_meet"] is False)
        self.assertTrue(manager.settings["current_park_id"] == 6)
        self.assertTrue(manager.settings["current_park_name"] == "Disney Magic Kingdom")
        manager.settings["skip_closed"] = False
        manager.settings["skip_meet"] = False
        self.assertTrue(manager.settings["skip_closed"] is False)

        manager.settings["new_param"] = 12
        self.assertTrue(manager.settings["new_param"] == 12)

        manager.save_settings()
        manager1 = SettingsManager("settings.json")
        self.assertTrue(manager1.settings["skip_closed"] is False)
        self.assertTrue(manager1.settings["new_param"] == 12)
        manager.settings["skip_closed"] = False
        manager.settings["skip_Meet"] = False
        manager.save_settings()

        f = open('theme-park-list.json')
        data = json.load(f)
        f.close()

        park_list = ThemeParkList(data)
        self.assertTrue(len(park_list.park_list) > 0)
        park_list.load_settings(manager)

        self.assertTrue(park_list.current_park.id == 6)
        self.assertTrue(park_list.current_park.name == "Disney Magic Kingdom")
        self.assertTrue(park_list.skip_closed is False)
        self.assertTrue(park_list.skip_meet is False)

        manager.settings["skip_closed"] = True
        manager.settings["skip_Meet"] = False
        manager.save_settings()

        scroll_speed = manager.get_scroll_speed()
        self.assertTrue(scroll_speed == 0.04)
        manager.settings["scroll_speed"] = "Fast"
        scroll_speed = manager.get_scroll_speed()
        self.assertTrue(scroll_speed == 0.02)
        manager.settings["scroll_speed"] = "Slow"
        scroll_speed = manager.get_scroll_speed()
        self.assertTrue(scroll_speed == 0.06)

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

        # 16 of the rides in the file have the is_open flag set to false,
        # but 3 of them say they're open, but the wait time is zero.
        num_open_rides = 0
        num_closed_rides = 0
        for ride in magic_kingdom.rides:
            if ride.is_open():
                num_open_rides += 1
            else:
                num_closed_rides += 1

        self.assertTrue(num_closed_rides == 19)

    def test_credentials(self):
        ssid, password = load_credentials()
        self.assertTrue(ssid == "FBI Surveillance Van 112")
        self.assertTrue(password == "9196190607")

    def test_url_decode(self):
        self.assertTrue(url_decode("FBI%20Surveillance%20Van%20112") == "FBI Surveillance Van 112")
        self.assertTrue(url_decode("FBI+Surveillance+Van+112") == "FBI Surveillance Van 112")
        self.assertTrue(url_decode("Paris%2C+France") == "Paris, France")

    def test_brightness_scale(self):
        orig_color = "0xfdf5e6"
        # scale by .75
        new_color = ColorUtils.scale_color(orig_color, .50)
        print(f"New color is {new_color}")
        self.assertTrue(new_color == "0x7e7a73")
        new_color = ColorUtils.scale_color("0x000000", .50)
        print(f"New color is {new_color}")
        self.assertTrue(new_color == "0x000000")
        new_color = ColorUtils.scale_color("0xcc3333", 1)
        self.assertTrue(new_color == "0xcc3333")
        new_color = ColorUtils.scale_color("0xffa500", 1)
        self.assertTrue(new_color == "0xffa500")

    # async def test_shopify(self):
    #     # Example Usage
    #     json_string = """{
    #         "data": {
    #             "orders": {
    #                 "edges": [
    #                     {
    #                         "node": {
    #                             "name": "#1047",
    #                             "processedAt": "2024-01-17T15:31:22Z"
    #                         }
    #                     }
    #                 ]
    #             }
    #         }
    #     }"""
    #
    #     subscription_date = parse_order_date(json_string)
    #     self.assertTrue(subscription_date.year == 2024)
    #     self.assertTrue(subscription_date.month == "01")
    #     self.assertTrue(subscription_date.day == "17")
    #
    #     test_date = date(2024, 1, 19)
    #     self.assertTrue(valid_subscription(subscription_date, test_date) is True)
    #
    #     test_date = date(2024, 2, 19)
    #     self.assertTrue(valid_subscription(subscription_date, test_date) is False)

    @patch('src.utils.ErrorHandler.storage')
    def test_error_handler_writable_filesystem(self, mock_storage):
        # Setup mock for writable filesystem
        mock_mount = MagicMock()
        mock_mount.readonly = False
        mock_storage.getmount.return_value = mock_mount
        
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            test_file = temp_file.name
        
        try:
            # Test ErrorHandler initialization with writable filesystem
            handler = ErrorHandler(test_file)
            self.assertFalse(handler.is_readonly)
            
            # Test writing messages
            handler.info("Test info message")
            handler.debug("Test debug message")
            
            # Verify messages were written to the file
            with open(test_file, 'r') as f:
                content = f.read()
                self.assertIn("Test info message", content)
                self.assertIn("Test debug message", content)
            
            # Test error handling
            try:
                # Generate a test exception
                raise ValueError("Test error")
            except ValueError as e:
                handler.error(e, "Test error description")
            
            # Verify error was written to the file
            with open(test_file, 'r') as f:
                content = f.read()
                self.assertIn("Test error description:Test error", content)
                self.assertIn("stack trace:", content)
        
        finally:
            # Clean up temporary file
            if os.path.exists(test_file):
                os.remove(test_file)
    
    @patch('src.utils.ErrorHandler.storage')
    def test_error_handler_readonly_filesystem(self, mock_storage):
        # Setup mock for read-only filesystem
        mock_mount = MagicMock()
        mock_mount.readonly = True
        mock_storage.getmount.return_value = mock_mount
        
        # Create a non-existent file path for testing
        test_file = "/nonexistent/path/error.log"
        
        # Test ErrorHandler initialization with read-only filesystem
        with patch('builtins.print') as mock_print:
            handler = ErrorHandler(test_file)
            self.assertTrue(handler.is_readonly)
            
            # Verify initialization message
            mock_print.assert_any_call("ErrorHandler initialized - Read-only filesystem")
            
            # Test writing messages to read-only filesystem
            handler.info("Test info message")
            handler.debug("Test debug message")
            
            # Verify messages were printed but not written
            mock_print.assert_any_call("Test info message")
            mock_print.assert_any_call("Test debug message")
            
            # Test error handling on read-only filesystem
            try:
                # Generate a test exception
                raise ValueError("Test readonly error")
            except ValueError as e:
                handler.error(e, "Test readonly error description")
            
            # Verify error was printed but not written
            mock_print.assert_any_call("Test readonly error description:Test readonly error")
            mock_print.assert_any_call("stack trace:")
    
    def test_error_handler_filter_non_ascii(self):
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            test_file = temp_file.name
        
        try:
            # Test static method directly
            self.assertEqual(ErrorHandler.filter_non_ascii("Normal ASCII text"), "Normal ASCII text")
            self.assertEqual(ErrorHandler.filter_non_ascii("Text with emoji 😊"), "Text with emoji ")
            self.assertEqual(ErrorHandler.filter_non_ascii("Special characters: ñáéíóú"), "Special characters: ")
            self.assertEqual(ErrorHandler.filter_non_ascii(None), "")
            
            # Test through instance methods
            with patch('src.utils.ErrorHandler.storage', MagicMock()):
                handler = ErrorHandler(test_file)
                # Generate text with non-ASCII characters
                mixed_text = "Error with Unicode: ⚠️ Warning! ⚠️"
                
                # Capture print output
                with patch('builtins.print'):
                    handler.write_to_file(mixed_text)
                
                # Verify only ASCII characters were written
                if not handler.is_readonly:
                    with open(test_file, 'r') as f:
                        content = f.read()
                        self.assertIn("Error with Unicode:  Warning! ", content)
                        self.assertNotIn("⚠️", content)
        
        finally:
            # Clean up temporary file
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_error_handler_filesystem_detection_fallback(self):
        # Test fallback when storage.getmount raises an exception
        with patch('src.utils.ErrorHandler.storage') as mock_storage:
            mock_storage.getmount.side_effect = AttributeError("No getmount method")
            
            # For writable case - create temp file that can be written
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                test_file = temp_file.name
            
            try:
                # Should detect filesystem is writable through fallback method
                handler = ErrorHandler(test_file)
                self.assertFalse(handler.is_readonly)
                
                # Test writing to the file still works
                handler.info("Test fallback message")
                
                with open(test_file, 'r') as f:
                    content = f.read()
                    self.assertIn("Test fallback message", content)
                
                # Now test with a path that can't be written to
                with patch('builtins.open') as mock_open:
                    mock_open.side_effect = OSError("Permission denied")
                    
                    handler = ErrorHandler("/protected/path/error.log")
                    self.assertTrue(handler.is_readonly)
            
            finally:
                # Clean up temporary file
                if os.path.exists(test_file):
                    os.remove(test_file)
    
    def test_async_http(self):
        # Connecting to sockets is different from an actual OS not
        # running CircuitPython on a chip.
        path = "/api/quotes.php"
        domain = "www.adafruit.com"
        #path = "/parks/6/queue_times.json"
        #domain = "queue-times.com"

        # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # ssl_sock = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT).wrap_socket(sock, False, True, True, domain)

        # addr_info = ""
        # try:
        #     addr_info = socket.getaddrinfo(domain, 443)
        # except socket.gaierror:
        #     print(f"Invalid domain {domain}. Can't resolve to an IP address.")
        #
        # print(f"Address info: {addr_info}")
        # addr = addr_info[0][-1]
        #
        # ssl_sock.context.check_hostname = False
        # ssl_sock.context.verify_mode = ssl.CERT_NONE
        # ssl_sock.setblocking(False)
        # ssl_sock.connect(addr)

#        asyncio.run(test_http_read(self, domain, path))
#        print(f"Header = {self.header}")
#        print(f"Body={self.body}")
#        str_json = self.body.decode('utf-8')
#        json_data = json.loads(str_json)
#        self.assertTrue(len(json_data[0]['author']) > 0)
#        self.assertTrue(len(json_data[0]['text']) > 0)

async def test_http_read(test_class, domain, path):
    head, body = await async_read_url(domain, path)
    test_class.header = head
    test_class.body = body

