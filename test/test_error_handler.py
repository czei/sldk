"""
Test for the ErrorHandler class
"""
import sys
import os
import pytest

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.error_handler import ErrorHandler

def test_error_handler_singleton():
    """Test that multiple instances with same filename return the same object"""
    # Reset class cache for testing
    ErrorHandler._instances = {}

    # Create two instances with the same filename
    handler1 = ErrorHandler("test_error_log")

    # Force a simple value for testing
    handler1.is_readonly = True

    # Create second instance with same name - should return same object state
    handler2 = ErrorHandler("test_error_log")

    # They should share state
    assert handler1.fileName == handler2.fileName
    assert handler2.is_readonly is True  # Should inherit value from handler1

    # Different filename should be a different instance
    handler3 = ErrorHandler("different_error_log")
    assert handler3.fileName != handler1.fileName

    # Clean up test files
    try:
        if os.path.exists("test_error_log"):
            os.remove("test_error_log")
        if os.path.exists("different_error_log"):
            os.remove("different_error_log")
    except:
        pass

    # Reset class cache after test
    ErrorHandler._instances = {}

def test_error_handler_methods():
    """Test basic error handler methods"""
    handler = ErrorHandler("test_error_log")
    
    # Test filter_non_ascii
    assert handler.filter_non_ascii("Hello\u2022World") == "HelloWorld"
    assert handler.filter_non_ascii(None) == ""
    
    # Test file_exists
    assert handler.file_exists("non_existent_file.txt") is False
    
    # Create a file and check it exists
    with open("test_temp_file.txt", "w") as f:
        f.write("test")
    assert handler.file_exists("test_temp_file.txt") is True
    
    # Clean up
    try:
        if os.path.exists("test_temp_file.txt"):
            os.remove("test_temp_file.txt")
        if os.path.exists("test_error_log"):
            os.remove("test_error_log")
    except:
        pass

def test_error_handler_logging():
    """Test that logging methods work"""
    handler = ErrorHandler("test_error_log")
    
    # Force writable for testing
    handler.is_readonly = False
    
    # Test debug method
    handler.debug("Debug message")
    
    # Test info method
    handler.info("Info message")
    
    # Test error method
    try:
        raise ValueError("Test error")
    except ValueError as e:
        handler.error(e, "Error occurred")
    
    # Verify file exists and contains the messages
    assert os.path.exists("test_error_log")
    
    with open("test_error_log", "r") as f:
        content = f.read()
        assert "Debug message" in content
        assert "Info message" in content
        assert "Error occurred" in content
    
    # Clean up
    try:
        if os.path.exists("test_error_log"):
            os.remove("test_error_log")
    except:
        pass