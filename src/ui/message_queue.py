"""
MessageQueue for managing the display of theme park information.
Copyright 2024 3DUPFitters LLC
"""
import asyncio

from src.utils.error_handler import ErrorHandler
from src.models.vacation import Vacation
from src.models.theme_park_list import ThemeParkList

# Initialize logger
logger = ErrorHandler("error_log")

# Constants
REQUIRED_MESSAGE = "queue-times.com"


class MessageQueue:
    """Manages the queue of messages to display"""
    
    def __init__(self, display, delay_param=4, regen_flag=False):
        """
        Initialize the message queue
        
        Args:
            display: The display to show messages on
            delay_param: The default delay between messages
            regen_flag: Whether to regenerate the queue automatically
        """
        self.display = display
        self.delay = delay_param
        self.regenerate_flag = regen_flag
        self.init()

    def init(self):
        """Initialize the message queue"""
        self.func_queue = []
        self.param_queue = []
        self.delay_queue = []
        self.index = 0
        self.has_completed_cycle = False

    async def add_scroll_message(self, the_message, delay=2):
        """
        Add a scrolling message to the queue
        
        Args:
            the_message: The message to scroll
            delay: The delay after showing the message
        """
        self.func_queue.append(self.display.show_scroll_message)
        self.param_queue.append(the_message)
        self.delay_queue.append(delay)

    async def add_splash(self, duration=4):
        """
        Add a splash screen to the queue
        
        Args:
            duration: Duration to show the splash screen (seconds)
        """
        logger.debug("Adding splash message to queue")
        self.func_queue.append(self.display.show_splash)
        self.param_queue.append(duration)
        self.delay_queue.append(0)  # No additional delay since duration is handled in show_splash

    async def add_vacation(self, vac):
        """
        Add vacation information to the queue
        
        Args:
            vac: The vacation information
        """
        if vac.is_set() is True:
            days_until = vac.get_days_until()
            if days_until > 1:
                vac_message = f"Vacation to {vac.name} in: {days_until} days"
                await self.add_scroll_message(vac_message, 0)
            elif days_until == 1:
                vac_message = f"Your vacation to {vac.name} is tomorrow!!!"
                await self.add_scroll_message(vac_message, 0)
            elif days_until == 0:
                vac_message = f"Your vacation to {vac.name} is TODAY!!!!!!!!!!!!!"
                await self.add_scroll_message(vac_message, 0)

    async def add_required_message(self, park_name):
        """
        Add the required attribution message to the queue
        
        Args:
            park_name: The name of the park
        """
        self.func_queue.append(self.display.show_scroll_message)
        required_message = f"Wait times for {park_name} provided by {REQUIRED_MESSAGE}"
        self.param_queue.append(required_message)
        self.delay_queue.append(self.delay)

    async def add_rides(self, park_list):
        """
        Add ride information to the queue based on display mode
        
        Args:
            park_list: The list of parks
        """
        # Use selected parks if available, otherwise fall back to current_park
        parks_to_display = []
        if hasattr(park_list, 'selected_parks') and park_list.selected_parks:
            parks_to_display = park_list.selected_parks
            logger.debug(f"MessageQueue.add_rides() called for {len(parks_to_display)} selected parks")
        else:
            # Fall back to single park mode for backward compatibility
            park = park_list.current_park
            if park and park.is_valid():
                parks_to_display = [park]
                logger.debug(f"MessageQueue.add_rides() called for single park: {park.name}:{park.id}")
        
        if not parks_to_display:
            self.func_queue.append(self.display.show_scroll_message)
            self.delay_queue.append(self.delay)
            self.param_queue.append("No parks selected")
            return

        # Always show all rides from all selected parks (single ride functionality removed)
        for park in parks_to_display:
            if park.is_open is False:
                self.func_queue.append(self.display.show_scroll_message)
                self.delay_queue.append(self.delay)
                self.param_queue.append(park.name + " is closed")
            else:
                await self._add_all_rides(park, park_list.skip_meet, park_list.skip_closed)
            
        self.regenerate_flag = False
        
    
    
    async def _add_all_rides(self, park, skip_meet, skip_closed):
        """
        Add all rides to the queue
        
        Args:
            park: The theme park
            skip_meet: Whether to skip meet & greet attractions
            skip_closed: Whether to skip closed rides
        """
        # Start with the park name
        self.func_queue.append(self.display.show_scroll_message)
        self.delay_queue.append(self.delay)
        self.param_queue.append(park.name + " wait times...")
        
        for ride in park.rides:
            await asyncio.sleep(0)
            if "Meet" in ride.name and skip_meet == True:
                logger.debug(f"Skipping character meet: {ride.name}")
                continue

            if ride.is_open() is False and skip_closed == True:
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

    async def show(self):
        """Show the next message in the queue"""
        if not self.func_queue:
            return
            
        await asyncio.create_task(
            self.func_queue[self.index](self.param_queue[self.index]))
        await asyncio.sleep(self.delay_queue[self.index])
        self.index += 1
        if self.index >= len(self.func_queue):
            self.index = 0
            self.has_completed_cycle = True  # Mark that we've shown all messages at least once