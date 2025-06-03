#!/usr/bin/env python3
"""Simple effects demo - shows individual effects clearly.

Run this to see specific effects in action.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sldk.display import UnifiedDisplay
from sldk.effects import EffectsEngine
from sldk.effects.effects import SparkleEffect, EdgeGlowEffect
from sldk.effects.particles import ParticleEngine, Sparkle, RainDrop


async def create_display_with_window(title="SLDK Effects Demo"):
    """Create display and window for simulator."""
    display = UnifiedDisplay()
    await display.initialize()
    
    # Create window for simulator
    if hasattr(display, 'create_window'):
        await display.create_window(title)
    
    # Start event loop for simulator
    if hasattr(display, 'run_event_loop'):
        asyncio.create_task(display.run_event_loop())
    
    return display


async def demo_sparkle_field():
    """Demo: Sparkle field effect."""
    print("\\n=== Sparkle Field Demo ===")
    print("Watch sparkles appear and fade across the display")
    
    display = await create_display_with_window("SLDK Effects - Sparkle Field")
    effects_engine = EffectsEngine(max_effects=1, target_fps=8)
    
    # Add sparkle effect
    sparkle = SparkleEffect(intensity=5, duration=10.0)
    effects_engine.add_effect(sparkle)
    
    # Fill with dark blue background
    for y in range(display.height):
        for x in range(display.width):
            await display.set_pixel(x, y, 0x001133)
    
    # Run for 10 seconds
    for frame in range(80):  # 8 FPS * 10 seconds
        print(f"\\rFrame {frame + 1}/80", end="")
        
        # Update effects
        await effects_engine.update(display)
        await display.show()
        await asyncio.sleep(0.125)  # 8 FPS
    
    print("\\nSparkle demo complete!")
    await display.clear()
    await display.show()


async def demo_edge_glow():
    """Demo: Edge glow effect."""
    print("\\n=== Edge Glow Demo ===")
    print("Watch the edges pulse with cyan light")
    
    display = await create_display_with_window("SLDK Effects - Edge Glow")
    effects_engine = EffectsEngine(max_effects=1, target_fps=10)
    
    # Add edge glow effect
    glow = EdgeGlowEffect(color=0x00FFFF, duration=8.0)
    effects_engine.add_effect(glow)
    
    # Run for 8 seconds
    for frame in range(80):  # 10 FPS * 8 seconds
        print(f"\\rFrame {frame + 1}/80", end="")
        
        # Fill center with dark color
        center_color = 0x002020
        for y in range(2, display.height - 2):
            for x in range(2, display.width - 2):
                await display.set_pixel(x, y, center_color)
        
        # Update effects
        await effects_engine.update(display)
        await display.show()
        await asyncio.sleep(0.1)  # 10 FPS
    
    print("\\nEdge glow demo complete!")
    await display.clear()
    await display.show()


async def demo_rain_particles():
    """Demo: Rain particle effect."""
    print("\\n=== Rain Particles Demo ===")
    print("Watch raindrops fall from the sky")
    
    display = await create_display_with_window("SLDK Effects - Rain Particles")
    particle_engine = ParticleEngine(max_particles=8)
    
    import random
    
    # Run for 10 seconds
    for frame in range(100):  # 10 FPS * 10 seconds
        print(f"\\rFrame {frame + 1}/100", end="")
        
        # Dark sky background
        for y in range(display.height):
            for x in range(display.width):
                await display.set_pixel(x, y, 0x001144)
        
        # Spawn raindrops occasionally
        if random.random() < 0.4:  # 40% chance per frame
            x = random.randint(0, display.width - 1)
            raindrop = RainDrop(x, -2, speed=12.0, color=0x4080FF, lifetime=3.0)
            particle_engine.add_particle(raindrop)
        
        # Update particles
        await particle_engine.update(display)
        await display.show()
        await asyncio.sleep(0.1)  # 10 FPS
    
    print("\\nRain demo complete!")
    await display.clear()
    await display.show()


async def demo_manual_sparkles():
    """Demo: Manually controlled sparkles."""
    print("\\n=== Manual Sparkles Demo ===")
    print("Watch individual sparkles with different colors")
    
    display = await create_display_with_window("SLDK Effects - Manual Sparkles")
    particle_engine = ParticleEngine(max_particles=6)
    
    import random
    
    # Pre-defined sparkle colors
    colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0xFF00FF, 0x00FFFF, 0xFFFFFF]
    
    # Run for 8 seconds
    for frame in range(80):  # 10 FPS * 8 seconds
        print(f"\\rFrame {frame + 1}/80", end="")
        
        # Black background
        await display.clear()
        
        # Spawn sparkle every 10 frames
        if frame % 10 == 0:
            x = random.randint(2, display.width - 3)
            y = random.randint(2, display.height - 3)
            color = random.choice(colors)
            sparkle = Sparkle(x, y, color=color, lifetime=2.0)
            particle_engine.add_particle(sparkle)
        
        # Update particles
        await particle_engine.update(display)
        await display.show()
        await asyncio.sleep(0.1)  # 10 FPS
    
    print("\\nManual sparkles demo complete!")
    await display.clear()
    await display.show()


async def demo_color_wipe():
    """Demo: Simple color wipe transition."""
    print("\\n=== Color Wipe Demo ===")
    print("Watch colors wipe across the display")
    
    display = await create_display_with_window("SLDK Effects - Color Wipe")
    colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0xFF00FF, 0x00FFFF]
    
    for color in colors:
        print(f"\\rWiping color: 0x{color:06X}", end="")
        
        # Wipe from left to right
        for x in range(display.width):
            for y in range(display.height):
                await display.set_pixel(x, y, color)
            
            await display.show()
            await asyncio.sleep(0.05)  # Smooth wipe
        
        # Hold color for a moment
        await asyncio.sleep(0.5)
    
    print("\\nColor wipe demo complete!")
    await display.clear()
    await display.show()


async def demo_breathing_effect():
    """Demo: Breathing brightness effect."""
    print("\\n=== Breathing Effect Demo ===")
    print("Watch the display 'breathe' with changing brightness")
    
    display = await create_display_with_window("SLDK Effects - Breathing Effect")
    
    # Fill with purple color
    base_color = 0x800080
    for y in range(display.height):
        for x in range(display.width):
            await display.set_pixel(x, y, base_color)
    
    import math
    
    # Breathing effect for 6 seconds
    for frame in range(120):  # 20 FPS * 6 seconds
        print(f"\\rFrame {frame + 1}/120", end="")
        
        # Calculate breathing brightness using sine wave
        time_factor = frame / 20.0  # Convert frame to time
        brightness = 0.3 + 0.7 * (math.sin(time_factor) + 1) / 2  # 0.3 to 1.0
        
        # Apply brightness to display if supported
        if hasattr(display, 'brightness'):
            display.brightness = brightness
        else:
            # Simulate brightness by modifying color intensity
            r = int(((base_color >> 16) & 0xFF) * brightness)
            g = int(((base_color >> 8) & 0xFF) * brightness)
            b = int((base_color & 0xFF) * brightness)
            dimmed_color = (r << 16) | (g << 8) | b
            
            for y in range(display.height):
                for x in range(display.width):
                    await display.set_pixel(x, y, dimmed_color)
        
        await display.show()
        await asyncio.sleep(0.05)  # 20 FPS
    
    print("\\nBreathing effect demo complete!")
    
    # Restore brightness
    if hasattr(display, 'brightness'):
        display.brightness = 1.0
    
    await display.clear()
    await display.show()


def simple_effects_demo():
    """Simple effects demo using direct device approach."""
    print("SLDK Simple Effects Demo")
    print("=" * 40)
    print("Showing lightweight effects optimized for ESP32")
    
    # Import device directly
    from sldk.simulator.devices import MatrixPortalS3
    import time
    import math
    import random
    
    # Create device
    device = MatrixPortalS3()
    device.initialize()
    
    # Demo state
    demo_stage = 0
    stage_start = 0
    sparkles = []
    stage_names = ["Sparkle Field", "Edge Glow", "Rain Particles", 
                   "Manual Sparkles", "Color Wipe", "Breathing Effect"]
    
    def update():
        """Update function called each frame."""
        nonlocal demo_stage, stage_start, sparkles
        
        current_time = time.time()
        if stage_start == 0:
            stage_start = current_time
        
        elapsed = current_time - stage_start
        
        if demo_stage == 0 and elapsed < 8:
            # Stage 1: Sparkle Field Effect
            # Dark blue background
            for y in range(device.height):
                for x in range(device.width):
                    device.matrix.set_pixel(x, y, 0x001133)
            
            # Add random sparkles
            if random.random() < 0.5:  # 50% chance per frame
                sparkles.append({
                    'x': random.randint(0, device.width - 1),
                    'y': random.randint(0, device.height - 1),
                    'life': 1.0,
                    'color': random.choice([0xFFFFFF, 0xFFFF00, 0x00FFFF])
                })
            
            # Update and draw sparkles
            for sparkle in sparkles[:]:
                sparkle['life'] -= 0.04
                if sparkle['life'] <= 0:
                    sparkles.remove(sparkle)
                else:
                    # Fade sparkle
                    brightness = sparkle['life']
                    color = sparkle['color']
                    r = int(((color >> 16) & 0xFF) * brightness)
                    g = int(((color >> 8) & 0xFF) * brightness) 
                    b = int((color & 0xFF) * brightness)
                    faded_color = (r << 16) | (g << 8) | b
                    device.matrix.set_pixel(sparkle['x'], sparkle['y'], faded_color)
                    
        elif demo_stage == 1 and elapsed < 8:
            # Stage 2: Edge Glow Effect
            # Dark center
            for y in range(device.height):
                for x in range(device.width):
                    device.matrix.set_pixel(x, y, 0x002020)
            
            # Glow intensity based on time
            glow_intensity = int((math.sin(elapsed * 2) + 1) * 127)
            glow_color = (0 << 16) | (glow_intensity << 8) | glow_intensity  # Cyan glow
            
            # Draw glowing edges
            for i in range(device.width):
                device.matrix.set_pixel(i, 0, glow_color)  # Top edge
                device.matrix.set_pixel(i, device.height - 1, glow_color)  # Bottom edge
            for i in range(device.height):
                device.matrix.set_pixel(0, i, glow_color)  # Left edge
                device.matrix.set_pixel(device.width - 1, i, glow_color)  # Right edge
                
        elif demo_stage == 2 and elapsed < 8:
            # Stage 3: Rain Particles
            device.matrix.fill(0x001144)  # Dark sky
            
            # Add rain drops from top
            if random.random() < 0.4:
                sparkles.append({
                    'x': random.randint(0, device.width - 1),
                    'y': -1,
                    'vy': random.uniform(12, 20),
                    'color': 0x4080FF,
                    'type': 'rain'
                })
            
            # Update rain drops
            for drop in sparkles[:]:
                drop['y'] += drop['vy'] * 0.1
                if drop['y'] >= device.height:
                    sparkles.remove(drop)
                else:
                    device.matrix.set_pixel(int(drop['x']), int(drop['y']), drop['color'])
                    
        elif demo_stage == 3 and elapsed < 8:
            # Stage 4: Manual Sparkles
            device.matrix.fill(0x000000)  # Black background
            
            # Add sparkle every 20 frames
            if int(elapsed * 10) % 20 == 0:
                sparkles.append({
                    'x': random.randint(2, device.width - 3),
                    'y': random.randint(2, device.height - 3),
                    'life': 1.0,
                    'color': random.choice([0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0xFF00FF, 0x00FFFF, 0xFFFFFF])
                })
            
            # Update sparkles
            for sparkle in sparkles[:]:
                sparkle['life'] -= 0.05
                if sparkle['life'] <= 0:
                    sparkles.remove(sparkle)
                else:
                    brightness = sparkle['life']
                    color = sparkle['color']
                    r = int(((color >> 16) & 0xFF) * brightness)
                    g = int(((color >> 8) & 0xFF) * brightness) 
                    b = int((color & 0xFF) * brightness)
                    faded_color = (r << 16) | (g << 8) | b
                    device.matrix.set_pixel(sparkle['x'], sparkle['y'], faded_color)
                    
        elif demo_stage == 4 and elapsed < 8:
            # Stage 5: Color Wipe
            colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0xFF00FF, 0x00FFFF]
            color_index = int(elapsed * 1.5) % len(colors)
            wipe_progress = (elapsed * 8) % device.width
            
            for y in range(device.height):
                for x in range(device.width):
                    if x <= wipe_progress:
                        device.matrix.set_pixel(x, y, colors[color_index])
                    else:
                        device.matrix.set_pixel(x, y, 0x000000)
                        
        elif demo_stage == 5:
            # Stage 6: Breathing Effect
            base_color = 0x800080  # Purple
            
            # Calculate breathing brightness using sine wave
            brightness = 0.3 + 0.7 * (math.sin(elapsed * 2) + 1) / 2  # 0.3 to 1.0
            
            # Apply brightness
            r = int(((base_color >> 16) & 0xFF) * brightness)
            g = int(((base_color >> 8) & 0xFF) * brightness)
            b = int((base_color & 0xFF) * brightness)
            dimmed_color = (r << 16) | (g << 8) | b
            
            device.matrix.fill(dimmed_color)
        
        # Advance stages
        stage_duration = 8
        if elapsed >= stage_duration:
            demo_stage = (demo_stage + 1) % 6  # 6 total stages
            stage_start = current_time
            sparkles.clear()  # Clear particles when changing stages
            
            # Update window title with current effect name
            import pygame
            if pygame.display.get_init():
                new_title = f"SLDK Simple Effects Demo - {stage_names[demo_stage]}"
                pygame.display.set_caption(new_title)
            
            print(f"Simple Effects Demo Stage {demo_stage + 1}: {stage_names[demo_stage]}")
        
        return True
    
    # Use device.run() 
    device.run(update_callback=update, title="SLDK Simple Effects Demo")


def main():
    """Main entry point."""
    simple_effects_demo()


if __name__ == "__main__":
    main()