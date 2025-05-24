#!/usr/bin/env python3
"""Run the app and capture detailed error information"""

import subprocess
import time
import sys

# Start the app in development mode, capturing all output
print("Starting app in development mode with detailed logging...")
process = subprocess.Popen(
    [sys.executable, "theme_park_main.py", "--dev"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,  # Combine stdout and stderr
    text=True,
    bufsize=1,  # Line buffered
    universal_newlines=True
)

# Read output for first 15 seconds
start_time = time.time()
web_server_started = False
error_found = False

print("\nApp output:")
print("-" * 50)

while time.time() - start_time < 15:
    line = process.stdout.readline()
    if line:
        print(line.strip())
        
        # Check for web server messages
        if "web server started" in line.lower():
            web_server_started = True
        if "error" in line.lower() and "web server" in line.lower():
            error_found = True
        if "Failed to start development web server" in line:
            error_found = True
        if "HTTPServer" in line:
            print(f"HTTPServer mentioned: {line}")
    
    # Check if process is still running
    if process.poll() is not None:
        print(f"\nApp exited early with code: {process.returncode}")
        break

print("-" * 50)

# Print summary
print("\nSummary:")
print(f"Web server started: {web_server_started}")
print(f"Web server errors found: {error_found}")

# Clean up
print("\nTerminating process...")
process.terminate()
process.wait()

# Check error log for additional info
print("\nChecking error log...")
try:
    with open("error_log", "r") as f:
        content = f.read()
        if "web server" in content.lower():
            # Find all web server related lines
            for line in content.split('\n'):
                if "web server" in line.lower() or "DevThemeParkWebServer" in line:
                    print(line)
except Exception as e:
    print(f"Error reading log: {e}")

print("\nDone.")