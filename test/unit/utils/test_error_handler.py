"""
Tests for the error handling utility.
"""
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from src.utils.error_handler import ErrorHandler
from test.helpers import with_temp_file

class TestErrorHandler:
    def test_initialization(self):
        """Test basic initialization"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            log_path = temp_file.name
            
        try:
            handler = ErrorHandler(log_path)
            assert handler.fileName == log_path
            # In test environment, should default to writable
            assert not handler.is_readonly
        finally:
            if os.path.exists(log_path):
                os.remove(log_path)
    
    @patch('src.utils.error_handler.storage')
    def test_readonly_filesystem_detection(self, mock_storage):
        """Test detection of read-only filesystem"""
        # Setup mock for read-only filesystem
        mock_mount = MagicMock()
        mock_mount.readonly = True
        mock_storage.getmount.return_value = mock_mount
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            log_path = temp_file.name
            
        try:
            with patch('builtins.print') as mock_print:
                handler = ErrorHandler(log_path)
                assert handler.is_readonly
                
                # Verify initialization message
                mock_print.assert_any_call("ErrorHandler initialized - read-only filesystem")
        finally:
            if os.path.exists(log_path):
                os.remove(log_path)
    
    @with_temp_file()
    def test_logging_messages(self, file_path):
        """Test logging messages to file"""
        handler = ErrorHandler(file_path)
        handler.info("Test info message")
        handler.debug("Test debug message")
        
        with open(file_path, 'r') as f:
            content = f.read()
            assert "Test info message" in content
            assert "Test debug message" in content
    
    @with_temp_file()
    def test_error_logging(self, file_path):
        """Test logging error with stack trace"""
        handler = ErrorHandler(file_path)
        
        try:
            # Generate a test exception
            raise ValueError("Test error")
        except ValueError as e:
            handler.error(e, "Error description")
        
        with open(file_path, 'r') as f:
            content = f.read()
            assert "Error description:Test error" in content
            assert "stack trace:" in content
            assert "ValueError" in content
    
    def test_filter_non_ascii(self):
        """Test filtering non-ASCII characters"""
        assert ErrorHandler.filter_non_ascii("Normal ASCII text") == "Normal ASCII text"
        assert ErrorHandler.filter_non_ascii("Text with emoji 😊") == "Text with emoji "
        assert ErrorHandler.filter_non_ascii("Special characters: ñáéíóú") == "Special characters: "
        assert ErrorHandler.filter_non_ascii(None) == ""
    
    @patch('builtins.open')
    def test_readonly_filesystem_write_fallback(self, mock_open):
        """Test fallback to console when filesystem is read-only"""
        # Force a write error to simulate read-only filesystem
        mock_open.side_effect = OSError("Read-only filesystem")
        
        with patch('builtins.print') as mock_print:
            handler = ErrorHandler("/nonexistent/path/error.log")
            # Should detect read-only state due to OSError
            assert handler.is_readonly
            
            # Log some messages
            handler.info("Test info message")
            handler.debug("Test debug message")
            
            # Verify they were printed to console
            mock_print.assert_any_call("Test info message")
            mock_print.assert_any_call("Test debug message")