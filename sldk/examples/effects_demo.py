#!/usr/bin/env python3
"""Effects system demo for SLDK.

Demonstrates the lightweight effects system with visual examples.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sldk.display.content import DisplayContent, StaticText
from sldk.display import UnifiedDisplay
from sldk.effects import EffectsEngine, SimpleEffect
from sldk.effects.effects import (
    RainbowCycleEffect, SparkleEffect, PulseEffect, 
    EdgeGlowEffect, CornerFlashEffect
)
from sldk.effects.transitions import TransitionEngine, FadeTransition, WipeTransition, SlideTransition
from sldk.effects.particles import ParticleEngine, Sparkle, RainDrop, Ember, Snow


class EffectsDemo:
    """Demonstration of SLDK effects system."""
    
    def __init__(self):
        """Initialize demo."""
        self.display = None
        self.effects_engine = EffectsEngine(max_effects=3, target_fps=10)
        self.transition_engine = TransitionEngine()
        self.particle_engine = ParticleEngine(max_particles=6)
        
        self.demo_stage = 0
        self.stage_start_time = 0
        self.stage_duration = 8.0  # 8 seconds per demo stage
        
        # Demo stages
        self.stages = [
            ("Rainbow Cycle", self.demo_rainbow),
            ("Sparkle Effect", self.demo_sparkle),
            ("Pulse Effect", self.demo_pulse),
            ("Edge Glow", self.demo_edge_glow),
            ("Corner Flash", self.demo_corner_flash),
            ("Particles: Rain", self.demo_rain),
            ("Particles: Fire", self.demo_fire),
            ("Particles: Snow", self.demo_snow),
            ("Transition: Fade", self.demo_fade_transition),
            ("Transition: Wipe", self.demo_wipe_transition),
            ("Transition: Slide", self.demo_slide_transition),
            ("Combined Effects", self.demo_combined),
        ]
    
    async def run(self):
        """Run the effects demonstration."""
        print("SLDK Effects System Demo")
        print("=" * 40)
        print("This demo showcases lightweight visual effects")
        print("optimized for ESP32 CircuitPython devices.")
        print("Press Ctrl+C to stop")
        print()
        
        # Initialize display
        self.display = UnifiedDisplay()
        await self.display.initialize()
        
        # Create window for simulator
        if hasattr(self.display, 'create_window'):
            await self.display.create_window("SLDK Effects System Demo")
        
        # Start event loop for simulator
        if hasattr(self.display, 'run_event_loop'):
            asyncio.create_task(self.display.run_event_loop())
        
        print(f"Display: {self.display.width}x{self.display.height} pixels")
        print()
        
        try:
            await self._run_demo_loop()
        except KeyboardInterrupt:
            print("\\nDemo stopped.")
        finally:
            await self.display.clear()
            await self.display.show()
    
    async def _run_demo_loop(self):
        """Main demo loop."""
        import time
        
        while True:
            current_time = time.time()
            
            # Check if it's time to advance to next stage
            if current_time - self.stage_start_time > self.stage_duration:
                await self._advance_stage()
                self.stage_start_time = current_time
            
            # Clear display
            await self.display.clear()
            
            # Run current demo stage
            stage_name, stage_func = self.stages[self.demo_stage]
            await stage_func()
            
            # Update all engines
            await self.effects_engine.update(self.display)
            await self.transition_engine.update(self.display)
            await self.particle_engine.update(self.display)
            
            # Update display
            await self.display.show()
            
            # Frame rate limiting
            await asyncio.sleep(0.1)  # 10 FPS
    
    async def _advance_stage(self):
        """Advance to next demo stage."""
        # Clear all effects
        self.effects_engine.clear_effects()
        self.particle_engine.clear_particles()
        
        # Advance stage
        self.demo_stage = (self.demo_stage + 1) % len(self.stages)
        stage_name, _ = self.stages[self.demo_stage]
        
        print(f"Demo Stage {self.demo_stage + 1}: {stage_name}")
    
    # Demo stage implementations
    
    async def demo_rainbow(self):
        """Demonstrate rainbow cycle effect."""
        # Add rainbow effect if not already active
        if not any(isinstance(effect, RainbowCycleEffect) for effect in self.effects_engine.active_effects):
            rainbow = RainbowCycleEffect(speed=1.5)
            self.effects_engine.add_effect(rainbow)
    
    async def demo_sparkle(self):
        """Demonstrate sparkle effect."""
        # Add sparkle effect
        if not any(isinstance(effect, SparkleEffect) for effect in self.effects_engine.active_effects):
            sparkle = SparkleEffect(intensity=4)
            self.effects_engine.add_effect(sparkle)
        
        # Add some base color
        await self._fill_with_gradient()
    
    async def demo_pulse(self):
        """Demonstrate pulse effect."""
        # Fill with color first
        await self._fill_with_color(0x004080)  # Dark blue
        
        # Add pulse effect
        if not any(isinstance(effect, PulseEffect) for effect in self.effects_engine.active_effects):
            pulse = PulseEffect(speed=2.0, min_brightness=0.3, max_brightness=1.0)
            self.effects_engine.add_effect(pulse)
    
    async def demo_edge_glow(self):
        """Demonstrate edge glow effect."""
        # Fill center with dark color
        await self._fill_center_area(0x001122)
        
        # Add edge glow
        if not any(isinstance(effect, EdgeGlowEffect) for effect in self.effects_engine.active_effects):
            glow = EdgeGlowEffect(color=0x00FFFF)
            self.effects_engine.add_effect(glow)
    
    async def demo_corner_flash(self):
        """Demonstrate corner flash effect."""
        # Fill with dark background
        await self._fill_with_color(0x202020)
        
        # Add corner flash
        if not any(isinstance(effect, CornerFlashEffect) for effect in self.effects_engine.active_effects):
            flash = CornerFlashEffect(color=0xFFFF00, flash_duration=0.3, interval=1.5)
            self.effects_engine.add_effect(flash)
    
    async def demo_rain(self):
        """Demonstrate rain particle effect."""
        # Add occasional raindrops
        import random
        
        if random.random() < 0.3:  # 30% chance per frame
            x = random.randint(0, self.display.width - 1)
            raindrop = RainDrop(x, -2, speed=15.0, color=0x4080FF)
            self.particle_engine.add_particle(raindrop)
        
        # Dark sky background
        await self._fill_with_color(0x001133)
    
    async def demo_fire(self):
        """Demonstrate fire ember effect."""
        import random
        
        # Spawn embers from bottom
        if random.random() < 0.4:  # 40% chance per frame
            x = random.randint(2, self.display.width - 3)
            ember = Ember(x, self.display.height, speed=8.0, drift=3.0, lifetime=3.0)
            self.particle_engine.add_particle(ember)
        
        # Dark background
        await self._fill_with_color(0x110000)
    
    async def demo_snow(self):
        """Demonstrate snow particle effect."""
        import random
        
        # Spawn snowflakes from top
        if random.random() < 0.2:  # 20% chance per frame
            x = random.randint(0, self.display.width - 1)
            snowflake = Snow(x, -1, speed=4.0, sway=2.0)
            self.particle_engine.add_particle(snowflake)
        
        # Gray sky background
        await self._fill_with_color(0x333344)
    
    async def demo_fade_transition(self):
        """Demonstrate fade transition."""
        # This is a simplified demo - normally you'd transition between actual content
        import time
        
        cycle_time = time.time() % 4.0  # 4 second cycle
        
        if cycle_time < 2.0:
            # First state
            await self._fill_with_color(0xFF0000)  # Red
        else:
            # Second state  
            await self._fill_with_color(0x0000FF)  # Blue
        
        # Simulate fade by varying brightness
        progress = (cycle_time % 2.0) / 2.0
        if hasattr(self.display, 'brightness'):
            if cycle_time < 2.0:
                self.display.brightness = 1.0 - (progress * 0.5)
            else:
                self.display.brightness = 0.5 + (progress * 0.5)
    
    async def demo_wipe_transition(self):
        """Demonstrate wipe transition."""
        import time
        
        cycle_time = time.time() % 3.0
        progress = (cycle_time % 1.5) / 1.5
        
        # Wipe from left to right
        split_x = int(progress * self.display.width)
        
        for y in range(self.display.height):
            for x in range(self.display.width):
                if x < split_x:
                    # New content (green gradient)
                    color = (0 << 16) | (int((x / self.display.width) * 255) << 8) | 0
                else:
                    # Old content (red gradient)
                    color = (int((x / self.display.width) * 255) << 16) | (0 << 8) | 0
                
                await self.display.set_pixel(x, y, color)
    
    async def demo_slide_transition(self):
        """Demonstrate slide transition."""
        import time
        
        cycle_time = time.time() % 4.0
        progress = (cycle_time % 2.0) / 2.0
        
        # Slide effect
        offset = int(progress * self.display.width) - self.display.width
        
        for y in range(self.display.height):
            for x in range(self.display.width):
                # Sliding content
                source_x = x - offset
                if 0 <= source_x < self.display.width:
                    # Blue to cyan gradient
                    color = (0 << 16) | (int((source_x / self.display.width) * 255) << 8) | 255
                    await self.display.set_pixel(x, y, color)
    
    async def demo_combined(self):
        """Demonstrate multiple effects combined."""
        # Base rainbow cycle
        if not any(isinstance(effect, RainbowCycleEffect) for effect in self.effects_engine.active_effects):
            rainbow = RainbowCycleEffect(speed=0.8)
            self.effects_engine.add_effect(rainbow)
        
        # Add sparkles
        if not any(isinstance(effect, SparkleEffect) for effect in self.effects_engine.active_effects):
            sparkle = SparkleEffect(intensity=2)
            self.effects_engine.add_effect(sparkle)
        
        # Add occasional particles
        import random
        if random.random() < 0.1:
            x = random.randint(0, self.display.width - 1)
            particle_type = random.randint(0, 2)
            
            if particle_type == 0:
                sparkle_particle = Sparkle(x, random.randint(0, self.display.height - 1), 
                                         color=0xFFFFFF, lifetime=0.8)
                self.particle_engine.add_particle(sparkle_particle)
            elif particle_type == 1:
                ember = Ember(x, self.display.height - 1, speed=6.0, drift=1.0, lifetime=2.0)
                self.particle_engine.add_particle(ember)
            else:
                snow = Snow(x, -1, speed=5.0, sway=1.0)
                self.particle_engine.add_particle(snow)
    
    # Helper methods
    
    async def _fill_with_color(self, color):
        """Fill display with solid color."""
        for y in range(self.display.height):
            for x in range(self.display.width):
                await self.display.set_pixel(x, y, color)
    
    async def _fill_with_gradient(self):
        """Fill display with gradient."""
        for y in range(self.display.height):
            for x in range(self.display.width):
                r = int((x / self.display.width) * 255)
                g = int((y / self.display.height) * 255)
                b = 128
                color = (r << 16) | (g << 8) | b
                await self.display.set_pixel(x, y, color)
    
    async def _fill_center_area(self, color):
        """Fill center area leaving edges clear."""
        start_x = self.display.width // 4
        end_x = 3 * self.display.width // 4
        start_y = self.display.height // 4
        end_y = 3 * self.display.height // 4
        
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                await self.display.set_pixel(x, y, color)


def simple_effects_demo():
    """Simple effects demo using direct device approach."""
    print("SLDK Effects System Demo")
    print("=" * 40)
    print("Showing various visual effects optimized for ESP32")
    
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
    stage_names = ["Rainbow Cycle", "Sparkle Effect", "Edge Glow", "Pulsing Effect", 
                   "Rain Particles", "Fire Embers", "Snow Particles", "Fade Transition",
                   "Wipe Transition", "Slide Transition", "Combined Effects"]
    
    def update():
        """Update function called each frame."""
        nonlocal demo_stage, stage_start, sparkles
        
        current_time = time.time()
        if stage_start == 0:
            stage_start = current_time
        
        elapsed = current_time - stage_start
        
        if demo_stage == 0 and elapsed < 8:
            # Stage 1: Rainbow Cycle Effect
            device.matrix.fill(0x000000)
            offset = int(elapsed * 30)
            for y in range(device.height):
                for x in range(device.width):
                    hue = (x * 6 + y * 3 + offset) % 360
                    if hue < 60:
                        color = 0xFF0000  # Red
                    elif hue < 120:
                        color = 0xFFFF00  # Yellow  
                    elif hue < 180:
                        color = 0x00FF00  # Green
                    elif hue < 240:
                        color = 0x00FFFF  # Cyan
                    elif hue < 300:
                        color = 0x0000FF  # Blue
                    else:
                        color = 0xFF00FF  # Magenta
                    device.matrix.set_pixel(x, y, color)
                    
        elif demo_stage == 1 and elapsed < 8:
            # Stage 2: Sparkle Effect
            # Fill with dark blue background
            for y in range(device.height):
                for x in range(device.width):
                    device.matrix.set_pixel(x, y, 0x001133)
            
            # Add random sparkles
            if random.random() < 0.3:  # 30% chance per frame
                sparkles.append({
                    'x': random.randint(0, device.width - 1),
                    'y': random.randint(0, device.height - 1),
                    'life': 1.0,
                    'color': random.choice([0xFFFFFF, 0xFFFF00, 0x00FFFF])
                })
            
            # Update and draw sparkles
            for sparkle in sparkles[:]:
                sparkle['life'] -= 0.05
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
                    
        elif demo_stage == 2 and elapsed < 8:
            # Stage 3: Edge Glow Effect
            device.matrix.fill(0x001122)  # Dark center
            
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
                
        elif demo_stage == 3:
            # Stage 4: Pulsing Effect
            device.matrix.fill(0x004080)  # Base blue color
            
            # Pulse brightness
            pulse = (math.sin(elapsed * 3) + 1) / 2  # 0 to 1
            
            # Apply pulse to center area
            for y in range(8, 24):
                for x in range(16, 48):
                    r = int(((0x004080 >> 16) & 0xFF) * pulse)
                    g = int(((0x004080 >> 8) & 0xFF) * pulse)
                    b = int((0x004080 & 0xFF) * pulse)
                    pulse_color = (r << 16) | (g << 8) | b
                    device.matrix.set_pixel(x, y, pulse_color)
                    
        elif demo_stage == 4:
            # Stage 5: Rain Particles
            device.matrix.fill(0x001144)  # Dark sky
            
            # Add rain drops from top
            if random.random() < 0.4:
                sparkles.append({
                    'x': random.randint(0, device.width - 1),
                    'y': -1,
                    'vy': random.uniform(15, 25),
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
                    
        elif demo_stage == 5:
            # Stage 6: Fire Embers
            device.matrix.fill(0x110000)  # Dark red background
            
            # Add embers from bottom
            if random.random() < 0.3:
                sparkles.append({
                    'x': random.randint(5, device.width - 5),
                    'y': device.height,
                    'vy': random.uniform(-8, -15),
                    'vx': random.uniform(-2, 2),
                    'life': 1.0,
                    'color': random.choice([0xFF4400, 0xFF6600, 0xFF8800]),
                    'type': 'ember'
                })
            
            # Update embers
            for ember in sparkles[:]:
                ember['x'] += ember['vx'] * 0.1
                ember['y'] += ember['vy'] * 0.1
                ember['life'] -= 0.02
                if ember['life'] <= 0 or ember['y'] < 0:
                    sparkles.remove(ember)
                else:
                    brightness = ember['life']
                    color = ember['color']
                    r = int(((color >> 16) & 0xFF) * brightness)
                    g = int(((color >> 8) & 0xFF) * brightness)
                    b = int((color & 0xFF) * brightness)
                    faded_color = (r << 16) | (g << 8) | b
                    if 0 <= int(ember['x']) < device.width:
                        device.matrix.set_pixel(int(ember['x']), int(ember['y']), faded_color)
                        
        elif demo_stage == 6:
            # Stage 7: Snow Particles
            device.matrix.fill(0x333344)  # Gray sky
            
            # Add snowflakes from top
            if random.random() < 0.2:
                sparkles.append({
                    'x': random.randint(0, device.width - 1),
                    'y': -1,
                    'vy': random.uniform(3, 8),
                    'vx': random.uniform(-1, 1),
                    'color': 0xFFFFFF,
                    'type': 'snow'
                })
            
            # Update snowflakes
            for flake in sparkles[:]:
                flake['x'] += flake['vx'] * 0.1
                flake['y'] += flake['vy'] * 0.1
                if flake['y'] >= device.height or flake['x'] < 0 or flake['x'] >= device.width:
                    sparkles.remove(flake)
                else:
                    device.matrix.set_pixel(int(flake['x']), int(flake['y']), flake['color'])
                    
        elif demo_stage == 7:
            # Stage 8: Fade Transition
            cycle_time = elapsed % 4.0
            if cycle_time < 2.0:
                # Red state
                intensity = 1.0 - (cycle_time % 2.0) * 0.5
                color = int(255 * intensity) << 16
                device.matrix.fill(color)
            else:
                # Blue state
                intensity = 0.5 + ((cycle_time - 2.0) % 2.0) * 0.5
                color = int(255 * intensity)
                device.matrix.fill(color)
                
        elif demo_stage == 8:
            # Stage 9: Wipe Transition
            cycle_time = elapsed % 3.0
            progress = (cycle_time % 1.5) / 1.5
            split_x = int(progress * device.width)
            
            for y in range(device.height):
                for x in range(device.width):
                    if x < split_x:
                        # New content (green gradient)
                        color = (0 << 16) | (int((x / device.width) * 255) << 8) | 0
                    else:
                        # Old content (red gradient)
                        color = (int((x / device.width) * 255) << 16) | (0 << 8) | 0
                    device.matrix.set_pixel(x, y, color)
                    
        elif demo_stage == 9:
            # Stage 10: Slide Transition
            cycle_time = elapsed % 4.0
            progress = (cycle_time % 2.0) / 2.0
            offset = int(progress * device.width) - device.width
            
            for y in range(device.height):
                for x in range(device.width):
                    source_x = x - offset
                    if 0 <= source_x < device.width:
                        # Blue to cyan gradient
                        color = (0 << 16) | (int((source_x / device.width) * 255) << 8) | 255
                        device.matrix.set_pixel(x, y, color)
                    else:
                        device.matrix.set_pixel(x, y, 0x000000)
                        
        elif demo_stage == 10:
            # Stage 11: Combined Effects
            # Rainbow background + sparkles
            offset = int(elapsed * 20)
            for y in range(device.height):
                for x in range(device.width):
                    hue = (x * 4 + y * 2 + offset) % 360
                    if hue < 120:
                        color = 0x440000  # Dark red
                    elif hue < 240:
                        color = 0x004400  # Dark green
                    else:
                        color = 0x000044  # Dark blue
                    device.matrix.set_pixel(x, y, color)
            
            # Add sparkles on top
            if random.random() < 0.2:
                sparkles.append({
                    'x': random.randint(0, device.width - 1),
                    'y': random.randint(0, device.height - 1),
                    'life': 1.0,
                    'color': 0xFFFFFF,
                    'type': 'sparkle'
                })
            
            # Draw sparkles
            for sparkle in sparkles[:]:
                sparkle['life'] -= 0.03
                if sparkle['life'] <= 0:
                    sparkles.remove(sparkle)
                else:
                    brightness = sparkle['life']
                    device.matrix.set_pixel(sparkle['x'], sparkle['y'], 0xFFFFFF)
        
        # Advance stages
        stage_duration = 8
        if elapsed >= stage_duration:
            demo_stage = (demo_stage + 1) % 11  # 11 total stages now
            stage_start = current_time
            sparkles.clear()  # Clear sparkles when changing stages
            
            # Update window title with current effect name
            import pygame
            if pygame.display.get_init():
                new_title = f"SLDK Effects Demo - {stage_names[demo_stage]}"
                pygame.display.set_caption(new_title)
            
            print(f"Effects Demo Stage {demo_stage + 1}: {stage_names[demo_stage]}")
        
        return True
    
    # Use device.run() 
    device.run(update_callback=update, title="SLDK Effects System Demo")


def main():
    """Main entry point."""
    simple_effects_demo()


if __name__ == "__main__":
    main()