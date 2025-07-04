"""
Generic MessageQueue for managing the display of content.
"""
import asyncio

from ..utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")


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
        # Force any currently running display operation to stop
        if hasattr(self.display, 'stop_current_operation'):
            self.display.stop_current_operation()

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

    async def add_static_message(self, message, duration=3):
        """
        Add a static message to the queue
        
        Args:
            message: The message to display
            duration: How long to show the message
        """
        self.func_queue.append(self.display.show_static_message)
        self.param_queue.append(message)
        self.delay_queue.append(duration)

    async def add_splash(self, duration=10, reveal_style=False):
        """
        Add a splash screen to the queue
        
        Args:
            duration: Duration to show the splash screen (seconds)
            reveal_style: If True, use reveal animation instead of static display
        """
        logger.debug(f"Adding splash message to queue with duration={duration}, reveal_style={reveal_style}")
        self.func_queue.append(self.display.show_splash)
        self.param_queue.append((duration, reveal_style))
        self.delay_queue.append(0)  # No additional delay since duration is handled in show_splash

    async def add_animation(self, animation, duration=5):
        """
        Add an animation to the queue
        
        Args:
            animation: Animation instance to display
            duration: Duration to show the animation
        """
        if hasattr(self.display, 'show_animation'):
            self.func_queue.append(self.display.show_animation)
            self.param_queue.append((animation, duration))
            self.delay_queue.append(0)
        else:
            # Fallback to static message if animations not supported
            await self.add_static_message("Animation", duration)

    async def add_custom_function(self, func, params=None, delay=2):
        """
        Add a custom display function to the queue
        
        Args:
            func: Function to call on the display
            params: Parameters to pass to the function
            delay: Delay after calling the function
        """
        self.func_queue.append(func)
        self.param_queue.append(params if params is not None else ())
        self.delay_queue.append(delay)

    async def show(self):
        """Show the next message in the queue"""
        if not self.func_queue:
            return
            
        try:
            # Bounds check to prevent index errors during queue rebuilds
            if (self.index >= len(self.func_queue) or 
                self.index >= len(self.param_queue) or 
                self.index >= len(self.delay_queue)):
                self.index = 0
                return
                
            # Handle parameters - if it's a tuple, unpack it; otherwise pass as single param
            params = self.param_queue[self.index]
            if isinstance(params, tuple):
                await asyncio.create_task(
                    self.func_queue[self.index](*params))
            else:
                await asyncio.create_task(
                    self.func_queue[self.index](params))
            await asyncio.sleep(self.delay_queue[self.index])
            self.index += 1
            if self.index >= len(self.func_queue):
                self.index = 0
                self.has_completed_cycle = True  # Mark that we've shown all messages at least once
        except IndexError:
            # Queue was modified during execution - reset index and return
            self.index = 0
            return

    def get_queue_length(self):
        """
        Get the number of items in the queue
        
        Returns:
            Number of items in the queue
        """
        return len(self.func_queue)
        
    def is_empty(self):
        """
        Check if the queue is empty
        
        Returns:
            True if queue is empty, False otherwise
        """
        return len(self.func_queue) == 0