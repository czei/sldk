"""
Unit tests for the board configuration system.
"""
import unittest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock

# Import board modules
from cpyapp.boards import (
    BoardBase, BoardCapabilities, BoardFactory,
    detect_board, create_board, list_boards,
    CustomBoard, CustomBoardTemplate, CustomBoardValidator,
    BoardSettings, BoardSettingsManager
)
from cpyapp.boards.configs import MatrixPortalS3, SimulatorBoard


class TestBoardBase(unittest.TestCase):
    """Test the base board class."""
    
    def test_board_capabilities(self):
        """Test board capability management."""
        board = SimulatorBoard()
        
        # Check has_capability
        self.assertTrue(board.has_capability(BoardCapabilities.HAS_RGB_MATRIX))
        self.assertTrue(board.has_capability(BoardCapabilities.HAS_WIFI))
        self.assertFalse(board.has_capability(BoardCapabilities.HAS_ETHERNET))
        
        # Check capabilities property
        self.assertIn(BoardCapabilities.HAS_RGB_MATRIX, board.capabilities)
        
    def test_board_properties(self):
        """Test board properties."""
        board = MatrixPortalS3()
        
        self.assertEqual(board.name, "matrixportal_s3")
        self.assertEqual(board.display_name, "Adafruit MatrixPortal S3")
        self.assertEqual(board.manufacturer, "Adafruit Industries")
        
        # Check display config
        self.assertEqual(board.display_config['type'], 'rgb_matrix')
        self.assertEqual(board.display_config['width'], 64)
        self.assertEqual(board.display_config['height'], 32)


class TestBoardDetection(unittest.TestCase):
    """Test board detection functionality."""
    
    @patch('cpyapp.boards.detection.IS_CIRCUITPYTHON', False)
    def test_detect_simulator(self):
        """Test detection returns simulator on desktop."""
        from cpyapp.boards.detection import BoardDetector
        
        board_type = BoardDetector.detect_board()
        self.assertEqual(board_type, BoardDetector.SIMULATOR)
        
    @patch('cpyapp.boards.detection.IS_CIRCUITPYTHON', False)
    def test_detect_display_type_simulator(self):
        """Test display detection on simulator."""
        from cpyapp.boards.detection import BoardDetector
        
        display_info = BoardDetector.detect_display_type()
        self.assertEqual(display_info['type'], 'simulator')
        self.assertEqual(display_info['width'], 64)
        self.assertEqual(display_info['height'], 32)
        
    @patch('cpyapp.boards.detection.IS_CIRCUITPYTHON', False)
    def test_full_hardware_report(self):
        """Test full hardware report generation."""
        from cpyapp.boards.detection import BoardDetector
        
        report = BoardDetector.get_full_hardware_report()
        
        self.assertIn('board', report)
        self.assertIn('platform', report)
        self.assertIn('display', report)
        self.assertIn('network', report)
        self.assertIn('storage', report)
        self.assertIn('peripherals', report)
        
        self.assertEqual(report['platform'], 'desktop')
        self.assertEqual(report['board'], 'simulator')


class TestBoardFactory(unittest.TestCase):
    """Test board factory functionality."""
    
    def test_create_auto_board(self):
        """Test auto board creation."""
        board = BoardFactory.create_board('auto')
        self.assertIsInstance(board, BoardBase)
        # On desktop, should be simulator
        self.assertEqual(board.name, 'simulator')
        
    def test_create_specific_board(self):
        """Test creating specific board."""
        board = BoardFactory.create_board('matrixportal_s3')
        self.assertIsInstance(board, MatrixPortalS3)
        self.assertEqual(board.name, 'matrixportal_s3')
        
    def test_create_unknown_board(self):
        """Test creating unknown board raises error."""
        with self.assertRaises(ValueError):
            BoardFactory.create_board('unknown_board_xyz')
            
    def test_list_available_boards(self):
        """Test listing available boards."""
        boards = BoardFactory.list_available_boards()
        
        # Check built-in boards exist
        self.assertIn('matrixportal_s3', boards)
        self.assertIn('matrixportal_m4', boards)
        self.assertIn('simulator', boards)
        self.assertIn('auto', boards)
        
        # Check board info
        self.assertEqual(boards['simulator']['type'], 'built-in')
        self.assertEqual(boards['auto']['type'], 'special')
        
    def test_register_custom_board(self):
        """Test registering custom board class."""
        class TestBoard(BoardBase):
            @property
            def name(self):
                return "test_board"
            
            @property
            def display_name(self):
                return "Test Board"
                
            @property
            def manufacturer(self):
                return "Test Inc"
                
            def setup_display(self):
                return None
                
            def setup_network(self):
                return None
        
        BoardFactory.register_board('test_board', TestBoard)
        board = BoardFactory.create_board('test_board')
        
        self.assertIsInstance(board, TestBoard)
        self.assertEqual(board.name, 'test_board')


class TestCustomBoard(unittest.TestCase):
    """Test custom board functionality."""
    
    def test_custom_board_from_dict(self):
        """Test creating custom board from dict."""
        config = {
            'name': 'my_board',
            'display_name': 'My Board',
            'manufacturer': 'Me',
            'capabilities': ['HAS_RGB_MATRIX'],
            'display': {
                'type': 'rgb_matrix',
                'width': 32,
                'height': 16
            }
        }
        
        board = CustomBoard(config)
        self.assertEqual(board.name, 'my_board')
        self.assertEqual(board.display_name, 'My Board')
        self.assertTrue(board.has_capability(BoardCapabilities.HAS_RGB_MATRIX))
        self.assertEqual(board.display_config['width'], 32)
        
    def test_custom_board_from_file(self):
        """Test creating custom board from JSON file."""
        config = {
            'name': 'file_board',
            'display_name': 'File Board',
            'manufacturer': 'Files Inc'
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_file = f.name
            
        try:
            board = CustomBoard(temp_file)
            self.assertEqual(board.name, 'file_board')
        finally:
            os.unlink(temp_file)
            
    def test_custom_board_validation(self):
        """Test custom board validation."""
        # Missing required field
        invalid_config = {
            'name': 'invalid',
            # Missing display_name and manufacturer
        }
        
        with self.assertRaises(ValueError):
            CustomBoard(invalid_config)
            
    def test_custom_board_template(self):
        """Test custom board template generation."""
        template = CustomBoardTemplate.generate_template('my_custom')
        
        self.assertEqual(template['name'], 'my_custom')
        self.assertIn('display_name', template)
        self.assertIn('capabilities', template)
        self.assertIn('display', template)
        self.assertIn('network', template)
        
    def test_custom_board_validator(self):
        """Test custom board configuration validation."""
        valid_config = {
            'name': 'valid',
            'display_name': 'Valid Board',
            'manufacturer': 'Valid Inc',
            'capabilities': ['HAS_RGB_MATRIX']
        }
        
        is_valid, errors = CustomBoardValidator.validate_config(valid_config)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Invalid capability
        invalid_config = {
            'name': 'invalid',
            'display_name': 'Invalid',
            'manufacturer': 'Invalid Inc',
            'capabilities': ['INVALID_CAPABILITY']
        }
        
        is_valid, errors = CustomBoardValidator.validate_config(invalid_config)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)


class TestBoardSettings(unittest.TestCase):
    """Test board settings management."""
    
    def test_board_settings_defaults(self):
        """Test board settings with defaults."""
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = os.path.join(temp_dir, 'test_settings.json')
            settings = BoardSettings('matrixportal_s3', settings_file)
            
            # Should have default values
            self.assertEqual(settings.get('display.brightness'), 0.5)
            self.assertEqual(settings.get('network.wifi_timeout'), 30)
            
    def test_board_settings_get_set(self):
        """Test getting and setting values."""
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = os.path.join(temp_dir, 'test_settings.json')
            settings = BoardSettings('simulator', settings_file)
            
            # Set value
            settings.set('display.brightness', 0.8)
            self.assertEqual(settings.get('display.brightness'), 0.8)
            
            # Set nested value
            settings.set('custom.nested.value', 'test')
            self.assertEqual(settings.get('custom.nested.value'), 'test')
            
            # Get with default
            self.assertEqual(settings.get('nonexistent', 'default'), 'default')
            
    def test_board_settings_save_load(self):
        """Test saving and loading settings."""
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = os.path.join(temp_dir, 'test_settings.json')
            
            # Create and modify settings
            settings1 = BoardSettings('simulator', settings_file)
            settings1.set('test.value', 123)
            settings1.save()
            
            # Load in new instance
            settings2 = BoardSettings('simulator', settings_file)
            self.assertEqual(settings2.get('test.value'), 123)
            
    def test_board_settings_manager(self):
        """Test board settings manager."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = BoardSettingsManager(temp_dir)
            
            # Get settings for different boards
            s3_settings = manager.get_board_settings('matrixportal_s3')
            m4_settings = manager.get_board_settings('matrixportal_m4')
            
            # Should be different instances
            self.assertIsNot(s3_settings, m4_settings)
            
            # Should have different defaults
            self.assertEqual(s3_settings.get('network.wifi_timeout'), 30)
            self.assertEqual(m4_settings.get('network.wifi_timeout'), 45)


class TestBoardIntegration(unittest.TestCase):
    """Test board system integration."""
    
    def test_board_with_display_factory(self):
        """Test board integration with display factory."""
        from cpyapp.display.factory import create_display
        
        # Create board
        board = create_board('simulator')
        
        # Create display with board
        display = create_display(board=board)
        
        # Display should be created (even if it's just the interface)
        self.assertIsNotNone(display)
        
    @patch('cpyapp.apps.simple.create_display')
    def test_board_with_simple_app(self, mock_create_display):
        """Test board integration with SimpleScrollApp."""
        from cpyapp.apps import SimpleScrollApp
        
        # Mock display
        mock_display = Mock()
        mock_create_display.return_value = mock_display
        
        # Create app with board
        app = SimpleScrollApp(
            data_source="Test",
            board="simulator"
        )
        
        # Check board was created
        self.assertEqual(app.board.name, 'simulator')
        self.assertIsInstance(app.board, SimulatorBoard)
        
        # Check display was created with board
        mock_create_display.assert_called_once()
        call_args = mock_create_display.call_args
        self.assertIsInstance(call_args[0][1], SimulatorBoard)


if __name__ == '__main__':
    unittest.main()