"""
ThemeParkList model to manage a collection of theme parks.
Copyright 2024 3DUPFitters LLC
"""

from src.utils.error_handler import ErrorHandler
from src.models.theme_park import ThemePark
from src.config.settings_manager import SettingsManager

# Initialize logger
logger = ErrorHandler("error_log")


class ThemeParkList:
    """
    The ThemeParkList class is used to manage a list of ThemePark objects.
    It provides various utility methods to interact with, and retrieve data from the list.
    """

    def __init__(self, json_response):
        """
        Initialize a list of theme parks from JSON data
        
        Args:
            json_response: JSON data containing theme parks
        """
        self.park_list = []
        self.current_park = ThemePark()
        self.skip_meet = False
        self.skip_closed = False
        
        # Handle empty or invalid JSON response
        if not json_response:
            logger.error("Empty JSON response when initializing ThemeParkList")
            return
            
        try:
            for company in json_response:
                # Handle case where JSON structure doesn't match expected format
                if not isinstance(company, dict):
                    continue
                    
                for parks in company:
                    if parks == "parks":
                        park = company[parks]
                        if not isinstance(park, list):
                            continue
                            
                        for item in park:
                            if not isinstance(item, dict):
                                continue
                                
                            name = ""
                            park_id = 0
                            latitude = 0
                            longitude = 0
                            
                            # Extract park properties
                            for element in item:
                                if element == "name":
                                    name = item[element]
                                if element == "id":
                                    park_id = item[element]
                                if element == "latitude":
                                    latitude = item[element]
                                if element == "longitude":
                                    longitude = item[element]
                                    
                            # Only add parks with valid names and IDs
                            if name and park_id:
                                park = ThemePark("", ThemePark.remove_non_ascii(name), park_id, latitude, longitude)
                                self.park_list.append(park)
            
            # Sort park list alphabetically                
            if self.park_list:
                sorted_park_list = sorted(self.park_list, key=lambda park: park.name)
                self.park_list = sorted_park_list
                logger.debug(f"Initialized ThemeParkList with {len(self.park_list)} parks")
            else:
                logger.error("No parks found in JSON response")
        except Exception as e:
            logger.error(e, "Error parsing JSON in ThemeParkList initialization")
            # Keep the empty park list

    @staticmethod
    def get_park_url_from_id(park_id):
        """
        Get the URL for a park based on its ID
        
        Args:
            park_id: The ID of the park
            
        Returns:
            The URL for the park's data
        """
        url1 = "https://queue-times.com/parks/"
        url2 = "/queue_times.json"
        return url1 + str(park_id) + url2

    def load_settings(self, sm):
        """
        Load settings from the settings manager
        
        Args:
            sm: The settings manager
        """
        keys = sm.settings.keys()

        if "current_park_id" in keys:
            park_id = sm.settings["current_park_id"]
            park = self.get_park_by_id(park_id)
            if park:
                self.current_park = park
        if "skip_meet" in keys:
            self.skip_meet = sm.settings["skip_meet"]
        if "skip_closed" in keys:
            self.skip_closed = sm.settings["skip_closed"]

    def get_park_url_from_name(self, park_name):
        """
        Takes the output from get_theme_parks_from_json and assembles
        the URL to get individual ride data.
        
        Args:
            park_name: The string describing the Theme Park
            
        Returns:
            JSON url for a particular theme park, or None if not found
        """
        # Magic Kingdom URL example: https://queue-times.com/parks/6/queue_times.json
        url1 = "https://queue-times.com/parks/"
        url2 = "/queue_times.json"
        for park in self.park_list:
            if park.name == park_name:
                park_id = park.id
                url = url1 + str(park_id) + url2
                return url
        return None

    def get_park_by_id(self, park_id):
        """
        Find a park by its ID
        
        Args:
            park_id: The ID of the park
            
        Returns:
            The ThemePark with the given ID, or None if not found
        """
        for park in self.park_list:
            if park.id == park_id:
                return park
        return None

    def get_park_location_from_id(self, park_id):
        """
        Get the location coordinates for a park by its ID
        
        Args:
            park_id: The id from QueueTimes.com
            
        Returns:
            A tuple of (latitude, longitude) for the park, or None if not found
        """
        for park in self.park_list:
            if park.id == park_id:
                return park.latitude, park.longitude
        return None

    def get_park_name_from_id(self, park_id):
        """
        Get the name of a park by its ID
        
        Args:
            park_id: The ID of the park
            
        Returns:
            The name of the park, or an empty string if not found
        """
        park_name = ""
        for park in self.park_list:
            if park.id == park_id:
                park_name = park.name
                return park_name
        return park_name

    def parse(self, str_params):
        """
        Parse parameters from a URL query string
        
        Args:
            str_params: The URL query string
        """
        params = str_params.split("&")
        # logger.debug(f"Params = {params}")
        self.skip_meet = False
        self.skip_closed = False
        for param in params:
            name_value = param.split("=")
            if name_value[0] == "park-id":
                park = self.get_park_by_id(int(name_value[1]))
                if park:
                    self.current_park = park
                    logger.debug(f"New park name = {self.current_park.name}")
                    logger.debug(f"New park id = {self.current_park.id}")
                    logger.debug(f"New park latitude = {self.current_park.latitude}")
                    logger.debug(f"New park longitude = {self.current_park.longitude}")
            if name_value[0] == "skip_closed":
                logger.debug("Skip closed is True")
                self.skip_closed = True
            if name_value[0] == "skip_meet":
                logger.debug("Skip meet is True")
                self.skip_meet = True

    def store_settings(self, sm):
        """
        Store settings in the settings manager
        
        Args:
            sm: The settings manager
        """
        sm.settings["current_park_name"] = self.current_park.name
        sm.settings["current_park_id"] = self.current_park.id
        sm.settings["skip_meet"] = self.skip_meet
        sm.settings["skip_closed"] = self.skip_closed