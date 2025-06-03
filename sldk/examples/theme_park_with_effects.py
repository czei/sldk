#!/usr/bin/env python3
"""Theme Park app enhanced with visual effects.

Demonstrates integrating the effects system with real application content.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sldk.app import SLDKApp
from sldk.display.content import ScrollingText, StaticText
from sldk.display.enhanced_content import SparklingText, GlowingText, AnimatedBackground, RainbowText
from sldk.effects import EffectsEngine
from sldk.effects.effects import SparkleEffect, EdgeGlowEffect, PulseEffect
from sldk.effects.particles import ParticleEngine, Sparkle


class EnhancedThemeParkApp(SLDKApp):
    """Theme park app with visual effects integration."""
    
    def __init__(self):
        """Initialize enhanced theme park app."""
        super().__init__(
            enable_web=True,
            update_interval=300  # 5 minutes
        )
        
        # Effects configuration
        self.effects_enabled = True
        self.current_effect_mode = "sparkle"  # sparkle, glow, rainbow, pulse
        self.effect_modes = ["sparkle", "glow", "rainbow", "pulse", "particles"]
        self.effect_mode_index = 0
        
        # Sample theme park data
        self.park_data = {
            "Magic Kingdom": {
                "Space Mountain": 45,
                "Pirates": 25, 
                "Haunted Mansion": 30,
                "Thunder Mountain": 40
            },
            "EPCOT": {
                "Guardians": 60,
                "Test Track": 35,
                "Spaceship Earth": 15,
                "Frozen": 50
            }
        }
        
        self.current_park = "Magic Kingdom"
        self.content_index = 0
    
    async def setup(self):
        """Initialize application content."""
        print("Setting up Enhanced Theme Park App with effects...")
        
        # Create initial content with effects
        await self._create_enhanced_content()
        
        print(f"Effects enabled: {self.effects_enabled}")
        print(f"Current effect mode: {self.current_effect_mode}")
    
    async def _create_enhanced_content(self):
        """Create content with visual effects based on current mode."""
        # Clear existing content
        self.content_queue.clear()
        
        park = self.park_data[self.current_park]
        
        if self.current_effect_mode == "sparkle":
            # Sparkling text for each ride
            for ride, wait_time in park.items():
                color = self._get_wait_time_color(wait_time)
                content = SparklingText(
                    text=f"{ride}: {wait_time}min",
                    color=color,
                    sparkle_color=0xFFFFFF,
                    sparkle_intensity=3,
                    duration=4.0
                )
                self.content_queue.add_content(content)
        
        elif self.current_effect_mode == "glow":
            # Glowing text for park name
            park_title = GlowingText(
                text=self.current_park,
                text_color=0xFFFF00,
                glow_color=0x00FFFF,
                duration=3.0
            )
            await self.content_queue.add_content(park_title)
            
            # Regular text for rides
            for ride, wait_time in park.items():
                color = self._get_wait_time_color(wait_time)
                content = StaticText(f"{ride}: {wait_time}min", color=color, duration=3.0)
                self.content_queue.add_content(content)
        
        elif self.current_effect_mode == "rainbow":
            # Rainbow cycling text
            for ride, wait_time in park.items():
                content = RainbowText(
                    text=f"{ride}: {wait_time}min",
                    cycle_speed=1.5,
                    duration=4.0
                )
                self.content_queue.add_content(content)
        
        elif self.current_effect_mode == "particles":
            # Animated backgrounds with different particle types
            particle_types = ["sparkle", "rain", "snow"]
            for i, (ride, wait_time) in enumerate(park.items()):
                particle_type = particle_types[i % len(particle_types)]
                
                # Create background with particles
                background = AnimatedBackground(
                    background_color=0x001122,
                    particle_type=particle_type,
                    particle_intensity=2,
                    duration=5.0
                )
                await self.content_queue.add_content(background)
        
        else:  # pulse mode
            # Pulsing brightness effect
            for ride, wait_time in park.items():
                color = self._get_wait_time_color(wait_time)
                content = StaticText(f"{ride}: {wait_time}min", color=color, duration=4.0)
                self.content_queue.add_content(content)
    
    def _get_wait_time_color(self, wait_time):
        """Get color based on wait time.
        
        Args:
            wait_time: Wait time in minutes
            
        Returns:
            int: RGB color value
        """
        if wait_time <= 20:
            return 0x00FF00  # Green - short wait
        elif wait_time <= 40:
            return 0xFFFF00  # Yellow - medium wait
        else:
            return 0xFF0000  # Red - long wait
    
    async def update_data(self):
        """Update theme park data periodically."""
        print("Updating theme park data...")
        
        # Simulate data changes
        import random
        
        for park_name, rides in self.park_data.items():
            for ride in rides:
                # Simulate wait time changes (+/- 5 minutes)
                current_wait = rides[ride]
                change = random.randint(-5, 5)
                new_wait = max(5, min(90, current_wait + change))
                rides[ride] = new_wait
        
        # Cycle effect modes occasionally
        if random.random() < 0.3:  # 30% chance to change effect
            self.effect_mode_index = (self.effect_mode_index + 1) % len(self.effect_modes)
            self.current_effect_mode = self.effect_modes[self.effect_mode_index]
            print(f"Switched to effect mode: {self.current_effect_mode}")
        
        # Switch parks occasionally
        if random.random() < 0.2:  # 20% chance to switch park
            parks = list(self.park_data.keys())
            current_index = parks.index(self.current_park)
            self.current_park = parks[(current_index + 1) % len(parks)]
            print(f"Switched to park: {self.current_park}")
        
        # Recreate content with new data and possibly new effects
        await self._create_enhanced_content()
        
        print("Data update complete")
    
    async def create_web_server(self):
        """Create web server with effects controls."""
        try:
            from ..web import SLDKWebServer
            web_server = SLDKWebServer(app=self)
            
            # Add effects control routes
            self._add_effects_routes(web_server)
            
            return web_server
        except ImportError:
            return None
    
    def _add_effects_routes(self, web_server):
        """Add effects control routes to web server."""
        from ..web.handlers import WebHandler
        from ..web.adapters import route
        import json
        
        class EffectsHandler(WebHandler):
            def __init__(self, server, app):
                super().__init__(server)
                self.app = app
            
            @route("/effects")
            def effects_page(self, request):
                """Effects control page."""
                from ..web.templates import HTMLBuilder
                
                builder = HTMLBuilder("Theme Park Effects Control")
                builder.add_heading("Theme Park Display with Effects", 1)
                
                # Current status
                builder.add_heading("Current Status", 2)
                builder.add_paragraph(f"Park: {self.app.current_park}")
                builder.add_paragraph(f"Effect Mode: {self.app.current_effect_mode}")
                builder.add_paragraph(f"Effects Enabled: {self.app.effects_enabled}")
                
                # Effect mode controls
                builder.add_heading("Effect Controls", 2)
                
                # Mode selection form
                form = builder.add_form(action="/effects/mode", method="POST")
                form.add_label("Effect Mode:")
                mode_options = [(mode, mode.title()) for mode in self.app.effect_modes]
                form.add_select("mode", mode_options, selected=self.app.current_effect_mode)
                form.add_button("Change Mode")
                form.end_form()
                
                # Toggle effects form
                form = builder.add_form(action="/effects/toggle", method="POST")
                toggle_text = "Disable Effects" if self.app.effects_enabled else "Enable Effects"
                form.add_button(toggle_text)
                form.end_form()
                
                # Park selection form
                form = builder.add_form(action="/effects/park", method="POST")
                form.add_label("Theme Park:")
                park_options = [(park, park) for park in self.app.park_data.keys()]
                form.add_select("park", park_options, selected=self.app.current_park)
                form.add_button("Switch Park")
                form.end_form()
                
                # Current wait times
                builder.add_heading("Current Wait Times", 2)
                park_data = self.app.park_data[self.app.current_park]
                
                table_html = "<table border='1' style='border-collapse: collapse;'>"
                table_html += "<tr><th>Ride</th><th>Wait Time</th><th>Status</th></tr>"
                
                for ride, wait_time in park_data.items():
                    if wait_time <= 20:
                        status = "✓ Short"
                        color = "green"
                    elif wait_time <= 40:
                        status = "⚠ Medium"
                        color = "orange"
                    else:
                        status = "✗ Long"
                        color = "red"
                    
                    table_html += f"<tr><td>{ride}</td><td>{wait_time} min</td>"
                    table_html += f"<td style='color: {color};'>{status}</td></tr>"
                
                table_html += "</table>"
                builder.add_to_body(table_html)
                
                return self.create_response(builder.build())
            
            @route("/effects/mode", methods=["POST"])
            async def change_effect_mode(self, request):
                """Change effect mode."""
                form_data = self.parse_form_data(request)
                new_mode = form_data.get('mode', 'sparkle')
                
                if new_mode in self.app.effect_modes:
                    self.app.current_effect_mode = new_mode
                    await self.app._create_enhanced_content()
                    print(f"Effect mode changed to: {new_mode}")
                
                return self.redirect("/effects")
            
            @route("/effects/toggle", methods=["POST"])
            async def toggle_effects(self, request):
                """Toggle effects on/off."""
                self.app.effects_enabled = not self.app.effects_enabled
                await self.app._create_enhanced_content()
                
                return self.redirect("/effects")
            
            @route("/effects/park", methods=["POST"])
            async def change_park(self, request):
                """Change theme park."""
                form_data = self.parse_form_data(request)
                new_park = form_data.get('park', '')
                
                if new_park in self.app.park_data:
                    self.app.current_park = new_park
                    await self.app._create_enhanced_content()
                    print(f"Park changed to: {new_park}")
                
                return self.redirect("/effects")
        
        handler = EffectsHandler(web_server, self)
        web_server.add_handler(handler)


async def main():
    """Run the enhanced theme park app."""
    print("Enhanced Theme Park App with Visual Effects")
    print("=" * 50)
    print("Features:")
    print("✓ Real-time wait times display")
    print("✓ Visual effects (sparkles, glow, rainbow, particles)")
    print("✓ Web interface for effect control")
    print("✓ Multiple theme parks")
    print("✓ ESP32-optimized performance")
    print()
    
    app = EnhancedThemeParkApp()
    
    try:
        # Initialize the display first
        await app._initialize_display()
        
        # Create window for simulator
        if hasattr(app.display, 'create_window'):
            await app.display.create_window("Enhanced Theme Park with Effects")
            
        # For simulator, start event loop in background
        if hasattr(app.display, 'run_event_loop'):
            asyncio.create_task(app.display.run_event_loop())
        
        await app.run()
    except KeyboardInterrupt:
        print("\\nApplication stopped.")


if __name__ == "__main__":
    asyncio.run(main())