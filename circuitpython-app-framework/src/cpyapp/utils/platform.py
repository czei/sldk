"""
Platform detection utilities for CircuitPython applications.
"""
import sys


def is_circuitpython():
    """
    Check if running on CircuitPython
    
    Returns:
        True if running on CircuitPython, False otherwise
    """
    return hasattr(sys, 'implementation') and sys.implementation.name == 'circuitpython'


def is_dev_mode():
    """
    Check if running in development mode
    
    Returns:
        True if --dev flag is present in command line args
    """
    return '--dev' in sys.argv


def get_platform_name():
    """
    Get a human-readable platform name
    
    Returns:
        Platform name string
    """
    if is_circuitpython():
        return "CircuitPython"
    else:
        return "Desktop Python"


def use_simple_simulator():
    """
    Check if simple simulator should be used instead of LED Simulator
    
    Returns:
        True if --simple-sim flag is present
    """
    return '--simple-sim' in sys.argv