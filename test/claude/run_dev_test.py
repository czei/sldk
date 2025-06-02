#!/usr/bin/env python3
"""Run the dev server and check for errors"""

import subprocess
import time
import sys
import os

# Start the app in development mode
print("Starting app in development mode...")
process = subprocess.Popen(
    [sys.executable, "theme_park_main.py", "--dev"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Give it time to start and run
print("Waiting for app to initialize...")
time.sleep(10)

# Check if process is still running
if process.poll() is None:
    print("App is running successfully")
    
    # Read any output
    try:
        stdout, stderr = process.communicate(timeout=5)
        if stdout:
            print("STDOUT:")
            print(stdout[:1000])  # First 1000 chars
        if stderr:
            print("STDERR:")
            print(stderr[:1000])  # First 1000 chars
    except subprocess.TimeoutExpired:
        print("App is still running (timeout as expected)")
    
    # Check error log
    if os.path.exists("error_log"):
        with open("error_log", "r") as f:
            error_content = f.read()
            if error_content:
                print("\nError log content:")
                print(error_content[-2000:])  # Last 2000 chars
    else:
        print("No error log file found")
    
    # Terminate the process
    print("\nTerminating app...")
    process.terminate()
    process.wait()
else:
    print(f"App exited with code: {process.returncode}")
    stdout, stderr = process.communicate()
    print("STDOUT:", stdout)
    print("STDERR:", stderr)

print("Test complete.")