#!/usr/bin/env python3
"""Test the development server endpoints to verify they use live data"""

import requests
import json
import subprocess
import time
import signal
import sys

# Start the development server
print("Starting development server...")
server_process = subprocess.Popen(
    [sys.executable, "theme_park_main.py", "--dev"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Give server time to start
time.sleep(3)

try:
    # Test the main page
    print("\nTesting main page...")
    response = requests.get("http://localhost:8000/")
    print(f"Main page status: {response.status_code}")
    
    # Test API endpoints
    print("\nTesting API endpoints...")
    
    # Test parks endpoint
    parks_response = requests.get("http://localhost:8000/api/parks")
    print(f"Parks endpoint status: {parks_response.status_code}")
    
    if parks_response.status_code == 200:
        parks_data = parks_response.json()
        print(f"Number of park groups: {len(parks_data)}")
        if parks_data:
            print(f"First park group: {parks_data[0].get('name', 'Unknown')}")
    
    # Test individual park endpoint  
    park_response = requests.get("http://localhost:8000/api/park?park_id=6")
    print(f"\nPark endpoint status: {park_response.status_code}")
    
    if park_response.status_code == 200:
        park_data = park_response.json()
        if 'lands' in park_data:
            print(f"Number of lands: {len(park_data['lands'])}")
            total_rides = sum(len(land.get('rides', [])) for land in park_data['lands'])
            print(f"Total rides: {total_rides}")
            
            # Check for real-time data indicators
            for land in park_data['lands']:
                if 'rides' in land and land['rides']:
                    first_ride = land['rides'][0]
                    print(f"\nSample ride data:")
                    print(f"  Name: {first_ride.get('name', 'Unknown')}")
                    print(f"  Wait time: {first_ride.get('wait_time', 'N/A')} minutes")
                    print(f"  Last updated: {first_ride.get('last_updated', 'N/A')}")
                    print(f"  Is open: {first_ride.get('is_open', 'N/A')}")
                    break
    
    # Test rides endpoint
    rides_response = requests.get("http://localhost:8000/api/rides?park_id=6")
    print(f"\nRides endpoint status: {rides_response.status_code}")
    
    if rides_response.status_code == 200:
        rides_data = rides_response.json()
        if 'rides' in rides_data:
            print(f"Number of rides: {len(rides_data['rides'])}")
            if rides_data['rides']:
                print(f"First ride: {rides_data['rides'][0].get('name', 'Unknown')}")

except Exception as e:
    print(f"Error during testing: {e}")

finally:
    # Stop the server
    print("\nStopping server...")
    server_process.terminate()
    server_process.wait()
    print("Server stopped.")