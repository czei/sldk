#!/usr/bin/env python3
"""Test real API calls work in development mode"""

import asyncio
import json
from src.network.http_client import HttpClient
from src.utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("real_api_test")

async def test_real_api():
    """Test fetching real data from queue-times.com API"""
    
    # Create HTTP client in dev mode (should use real API)
    client = HttpClient()
    
    logger.info(f"Testing real API with HTTP client configured for {'live' if client.use_live_data else 'mock'} data")
    
    # Try to fetch park list
    logger.info("Fetching park list from queue-times.com...")
    try:
        response = await client.get("https://queue-times.com/parks.json")
        if response and response.text:
            data = json.loads(response.text)
            logger.info(f"SUCCESS: Got {len(data)} park groups from real API")
            
            # Print first park group to verify structure
            if data:
                first_group = data[0]
                logger.info(f"First park group: {first_group.get('name', 'Unknown')}")
                if 'parks' in first_group and first_group['parks']:
                    logger.info(f"First park in group: {first_group['parks'][0].get('name', 'Unknown')}")
        else:
            logger.error(None, "Failed to get response from parks.json")
    except Exception as e:
        logger.error(e, "Error fetching park list")
    
    # Try to fetch ride data for Magic Kingdom
    logger.info("\nFetching ride data for Magic Kingdom (park ID 6)...")
    try:
        response = await client.get("https://queue-times.com/parks/6/queue_times.json")
        if response and response.text:
            data = json.loads(response.text)
            if 'lands' in data:
                total_rides = sum(len(land.get('rides', [])) for land in data['lands'])
                logger.info(f"SUCCESS: Got {len(data['lands'])} lands with {total_rides} total rides")
                
                # Show first ride to verify real-time data
                for land in data['lands']:
                    if 'rides' in land and land['rides']:
                        first_ride = land['rides'][0]
                        logger.info(f"Sample ride: {first_ride.get('name', 'Unknown')}")
                        logger.info(f"  Wait time: {first_ride.get('wait_time', 'N/A')} minutes")
                        logger.info(f"  Is open: {first_ride.get('is_open', 'N/A')}")
                        logger.info(f"  Last updated: {first_ride.get('last_updated', 'N/A')}")
                        break
            else:
                logger.info("Response structure doesn't match expected format")
        else:
            logger.error(None, "Failed to get response from park ride data")
    except Exception as e:
        logger.error(e, "Error fetching ride data")

if __name__ == "__main__":
    logger.info("Testing real API calls in development mode...")
    asyncio.run(test_real_api())
    logger.info("Real API test complete.")