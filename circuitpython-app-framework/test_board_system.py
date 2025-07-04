#!/usr/bin/env python3
"""
Simple test of the board configuration system.
"""
import sys
sys.path.insert(0, 'src')

from cpyapp.boards import (
    BoardFactory, BoardCapabilities, 
    detect_board, get_hardware_report, list_boards,
    CustomBoardTemplate
)

print("=== Board Configuration System Test ===\n")

# Test 1: Board detection
print("1. Board Detection:")
detected = detect_board()
print(f"   Detected board: {detected}")

# Test 2: Hardware report
print("\n2. Hardware Report:")
report = get_hardware_report()
for key, value in report.items():
    print(f"   {key}: {value}")

# Test 3: List available boards
print("\n3. Available Boards:")
boards = list_boards()
for name, info in boards.items():
    print(f"   - {name}: {info['display_name']} ({info['type']})")

# Test 4: Create boards
print("\n4. Creating Boards:")

# Auto-detect
board_auto = BoardFactory.create_board('auto')
print(f"   Auto: {board_auto.display_name}")

# Specific board
board_s3 = BoardFactory.create_board('matrixportal_s3')
print(f"   S3: {board_s3.display_name}")
print(f"      Display: {board_s3.display_config['width']}x{board_s3.display_config['height']}")
print(f"      Capabilities: {len(board_s3.capabilities)}")

# Test 5: Check capabilities
print("\n5. Board Capabilities:")
sim_board = BoardFactory.create_board('simulator')
print(f"   Simulator capabilities:")
print(f"   - Has RGB Matrix: {sim_board.has_capability(BoardCapabilities.HAS_RGB_MATRIX)}")
print(f"   - Has WiFi: {sim_board.has_capability(BoardCapabilities.HAS_WIFI)}")
print(f"   - Has Battery: {sim_board.has_capability(BoardCapabilities.HAS_BATTERY)}")

# Test 6: Custom board config
print("\n6. Custom Board Template:")
template = CustomBoardTemplate.generate_template('my_device')
print(f"   Generated template for: {template['name']}")
print(f"   Display type: {template['display']['type']}")
print(f"   Network type: {template['network']['type']}")

# Test 7: Create custom board
print("\n7. Custom Board Creation:")
custom_config = {
    'name': 'test_board',
    'display_name': 'Test Board',
    'manufacturer': 'Test Inc',
    'capabilities': ['HAS_RGB_MATRIX'],
    'display': {
        'type': 'rgb_matrix',
        'width': 16,
        'height': 8
    }
}
custom_board = BoardFactory.create_board(custom_config)
print(f"   Created: {custom_board.display_name}")
print(f"   Size: {custom_board.display_config['width']}x{custom_board.display_config['height']}")

print("\n=== Test Complete ===")