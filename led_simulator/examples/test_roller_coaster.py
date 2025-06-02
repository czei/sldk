#!/usr/bin/env python3
"""Quick test of roller coaster animation."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from roller_coaster_animation import main, RollerCoaster, create_track_bitmap

# Quick test
print("Testing roller coaster track generation...")
coaster = RollerCoaster(64, 32)
print(f"Track has {len(coaster.track_points)} points")

# Test physics
print("\nTesting physics for 50 steps:")
for i in range(50):
    coaster.update_cart()
    if i % 10 == 0:
        print(f"Step {i}: Cart at ({coaster.cart_x}, {coaster.cart_y}), velocity={coaster.cart_velocity:.2f}")

print("\nTrack generation and physics test complete!")
print("Run roller_coaster_animation.py to see the full animation.")