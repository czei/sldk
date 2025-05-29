#!/usr/bin/env python3
"""Test script to verify if development server is using live data"""

import asyncio
import json
from src.network.http_client import HttpClient
from src.utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("test_log")

async def test_live_data():
    """Test if the HTTP client is fetching live data"""
    
    # Create HTTP client (in dev mode, should use live data by default)
    client = HttpClient()
    
    # Test getting park list
    logger.info("Testing park list fetch...")
    parks_response = await client.get("https://queue-times.com/parks.json")
    if parks_response and parks_response.text:
        try:
            parks_data = json.loads(parks_response.text)
            logger.info(f"Got {len(parks_data)} park groups from API")
            
            # Print first park group to verify it's real data
            if parks_data:
                first_group = parks_data[0]
                logger.info(f"First park group: {first_group.get('name', 'Unknown')}")
                if 'parks' in first_group:
                    logger.info(f"First park in group: {first_group['parks'][0].get('name', 'Unknown')}")
        except json.JSONDecodeError as e:
            logger.error(e, "Failed to parse park list JSON")
    else:
        logger.error(None, "Failed to fetch park list")
    
    # Test getting ride data for a specific park (Magic Kingdom)
    logger.info("\nTesting ride data fetch for Magic Kingdom...")
    rides_response = await client.get("https://queue-times.com/parks/6/queue_times.json")
    if rides_response and rides_response.text:
        try:
            rides_data = json.loads(rides_response.text)
            
            # Check if data looks like real data (has lands and rides)
            if 'lands' in rides_data:
                total_rides = sum(len(land.get('rides', [])) for land in rides_data['lands'])
                logger.info(f"Got {len(rides_data['lands'])} lands with {total_rides} total rides")
                
                # Check first ride to see if it has real-time data
                for land in rides_data['lands']:
                    if 'rides' in land and land['rides']:
                        first_ride = land['rides'][0]
                        logger.info(f"First ride: {first_ride.get('name', 'Unknown')}")
                        logger.info(f"Wait time: {first_ride.get('wait_time', 'N/A')} minutes")
                        logger.info(f"Last updated: {first_ride.get('last_updated', 'N/A')}")
                        break
            else:
                logger.info("WARNING: Rides data doesn't contain 'lands' - might be mock data")
        except json.JSONDecodeError as e:
            logger.error(e, "Failed to parse ride data JSON")
    else:
        logger.error(None, "Failed to fetch ride data")
    
    # Check if client is configured for live data
    logger.info(f"\nHTTP client use_live_data flag: {client.use_live_data}")

if __name__ == "__main__":
    logger.info("Starting live data test...")
    asyncio.run(test_live_data())
    logger.info("Live data test complete.")