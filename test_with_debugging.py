#!/usr/bin/env python3
"""Test with debugging output"""

import subprocess
import time
import sys
import urllib.request

# Start app and capture output
process = subprocess.Popen(
    [sys.executable, "theme_park_main.py", "--dev"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# Read output for 20 seconds, looking for web server messages
start_time = time.time()
server_messages = []

print("Monitoring app output for web server messages...")
while time.time() - start_time < 20:
    line = process.stdout.readline()
    if line:
        line = line.strip()
        if any(keyword in line.lower() for keyword in ['web server', 'httpserver', 'localhost', '8080', 'port']):
            server_messages.append(line)
            print(f"SERVER: {line}")
    
    # Try to connect after 10 seconds
    if time.time() - start_time > 10 and time.time() - start_time < 11:
        print("\nAttempting connection to localhost:8080...")
        try:
            response = urllib.request.urlopen("http://localhost:8080", timeout=2)
            print(f"SUCCESS: Connected! Status: {response.getcode()}")
        except Exception as e:
            print(f"FAILED: {e}")

# Print all server messages
print("\nAll server-related messages:")
for msg in server_messages:
    print(msg)

# Clean up
process.terminate()
process.wait()

# Check error log
print("\nRecent error log entries:")
try:
    with open("error_log", "r") as f:
        lines = f.readlines()
        for line in lines[-50:]:
            if any(keyword in line.lower() for keyword in ['server', '8080', 'localhost', 'httpserver']):
                print(line.strip())
except:
    pass