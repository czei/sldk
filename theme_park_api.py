import wifi
import ssl
import adafruit_requests
import socketpool
import terminalio
import asyncio
import displayio
import adafruit_display_text
import datetime
from adafruit_display_text.label import Label


def populate_park_list():
    """
    Returns an iterable list of theme parks and their ids from Queue Times.
    ONLY WORKS ON CircuitPython hardware.
    :return:
    """
    url = "https://queue-times.com/parks.json"
    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())
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
                for item in park:
                    # print(f"park = {item}")
                    for element in item:
                        if element == "name":
                            name = item[element]
                        if element == "id":
                            park_id = item[element]
                    name_id = tuple([name, park_id])
                    # print(f"Adding tuple {name_id}")
                    park_list.append(name_id)

    # print(park_list)

    return park_list


def get_rides_from_json(json_data):
    """
    Returns a list of the names of rides at a particular park contained in the JSON
    :param json_data: A JSON file containing data for a particular park
    :return: name, id, wait_time, is_open
    """
    ride_list = []
    lands_list = json_data["lands"]
    for land in lands_list:
        # print(f"company = {company}")
        rides = land["rides"]
        for ride in rides:
            name = ride["name"]
            ride_id = ride["id"]
            wait_time = ride["wait_time"]
            is_open = ride["is_open"]
            park_desc = [name, ride_id, wait_time, is_open]
            ride_list.append(park_desc)
    return ride_list


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


def get_park_name_from_id(park_list, park_id):
    for park in park_list:
        if park[1] == park_id:
            park_name = park[0]
            return park_name


class ThemeParkRide:
    def __init__(self, name, new_id, wait_time, is_open):
        self.name = name
        self.id = new_id
        self.wait_time = wait_time
        self.is_open = is_open


class ThemePark:
    def __init__(self, json_data=(), name="", id=0):
        """
        :param self:
        :param json_data: Python JSON objects from a single park
        :return:
        """
        self.counter = 0
        self.name = name
        self.id = id
        self.rides = self.get_rides_from_json(json_data)
        self.new_flag = False

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

    @staticmethod
    def get_rides_from_json(json_data):
        """
        Returns a list of the names of rides at a particular park contained in the JSON
        :param json_data: A JSON file containing data for a particular park
        :return: name, id, wait_time, is_open
        """
        ride_list = []

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
                is_open = ride["is_open"]
                this_ride_object = ThemeParkRide(name, ride_id, wait_time, is_open)
                ride_list.append(this_ride_object)

        return ride_list

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
                return ride.is_open

    def increment(self):
        self.counter += 1
        if self.counter >= len(self.rides):
            self.counter = 0

    def update(self, json_data):
        self.rides = self.get_rides_from_json(json_data)
        self.new_flag = False

    def get_current_ride_name(self):
        return self.rides[self.counter].name

    def is_current_ride_open(self):
        if self.rides[self.counter].is_open is False:
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
        self.new_flag = True
        self.counter = 0


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

    def parse(self, str_params):
        params = str_params.split("&")
        self.name = params[0].split("=")[1]
        self.year = int(params[1].split("=")[1])
        self.month = int(params[2].split("=")[1])
        self.day = int(params[3].split("=")[1])

    def get_days_util(self):
        today = datetime.date.today()
        future = datetime.date(self.year, self.month, self.day)
        diff = future - today
        return diff.days

    def is_set(self):
        isset = False
        if len(self.name) > 0 and self.year > 0 and self.month > 0 and self.day > 0:
            isset = True

        return isset

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
    def __init__(self, display_hardware, scrolldelay=0.03):
        super().__init__(scrolldelay)
        # self.scrolling_label = ScrollingLabel(terminalio.FONT, text="Test Text That You Should Not See", max_characters=10, animate_time=self.scroll_delay)
        self.font = terminalio.FONT
        self.hardware = display_hardware

        # Configure generic scrolling message
        self.scrolling_label = adafruit_display_text.label.Label(terminalio.FONT)
        self.scrolling_label.x = 0
        self.scrolling_label.y = 15
        self.scrolling_label.color = self.BLUE_COLOR
        self.scrolling_group = displayio.Group()
        self.scrolling_group.append(self.scrolling_label)
        self.scrolling_group.hidden = True

        # Configure Ride Times
        self.wait_time_name = adafruit_display_text.label.Label(terminalio.FONT)
        self.wait_time_name.x = 0
        self.wait_time_name.y = 6
        self.wait_time_name.scale = 1
        self.wait_time_name.color = self.BLUE_COLOR
        self.wait_time_name_group = displayio.Group()
        self.wait_time_name_group.append(self.wait_time_name)
        self.wait_time_name_group.hidden = True

        self.wait_time = adafruit_display_text.label.Label(terminalio.FONT)
        self.wait_time.x = 0
        self.wait_time.y = 22
        self.wait_time.scale = (2)
        self.wait_time_name.color = self.BLUE_COLOR
        self.wait_time_group = displayio.Group()
        self.wait_time_group.append(self.wait_time)
        self.wait_time_group.hidden = True

        self.closed = adafruit_display_text.label.Label(terminalio.FONT)
        self.closed.x = 14
        self.closed.y = 22
        self.closed.scale = (1)
        self.closed.text = "Closed"
        self.closed.color = self.WHITE_COLOR
        self.closed_group = displayio.Group()
        self.closed_group.append(self.closed)
        self.closed_group.hidden = True

        self.main_group = displayio.Group()
        self.hardware.root_group = self.main_group
        self.main_group.hidden = False
        self.main_group.append(self.scrolling_group)
        self.main_group.append(self.wait_time_name_group)
        self.main_group.append(self.wait_time_group)
        self.main_group.append(self.closed_group)
        self.hardware.show(self.main_group)

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

        self.matrix_portal=mp

        self.WAIT_TIME=0
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
        self.RIDE_NAME=1
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
        self.STANDBY=2
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

    def __init__(self, d, delay_param=4):
        self.display = d
        self.delay = delay_param
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

    async def add_vacation(self, vac):
        self.func_queue = []
        self.param_queue = []
        self.delay_queue = []

    async def add_rides(self, park):
        print(f"Initalizing message for park: {park.name}")
        self.func_queue = []
        self.param_queue = []
        self.delay_queue = []
        self.index = 0
        self.func_queue.append(self.display.show_scroll_message)
        self.param_queue.append(REQUIRED_MESSAGE)
        self.delay_queue.append(0)
        self.func_queue.append(self.display.show_scroll_message)
        self.param_queue.append(park.name + ":")
        self.delay_queue.append(0)

        for ride in park.rides:
            if ride.is_open is True:
                self.func_queue.append(self.display.show_ride_wait_time)
                self.param_queue.append(str(ride.wait_time))
            else:
                self.func_queue.append(self.display.show_ride_closed)
                self.param_queue.append("Closed")
            self.delay_queue.append(0)

            self.func_queue.append(self.display.show_ride_name)
            self.param_queue.append(ride.name)
            self.delay_queue.append(self.delay)

    async def show(self):
        await asyncio.create_task(
            self.func_queue[self.index](self.param_queue[self.index]))
        await asyncio.sleep(self.delay_queue[self.index])
        self.index += 1
        if self.index >= len(self.func_queue):
            self.index = 0

