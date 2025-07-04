"""
Board configuration system for CircuitPython applications.

This module provides:
- Automatic board detection
- Built-in configurations for common boards
- Custom board support
- Hardware abstraction layer
- Board-specific settings management

Example usage:
    # Auto-detect board
    board = BoardFactory.create_board('auto')
    
    # Use specific board
    board = BoardFactory.create_board('matrixportal_s3')
    
    # Use custom board config
    board = BoardFactory.create_board('my_custom_board.json')
    
    # Set up hardware
    display = board.setup_display()
    network = board.setup_network()
    
    # Check capabilities
    if board.has_capability(BoardCapabilities.HAS_WIFI):
        print("Board has WiFi")
"""

# Base classes
from .base import BoardBase, BoardCapabilities

# Built-in board configurations
from .configs import (
    MatrixPortalS3,
    MatrixPortalM4,
    RaspberryPi,
    SimulatorBoard
)

# Board detection
from .detection import BoardDetector

# Hardware abstraction
from .hardware import (
    PinMapper,
    DisplayController,
    NetworkController,
    PowerController,
    RTCController
)

# Custom board support
from .custom import (
    CustomBoard,
    CustomBoardTemplate,
    CustomBoardValidator,
    create_custom_board_docs
)

# Board factory
from .factory import BoardFactory, BoardConfigMerger

# Settings management
from .settings import (
    BoardSettings,
    BoardSettingsManager,
    get_runtime_config
)

# Convenience functions
def detect_board():
    """
    Detect the current board
    
    Returns:
        str: Board identifier
    """
    return BoardDetector.detect_board()


def create_board(board_spec='auto', config_overrides=None):
    """
    Create a board configuration
    
    Args:
        board_spec: Board name, 'auto' for detection, or path to config file
        config_overrides: Optional dict of configuration overrides
        
    Returns:
        BoardBase: Board instance
    """
    return BoardFactory.create_board(board_spec, config_overrides)


def list_boards():
    """
    List all available board configurations
    
    Returns:
        dict: Available boards with descriptions
    """
    return BoardFactory.list_available_boards()


def get_hardware_report():
    """
    Get a complete hardware detection report
    
    Returns:
        dict: Hardware information
    """
    return BoardDetector.get_full_hardware_report()


# Export main classes and functions
__all__ = [
    # Base classes
    'BoardBase',
    'BoardCapabilities',
    
    # Built-in boards
    'MatrixPortalS3',
    'MatrixPortalM4', 
    'RaspberryPi',
    'SimulatorBoard',
    
    # Detection
    'BoardDetector',
    'detect_board',
    'get_hardware_report',
    
    # Hardware abstraction
    'PinMapper',
    'DisplayController',
    'NetworkController',
    'PowerController',
    'RTCController',
    
    # Custom boards
    'CustomBoard',
    'CustomBoardTemplate',
    'CustomBoardValidator',
    'create_custom_board_docs',
    
    # Factory
    'BoardFactory',
    'BoardConfigMerger',
    'create_board',
    'list_boards',
    
    # Settings
    'BoardSettings',
    'BoardSettingsManager',
    'get_runtime_config'
]