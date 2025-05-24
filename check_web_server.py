#!/usr/bin/env python3
"""Check if the web server is running"""

import subprocess
import time
import urllib.request
import sys

# Start the app in development mode
print("Starting app in development mode...")
process = subprocess.Popen(
    [sys.executable, "theme_park_main.py", "--dev"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Give it time to start
time.sleep(5)

# Check if web server is accessible
print("Checking web server...")
try:
    response = urllib.request.urlopen("http://localhost:8080")
    print(f"Web server is running! Status: {response.getcode()}")
    content = response.read().decode('utf-8')
    print("Found web page with content starting with:", content[:100])
except Exception as e:
    print(f"Error accessing web server: {e}")

# Also check the API endpoint
print("\nChecking API endpoint...")
try:
    response = urllib.request.urlopen("http://localhost:8080/api/parks")
    print(f"API endpoint accessible! Status: {response.getcode()}")
    content = response.read().decode('utf-8')
    import json
    data = json.loads(content)
    print(f"API returned {len(data)} park groups")
except Exception as e:
    print(f"Error accessing API: {e}")

# Check error log for web server messages
print("\nChecking error log for web server messages...")
if process.poll() is None:
    # Still running, check logs
    with open("error_log", "r") as f:
        content = f.read()
        if "web server started" in content.lower():
            print("Web server start message found in logs")
        if "localhost:8080" in content or "localhost:8000" in content:
            print("Found localhost reference in logs")

# Terminate
print("\nTerminating...")
process.terminate()
process.wait()
print("Done.")