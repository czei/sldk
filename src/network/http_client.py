"""
HTTP client for making API requests.
Copyright 2024 3DUPFitters LLC
"""
import json
import adafruit_requests
import ssl
import socketpool
import wifi
from src.utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")


class Response:
    """HTTP response object"""
    
    def __init__(self, status_code= 200, text= ""):
        """
        Initialize a response
        
        Args:
            status_code: The HTTP status code
            text: The response body text
        """
        self.status_code = status_code
        self.text = text
        self._json = None
        # Don't create session here - it should be done after WiFi is connected

        
    def json(self):
        """
        Parse the response body as JSON with error handling
        
        Returns:
            The parsed JSON data
            
        Raises:
            ValueError: If the text cannot be parsed as JSON
        """
        if self._json is None:
            try:
                # Strip any BOM or whitespace that might cause parsing issues
                text_to_parse = self.text.strip()
                if text_to_parse.startswith('\ufeff'):
                    text_to_parse = text_to_parse[1:]
                
                # Handle empty responses
                if not text_to_parse:
                    return {}
                    
                self._json = json.loads(text_to_parse)
            except json.JSONDecodeError as e:
                logger.error(e, f"JSON parse error: {str(e)}")
                logger.debug(f"Response text was: {self.text[:100]}...")
                raise ValueError(f"syntax error in JSON: {str(e)}")
        return self._json


class HttpClient:
    """
    HTTP client for making API requests
    
    This class provides a wrapper around the underlying HTTP implementation,
    which may be adafruit_requests, urllib, or another library.
    """
    
    def __init__(self, session=None):
        """
        Initialize the HTTP client
        
        Args:
            session: The underlying session to use for requests
        """
        self.session = session
        self.use_live_data = True  # Flag to force live data in dev mode
        
        try:
            # Try to import adafruit_requests for CircuitPython
            import adafruit_requests
            self.adafruit_requests = adafruit_requests
            self.using_adafruit = True
        except ImportError:
            self.using_adafruit = False
            
        # Always set up urllib as fallback, even if adafruit is available
        try:
            import urllib.request
            from urllib.error import URLError
            self.urllib = urllib.request
            self.URLError = URLError
        except ImportError:
            # urllib might not be available in CircuitPython
            self.urllib = None
            self.URLError = None
            
    async def get(self, url, headers=None, max_retries=3):
        """
        Make a GET request with retries

        Args:
            url: The URL to request
            headers: Optional headers to include
            max_retries: Maximum number of retry attempts

        Returns:
            A Response object
        """
        if headers is None:
            headers = {
                "User-Agent": "Mozilla/5.0 (CircuitPython)"
            }

        retry_count = 0
        last_error = None

        # In development mode, check if we should use mock data for queue-times.com API
        if "queue-times.com" in url and not self.session and not self.use_live_data:
            logger.info(f"Dev mode - Using mock data for {url}")

            # Check if we're getting the park list
            if url == "https://queue-times.com/parks.json":
                # Return a properly formatted park list for the ThemeParkList class
                # Note: ThemeParkList expects a specific structure matching queue-times.com API
                mock_data = """[
                    {
                        "name": "Disney Parks",
                        "parks": [
                            {"id": 6, "name": "Disney Magic Kingdom", "latitude": 28.4177, "longitude": -81.5812},
                            {"id": 5, "name": "Disney's EPCOT", "latitude": 28.3747, "longitude": -81.5494},
                            {"id": 8, "name": "Disney's Hollywood Studios", "latitude": 28.3577, "longitude": -81.5570},
                            {"id": 7, "name": "Disney's Animal Kingdom", "latitude": 28.3587, "longitude": -81.5917}
                        ]
                    },
                    {
                        "name": "Universal Parks",
                        "parks": [
                            {"id": 3, "name": "Universal Studios Florida", "latitude": 28.4749, "longitude": -81.4664},
                            {"id": 4, "name": "Islands of Adventure", "latitude": 28.4722, "longitude": -81.4702}
                        ]
                    },
                    {
                        "name": "SeaWorld Parks",
                        "parks": [
                            {"id": 14, "name": "SeaWorld Orlando", "latitude": 28.4115, "longitude": -81.4615}
                        ]
                    }
                ]"""
                return Response(status_code=200, text=mock_data)

            # Check if we're getting a specific park
            elif "/parks/" in url and "/queue_times.json" in url:
                # Parse park ID from URL
                import re
                park_id_match = re.search(r'/parks/(\d+)/', url)
                if park_id_match:
                    park_id = park_id_match.group(1)

                    # Return proper mock data for each supported park
                    if park_id == "6":
                        # Disney Magic Kingdom (ID 6)
                        try:
                            import os
                            test_data_path = os.path.join(os.path.dirname(__file__), "../../test/fixtures/magic-kingdom.json")
                            if os.path.exists(test_data_path):
                                with open(test_data_path, "r") as f:
                                    mock_data = f.read()
                                    return Response(status_code=200, text=mock_data)
                        except Exception as e:
                            logger.error(e, "Error loading Magic Kingdom test data, using fallback mock data")
                            
                    elif park_id == "5":
                        # Disney's EPCOT (ID 5)
                        try:
                            import os
                            test_data_path = os.path.join(os.path.dirname(__file__), "../../test/fixtures/epcot-test-data.json")
                            if os.path.exists(test_data_path):
                                with open(test_data_path, "r") as f:
                                    mock_data = f.read()
                                    return Response(status_code=200, text=mock_data)
                        except Exception as e:
                            logger.error(e, "Error loading EPCOT test data, using fallback mock data")

                    # Fallback mock data for any park
                    mock_data = """{"lands": [{"id": 1, "name": "Main Street USA", "rides": [
                        {"id": 101, "name": "Space Mountain", "is_open": true, "wait_time": 45, "last_updated": "2023-04-12T10:30:00Z"},
                        {"id": 102, "name": "Haunted Mansion", "is_open": true, "wait_time": 30, "last_updated": "2023-04-12T10:35:00Z"},
                        {"id": 103, "name": "Pirates of the Caribbean", "is_open": true, "wait_time": 20, "last_updated": "2023-04-12T10:40:00Z"}
                    ]}]}"""
                    return Response(status_code=200, text=mock_data)

            # For any other URL, return empty response
            return Response(status_code=200, text="{}")

        while retry_count < max_retries:
            try:
                if self.using_adafruit and self.session:
                    # For Adafruit CircuitPython requests
                    try:
                        # Import OutOfRetries exception to explicitly handle it
                        try:
                            from adafruit_requests import OutOfRetries
                            out_of_retries_exception = OutOfRetries
                        except ImportError:
                            # If import fails, create a generic exception class for type checking
                            class OutOfRetries(Exception): pass
                            out_of_retries_exception = OutOfRetries

                        try:
                            resp = self.session.get(url, headers=headers)
                            return Response(
                                status_code=resp.status_code,
                                text=resp.text if hasattr(resp, 'text') else ""
                            )
                        except out_of_retries_exception as retry_error:
                            # Special handling for OutOfRetries - needs longer retry delay
                            logger.error(retry_error, f"Socket failures detected (attempt {retry_count+1}) - WiFi issues likely")
                            last_error = retry_error
                            retry_count += 1
                            import asyncio
                            # Longer backoff delay for network issues
                            await asyncio.sleep(5 * retry_count)
                            # Try to reset the session if possible
                            try:
                                # Get a new session from socket pool
                                pool = socketpool.SocketPool(wifi.radio)
                                ssl_context = ssl.create_default_context()
                                import adafruit_requests
                                self.session = adafruit_requests.Session(pool, ssl_context)
                                logger.info("Successfully recreated HTTP session after OutOfRetries")
                            except Exception as session_error:
                                logger.error(session_error, "Failed to recreate HTTP session")
                            continue
                        except Exception as adafruit_error:
                            logger.error(adafruit_error, f"Error in Adafruit request (attempt {retry_count+1})")
                            last_error = adafruit_error
                            retry_count += 1
                    except Exception as adafruit_error:
                        logger.error(adafruit_error, f"Error in Adafruit request outer block (attempt {retry_count+1})")
                        last_error = adafruit_error
                        retry_count += 1
                else:
                    # For standard Python urllib
                    try:
                        request = self.urllib.Request(url, headers=headers)
                        with self.urllib.urlopen(request) as response:
                            return Response(
                                status_code=response.status,
                                text=response.read().decode('utf-8')
                            )
                    except self.URLError as url_error:
                        logger.error(url_error, f"URLError (attempt {retry_count+1})")
                        last_error = url_error
                        retry_count += 1
                    except Exception as urllib_error:
                        logger.error(urllib_error, f"Error in urllib request (attempt {retry_count+1})")
                        last_error = urllib_error
                        retry_count += 1

                # If execution reaches here, there was an error
                import asyncio
                await asyncio.sleep(2 * retry_count)  # Exponential backoff

            except Exception as outer_error:
                # Catch any unexpected exceptions in the retry loop itself
                logger.error(outer_error, f"Unexpected error in HTTP GET retry loop (attempt {retry_count+1})")
                last_error = outer_error
                retry_count += 1
                import asyncio
                await asyncio.sleep(2 * retry_count)  # Exponential backoff

        # All retries failed - return empty Response with error status
        error_msg = str(last_error) if last_error else "Unknown error"
        logger.error(None, f"All {max_retries} GET attempts to {url} failed: {error_msg}")
        return Response(status_code=500, text="{}")
            
    async def post(self, url, data, headers=None):
        """
        Make a POST request
        
        Args:
            url: The URL to request
            data: The data to send (dict will be converted to JSON)
            headers: Optional headers to include
            
        Returns:
            A Response object
        """
        if headers is None:
            headers = {
                "User-Agent": "Mozilla/5.0 (CircuitPython)",
                "Content-Type": "application/json"
            }
            
        # Convert dict to JSON string
        if isinstance(data, dict):
            data = json.dumps(data)
            
        try:
            if self.using_adafruit:
                resp = self.session.post(url, data=data, headers=headers)
                return Response(
                    status_code=resp.status_code,
                    text=resp.text
                )
            else:
                # Use stdlib for non-CircuitPython
                request = self.urllib.Request(
                    url, 
                    data=data.encode('utf-8') if isinstance(data, str) else data,
                    headers=headers,
                    method="POST"
                )
                with self.urllib.urlopen(request) as response:
                    return Response(
                        status_code=response.status,
                        text=response.read().decode('utf-8')
                    )
                    
        except Exception as e:
            logger.error(e, f"Error making POST request to {url}")
            return Response(status_code=500, text=str(e))
    
    def set_use_live_data(self, use_live_data):
        """
        Set whether to use live data or mock data in development mode
        
        Args:
            use_live_data: Boolean flag to use live data
        """
        self.use_live_data = use_live_data
        logger.info(f"HTTP client configured to use {'live' if use_live_data else 'mock'} data")