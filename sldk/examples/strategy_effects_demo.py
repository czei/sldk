"""Demo of the new SLDK strategy-based effects system.

Demonstrates how to use the new strategy-based effects with content classes
to create engaging display animations.
"""

import asyncio
import time
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import SLDK components
from sldk.display.simulator import SimulatorDisplay
from sldk.display.manager import DisplayManager
from sldk.content_classes import create_splash, create_text, create_scrolling_text, create_alert
from sldk.effects import RevealEffect, FadeInEffect, SlideInEffect, PulseEffect, FlashEffect


async def demo_reveal_effects():
    """Demonstrate reveal effects with splash content."""
    print("Demo: Reveal Effects")
    
    # Create display and manager
    display = SimulatorDisplay(width=64, height=32)
    manager = DisplayManager(display)
    
    await manager.start()
    await display.create_window("SLDK Effects Demo - Reveal")
    
    try:
        # Demo different reveal directions
        reveal_demos = [
            ("THEME PARK", RevealEffect(duration=2.0, direction='right')),
            ("WAITS", RevealEffect(duration=2.0, direction='left')),
            ("SYSTEM", RevealEffect(duration=2.0, direction='down')),
            ("READY", RevealEffect(duration=2.0, direction='up')),
        ]
        
        for text, effect in reveal_demos:
            # Create splash content with reveal effect
            content = create_splash(text, duration=4.0).with_effect(effect)
            
            # Add to display manager
            manager.add_display_item(content.to_display_item())
            
            # Process until complete
            while manager.get_current_item():
                await manager.process_queue()
                await asyncio.sleep(0.1)
            
            # Brief pause between demos
            await asyncio.sleep(1)
            
    finally:
        await manager.stop()


async def demo_transition_effects():
    """Demonstrate transition effects."""
    print("Demo: Transition Effects")
    
    display = SimulatorDisplay(width=64, height=32)
    manager = DisplayManager(display)
    
    await manager.start()
    await display.create_window("SLDK Effects Demo - Transitions")
    
    try:
        # Demo different transition effects
        transitions = [
            ("FADE IN", FadeInEffect(duration=2.0)),
            ("SLIDE LEFT", SlideInEffect(duration=2.0, direction='left')),
            ("SLIDE RIGHT", SlideInEffect(duration=2.0, direction='right')),
            ("PULSE", PulseEffect(duration=3.0, pulses=3)),
            ("FLASH", FlashEffect(duration=2.0, flashes=4)),
        ]
        
        for text, effect in transitions:
            content = create_text(text, duration=3.0).with_effect(effect)
            manager.add_display_item(content.to_display_item())
            
            while manager.get_current_item():
                await manager.process_queue()
                await asyncio.sleep(0.1)
            
            await asyncio.sleep(1)
            
    finally:
        await manager.stop()


async def demo_combined_effects():
    """Demonstrate combining multiple effects."""
    print("Demo: Combined Effects")
    
    display = SimulatorDisplay(width=64, height=32)
    manager = DisplayManager(display)
    
    await manager.start()
    await display.create_window("SLDK Effects Demo - Combined")
    
    try:
        # Create content with multiple effects
        splash = create_splash("SLDK DEMO", duration=6.0).with_effects([
            RevealEffect(duration=2.0, direction='right'),
            PulseEffect(duration=2.0, pulses=2)
        ])
        
        manager.add_display_item(splash.to_display_item())
        
        while manager.get_current_item():
            await manager.process_queue()
            await asyncio.sleep(0.1)
        
        # Scrolling text with fade in
        scrolling = create_scrolling_text(
            "This is a scrolling message with fade in effect!", 
            duration=8.0
        ).with_effect(FadeInEffect(duration=1.5))
        
        manager.add_display_item(scrolling.to_display_item())
        
        while manager.get_current_item():
            await manager.process_queue()
            await asyncio.sleep(0.1)
        
        # Alert with flash effect
        alert = create_alert("SYSTEM ALERT", duration=4.0).with_effect(
            FlashEffect(duration=3.0, flashes=5)
        )
        
        manager.add_display_item(alert.to_display_item())
        
        while manager.get_current_item():
            await manager.process_queue()
            await asyncio.sleep(0.1)
            
    finally:
        await manager.stop()


async def demo_theme_park_style():
    """Demonstrate Theme Park style content with effects."""
    print("Demo: Theme Park Style")
    
    display = SimulatorDisplay(width=64, height=32)
    manager = DisplayManager(display)
    
    await manager.start()
    await display.create_window("SLDK Effects Demo - Theme Park")
    
    try:
        # Opening splash with reveal (This is the exact pattern the user requested!)
        opening = create_splash("THEME PARK WAITS", duration=4.0).with_effect(
            RevealEffect(duration=2.0, direction='right', pause_at_end=2.0)
        )
        manager.add_display_item(opening.to_display_item())
        
        while manager.get_current_item():
            await manager.process_queue()
            await asyncio.sleep(0.1)
        
        # System status with fade
        status = create_text("System Online", color=0x00FF00, duration=3.0).with_effect(
            FadeInEffect(duration=1.0)
        )
        manager.add_display_item(status.to_display_item())
        
        while manager.get_current_item():
            await manager.process_queue()
            await asyncio.sleep(0.1)
        
        # Loading message with pulse
        loading = create_text("Loading Wait Times...", color=0xFFFF00, duration=4.0).with_effect(
            PulseEffect(duration=3.0, pulses=3)
        )
        manager.add_display_item(loading.to_display_item())
        
        while manager.get_current_item():
            await manager.process_queue()
            await asyncio.sleep(0.1)
        
        # Ready message with slide in
        ready = create_text("Ready!", color=0x00FF00, duration=3.0).with_effect(
            SlideInEffect(duration=1.5, direction='up')
        )
        manager.add_display_item(ready.to_display_item())
        
        while manager.get_current_item():
            await manager.process_queue()
            await asyncio.sleep(0.1)
            
    finally:
        await manager.stop()


async def demo_api_showcase():
    """Demonstrate the exact API pattern the user requested."""
    print("Demo: API Showcase - Option A Pattern")
    print("Demonstrating: SplashContent('THEME PARK WAITS').with_effect(RevealEffect())")
    
    display = SimulatorDisplay(width=64, height=32)
    manager = DisplayManager(display)
    
    await manager.start()
    await display.create_window("SLDK API Showcase")
    
    try:
        # The exact pattern requested by the user:
        # content_queue.add_content(
        #     SplashContent("THEME PARK WAITS").with_effect(RevealEffect())
        # )
        
        # Create the splash content with reveal effect using the exact pattern
        splash_with_reveal = create_splash("THEME PARK WAITS").with_effect(RevealEffect())
        
        # Add to the display manager (equivalent to content_queue.add_content)
        manager.add_display_item(splash_with_reveal.to_display_item())
        
        print("Added: SplashContent('THEME PARK WAITS').with_effect(RevealEffect())")
        
        # Process the queue until the item is complete
        while manager.get_current_item():
            await manager.process_queue()
            await asyncio.sleep(0.1)
        
        # Demonstrate chaining multiple effects
        multi_effect_splash = create_splash("MULTI EFFECTS").with_effects([
            RevealEffect(duration=1.5),
            PulseEffect(duration=2.0, pulses=2)
        ])
        
        manager.add_display_item(multi_effect_splash.to_display_item())
        
        print("Added: SplashContent('MULTI EFFECTS').with_effects([RevealEffect(), PulseEffect()])")
        
        while manager.get_current_item():
            await manager.process_queue()
            await asyncio.sleep(0.1)
            
    finally:
        await manager.stop()


def simple_strategy_effects_demo():
    """Simple strategy effects demo using direct device approach."""
    print("SLDK Strategy Effects Demo")
    print("=" * 40)
    print("Demonstrating strategy-based effects concepts")
    
    # Import device directly
    from sldk.simulator.devices import MatrixPortalS3
    import time
    import math
    
    # Create device
    device = MatrixPortalS3()
    device.initialize()
    
    # Demo state
    demo_stage = 0
    stage_start = 0
    stage_names = ["API Showcase", "Reveal Effects", "Transition Effects", 
                   "Combined Effects", "Theme Park Style"]
    
    def update():
        """Update function called each frame."""
        nonlocal demo_stage, stage_start
        
        current_time = time.time()
        if stage_start == 0:
            stage_start = current_time
        
        elapsed = current_time - stage_start
        
        # Clear to black
        device.matrix.fill(0x000000)
        
        if demo_stage == 0 and elapsed < 6:
            # Stage 1: API Showcase - "THEME PARK WAITS" with reveal
            text = "THEME PARK WAITS"
            reveal_duration = 3.0
            
            if elapsed < reveal_duration:
                # Reveal from left to right
                progress = elapsed / reveal_duration
                reveal_chars = int(len(text) * progress)
                
                for i, char in enumerate(text[:reveal_chars]):
                    char_x = 1 + i * 3
                    if char_x < device.width:
                        device.matrix.set_pixel(char_x, 12, 0x00FF00)
                        device.matrix.set_pixel(char_x, 13, 0x00FF00)
                        device.matrix.set_pixel(char_x, 14, 0x00FF00)
            else:
                # Fully revealed
                for i, char in enumerate(text):
                    char_x = 1 + i * 3
                    if char_x < device.width:
                        device.matrix.set_pixel(char_x, 12, 0x00FF00)
                        device.matrix.set_pixel(char_x, 13, 0x00FF00)
                        device.matrix.set_pixel(char_x, 14, 0x00FF00)
                        
        elif demo_stage == 1 and elapsed < 6:
            # Stage 2: Reveal Effects - different directions
            texts = ["RIGHT", "LEFT", "DOWN", "UP"]
            text_index = int(elapsed / 1.5) % len(texts)
            text = texts[text_index]
            
            # Different reveal directions
            if text_index == 0:  # Right reveal
                progress = (elapsed % 1.5) / 1.5
                reveal_chars = int(len(text) * progress)
                for i in range(reveal_chars):
                    device.matrix.set_pixel(10 + i * 6, 12, 0xFF0000)
            elif text_index == 1:  # Left reveal  
                progress = (elapsed % 1.5) / 1.5
                reveal_chars = int(len(text) * progress)
                for i in range(reveal_chars):
                    char_x = 40 - i * 6
                    if char_x >= 0:
                        device.matrix.set_pixel(char_x, 12, 0x00FF00)
            # Add other directions...
                        
        elif demo_stage == 2 and elapsed < 6:
            # Stage 3: Transition Effects - fade, slide, pulse
            effect_type = int(elapsed / 2) % 3
            
            if effect_type == 0:  # Fade in
                progress = (elapsed % 2) / 2
                intensity = int(255 * progress)
                color = (intensity << 16) | (intensity << 8) | intensity
                
                # Draw "FADE" with varying intensity
                for i in range(4):
                    device.matrix.set_pixel(20 + i * 6, 12, color)
                    
            elif effect_type == 1:  # Slide in
                progress = (elapsed % 2) / 2
                slide_x = int((device.width + 24) * progress) - 24
                
                for i in range(5):  # "SLIDE"
                    char_x = slide_x + i * 4
                    if 0 <= char_x < device.width:
                        device.matrix.set_pixel(char_x, 12, 0x00FFFF)
                        
            else:  # Pulse
                pulse_intensity = (math.sin(elapsed * 6) + 1) / 2
                color_val = int(255 * pulse_intensity)
                color = (color_val << 8)  # Green pulse
                
                for i in range(5):  # "PULSE"
                    device.matrix.set_pixel(15 + i * 6, 12, color)
                    
        elif demo_stage == 3 and elapsed < 6:
            # Stage 4: Combined Effects - reveal + pulse
            text = "COMBINED"
            reveal_duration = 2.0
            
            if elapsed < reveal_duration:
                # Reveal phase
                progress = elapsed / reveal_duration
                reveal_chars = int(len(text) * progress)
                
                for i in range(reveal_chars):
                    device.matrix.set_pixel(5 + i * 6, 12, 0xFFFF00)
            else:
                # Pulse phase
                pulse_intensity = (math.sin((elapsed - reveal_duration) * 4) + 1) / 2
                color_val = int(255 * pulse_intensity)
                color = (color_val << 16) | (color_val << 8)  # Yellow pulse
                
                for i in range(len(text)):
                    device.matrix.set_pixel(5 + i * 6, 12, color)
                    
        elif demo_stage == 4:
            # Stage 5: Theme Park Style - sequence of messages
            sequence_time = elapsed % 12
            
            if sequence_time < 3:
                # "THEME PARK WAITS" reveal
                text = "THEME PARK"
                progress = sequence_time / 3
                reveal_chars = int(len(text) * progress)
                
                for i in range(reveal_chars):
                    char_x = 2 + i * 5
                    if char_x < device.width:
                        device.matrix.set_pixel(char_x, 10, 0x00FF00)
                        
            elif sequence_time < 6:
                # "System Online" fade in
                progress = (sequence_time - 3) / 3
                intensity = int(255 * progress)
                color = (0 << 16) | (intensity << 8) | (0 << 8)
                
                text = "ONLINE"
                for i in range(len(text)):
                    device.matrix.set_pixel(10 + i * 6, 15, color)
                    
            elif sequence_time < 9:
                # "Loading..." pulse
                pulse_intensity = (math.sin((sequence_time - 6) * 3) + 1) / 2
                color_val = int(255 * pulse_intensity)
                color = (color_val << 16) | (color_val << 8)
                
                text = "LOADING"
                for i in range(len(text)):
                    device.matrix.set_pixel(5 + i * 7, 12, color)
                    
            else:
                # "Ready!" slide in
                progress = (sequence_time - 9) / 3
                slide_y = int(device.height * (1 - progress))
                
                if slide_y < device.height:
                    text = "READY!"
                    for i in range(len(text)):
                        device.matrix.set_pixel(15 + i * 6, slide_y, 0x00FF00)
        
        # Advance stages
        stage_duration = 6
        if elapsed >= stage_duration:
            demo_stage = (demo_stage + 1) % 5  # 5 total stages
            stage_start = current_time
            
            # Update window title with current effect name
            import pygame
            if pygame.display.get_init():
                new_title = f"SLDK Strategy Effects Demo - {stage_names[demo_stage]}"
                pygame.display.set_caption(new_title)
            
            print(f"Strategy Demo Stage {demo_stage + 1}: {stage_names[demo_stage]}")
        
        return True
    
    # Use device.run() 
    device.run(update_callback=update, title="SLDK Strategy Effects Demo")


def main():
    """Main entry point."""
    simple_strategy_effects_demo()


if __name__ == "__main__":
    main()