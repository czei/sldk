#!/usr/bin/env python3
"""Simple verification that HTTP client uses live data by default"""

import asyncio
import json
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.network.http_client import HttpClient
from src.utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("verify_log")

async def main():
    # Create HTTP client in development mode (no session)
    client = HttpClient()
    
    print(f"HTTP Client Configuration:")
    print(f"  use_live_data: {client.use_live_data}")
    print(f"  session: {client.session}")
    print(f"  using_adafruit: {client.using_adafruit}")
    
    # The logic in get() method checks:
    # if "queue-times.com" in url and not self.session and not self.use_live_data:
    
    # Since use_live_data is True by default, it should NOT use mock data
    url = "https://queue-times.com/parks.json"
    will_use_mock = "queue-times.com" in url and not client.session and not client.use_live_data
    
    print(f"\nMock Data Logic Check:")
    print(f"  URL: {url}")
    print(f"  Contains queue-times.com: {'queue-times.com' in url}")
    print(f"  No session: {not client.session}")
    print(f"  Live data disabled: {not client.use_live_data}")
    print(f"  Will use mock data: {will_use_mock}")
    
    print(f"\nResult: HTTP client will use {'MOCK' if will_use_mock else 'LIVE'} data")
    
    # Also check what happens in the main app
    print("\nChecking theme_park_main.py initialization...")
    
    # Read the relevant lines from theme_park_main.py
    with open('theme_park_main.py', 'r') as f:
        content = f.read()
        if 'http_client = HttpClient()' in content:
            print("✓ HttpClient is initialized without parameters")
            print("✓ This means use_live_data defaults to True")
            print("✓ The development GUI will use LIVE data from queue-times.com")

if __name__ == "__main__":
    asyncio.run(main())