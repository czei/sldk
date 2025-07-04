"""Utility functions and classes."""

from .error_handler import ErrorHandler
from .platform import is_circuitpython, is_dev_mode
from .system import set_system_clock
from .timer import Timer

__all__ = ['ErrorHandler', 'is_circuitpython', 'is_dev_mode', 'set_system_clock', 'Timer']