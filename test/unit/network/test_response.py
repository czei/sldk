"""
Tests for the Response class in the HTTP client module.
"""
import json
import pytest
from unittest.mock import patch, MagicMock

from src.network.http_client import Response


class TestResponse:
    def test_initialization(self):
        """Test Response initialization"""
        # Default initialization
        response = Response()
        assert response.status_code == 200
        assert response.text == ""
        assert response._json is None
        
        # Initialization with parameters
        response = Response(404, "Not Found")
        assert response.status_code == 404
        assert response.text == "Not Found"
    
    def test_json_parsing(self):
        """Test JSON parsing of response text"""
        # Test valid JSON
        response = Response(200, '{"key": "value"}')
        data = response.json()
        assert data["key"] == "value"
        
        # Test caching behavior
        response._json = {"cached": True}
        data = response.json()
        assert data["cached"] is True
    
    def test_json_parsing_with_whitespace(self):
        """Test JSON parsing with whitespace"""
        response = Response(200, ' \n{"key": "value"}\n ')
        data = response.json()
        assert data["key"] == "value"
    
    def test_json_parsing_with_bom(self):
        """Test JSON parsing with BOM character"""
        response = Response(200, '\ufeff{"key": "value"}')
        data = response.json()
        assert data["key"] == "value"
    
    def test_json_parsing_with_empty_response(self):
        """Test JSON parsing with empty response"""
        response = Response(200, '')
        data = response.json()
        assert data == {}
        
        response = Response(200, ' ')
        data = response.json()
        assert data == {}
    
    def test_json_parsing_error(self):
        """Test error handling when JSON parsing fails"""
        response = Response(200, '{"invalid": json}')
        
        # Mock the logger to avoid actual error logging
        with patch('src.network.http_client.logger') as mock_logger:
            with pytest.raises(ValueError) as excinfo:
                response.json()
            
            # Verify the error message contains "syntax error in JSON"
            assert "syntax error in JSON" in str(excinfo.value)
            
            # Verify logger was called to log the error
            assert mock_logger.error.called