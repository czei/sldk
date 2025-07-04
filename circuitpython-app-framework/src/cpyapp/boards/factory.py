"""
Board factory for creating board configurations.
"""
import os
import json
from .base import BoardBase
from .configs import MatrixPortalS3, MatrixPortalM4, RaspberryPi, SimulatorBoard
from .custom import CustomBoard
from .detection import BoardDetector
from ..utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("board_factory")


class BoardFactory:
    """Factory for creating board configurations"""
    
    # Built-in board registry
    _BOARDS = {
        'matrixportal_s3': MatrixPortalS3,
        'matrixportal_m4': MatrixPortalM4,
        'raspberry_pi': RaspberryPi,
        'simulator': SimulatorBoard,
        'auto': None  # Special case for auto-detection
    }
    
    # Custom board registry
    _custom_boards = {}
    
    @classmethod
    def register_board(cls, name, board_class):
        """
        Register a custom board class
        
        Args:
            name: Board identifier
            board_class: Board class (must inherit from BoardBase)
        """
        if not issubclass(board_class, BoardBase):
            raise TypeError("Board class must inherit from BoardBase")
        
        cls._custom_boards[name] = board_class
        logger.info(f"Registered custom board: {name}")
    
    @classmethod
    def create_board(cls, board_spec='auto', config_overrides=None):
        """
        Create a board configuration
        
        Args:
            board_spec: Board name, 'auto' for detection, or path to config file
            config_overrides: Optional dict of configuration overrides
            
        Returns:
            BoardBase: Board instance
        """
        # Handle auto-detection
        if board_spec == 'auto':
            detected = BoardDetector.detect_board()
            logger.info(f"Auto-detected board: {detected}")
            
            if detected == BoardDetector.SIMULATOR:
                board_spec = 'simulator'
            elif detected == BoardDetector.MATRIXPORTAL_S3:
                board_spec = 'matrixportal_s3'
            elif detected == BoardDetector.MATRIXPORTAL_M4:
                board_spec = 'matrixportal_m4'
            elif detected == BoardDetector.RASPBERRY_PI:
                board_spec = 'raspberry_pi'
            else:
                logger.warning(f"Unknown board detected: {detected}, using simulator")
                board_spec = 'simulator'
        
        # Handle dict configurations
        if isinstance(board_spec, dict):
            board = CustomBoard(board_spec)
            logger.info(f"Created custom board from dict")
        # Check built-in boards
        elif board_spec in cls._BOARDS:
            board_class = cls._BOARDS[board_spec]
            board = board_class()
            logger.info(f"Created built-in board: {board_spec}")
        
        # Check custom registered boards
        elif board_spec in cls._custom_boards:
            board_class = cls._custom_boards[board_spec]
            board = board_class()
            logger.info(f"Created registered custom board: {board_spec}")
        
        # Check if it's a file path
        elif os.path.exists(board_spec):
            board = CustomBoard(board_spec)
            logger.info(f"Created custom board from file: {board_spec}")
        
        # Try to load from boards config directory
        else:
            config_path = cls._find_board_config(board_spec)
            if config_path:
                board = CustomBoard(config_path)
                logger.info(f"Created custom board from config: {config_path}")
            else:
                raise ValueError(f"Unknown board: {board_spec}")
        
        # Apply configuration overrides
        if config_overrides:
            cls._apply_overrides(board, config_overrides)
        
        return board
    
    @classmethod
    def _find_board_config(cls, board_name):
        """
        Find board configuration file
        
        Args:
            board_name: Board name to search for
            
        Returns:
            str: Path to config file or None
        """
        # Search paths
        search_paths = [
            # Current directory
            f"{board_name}.json",
            f"boards/{board_name}.json",
            
            # User config directory
            os.path.expanduser(f"~/.config/cpyapp/boards/{board_name}.json"),
            
            # System config directory
            f"/etc/cpyapp/boards/{board_name}.json",
        ]
        
        # Add package directory
        package_dir = os.path.dirname(__file__)
        search_paths.append(os.path.join(package_dir, 'configs', f'{board_name}.json'))
        
        for path in search_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    @classmethod
    def _apply_overrides(cls, board, overrides):
        """
        Apply configuration overrides to a board
        
        Args:
            board: Board instance
            overrides: Dict of overrides
        """
        # Override display config
        if 'display' in overrides:
            board._display_config.update(overrides['display'])
        
        # Override network config
        if 'network' in overrides:
            board._network_config.update(overrides['network'])
        
        # Override power config
        if 'power' in overrides:
            board._power_config.update(overrides['power'])
        
        # Override pin mappings
        if 'pins' in overrides:
            board._pin_mappings.update(overrides['pins'])
        
        # Override capabilities
        if 'capabilities' in overrides:
            # Add new capabilities
            for cap in overrides['capabilities'].get('add', []):
                board._capabilities.add(cap)
            
            # Remove capabilities
            for cap in overrides['capabilities'].get('remove', []):
                board._capabilities.discard(cap)
    
    @classmethod
    def list_available_boards(cls):
        """
        List all available board configurations
        
        Returns:
            dict: Available boards with descriptions
        """
        boards = {}
        
        # Built-in boards
        for name, board_class in cls._BOARDS.items():
            if board_class:
                board = board_class()
                boards[name] = {
                    'type': 'built-in',
                    'display_name': board.display_name,
                    'manufacturer': board.manufacturer
                }
            else:
                boards[name] = {
                    'type': 'special',
                    'display_name': 'Auto-detect board',
                    'manufacturer': 'Automatic'
                }
        
        # Custom registered boards
        for name, board_class in cls._custom_boards.items():
            board = board_class()
            boards[name] = {
                'type': 'registered',
                'display_name': board.display_name,
                'manufacturer': board.manufacturer
            }
        
        # Search for config files
        config_dirs = [
            'boards',
            os.path.expanduser('~/.config/cpyapp/boards'),
            '/etc/cpyapp/boards'
        ]
        
        for config_dir in config_dirs:
            if os.path.exists(config_dir):
                for filename in os.listdir(config_dir):
                    if filename.endswith('.json'):
                        name = filename[:-5]  # Remove .json
                        if name not in boards:
                            try:
                                with open(os.path.join(config_dir, filename), 'r') as f:
                                    config = json.load(f)
                                boards[name] = {
                                    'type': 'config_file',
                                    'display_name': config.get('display_name', name),
                                    'manufacturer': config.get('manufacturer', 'Unknown'),
                                    'path': os.path.join(config_dir, filename)
                                }
                            except:
                                pass
        
        return boards
    
    @classmethod
    def validate_board(cls, board_spec):
        """
        Validate a board configuration
        
        Args:
            board_spec: Board name or path to config
            
        Returns:
            tuple: (is_valid, board_instance, errors)
        """
        errors = []
        board = None
        
        try:
            # Try to create the board
            board = cls.create_board(board_spec)
            
            # Validate hardware
            hw_valid, hw_errors = board.validate_hardware()
            if not hw_valid:
                errors.extend(hw_errors)
            
        except Exception as e:
            errors.append(f"Failed to create board: {e}")
        
        return len(errors) == 0, board, errors


class BoardConfigMerger:
    """Merges board configurations with user settings"""
    
    @staticmethod
    def merge_configs(board_config, user_config, settings_manager=None):
        """
        Merge board configuration with user settings
        
        Args:
            board_config: Base board configuration
            user_config: User configuration overrides
            settings_manager: Optional settings manager for persistence
            
        Returns:
            dict: Merged configuration
        """
        import copy
        
        # Deep copy the board config
        merged = copy.deepcopy(board_config)
        
        # Load saved settings if available
        if settings_manager:
            saved_config = settings_manager.get('board_config', {})
            BoardConfigMerger._deep_merge(merged, saved_config)
        
        # Apply user config overrides
        BoardConfigMerger._deep_merge(merged, user_config)
        
        # Save merged config if settings manager provided
        if settings_manager:
            settings_manager.set('board_config', merged)
            settings_manager.save()
        
        return merged
    
    @staticmethod
    def _deep_merge(base_dict, override_dict):
        """
        Deep merge override_dict into base_dict
        
        Args:
            base_dict: Base dictionary (modified in place)
            override_dict: Override dictionary
        """
        for key, value in override_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                # Recursively merge dictionaries
                BoardConfigMerger._deep_merge(base_dict[key], value)
            else:
                # Override the value
                base_dict[key] = value