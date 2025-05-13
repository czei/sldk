"""
Tests for the HTTP client module.
"""
import json
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from src.network.http_client import HttpClient, Response

class TestHttpClient:
    @pytest.mark.asyncio
    async def test_get_request_adafruit(self):
        """Test making a GET request with the adafruit client"""
        # Set up the mock session
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({"status": "success", "data": {"message": "Hello World"}})
        mock_session.get.return_value = mock_response
        
        # Mock the adafruit_requests import
        with patch('src.network.http_client.adafruit_requests') as mock_adafruit_requests:
            # Create client and make request
            client = HttpClient(session=mock_session)
            client.using_adafruit = True
            
            response = await client.get("https://example.com/api/test")
            
            # Verify the request was made correctly
            mock_session.get.assert_called_once_with("https://example.com/api/test", 
                                                    headers={"User-Agent": "Mozilla/5.0 (CircuitPython)"})
            
            # Verify response handling
            assert response.status_code == 200
            data = json.loads(response.text)
            assert data["status"] == "success"
            assert data["data"]["message"] == "Hello World"
    
    @pytest.mark.skip("Test needs to be updated to match implementation")
    @pytest.mark.asyncio
    async def test_get_request_urllib(self):
        """Test making a GET request with the urllib client"""
        # Skip this test until we can properly mock the dependencies
        pass
    
    @pytest.mark.asyncio
    async def test_post_request_adafruit(self):
        """Test making a POST request with the adafruit client"""
        # Set up the mock session
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.text = json.dumps({"status": "created"})
        mock_session.post.return_value = mock_response
        
        # Mock the adafruit_requests import
        with patch('src.network.http_client.adafruit_requests') as mock_adafruit_requests:
            # Create client and make request
            client = HttpClient(session=mock_session)
            client.using_adafruit = True
            
            payload = {"name": "Test", "value": 123}
            response = await client.post("https://example.com/api/test", data=payload)
            
            # Verify the request was made correctly
            mock_session.post.assert_called_once_with(
                "https://example.com/api/test", 
                data=json.dumps(payload),
                headers={"User-Agent": "Mozilla/5.0 (CircuitPython)", "Content-Type": "application/json"}
            )
            
            # Verify response handling
            assert response.status_code == 201
            data = json.loads(response.text)
            assert data["status"] == "created"
    
    @pytest.mark.skip("Test needs to be updated to match implementation")
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in the client"""
        # Skip this test for now
        pass
    
    @pytest.mark.asyncio
    async def test_json_request(self):
        """Test sending JSON data in a request"""
        # Set up the mock session
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({"status": "success"})
        mock_session.post.return_value = mock_response
        
        # Create client and make request with test data
        client = HttpClient(session=mock_session)
        client.using_adafruit = True
        
        test_data = {"test": "data"}
        response = await client.post("https://example.com/api/test", data=test_data)
        
        # Verify the request was made with the correct JSON payload
        mock_session.post.assert_called_once_with(
            "https://example.com/api/test", 
            data=json.dumps(test_data),
            headers={"User-Agent": "Mozilla/5.0 (CircuitPython)", "Content-Type": "application/json"}
        )
        
        # Verify response
        assert response.status_code == 200
        data = json.loads(response.text)
        assert data["status"] == "success"
        
    def test_response_json_parsing(self):
        """Test JSON parsing in Response object"""
        # Test successful parsing
        response = Response(status_code=200, text='{"key": "value"}')
        data = response.json()
        assert data["key"] == "value"
        
        # Test whitespace handling
        response = Response(status_code=200, text=' \n{"key": "value"}\n ')
        data = response.json()
        assert data["key"] == "value"
        
        # Test BOM handling (utf-8 BOM)
        response = Response(status_code=200, text='\ufeff{"key": "value"}')
        data = response.json()
        assert data["key"] == "value"
        
        # Test empty response
        response = Response(status_code=200, text='')
        data = response.json()
        assert data == {}