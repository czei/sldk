import time


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
    lands_list = json_data['lands']
    for land in lands_list:
        # print(f"company = {company}")
        rides = land['rides']
        for ride in rides:
            name = ride['name']
            ride_id = ride['id']
            wait_time = ride['wait_time']
            is_open = ride['is_open']
            park_desc = ([name, ride_id, wait_time, is_open])
            ride_list.append(park_desc)
    return ride_list


def get_park_url(park_list, park_name):
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


class ThemeParkRide:
    def __init__(self, name, new_id, wait_time, is_open):
        self.name = name
        self.id = new_id
        self.wait_time = wait_time
        self.is_open = is_open


class ThemePark:
    def __init__(self, name, json_data):
        """
        :param self:
        :param json_data: Python JSON objects from a single park
        :return:
        """
        self.counter = 0
        self.name = name
        self.rides = self.get_rides_from_json(json_data)

    @staticmethod
    def get_rides_from_json(json_data):
        """
        Returns a list of the names of rides at a particular park contained in the JSON
        :param json_data: A JSON file containing data for a particular park
        :return: name, id, wait_time, is_open
        """
        ride_list = []
        lands_list = json_data['lands']
        for land in lands_list:
            rides = land['rides']
            for ride in rides:
                name = ride['name']
                # print(f"Ride = {name}")
                ride_id = ride['id']
                wait_time = ride['wait_time']
                is_open = ride['is_open']
                this_ride_object = ThemeParkRide(name, ride_id, wait_time, is_open)
                ride_list.append(this_ride_object)

        return ride_list

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


class DisplayMode:
    """
    Is the display showing the name of the ride or the wait time?
    """

    def __init__(self, wait_delay):
        self.modes = ["Scrolling", "Wait"]
        self.current_mode = 0
        self.WAIT_DELAY = wait_delay
        self.last_update = time.monotonic()

    def get_current_mode(self):
        return self.modes[self.current_mode]

    def time_to_switch_mode(self):
        the_time = time.monotonic()
        if the_time > (self.last_update + self.WAIT_DELAY):
            self.last_update = time.monotonic()
            self.increment_mode()
            return True
        return False

    def print_status(self):
        the_time = time.monotonic()
        print(f"Time is {the_time} last update is {self.last_update} delay is {self.WAIT_DELAY}")

    def increment_mode(self):
        self.current_mode += 1
        self.last_update = time.monotonic()
        if self.current_mode >= len(self.modes):
            self.current_mode = 0


class ParkUpdateTimer:
    """
    Is the display showing the name of the ride or the wait time?
    """

    def __init__(self, wait_delay):
        self.WAIT_DELAY = wait_delay
        self.last_update = time.monotonic()

    def time_to_do_something(self):
        the_time = time.monotonic()
        if the_time > (self.last_update + self.WAIT_DELAY):
            self.last_update = time.monotonic()
            return True
        return False

    def print_status(self):
        the_time = time.monotonic()
        print(f"Time is {the_time} last update is {self.last_update} delay is {self.WAIT_DELAY}")


class DisplayStyle:
    """
    Mostly static or scrolling, but could expand in the future
    """
    def __init__(self):
        self.SCROLLING = 0
        self.STATIC = 1


def display_message_renderer(message, style):
    print(f"message={message}, style={style}")
    return message


class DisplayMessage:
    """
    Something to put on the screen, like a ride wait time.
    """

    def __init__(self, message, style, renderer):
        self.message = message
        self.display_style = style
        self.renderer = renderer

    def render(self):
        return self.renderer(self.message, self.display_style)

