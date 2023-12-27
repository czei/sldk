import terminalio
import asyncio
import displayio
from adafruit_datetime import datetime
from adafruit_display_text.label import Label
import json

try:
    import rtc
    import microcontroller
except ModuleNotFoundError:
    # Mocking the unavailable modules in non-embedded environments
    # You can add more according to your needs, these are just placeholders
    class rtc:
        class RTC:
            def __init__(self):
                self.datetime = datetime()

def set_system_clock(http_requests):
    # Set device time from the internet
    response = http_requests.get(
        'http://worldtimeapi.org/api/timezone/America/New_York')
    time_data = response.json()
    date_string = time_data["datetime"]
    date_elements = date_string.split("T")
    date = date_elements[0].split("-")
    the_time = date_elements[1].split(".")
    the_time = the_time[0].split(":")

    # Pass elements to datetime constructor
    #            int(float(offset)*1000000)
    datetime_object = (
        int(date[0]),
        int(date[1]),
        int(date[2]),
        int(the_time[0]),
        int(the_time[1]),
        int(the_time[2]),
        -1,
        -1,
        -1
    )

    print(f"Setting the time to {datetime_object}")
    rtc.RTC().datetime = datetime_object
    return datetime_object


def populate_park_list(requests):
    """
    Returns an iterable list of theme parks and their ids from Queue Times.
    ONLY WORKS ON CircuitPython hardware.
    :return:
    """
    url = "https://queue-times.com/parks.json"
    # pool = socketpool.SocketPool(wifi.radio)
    # requests = adafruit_requests.Session(pool, ssl.create_default_context())
    response = requests.get(url)
    json_response = response.json()
    return sorted(get_theme_parks_from_json(json_response))


def get_theme_parks_from_json(json):
    """
    Return a list of theme parks and their ids
    :return: a tuple of park name and id
    """
    park_list = []
    for company in json:
        # print(f"company = {company}")
        for parks in company:
            if parks == "parks":
                # print(f"park list = {parks}")
                park = company[parks]
                name = ""
                park_id = 0
                latitude = 0
                longitude = 0
                for item in park:
                    # print(f"park = {item}")
                    for element in item:
                        if element == "name":
                            name = item[element]
                        if element == "id":
                            park_id = item[element]
                        if element == "latitude":
                            latitude = item[element]
                        if element == "longitude":
                            longitude = item[element]
                    name_id = tuple([name, park_id, latitude, longitude])
                    # print(f"Adding tuple {name_id}")
                    park_list.append(name_id)

    return park_list



def get_park_url_from_name(park_list, park_name):
    """
    Takes the output from get_theme_parks_from_json and assembles
    the URL to get individual ride data.
    :param park_list: A list of tuples of park names and ids
    :param park_name: The string describing the Theme Park
    :return: JSON url for a particular theme park
    """
    # Magic Kingdom URL example: https://queue-times.com/parks/6/queue_times.json
    url1 = "https://queue-times.com/parks/"
    url2 = "/queue_times.json"
    for park in park_list:
        if park[0] == park_name:
            park_id = park[1]
            url = url1 + str(park_id) + url2
            return url


def get_park_url_from_id(park_list, park_id):
    """
    Takes the output from get_theme_parks_from_json and assembles
    the URL to get individual ride data.
    :param park_list: A list of tuples of park names and ids
    :param park_id: The id from QueueTimes.com
    :return: JSON url for a particular theme park
    """
    # Magic Kingdom URL example: https://queue-times.com/parks/6/queue_times.json
    url1 = "https://queue-times.com/parks/"
    url2 = "/queue_times.json"
    return url1 + str(park_id) + url2


def get_park_location_from_id(park_list, park_id):
    """
    Takes the output from get_theme_parks_from_json and assembles
    the URL to get individual ride data.
    :param park_list: A list of tuples of park names and ids
    :param park_id: The id from QueueTimes.com
    :return: JSON url for a particular theme park
    """
    # Magic Kingdom URL example: https://queue-times.com/parks/6/queue_times.json
    for park in park_list:
        if park[1] == park_id:
            return park[2], park[3]


def get_park_name_from_id(park_list, park_id):
    park_name = ""
    for park in park_list:
        if park[1] == park_id:
            park_name = park[0]
            return park_name


class ThemeParkRide:
    def __init__(self, name, new_id, wait_time, open_flag):
        self.name = name
        self.id = new_id
        self.wait_time = wait_time
        self.open_flag = open_flag

    def is_open(self):
        """
        The listings will often mark a ride as "open" when its obvious
        after hours and the park is closed, but the wait time will be zero.
        Because of this discrepancy we have to check both.
        :return:
        """
        return self.open_flag is True and self.wait_time > 0


class ThemePark:
    def __init__(self, json_data=(), name="", id=0, latitude=0.0, longitude=0.0):
        """
        :param self:
        :param json_data: Python JSON objects from a single park
        :return:
        """
        self.counter = 0
        self.name = name
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.rides = self.get_rides_from_json(json_data)
        self.skip_meet = False
        self.skip_closed = False
        self.is_open = False

    @staticmethod
    def remove_non_ascii(orig_str):
        """
        Removes non-ascii characters from the data feed assigned
        park names that includes foreign languages.
        """
        new_str = ""
        for c in orig_str:
            if ord(c) < 128:
                new_str += c
        return new_str

    def get_rides_from_json(self,json_data):
        """
        Returns a list of the names of rides at a particular park contained in the JSON
        :param json_data: A JSON file containing data for a particular park
        :return: name, id, wait_time, open_flag
        """
        ride_list = []
        self.is_open = False

        # print(f"Json_data is: {json_data}")
        if len(json_data) <= 0:
            return ride_list

        lands_list = json_data["lands"]
        for land in lands_list:
            rides = land["rides"]
            for ride in rides:
                name = ride["name"]
                # print(f"Ride = {name}")
                ride_id = ride["id"]
                wait_time = ride["wait_time"]
                open_flag = ride["is_open"]
                this_ride_object = ThemeParkRide(name, ride_id, wait_time, open_flag)
                if this_ride_object.is_open() is True:
                    self.is_open = True
                ride_list.append(this_ride_object)

        return ride_list

    def is_valid(self):
        return self.id >= 0

    def set_rides(self, ride_json):
        self.rides = self.get_rides_from_json(ride_json)
        self.counter = 0

    def get_wait_time(self, ride_name):
        for ride in self.rides:
            if ride.name == ride_name:
                return ride.wait_time

    def is_ride_open(self, ride_name):
        for ride in self.rides:
            if ride.name == ride_name:
                return ride.open_flag

    def increment(self):
        self.counter += 1
        if self.counter >= len(self.rides):
            self.counter = 0

    def update(self, json_data):
        self.rides = self.get_rides_from_json(json_data)

    def get_current_ride_name(self):
        return self.rides[self.counter].name

    def is_current_ride_open(self):
        if self.rides[self.counter].open_flag is False:
            return False
        else:
            return True

    def get_current_ride_time(self):
        return self.rides[self.counter].wait_time

    def get_next_ride_name(self):
        self.increment()
        return self.rides[self.counter].name

    def get_num_rides(self):
        return len(self.rides)

    def change_parks(self, new_name, new_id):
        self.name = new_name
        self.id = new_id
        self.counter = 0

    def parse(self, str_params, park_list):
        params = str_params.split("&")
        print(f"Params = {params}")
        self.skip_meet = "False"
        self.skip_closed = "False"
        for param in params:
            name_value = param.split("=")
            # print(f"param = {param}")
            # print(f"Name_value = {name_value}")
            if name_value[0] == "park-id":
                self.id = int(name_value[1])
                self.name = get_park_name_from_id(park_list, self.id)
                location = get_park_location_from_id(park_list, self.id)
                self.latitude = location[0]
                self.longitude = location[1]
                print(f"New park name = {self.name}")
                print(f"New park id = {self.id}")
                print(f"New park latitude = {self.latitude}")
                print(f"New park longitude = {self.longitude}")
            if name_value[0] == "skip_closed":
                print("Skip closed is True")
                self.skip_closed = "True"
            if name_value[0] == "skip_meet":
                print("Skip meet is True")
                self.skip_meet = "True"
    def store_settings(self, sm):
        sm.settings["current_park_name"] = self.name
        sm.settings["current_park_id"] = self.id
        sm.settings["skip_meet"] = self.skip_meet
        sm.settings["skip_closed"] = self.skip_closed

    def load_settings(self, sm):
        keys = sm.settings.keys()
        if "current_park_name" in keys:
            self.name = sm.settings["current_park_name"]
        if "current_park_id" in keys:
            self.id = sm.settings["current_park_id"]
        if "skip_meet" in keys:
            self.skip_meet = sm.settings["skip_meet"]
        if "skip_closed" in keys:
            self.skip_closed = sm.settings["skip_closed"]
        print(f"Loaded park {self.name} at ID: {self.id}")


class ThemeParkIterator:
    def __init__(self, park):
        """
        :param self:
        :return:
        """
        self.park = park


class DisplayStyle:
    """
    Mostly static or scrolling, but could expand in the future
    """

    def __init__(self):
        self.SCROLLING = 0
        self.STATIC = 1


class Vacation:
    def __init__(self, park_name="", year=0, month=0, day=0):
        self.name = park_name
        self.year = year
        self.month = month
        self.day = day

    def print(self):
        print(f"Vacation: {self.name}, {self.year}, {self.month}, {self.day}, isset={self.is_set()}")

    def parse(self, str_params):
        params = str_params.split("&")
        for param in params:
            name_value = param.split("=")
            if name_value[0] == "Name":
                self.name = str(name_value[1])
            if name_value[0] == "Year":
                self.year = int(name_value[1])
            if name_value[0] == "Month":
                self.month = int(name_value[1])
            if name_value[0] == "Day":
                self.day = int(name_value[1])

    def get_days_until(self):
        today = datetime.now()
        print(f"The current year is {today.year}")
        future = datetime(self.year, self.month, self.day)
        diff = future - today
        return diff.days + 1

    def is_set(self):
        if len(self.name) > 0 and self.year > 1999 and self.month > 0 and self.day > 0:
            return True

        return False

    def store_settings(self, sm):
        sm.settings["next_visit"] = self.name
        sm.settings["next_visit_year"] = self.year
        sm.settings["next_visit_month"] = self.month
        sm.settings["next_visit_day"] = self.day

    def load_settings(self, sm):
        if "next_visit" in sm.settings.keys():
            self.name = sm.settings.get("next_visit")
        if "next_visit_year" in sm.settings.keys():
            self.year = sm.settings.get("next_visit_year")
        if "next_visit_month" in sm.settings.keys():
            self.month = sm.settings.get("next_visit_month")
        if "next_visit_day" in sm.settings.keys():
            self.day = sm.settings.get("next_visit_day")


class Display:
    def __init__(self, scrolldelay=0.03):
        self.scroll_delay = scrolldelay
        self.RED_COLOR = 0xCC3333
        self.BLUE_COLOR = 0x0000AA
        self.BLACK_COLOR = 0x000000
        self.WHITE_COLOR = 0xFFFFFF

    async def show_ride_closed(self, dummy):
        print("Ride closed")

    async def show_ride_wait_time(self, ride_wait_time):
        print(f"Ride wait time is {ride_wait_time}")

    async def show_configuration_message(self):
        print(f"Showing configuration message: {CONFIGURATION_MESSAGE}")

    async def show_ride_name(self, ride_name):
        print(f"Ride name is {ride_name}")

    async def show_scroll_message(self, message):
        print(f"Scrolling message: {message}")


class AsyncScrollingDisplay(Display):
    def __init__(self, display_hardware, scrolldelay=0.04):
        super().__init__(scrolldelay)
        self.font = terminalio.FONT
        self.hardware = display_hardware

        # Configure generic scrolling message
        self.scrolling_label = Label(terminalio.FONT)
        self.scrolling_label.x = 0
        self.scrolling_label.y = 15
        self.scrolling_group = displayio.Group()
        self.scrolling_group.append(self.scrolling_label)
        self.scrolling_group.hidden = True

        # Configure Ride Times
        self.wait_time_name = Label(terminalio.FONT)
        self.wait_time_name.x = 0
        self.wait_time_name.y = 6
        self.wait_time_name.scale = 1
        self.wait_time_name_group = displayio.Group()
        self.wait_time_name_group.append(self.wait_time_name)
        self.wait_time_name_group.hidden = True

        self.wait_time = Label(terminalio.FONT)
        self.wait_time.x = 0
        self.wait_time.y = 22
        self.wait_time.scale = (2)
        self.wait_time_group = displayio.Group()
        self.wait_time_group.append(self.wait_time)
        self.wait_time_group.hidden = True

        self.closed = Label(terminalio.FONT)
        self.closed.x = 14
        self.closed.y = 22
        self.closed.scale = (1)
        self.closed.text = "Closed"
        self.closed_group = displayio.Group()
        self.closed_group.append(self.closed)
        self.closed_group.hidden = True

        self.main_group = displayio.Group()
        self.main_group.hidden = False
        self.main_group.append(self.scrolling_group)
        self.main_group.append(self.wait_time_name_group)
        self.main_group.append(self.wait_time_group)
        self.main_group.append(self.closed_group)
        self.hardware.root_group = self.main_group

    def set_colors(self, settings):
        new_color = int(settings.settings["ride_wait_time_color"])
        print(f"The new color is {new_color}")
        self.wait_time_name.color = int(settings.settings["ride_name_color"])
        self.wait_time.color = int(settings.settings["ride_wait_time_color"])
        self.closed.color = int(settings.settings["ride_wait_time_color"])
        self.scrolling_label.color = int(settings.settings["default_color"])

    async def off(self):
        self.scrolling_group.hidden = True
        self.wait_time_name_group.hidden = True
        self.wait_time_group.hidden = True
        self.closed_group.hidden = True

    async def show_ride_closed(self, dummy):
        await super().show_ride_closed(dummy)
        self.closed_group.hidden = False

    async def show_ride_wait_time(self, ride_wait_time):
        await super().show_ride_wait_time(ride_wait_time)
        self.wait_time.text = ride_wait_time
        self.center_time(self.wait_time)
        self.wait_time_group.hidden = False

    async def show_configuration_message(self):
        self.wait_time_group.hidden = True
        self.wait_time_name_group.hidden = True
        await super().show_configuration_message()

    async def show_ride_name(self, ride_name):
        await super().show_ride_name(ride_name)
        self.wait_time_name.text = ride_name
        self.wait_time_name_group.hidden = False
        while self.scroll(self.wait_time_name) is True:
            await asyncio.sleep(self.scroll_delay)
        await asyncio.sleep(1)
        self.wait_time.text = ""
        self.wait_time_name.text = ""
        self.wait_time_group.hidden = True
        self.wait_time_name_group.hidden = True
        self.closed_group.hidden = True

    async def show_scroll_message(self, message):
        print(f"Scrolling message: {message}")
        self.wait_time_group.hidden = True
        self.wait_time_name_group.hidden = True
        self.scrolling_label.text = message
        self.scrolling_group.hidden = False
        while self.scroll(self.scrolling_label) is True:
            await asyncio.sleep(self.scroll_delay)
        self.scrolling_group.hidden = True

    def scroll(self, line):
        line.x = line.x - 1
        line_width = line.bounding_box[2]
        if line.x < -line_width:
            line.x = self.hardware.width
            return False
        return True

    def center_time(self, text_label):
        label_width = text_label.bounding_box[2]
        text_label.x = int(self.hardware.width / 2 - (label_width * len(text_label)))


class MatrixPortalDisplay(Display):
    def __init__(self, mp, scrolldelay=0.03):
        super().__init__(scrolldelay)

        self.matrix_portal = mp

        self.WAIT_TIME = 0
        self.matrix_portal.add_text(
            text_font=terminalio.FONT,
            text_position=(
                23,
                int(self.matrix_portal.graphics.display.height * 0.75) - 2,
            ),
            text_color=self.BLUE_COLOR,
            scrolling=False,
            text_scale=2,
        )

        # Ride Name
        self.RIDE_NAME = 1
        self.matrix_portal.add_text(
            text_font=terminalio.FONT,
            text_position=(
                0,
                int(self.matrix_portal.graphics.display.height * 0.25) + 10,
            ),
            text_color=self.RED_COLOR,
            scrolling=True,
            text_scale=1,
        )

        # Standby
        self.STANDBY = 2
        self.matrix_portal.add_text(
            text_font=terminalio.FONT,
            text_position=(
                (int((self.matrix_portal.graphics.display.width - 7 * 6) / 2)),
                6,
            ),
            text_color=self.BLUE_COLOR,
        )

    async def show_ride_closed(self, dummy):
        self.matrix_portal.set_text("Closed", self.STANDBY)

    async def show_ride_wait_time(self, ride_wait_time):
        self.matrix_portal.set_text("", self.RIDE_NAME)
        self.matrix_portal.set_text(ride_wait_time, self.WAIT_TIME)
        self.matrix_portal.set_text("Standby", self.STANDBY)

    async def show_configuration_message(self):
        self.matrix_portal.set_text("", self.STANDBY)
        self.matrix_portal.set_text("", self.WAIT_TIME)
        self.matrix_portal.set_text("Configure at ", self.RIDE_NAME)
        self.matrix_portal.scroll_text(self.scroll_delay)
        self.matrix_portal.set_text("http://themeparkwaits.local", self.RIDE_NAME)
        self.matrix_portal.scroll_text(self.scroll_delay)

    async def show_ride_name(self, ride_name):
        self.matrix_portal.set_text("", self.STANDBY)
        self.matrix_portal.set_text("", self.WAIT_TIME)
        self.matrix_portal.set_text(ride_name, self.RIDE_NAME)
        self.matrix_portal.scroll_text(self.scroll_delay)

    async def show_scroll_message(self, message):
        print(f"Scrolling message: {message}")
        self.matrix_portal.set_text("", self.STANDBY)
        self.matrix_portal.set_text("", self.WAIT_TIME)
        self.matrix_portal.set_text(message, self.RIDE_NAME)
        self.matrix_portal.scroll_text(self.scroll_delay)


REQUIRED_MESSAGE = "Data provided by http://queue-times.com"
CONFIGURATION_MESSAGE = "Configure at http://themeparkwaits.local"


#  The things to display on the screen
class MessageQueue:
    def __init__(self, d, delay_param=4, regen_flag=False):
        self.display = d
        self.delay = delay_param
        self.regenerate_flag = regen_flag
        self.func_queue = []
        self.param_queue = []
        self.delay_queue = []
        self.func_queue.append(d.show_scroll_message)
        self.param_queue.append(REQUIRED_MESSAGE)
        self.delay_queue.append(self.delay)
        self.func_queue.append(d.show_scroll_message)
        self.param_queue.append(CONFIGURATION_MESSAGE)
        self.delay_queue.append(self.delay)
        self.index = 0

    async def add_rides(self, park, vac):
        print(f"MessageQueue.add_rides() called for: {park.name} with id: {park.id}")
        self.func_queue = []
        self.param_queue = []
        self.delay_queue = []
        self.index = 0
        self.func_queue.append(self.display.show_scroll_message)
        self.param_queue.append(REQUIRED_MESSAGE)
        self.delay_queue.append(self.delay)
        self.func_queue.append(self.display.show_scroll_message)
        self.param_queue.append(park.name + ":")
        self.delay_queue.append(self.delay)

        if vac.is_set() is True:
            days_until = vac.get_days_until()
            if days_until >= 0:
                vac_message = f"Vacation to {vac.name} in: {days_until} days"
                print(f"Adding vacation message: {vac_message}")
                self.func_queue.insert(0, self.display.show_scroll_message)
                self.param_queue.insert(0, vac_message)
                self.delay_queue.insert(0, 0)

        for ride in park.rides:
            print(f"Trying to add ride {ride.name} closed={ride.open_flag}")
            if "Meet" in ride.name and park.skip_meet == "True":
                continue

            if ride.is_closed() is True and park.skip_closed == "True":
                continue

            if ride.open_flag is True:
                self.func_queue.append(self.display.show_ride_wait_time)
                self.param_queue.append(str(ride.wait_time))
                self.delay_queue.append(0)
            else:
                self.func_queue.append(self.display.show_ride_closed)
                self.param_queue.append("Closed")
                self.delay_queue.append(0)

            self.func_queue.append(self.display.show_ride_name)
            self.param_queue.append(ride.name)
            self.delay_queue.append(self.delay)

            self.regenerate_flag = False

    async def show(self):
        await asyncio.create_task(
            self.func_queue[self.index](self.param_queue[self.index]))
        await asyncio.sleep(self.delay_queue[self.index])
        self.index += 1
        if self.index >= len(self.func_queue):
            self.index = 0


class ColorUtils:
    # def __init__(self, d, delay_param=4):
    colors = {'White': '0xffffff',
              'Red': '0xcc3333',
              'Yellow': '0xff9600',
              'Orange': '0xff2800',
              'Green': '0x00ff00',
              'Teal': '0x00ff78',
              'Cyan': '0x00ffff',
              'Blue': '0x0000aa',
              'Purple': '0xb400ff',
              'Magenta': '0xff0016',
              'Black': '0x000000',
              'Gold': '0xffde1e',
              'Pink': '0xf25aff',
              'Aqua': '0x32ffff',
              'Jade': '0x00ff28',
              'Amber': '0xff6400',
              'Old Lace': '0xfdf5e6'}

    @staticmethod
    def html_color_chooser(name, hex_num_str):
        """
        :param name: Name of the HTML select field
        :param hex_num_str:  A string representation of the selected color
        :return:
        """
        html = ""
        html += f"<select name=\"{name}\" id=\"{id}\">\n"
        for color in ColorUtils.colors:
            if ColorUtils.colors[color] == hex_num_str:
                html += f"<option value=\"{ColorUtils.colors[color]}\" selected>{color}</option>\n"
            else:
                html += f"<option value=\"{ColorUtils.colors[color]}\">{color}</option>\n"

        html += "</select>"
        return html

    @staticmethod
    def hex_str_to_number(hex_string):
        return int(hex_string, 16)

    @staticmethod
    def number_to_hex_string(num):
        return hex(num)


# Can't get dataclasses to work on MatrixPortal S3.
# Saving to JSON by hand.
# @dataclasses.dataclass
class SettingsManager:
    def __init__(self, filename):
        self.filename = filename
        self.settings = self.load_settings()
        if self.settings.get("skip_closed") is None:
            self.settings["skip_closed"] = False
        if self.settings.get("skip_meet") is None:
            self.settings["skip_meet"] = False
        if self.settings.get("default_color") is None:
            self.settings["default_color"] = ColorUtils.colors["Yellow"]
        if self.settings.get("ride_name_color") is None:
            self.settings["ride_name_color"] = ColorUtils.colors["Blue"]
        if self.settings.get("ride_wait_time_color") is None:
            self.settings["ride_wait_time_color"] = ColorUtils.colors["White"]
        # Features not implemented yet
        #if self.settings.get("park_name_color") is None:
        #    self.settings["park_name_color"] = ColorUtils.colors["Blue"]
        #if self.settings.get("vacation_color") is None:
        #    self.settings["vacation_color"] = ColorUtils.colors["Red"]

    @staticmethod
    def get_pretty_name(settings_name):
        # Change underscore to spaces
        new_name = settings_name.replace("_", " ")
        return " ".join(word[0].upper() + word[1:] for word in new_name.split(' '))

    def load_settings(self):
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except OSError:
            return {}

    def save_settings(self):
        with open(self.filename, 'w') as f:
            json.dump(self.settings, f)
