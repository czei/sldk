"""
CircuitPython boot.py for Theme Park Wait Times Display.

This file runs once on boot before code.py.
Used for initial setup and configuration.
"""
import board
import storage
import digitalio

# Enable write access to the filesystem for settings
# Uncomment if you need the device to save settings
# storage.remount("/", False)

# Optional: Set up a button to enable USB write access on boot
# This allows you to edit files when needed
# button = digitalio.DigitalInOut(board.BUTTON_A)
# button.direction = digitalio.Direction.INPUT
# button.pull = digitalio.Pull.UP
# 
# if not button.value:  # Button pressed on boot
#     storage.remount("/", False)  # Enable write access

print("Theme Park Wait Times Display - Boot Complete")