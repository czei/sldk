"""
Weather Display Boot File

This file runs on CircuitPython startup to configure the environment.
"""
import storage
import board
import digitalio

# Check if we should enable write access to the filesystem
# Hold the button during boot to enable write access
button = digitalio.DigitalInOut(board.BUTTON_UP)
button.switch_to_input(pull=digitalio.Pull.UP)

# If button is pressed, enable write access
if not button.value:
    storage.remount("/", readonly=False)
    print("Write access enabled - you can modify files via USB")
else:
    print("Read-only mode - files protected from corruption")
    
button.deinit()