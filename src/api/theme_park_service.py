"""
Service for fetching and managing theme park data.
Copyright 2024 3DUPFitters LLC
"""
import asyncio
import json

from src.models.theme_park import ThemePark
from src.models.theme_park_list import ThemeParkList
from src.models.vacation import Vacation
from src.config.settings_manager import SettingsManager
from src.utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")


class ThemeParkService:
    """
    Service for fetching and managing theme park data
    """
    
    def __init__(self, http_client, settings_manager):
        """
        Initialize the theme park service
        
        Args:
            http_client: The HTTP client to use for requests
            settings_manager: The settings manager
        """
        self.http_client = http_client
        self.settings_manager = settings_manager
        self.park_list = None
        self.vacation = Vacation()
        self.update_needed = False  # Flag to indicate if an update should be forced
        
    async def initialize(self):
        """Initialize the service by fetching park list and setting clock"""
        # Track initialization steps for better error reporting
        steps_completed = []
        
        try:

                
            # Step 2: Fetch the park list
            for attempt in range(3):  # Multiple attempts for park list
                try:
                    logger.info(f"Attempting to fetch park list (attempt {attempt+1}/3)")
                    await self.fetch_park_list()
                    if self.park_list and self.park_list.park_list:
                        steps_completed.append("fetch_park_list")
                        logger.info(f"Successfully fetched {len(self.park_list.park_list)} parks on attempt {attempt+1}")
                        break
                    else:
                        logger.error(f"Park list fetch attempt {attempt+1} returned empty list")
                        # Small delay before retrying
                        await asyncio.sleep(3)
                except Exception as list_error:
                    logger.error(list_error, f"Error fetching park list on attempt {attempt+1}/3")
                    await asyncio.sleep(3)
            
            # Create empty park list if all attempts failed
            if "fetch_park_list" not in steps_completed:
                logger.info("Creating empty park list as fallback after failed attempts")
                self.park_list = ThemeParkList([])
            
            # Step 3: Load settings (even for empty park list)
            if self.park_list:
                self.park_list.load_settings(self.settings_manager)
                steps_completed.append("load_park_settings")
                
            # Step 4: Load vacation settings
            self.vacation.load_settings(self.settings_manager)
            steps_completed.append("load_vacation_settings")
            
            # Log initialization success/partial success
            if len(steps_completed) >= 3:  # Clock setting might fail but that's ok
                logger.info(f"Theme park service initialized. Steps completed: {', '.join(steps_completed)}")
            else:
                logger.error(f"Theme park service partially initialized. Steps completed: {', '.join(steps_completed)}")
            
        except Exception as e:
            logger.error(e, f"Error initializing theme park service. Steps completed: {', '.join(steps_completed)}")
            
            # Create park list if it doesn't exist yet (failsafe)
            if self.park_list is None:
                self.park_list = ThemeParkList([])
                logger.info("Created empty park list as failsafe after initialization error")
            
    async def fetch_park_list(self):
        """
        Fetch the list of theme parks
        
        Returns:
            A ThemeParkList object, or None if fetch failed
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                url = "https://queue-times.com/parks.json"
                logger.info(f"Fetching park list from {url} (attempt {retry_count + 1}/{max_retries})")
                
                response = await self.http_client.get(url)
                
                if not response or not hasattr(response, 'text'):
                    logger.error(f"Invalid response when fetching park list (attempt {retry_count + 1})")
                    retry_count += 1
                    await asyncio.sleep(1)
                    continue
                
                # Try to parse JSON
                try:
                    data = json.loads(response.text)
                    if not data:
                        logger.error(f"Empty JSON data from park list API (attempt {retry_count + 1})")
                        retry_count += 1
                        await asyncio.sleep(1)
                        continue
                    
                    # Create park list
                    self.park_list = ThemeParkList(data)
                    
                    # Verify park list has parks
                    if not self.park_list.park_list:
                        logger.error(f"Park list created but no parks were found (attempt {retry_count + 1})")
                        retry_count += 1
                        await asyncio.sleep(1)
                        continue
                    
                    logger.info(f"Successfully fetched {len(self.park_list.park_list)} parks")
                    return self.park_list
                    
                except json.JSONDecodeError as json_error:
                    logger.error(json_error, f"JSON decode error for park list (attempt {retry_count + 1})")
                    retry_count += 1
                    await asyncio.sleep(1)
                    continue
                
            except Exception as e:
                logger.error(e, f"Error fetching park list (attempt {retry_count + 1})")
                retry_count += 1
                await asyncio.sleep(1)
        
        # All retries failed
        logger.error(f"Failed to fetch park list after {max_retries} attempts")
        
        # Create empty park list as fallback
        self.park_list = ThemeParkList([])
        return self.park_list
            
    async def fetch_park_data(self, park_id):
        """
        Fetch data for a specific park
        
        Args:
            park_id: The ID of the park
            
        Returns:
            Park data as a dictionary, or None if fetch failed
        """
        try:
            url = ThemeParkList.get_park_url_from_id(park_id)
            response = await self.http_client.get(url)
            return json.loads(response.text)
            
        except Exception as e:
            logger.error(e, f"Error fetching park data for park ID {park_id}")
            return None
            
    async def update_current_park(self):
        """
        Update the currently selected park with fresh data
        
        Returns:
            True if successful, False otherwise
        """
        if not self.park_list or not self.park_list.current_park.is_valid():
            logger.debug("No valid current park to update")
            return False
            
        try:
            park_data = await self.fetch_park_data(self.park_list.current_park.id)
            if park_data:
                self.park_list.current_park.update(park_data)
                return True
            return False
            
        except Exception as e:
            logger.error(e, "Error updating current park")
            return False
            
    def save_settings(self):
        """Save all settings"""
        if self.park_list:
            self.park_list.store_settings(self.settings_manager)
        
        self.vacation.store_settings(self.settings_manager)
        self.settings_manager.save_settings()
        
    def parse_query_params(self, params):
        """
        Parse query parameters for park and vacation settings
        
        Args:
            params: The query parameter string
        """
        if not self.park_list:
            return
            
        # Check for park parameters
        if "park-id=" in params:
            self.park_list.parse(params)
            
        # Check for vacation parameters
        if "Name=" in params:
            self.vacation.parse(params)
            
        # Save the settings
        self.save_settings()