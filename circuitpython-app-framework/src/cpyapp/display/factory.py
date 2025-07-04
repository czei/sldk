"""
Factory for creating the appropriate display implementation.
Uses the unified display that works on both CircuitPython and LED Simulator.
Integrates with the board configuration system for hardware-specific setup.
"""
import sys
import os
from ..utils.error_handler import ErrorHandler
from ..boards import BoardFactory, BoardCapabilities

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


def use_simple_simulator():
    """
    Check if simple simulator should be used instead of LED Simulator
    
    Returns:
        True if --simple-sim flag is present
    """
    return '--simple-sim' in sys.argv


def create_display(config=None, board=None):
    """
    Factory function to create the appropriate display
    
    Args:
        config: Optional configuration dictionary
        board: Optional board instance or board spec string
    
    Returns:
        Display implementation appropriate for the current platform
    """
    # Handle board parameter
    if board is not None:
        if isinstance(board, str):
            # Create board from spec
            board = BoardFactory.create_board(board)
        
        # Check if board has display capability
        if not (board.has_capability(BoardCapabilities.HAS_RGB_MATRIX) or 
                board.has_capability(BoardCapabilities.HAS_OLED) or
                board.has_capability(BoardCapabilities.HAS_EPAPER)):
            logger.warning(f"Board {board.name} does not have display capabilities")
        
        # Merge board display config with provided config
        if config is None:
            config = {}
        config['board'] = board
        config.update(board.display_config)
        
        # Try to use board's display setup
        try:
            display = board.setup_display()
            if display is not None:
                logger.info(f"Using display from board {board.name}")
                return display
        except Exception as e:
            logger.warning(f"Board display setup failed: {e}, falling back to default")
    
    # Check for simple simulator override
    if is_dev_mode() and use_simple_simulator():
        logger.info("Development mode with --simple-sim flag detected, using simple simulator")
        try:
            from .simulator import SimulatedLEDMatrix
            return SimulatedLEDMatrix(config)
        except ImportError as e:
            logger.error(e, "Error importing simple simulator")
            # Fall through to unified display
    
    # Use unified display for both CircuitPython and LED Simulator
    if is_circuitpython():
        logger.info("CircuitPython detected, using unified display with hardware backend")
    else:
        logger.info("Desktop platform detected, using unified display with LED Simulator backend")
    
    try:
        from .unified import UnifiedDisplay
        return UnifiedDisplay(config)
    except ImportError as e:
        logger.error(e, "Error importing unified display")
        
        # Fallback to hardware or simulator based on platform
        if is_circuitpython():
            try:
                from .hardware import MatrixDisplay
                logger.info("Falling back to hardware display")
                return MatrixDisplay(config)
            except ImportError:
                logger.error(None, "Hardware display also failed")
                # Create a minimal display fallback
                from .interface import DisplayInterface
                return DisplayInterface()
        else:
            try:
                from .simulator import SLDKSimulatorDisplay
                logger.info("Falling back to SLDK simulator display")
                return SLDKSimulatorDisplay(config)
            except ImportError:
                logger.info("LED Simulator not available, using simple simulator")
                try:
                    from .simulator import SimulatedLEDMatrix
                    return SimulatedLEDMatrix(config)
                except ImportError:
                    # Final fallback
                    from .interface import DisplayInterface
                    return DisplayInterface()