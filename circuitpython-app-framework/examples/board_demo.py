"""
Example demonstrating the board configuration system.
"""
from cpyapp.apps import SimpleScrollApp
from cpyapp.boards import detect_board, get_hardware_report, list_boards

# Print hardware detection report
print("\n=== Hardware Detection Report ===")
report = get_hardware_report()
print(f"Board: {report['board']}")
print(f"Platform: {report['platform']}")
print(f"Display: {report['display']}")
print(f"Network: {report['network']}")
print(f"Storage: {report['storage']}")
print(f"Peripherals: {report['peripherals']}")

# List available boards
print("\n=== Available Boards ===")
boards = list_boards()
for name, info in boards.items():
    print(f"{name}: {info['display_name']} by {info['manufacturer']}")

# Example 1: Auto-detect board
print("\n=== Example 1: Auto-detect ===")
app1 = SimpleScrollApp(
    data_source="Auto-detected board!",
    board="auto"
)
print(f"Using board: {app1.board.display_name}")
print(f"Capabilities: {list(app1.board.capabilities)}")

# Example 2: Specific board
print("\n=== Example 2: Specific Board ===")
app2 = SimpleScrollApp(
    data_source="MatrixPortal S3!",
    board="matrixportal_s3"
)
print(f"Using board: {app2.board.display_name}")

# Example 3: Custom board configuration
print("\n=== Example 3: Custom Board ===")
custom_board_config = {
    "name": "my_custom_led",
    "display_name": "My Custom LED Board", 
    "manufacturer": "DIY Electronics",
    "capabilities": ["HAS_RGB_MATRIX", "HAS_WIFI"],
    "display": {
        "type": "rgb_matrix",
        "width": 32,
        "height": 16,
        "brightness": 0.7
    },
    "network": {
        "type": "wifi",
        "module": "native"
    }
}

app3 = SimpleScrollApp(
    data_source="Custom board!",
    board=custom_board_config
)
print(f"Using board: {app3.board.display_name}")
print(f"Display: {app3.board.display_config['width']}x{app3.board.display_config['height']}")

# Example 4: Board with custom settings
print("\n=== Example 4: Board Settings ===")
app4 = SimpleScrollApp(
    data_source="Board settings demo",
    board="simulator"
)

# Access board settings
board_settings = app4.board_settings_manager.get_board_settings(app4.board.name)
print(f"Display brightness: {board_settings.get('display.brightness')}")
print(f"Network timeout: {board_settings.get('network.wifi_timeout')}")

# Modify settings
board_settings.set('display.brightness', 0.8)
board_settings.save()

# Example 5: Check board capabilities
print("\n=== Example 5: Board Capabilities ===")
from cpyapp.boards import BoardCapabilities

if app1.board.has_capability(BoardCapabilities.HAS_WIFI):
    print("Board has WiFi support")
    
if app1.board.has_capability(BoardCapabilities.HAS_BATTERY):
    level = app1.board.get_battery_level()
    if level:
        print(f"Battery level: {level * 100:.0f}%")
    else:
        print("Battery monitoring not available")

# Run one of the apps (comment out in CircuitPython)
# app1.run()