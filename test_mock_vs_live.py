#!/usr/bin/env python3
"""Test to check if HTTP client is using mock or live data"""

import sys
import json

# Add src to path
if 'src' not in sys.path:
    sys.path.append('src')

from src.network.http_client import HttpClient
from src.utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("test_mock_log")

def test_mock_behavior():
    """Test if HTTP client returns mock data in dev mode"""
    
    # Create HTTP client without session (dev mode)
    client = HttpClient(session=None)
    
    logger.info(f"HTTP client use_live_data flag: {client.use_live_data}")
    logger.info(f"HTTP client session: {client.session}")
    
    # Create a simple test - no async needed for this check
    url = "https://queue-times.com/parks.json"
    
    # Check the actual mock data logic
    logger.info(f"Testing URL: {url}")
    logger.info(f"Mock data check conditions:")
    logger.info(f"  - 'queue-times.com' in url: {'queue-times.com' in url}")
    logger.info(f"  - not self.session: {not client.session}")
    logger.info(f"  - not self.use_live_data: {not client.use_live_data}")
    logger.info(f"  - Would use mock data: {'queue-times.com' in url and not client.session and not client.use_live_data}")
    
    # Show what the current code would do
    if "queue-times.com" in url and not client.session and not client.use_live_data:
        logger.info("RESULT: Would use MOCK data")
    else:
        logger.info("RESULT: Would use LIVE data")
    
    # Test changing the flag
    logger.info("\nTesting with use_live_data = False:")
    client.set_use_live_data(False)
    if "queue-times.com" in url and not client.session and not client.use_live_data:
        logger.info("RESULT: Would use MOCK data")
    else:
        logger.info("RESULT: Would use LIVE data")

if __name__ == "__main__":
    test_mock_behavior()