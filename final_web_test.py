#!/usr/bin/env python3
"""Final test to verify web server is running correctly"""

import subprocess
import time
import urllib.request
import sys

# Start the app
print("Starting app...")
process = subprocess.Popen(
    [sys.executable, "theme_park_main.py", "--dev"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Give it more time to fully initialize
print("Waiting for initialization...")
time.sleep(10)

# Test web server access
print("\nTesting web server at http://localhost:8080")
try:
    response = urllib.request.urlopen("http://localhost:8080", timeout=5)
    print(f"✓ Web server is accessible! Status: {response.getcode()}")
    content = response.read().decode('utf-8')
    print(f"✓ Page title found: {'Theme Park Waits' in content}")
    print(f"✓ Form elements found: {'<form' in content}")
    print(f"✓ Park selector found: {'park-select' in content}")
except Exception as e:
    print(f"✗ Error accessing web server: {e}")

# Test API endpoint
print("\nTesting API endpoint at http://localhost:8080/api/parks")
try:
    response = urllib.request.urlopen("http://localhost:8080/api/parks", timeout=5)
    print(f"✓ API endpoint accessible! Status: {response.getcode()}")
    content = response.read().decode('utf-8')
    if content:
        import json
        data = json.loads(content)
        print(f"✓ API returned {len(data)} park groups")
        if data:
            print(f"✓ First park group: {data[0].get('name', 'Unknown')}")
except Exception as e:
    print(f"✗ Error accessing API: {e}")

# Check if process is still running
if process.poll() is None:
    print("\n✓ App is still running successfully")
else:
    print(f"\n✗ App exited with code: {process.returncode}")

# Cleanup
print("\nTerminating...")
process.terminate()
process.wait()
print("Done.")