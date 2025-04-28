import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add the src directory to the path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock the CircuitPython-specific modules
sys.modules['storage'] = MagicMock()
sys.modules['adafruit_requests'] = MagicMock()
sys.modules['adafruit_datetime'] = MagicMock()
sys.modules['board'] = MagicMock()
sys.modules['rtc'] = MagicMock()
sys.modules['microcontroller'] = MagicMock()
sys.modules['wifi'] = MagicMock()
sys.modules['socketpool'] = MagicMock()
sys.modules['ssl'] = MagicMock()
sys.modules['adafruit_httpserver'] = MagicMock()
sys.modules['displayio'] = MagicMock()
sys.modules['rgbmatrix'] = MagicMock()
sys.modules['framebufferio'] = MagicMock()
sys.modules['supervisor'] = MagicMock()
sys.modules['mdns'] = MagicMock()

# Now we can import the ErrorHandler
from src.utils.error_handler import ErrorHandler

class TestErrorHandler(unittest.TestCase):
    
    def test_error_handler_writable_filesystem(self):
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            test_file = temp_file.name
        
        try:
            # Initialize the ErrorHandler with a direct mock of is_readonly
            with patch.object(ErrorHandler, '__init__', return_value=None) as mock_init:
                handler = ErrorHandler.__new__(ErrorHandler)
                handler.fileName = test_file
                handler.is_readonly = False
                
                # Test writing messages
                handler.info("Test info message")
                handler.debug("Test debug message")
                
                # Verify messages were written to the file
                with open(test_file, 'r') as f:
                    content = f.read()
                    self.assertIn("Test info message", content)
                    self.assertIn("Test debug message", content)
                
                # Test error handling
                try:
                    # Generate a test exception
                    raise ValueError("Test error")
                except ValueError as e:
                    handler.error(e, "Test error description")
                
                # Verify error was written to the file
                with open(test_file, 'r') as f:
                    content = f.read()
                    self.assertIn("Test error description:Test error", content)
                    self.assertIn("stack trace:", content)
        
        finally:
            # Clean up temporary file
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_error_handler_readonly_filesystem(self):
        # Create a non-existent file path for testing
        test_file = "/nonexistent/path/error.log"
        
        # Test ErrorHandler with a directly set read-only flag
        with patch('builtins.print') as mock_print:
            with patch.object(ErrorHandler, '__init__', return_value=None) as mock_init:
                handler = ErrorHandler.__new__(ErrorHandler)
                handler.fileName = test_file
                handler.is_readonly = True
                
                # Test writing messages to read-only filesystem
                handler.info("Test info message")
                handler.debug("Test debug message")
                
                # Verify messages were printed but not written
                mock_print.assert_any_call("Test info message")
                mock_print.assert_any_call("Test debug message")
                
                # Test error handling on read-only filesystem
                try:
                    # Generate a test exception
                    raise ValueError("Test readonly error")
                except ValueError as e:
                    handler.error(e, "Test readonly error description")
                
                # Verify error was printed but not written
                mock_print.assert_any_call("Test readonly error description:Test readonly error")
                
                # The stack trace string might be combined with other output
                called_with_stack_trace = False
                for call_args, _ in mock_print.call_args_list:
                    if call_args and "stack trace:" in str(call_args[0]):
                        called_with_stack_trace = True
                        break
                self.assertTrue(called_with_stack_trace, "No print call contained 'stack trace:'")
            
    
    def test_error_handler_filter_non_ascii(self):
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            test_file = temp_file.name
        
        try:
            # Test static method directly
            self.assertEqual(ErrorHandler.filter_non_ascii("Normal ASCII text"), "Normal ASCII text")
            self.assertEqual(ErrorHandler.filter_non_ascii("Text with emoji 😊"), "Text with emoji ")
            self.assertEqual(ErrorHandler.filter_non_ascii("Special characters: ñáéíóú"), "Special characters: ")
            self.assertEqual(ErrorHandler.filter_non_ascii(None), "")
            
            # Test through instance methods
            with patch('src.utils.ErrorHandler.storage', MagicMock()):
                handler = ErrorHandler(test_file)
                # Generate text with non-ASCII characters
                mixed_text = "Error with Unicode: ⚠️ Warning! ⚠️"
                
                # Capture print output
                with patch('builtins.print'):
                    handler.write_to_file(mixed_text)
                
                # Verify only ASCII characters were written
                if not handler.is_readonly:
                    with open(test_file, 'r') as f:
                        content = f.read()
                        self.assertIn("Error with Unicode:  Warning! ", content)
                        self.assertNotIn("⚠️", content)
        
        finally:
            # Clean up temporary file
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_error_handler_filter_non_ascii_static_method(self):
        """Test the static method for filtering non-ASCII characters"""
        self.assertEqual(ErrorHandler.filter_non_ascii("Normal ASCII text"), "Normal ASCII text")
        self.assertEqual(ErrorHandler.filter_non_ascii("Text with emoji 😊"), "Text with emoji ")
        self.assertEqual(ErrorHandler.filter_non_ascii("Special characters: ñáéíóú"), "Special characters: ")
        self.assertEqual(ErrorHandler.filter_non_ascii(None), "")
    
    def test_error_handler_automatic_state_update(self):
        """Test that the handler updates its state if a write unexpectedly fails"""
        # Create a temp file that we'll use for initial setup
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            test_file = temp_file.name
            
        try:
            # Initialize with writable filesystem
            with patch.object(ErrorHandler, '__init__', return_value=None):
                handler = ErrorHandler.__new__(ErrorHandler)
                handler.fileName = test_file
                handler.is_readonly = False
                
                # First write should succeed
                handler.info("First message")
                
                # Check file was written to
                with open(test_file, 'r') as f:
                    self.assertIn("First message", f.read())
                
                # Now make writes fail with OSError
                with patch('builtins.open') as mock_open:
                    mock_open.side_effect = OSError("Disk full")
                    with patch('builtins.print') as mock_print:
                        # This should fail and update state
                        handler.write_to_file("This will fail")
                        
                        # Verify error handler updated its state
                        self.assertTrue(handler.is_readonly)
                        
                        # Should have printed the state update message
                        mock_print.assert_any_call("Filesystem detected as read-only, logs will be displayed on console only")
                        
                        # Next write should not attempt to open the file
                        mock_open.reset_mock()
                        handler.write_to_file("This should not call open")
                        mock_open.assert_not_called()
        finally:
            # Clean up
            if os.path.exists(test_file):
                os.remove(test_file)

if __name__ == '__main__':
    unittest.main()