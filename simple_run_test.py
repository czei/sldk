#!/usr/bin/env python3
"""Simple run test"""

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

# Wait 15 seconds
print("Waiting 15 seconds...")
time.sleep(15)

# Kill process
print("Terminating...")
process.terminate()
process.wait()

# Check error log
print("\nError log contents:")
try:
    with open("error_log", "r") as f:
        content = f.read()
        print(content)
except Exception as e:
    print(f"Error reading log: {e}")

print("\nDone.")