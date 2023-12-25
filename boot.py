

import board
import digitalio
import time
import storage

# Define the button pin
button_pin = board.BUTTON_DOWN  # Change this to the actual pin connected to your button

# Create a digital input object for the button
button = digitalio.DigitalInOut(button_pin)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP  # You may need to adjust the pull direction based on your circuit
drive_state = not button.value

# False makes the USB drive read-only to the computer
# storage.remount("/", False)
# print(f"Drive mount logic is: {drive_state}")
storage.remount("/", drive_state)
