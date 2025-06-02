#!/usr/bin/env python3
"""Test with progress tracking"""

import subprocess
import time
import sys

# Start the app
print("Starting app...")
process = subprocess.Popen(
    [sys.executable, "theme_park_main.py", "--dev"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait 20 seconds
print("Waiting 20 seconds...")
time.sleep(20)

# Kill process
print("Terminating...")
process.terminate()
process.wait()

# Check error log
print("\nLast 100 lines of error log:")
try:
    with open("error_log", "r") as f:
        lines = f.readlines()
        for line in lines[-100:]:
            print(line.strip())
except Exception as e:
    print(f"Error reading log: {e}")

print("\nDone.")