"""
Factory for creating the appropriate display implementation.
Detects the platform and returns the correct display object.
Copyright 2024 3DUPFitters LLC
"""
import sys
import os
import platform
from src.utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")


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


def create_display(config=None):
    """
    Factory function to create the appropriate display
    
    Args:
        config: Optional configuration dictionary
    
    Returns:
        Display implementation appropriate for the current platform
    """
    # Force simulator if --dev flag is present
    if is_dev_mode():
        logger.info("Development mode detected, using simulated display")
        from src.ui.simulator_display import SimulatedLEDMatrix
        return SimulatedLEDMatrix()
    
    # Check if running on CircuitPython
    if is_circuitpython():
        logger.info("CircuitPython detected, using hardware display")
        # Import the real hardware display
        try:
            from src.ui.display_impl import Display
            return Display(config)
        except ImportError as e:
            logger.error(e, "Error importing hardware display")
            # Fall back to simulator if hardware display fails
            from src.ui.simulator_display import SimulatedLEDMatrix
            return SimulatedLEDMatrix()
    
    # Not on CircuitPython, use simulator
    logger.info(f"Desktop platform detected ({platform.system()}), using simulated display")
    from src.ui.simulator_display import SimulatedLEDMatrix
    return SimulatedLEDMatrix()