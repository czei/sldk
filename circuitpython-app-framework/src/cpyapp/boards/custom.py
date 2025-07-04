"""
Custom board support for user-defined hardware configurations.
"""
import json
import os
from .base import BoardBase, BoardCapabilities
from .hardware import DisplayController, NetworkController, PowerController, RTCController


class CustomBoard(BoardBase):
    """Custom board implementation that loads configuration from file or dict"""
    
    def __init__(self, config):
        """
        Initialize custom board from configuration
        
        Args:
            config: Dict configuration or path to JSON config file
        """
        super().__init__()
        
        # Load configuration
        if isinstance(config, str):
            # Load from file
            with open(config, 'r') as f:
                self._config = json.load(f)
        else:
            # Use dict directly
            self._config = config
        
        # Validate configuration
        self._validate_config()
        
        # Set up board from config
        self._setup_from_config()
    
    def _validate_config(self):
        """Validate the configuration has required fields"""
        required_fields = ['name', 'display_name', 'manufacturer']
        for field in required_fields:
            if field not in self._config:
                raise ValueError(f"Custom board config missing required field: {field}")
    
    def _setup_from_config(self):
        """Set up board properties from configuration"""
        # Set capabilities
        capabilities_list = self._config.get('capabilities', [])
        for cap in capabilities_list:
            if hasattr(BoardCapabilities, cap):
                self._capabilities.add(getattr(BoardCapabilities, cap))
        
        # Set configurations
        self._display_config = self._config.get('display', {})
        self._network_config = self._config.get('network', {})
        self._power_config = self._config.get('power', {})
        self._pin_mappings = self._config.get('pins', {})
    
    @property
    def name(self):
        return self._config['name']
    
    @property
    def display_name(self):
        return self._config['display_name']
    
    @property
    def manufacturer(self):
        return self._config['manufacturer']
    
    def setup_display(self):
        """Set up display based on configuration"""
        if not self._display_config:
            return None
        
        display_type = self._display_config.get('type')
        if not display_type:
            return None
        
        controller = DisplayController(display_type, self._display_config)
        return controller.initialize()
    
    def setup_network(self):
        """Set up network based on configuration"""
        if not self._network_config:
            return None
        
        network_type = self._network_config.get('type')
        if not network_type:
            return None
        
        controller = NetworkController(network_type, self._network_config)
        return controller.initialize()


class CustomBoardTemplate:
    """Template generator for creating custom board configurations"""
    
    @staticmethod
    def generate_template(board_name="custom_board"):
        """
        Generate a template configuration for a custom board
        
        Args:
            board_name: Name for the custom board
            
        Returns:
            dict: Template configuration
        """
        return {
            "name": board_name,
            "display_name": "Custom Board",
            "manufacturer": "Your Company",
            "version": "1.0",
            
            "capabilities": [
                "HAS_RGB_MATRIX",
                "HAS_WIFI"
            ],
            
            "display": {
                "type": "rgb_matrix",
                "width": 64,
                "height": 32,
                "bit_depth": 4,
                "brightness": 0.5,
                "comment": "Add pin mappings for your specific hardware"
            },
            
            "network": {
                "type": "wifi",
                "module": "native",
                "comment": "Set to 'esp32' if using ESP32 co-processor"
            },
            
            "power": {
                "default_brightness": 0.5,
                "low_power_brightness": 0.2,
                "battery_pin": "BATTERY",
                "battery_min_voltage": 3.0,
                "battery_max_voltage": 4.2
            },
            
            "pins": {
                "neopixel": "NEOPIXEL",
                "button_1": "D5",
                "button_2": "D6",
                "comment": "Map logical names to physical pin names"
            },
            
            "rtc": {
                "type": "internal",
                "comment": "Set to 'ds3231' for external RTC"
            }
        }
    
    @staticmethod
    def save_template(filename, board_name="custom_board"):
        """
        Save a template configuration to file
        
        Args:
            filename: Output filename
            board_name: Name for the custom board
        """
        template = CustomBoardTemplate.generate_template(board_name)
        
        with open(filename, 'w') as f:
            json.dump(template, f, indent=2)
        
        print(f"Template saved to {filename}")
        print("Edit this file to match your hardware configuration")


class CustomBoardValidator:
    """Validates custom board configurations"""
    
    @staticmethod
    def validate_config(config):
        """
        Validate a custom board configuration
        
        Args:
            config: Configuration dict or path to config file
            
        Returns:
            tuple: (is_valid, errors)
        """
        errors = []
        
        # Load config if it's a file path
        if isinstance(config, str):
            try:
                with open(config, 'r') as f:
                    config = json.load(f)
            except Exception as e:
                return False, [f"Failed to load config file: {e}"]
        
        # Check required fields
        required_fields = ['name', 'display_name', 'manufacturer']
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Validate capabilities
        if 'capabilities' in config:
            valid_capabilities = [attr for attr in dir(BoardCapabilities) 
                               if attr.startswith('HAS_')]
            for cap in config['capabilities']:
                if cap not in valid_capabilities:
                    errors.append(f"Invalid capability: {cap}")
        
        # Validate display config
        if 'display' in config:
            display = config['display']
            if 'type' in display:
                valid_types = ['rgb_matrix', 'oled', 'epaper', 'simulator']
                if display['type'] not in valid_types:
                    errors.append(f"Invalid display type: {display['type']}")
            
            if 'width' in display and not isinstance(display['width'], int):
                errors.append("Display width must be an integer")
            
            if 'height' in display and not isinstance(display['height'], int):
                errors.append("Display height must be an integer")
        
        # Validate network config
        if 'network' in config:
            network = config['network']
            if 'type' in network:
                valid_types = ['wifi', 'ethernet', 'bluetooth', 'simulator']
                if network['type'] not in valid_types:
                    errors.append(f"Invalid network type: {network['type']}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def test_board(config):
        """
        Test a custom board configuration
        
        Args:
            config: Configuration dict or path to config file
            
        Returns:
            dict: Test results
        """
        results = {
            'config_valid': False,
            'board_created': False,
            'display_initialized': False,
            'network_initialized': False,
            'errors': []
        }
        
        # Validate config
        is_valid, errors = CustomBoardValidator.validate_config(config)
        results['config_valid'] = is_valid
        if not is_valid:
            results['errors'] = errors
            return results
        
        # Try to create board
        try:
            board = CustomBoard(config)
            results['board_created'] = True
            
            # Try to initialize display
            try:
                display = board.setup_display()
                results['display_initialized'] = display is not None
            except Exception as e:
                results['errors'].append(f"Display initialization failed: {e}")
            
            # Try to initialize network
            try:
                network = board.setup_network()
                results['network_initialized'] = network is not None
            except Exception as e:
                results['errors'].append(f"Network initialization failed: {e}")
            
        except Exception as e:
            results['errors'].append(f"Board creation failed: {e}")
        
        return results


def create_custom_board_docs(board_config, output_file):
    """
    Generate documentation for a custom board configuration
    
    Args:
        board_config: Board configuration dict or path
        output_file: Output markdown file path
    """
    # Load config
    if isinstance(board_config, str):
        with open(board_config, 'r') as f:
            config = json.load(f)
    else:
        config = board_config
    
    # Generate documentation
    doc = f"""# {config.get('display_name', 'Custom Board')} Configuration

## Overview
- **Name**: {config.get('name', 'unknown')}
- **Manufacturer**: {config.get('manufacturer', 'unknown')}
- **Version**: {config.get('version', '1.0')}

## Capabilities
"""
    
    if 'capabilities' in config:
        for cap in config['capabilities']:
            doc += f"- {cap}\n"
    else:
        doc += "- No capabilities defined\n"
    
    doc += "\n## Display Configuration\n"
    if 'display' in config:
        display = config['display']
        doc += f"- **Type**: {display.get('type', 'not specified')}\n"
        doc += f"- **Resolution**: {display.get('width', '?')}x{display.get('height', '?')}\n"
        doc += f"- **Bit Depth**: {display.get('bit_depth', 'not specified')}\n"
        doc += f"- **Default Brightness**: {display.get('brightness', 'not specified')}\n"
    else:
        doc += "No display configuration defined\n"
    
    doc += "\n## Network Configuration\n"
    if 'network' in config:
        network = config['network']
        doc += f"- **Type**: {network.get('type', 'not specified')}\n"
        doc += f"- **Module**: {network.get('module', 'not specified')}\n"
    else:
        doc += "No network configuration defined\n"
    
    doc += "\n## Pin Mappings\n"
    if 'pins' in config:
        for name, pin in config['pins'].items():
            if name != 'comment':
                doc += f"- **{name}**: {pin}\n"
    else:
        doc += "No pin mappings defined\n"
    
    # Save documentation
    with open(output_file, 'w') as f:
        f.write(doc)
    
    print(f"Documentation saved to {output_file}")