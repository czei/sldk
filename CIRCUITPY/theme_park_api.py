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


def get_wait_time(park_json, ride_name):
    """
    :param park_json:  The parsed JSON from a particular park
    :param ride_name:  The individual ride at that park you want the time for
    :return: Standby wait time in minutes as a string. Returns "closed" if the ride is closed
    """
    ride_list = get_rides_from_json(park_json)
    for ride in ride_list:
        if ride[0] == ride_name:
            target_ride_time = ride[2]
            is_open = ride[3]
            if is_open is False:
                return "Closed"
            else:
                return target_ride_time


class Rides:
    def __init__(self, json_data):
        """
        :param self:
        :param json_data: Python JSON objects from a single park
        :return:
        """
        self.counter = 0
        self.rides = get_rides_from_json(json_data)

    def increment_counter(self):
        self.counter += 1
        if self.counter >= len(self.rides):
            self.counter = 0

    def get_current_ride_name(self):
        return self.rides[self.counter][0]

    def get_next_ride_name(self):
        self.increment_counter()
        return self.rides[self.counter][0]

    def get_num_rides(self):
        return len(self.rides)
