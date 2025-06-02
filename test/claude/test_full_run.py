#!/usr/bin/env python3
"""Test full run to see if web server starts"""

import subprocess
import time
import sys
import urllib.request

# Start the app
print("Starting app...")
process = subprocess.Popen(
    [sys.executable, "theme_park_main.py", "--dev"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# Monitor output
start_time = time.time()
web_server_started = False
update_completed = False

print("\nMonitoring app output...")
while time.time() - start_time < 60:  # Run for 60 seconds
    line = process.stdout.readline()
    if line:
        line = line.strip()
        print(f"[{time.time() - start_time:.1f}s] {line}")
        
        if "web server started" in line.lower():
            web_server_started = True
            print("*** WEB SERVER STARTED ***")
        
        if "update complete" in line.lower() or "wait times initialized" in line.lower():
            update_completed = True
            print("*** UPDATE COMPLETED ***")
            
        if "all initialization complete" in line.lower():
            print("*** INITIALIZATION COMPLETE ***")
    
    # Try to connect to web server after 30 seconds
    if time.time() - start_time > 30 and not web_server_started:
        print("\nChecking for web server at 30 seconds...")
        try:
            response = urllib.request.urlopen("http://localhost:8080", timeout=2)
            print(f"Web server IS accessible! Status: {response.getcode()}")
            web_server_started = True
        except:
            print("Web server not accessible yet")

# Final check
print(f"\nFinal status after 60 seconds:")
print(f"Web server started: {web_server_started}")
print(f"Update completed: {update_completed}")

# Clean up
process.terminate()
process.wait()
print("\nDone.")