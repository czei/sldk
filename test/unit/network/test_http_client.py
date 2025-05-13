"""
Tests for the HTTP client module.
"""
import json
import pytest
from unittest.mock import patch, MagicMock

from src.network.http_client import HttpClient
from test.helpers import mock_network_response, with_temp_json

class TestHttpClient:
    @patch('src.network.http_client.requests')
    def test_get_request(self, mock_requests):
        """Test making a GET request with the client"""
        # Set up the mock response
        mock_response = mock_network_response(
            status_code=200,
            content=json.dumps({"status": "success", "data": {"message": "Hello World"}})
        )
        mock_requests.get.return_value = mock_response
        
        # Create client and make request
        client = HttpClient()
        response = client.get("https://example.com/api/test")
        
        # Verify the request was made correctly
        mock_requests.get.assert_called_once_with("https://example.com/api/test", timeout=10)
        
        # Verify response handling
        assert response.status_code == 200
        data = json.loads(response.text)
        assert data["status"] == "success"
        assert data["data"]["message"] == "Hello World"
    
    @patch('src.network.http_client.requests')
    def test_post_request(self, mock_requests):
        """Test making a POST request with the client"""
        # Set up the mock response
        mock_response = mock_network_response(
            status_code=201,
            content=json.dumps({"status": "created"})
        )
        mock_requests.post.return_value = mock_response
        
        # Create client and make request
        client = HttpClient()
        payload = {"name": "Test", "value": 123}
        response = client.post("https://example.com/api/test", data=payload)
        
        # Verify the request was made correctly
        mock_requests.post.assert_called_once_with(
            "https://example.com/api/test", 
            json=payload,
            timeout=10
        )
        
        # Verify response handling
        assert response.status_code == 201
        data = json.loads(response.text)
        assert data["status"] == "created"
    
    @patch('src.network.http_client.requests')
    def test_error_handling(self, mock_requests):
        """Test error handling in the client"""
        # Set up the mock to raise an exception
        mock_requests.get.side_effect = Exception("Network error")
        
        # Create client and attempt request
        client = HttpClient()
        
        # The client should handle the exception gracefully
        response = client.get("https://example.com/api/test")
        
        # Verify the handling based on your implementation
        # This depends on how your HttpClient handles exceptions
        assert response is None or response.status_code >= 400
    
    @with_temp_json({"test": "data"})
    @patch('src.network.http_client.requests')
    def test_json_request(self, mock_requests, json_path):
        """Test reading JSON and sending it in a request"""
        # Set up the mock response
        mock_response = mock_network_response(
            status_code=200,
            content=json.dumps({"status": "success"})
        )
        mock_requests.post.return_value = mock_response
        
        # Read the test JSON file
        with open(json_path, 'r') as f:
            test_data = json.load(f)
        
        # Create client and make request with the test data
        client = HttpClient()
        response = client.post("https://example.com/api/test", data=test_data)
        
        # Verify the request was made with the correct JSON payload
        mock_requests.post.assert_called_once_with(
            "https://example.com/api/test", 
            json={"test": "data"},
            timeout=10
        )
        
        # Verify response
        assert response.status_code == 200