"""
Weather Alerts Plugin

This plugin adds weather alert monitoring and display capabilities
to the weather display application.
"""
from cpyapp.core.plugin import Plugin
from cpyapp.utils.error_handler import ErrorHandler
from cpyapp.styles.colors import RGB_COLORS

# Initialize logger
logger = ErrorHandler("error_log")


class WeatherAlertsPlugin(Plugin):
    """
    Plugin for displaying weather alerts and warnings.
    
    This plugin monitors for severe weather alerts and displays
    them prominently on the LED matrix.
    """
    
    def __init__(self, app):
        """Initialize weather alerts plugin."""
        super().__init__(app, "weather_alerts")
        
        # Alert configuration
        self.alert_types = {
            'tornado': {'color': RGB_COLORS['red'], 'priority': 10, 'flash': True},
            'severe_thunderstorm': {'color': RGB_COLORS['orange'], 'priority': 8, 'flash': True},
            'flood': {'color': RGB_COLORS['blue'], 'priority': 7, 'flash': False},
            'winter_storm': {'color': RGB_COLORS['cyan'], 'priority': 6, 'flash': False},
            'heat': {'color': RGB_COLORS['red'], 'priority': 5, 'flash': False},
            'wind': {'color': RGB_COLORS['yellow'], 'priority': 4, 'flash': False},
            'fog': {'color': RGB_COLORS['gray'], 'priority': 3, 'flash': False}
        }
        
        self.active_alerts = []
        self.last_check = 0
        self.check_interval = 300  # Check every 5 minutes
        
    def on_start(self):
        """Initialize alert monitoring."""
        logger.info("Weather alerts plugin started")
        self.check_alerts()
        
    def on_update(self):
        """Check for new alerts periodically."""
        import time
        current_time = time.monotonic()
        
        if current_time - self.last_check > self.check_interval:
            self.check_alerts()
            self.last_check = current_time
            
    def check_alerts(self):
        """Check for weather alerts from API."""
        # In a real implementation, this would fetch alerts from weather API
        # For demo, we'll use mock data
        
        # Example alert structure
        mock_alerts = []
        
        # Simulate random alerts for demo
        import random
        if random.random() < 0.1:  # 10% chance of alert
            mock_alerts.append({
                'type': 'heat',
                'title': 'Heat Advisory',
                'description': 'High temperatures expected',
                'start': 'Today 12PM',
                'end': 'Today 8PM'
            })
            
        self.active_alerts = mock_alerts
        
        if self.active_alerts:
            self.display_alerts()
            
    def display_alerts(self):
        """Display active weather alerts."""
        for alert in self.active_alerts:
            alert_type = alert.get('type', 'unknown')
            config = self.alert_types.get(alert_type, {})
            
            # Create alert message
            alert_msg = {
                'text': f"⚠️ {alert['title']}",
                'color': config.get('color', RGB_COLORS['yellow']),
                'priority': config.get('priority', 5),
                'delay': 3
            }
            
            # Add to message queue with high priority
            if hasattr(self.app, 'add_priority_message'):
                self.app.add_priority_message(alert_msg)
            else:
                # Fallback to regular message
                logger.warning("Priority message queue not available")
                
    def format_alert_details(self, alert):
        """Format detailed alert information."""
        messages = []
        
        # Alert title with warning icon
        messages.append({
            'text': f"⚠️ {alert['title']} ⚠️",
            'color': self.alert_types.get(alert['type'], {}).get('color', RGB_COLORS['yellow']),
            'delay': 3
        })
        
        # Alert timing
        if 'start' in alert and 'end' in alert:
            messages.append({
                'text': f"From {alert['start']} to {alert['end']}",
                'color': RGB_COLORS['white'],
                'delay': 2
            })
            
        # Alert description
        messages.append({
            'text': alert.get('description', ''),
            'color': RGB_COLORS['white'],
            'delay': 2.5
        })
        
        # Safety recommendations
        recommendations = self.get_safety_recommendations(alert['type'])
        for rec in recommendations:
            messages.append({
                'text': f"• {rec}",
                'color': RGB_COLORS['yellow'],
                'delay': 2
            })
            
        return messages
        
    def get_safety_recommendations(self, alert_type):
        """Get safety recommendations for alert type."""
        recommendations = {
            'tornado': [
                "Seek shelter immediately",
                "Move to interior room",
                "Stay away from windows"
            ],
            'severe_thunderstorm': [
                "Stay indoors",
                "Avoid metal objects",
                "Unplug electronics"
            ],
            'flood': [
                "Avoid low areas",
                "Don't drive through water",
                "Move to higher ground"
            ],
            'heat': [
                "Stay hydrated",
                "Limit outdoor activity",
                "Take frequent breaks"
            ],
            'winter_storm': [
                "Stay indoors",
                "Dress warmly",
                "Check heating system"
            ]
        }
        
        return recommendations.get(alert_type, ["Stay informed", "Follow local guidance"])
        
    def on_stop(self):
        """Clean up when plugin stops."""
        self.active_alerts = []
        logger.info("Weather alerts plugin stopped")


class WeatherRadarPlugin(Plugin):
    """
    Plugin for displaying weather radar information.
    
    This plugin shows animated radar imagery on the LED matrix
    (simplified for low resolution).
    """
    
    def __init__(self, app):
        """Initialize weather radar plugin."""
        super().__init__(app, "weather_radar")
        
        self.radar_frames = []
        self.current_frame = 0
        self.animation_speed = 0.5  # Seconds per frame
        self.last_frame_time = 0
        
    def on_start(self):
        """Initialize radar display."""
        logger.info("Weather radar plugin started")
        self.generate_radar_frames()
        
    def generate_radar_frames(self):
        """Generate simplified radar animation frames."""
        # In a real implementation, this would fetch radar data
        # For demo, we'll create simple animation frames
        
        # Create 5 frames of "radar sweep"
        for i in range(5):
            frame = {
                'type': 'radar',
                'data': self.create_radar_pattern(i),
                'timestamp': f"Frame {i+1}/5"
            }
            self.radar_frames.append(frame)
            
    def create_radar_pattern(self, frame_num):
        """Create a simple radar pattern for LED matrix."""
        # This would create actual radar data visualization
        # For now, return a text representation
        patterns = [
            "Clear ☀️",
            "Clouds →",
            "Rain ↗️",
            "Storm ⛈️",
            "Clearing ↘️"
        ]
        return patterns[frame_num % len(patterns)]
        
    def on_update(self):
        """Update radar animation."""
        import time
        current_time = time.monotonic()
        
        if current_time - self.last_frame_time > self.animation_speed:
            self.show_next_frame()
            self.last_frame_time = current_time
            
    def show_next_frame(self):
        """Display next radar frame."""
        if not self.radar_frames:
            return
            
        frame = self.radar_frames[self.current_frame]
        
        # Create radar message
        radar_msg = {
            'text': f"Radar: {frame['data']}",
            'color': self.get_radar_color(frame['data']),
            'delay': self.animation_speed
        }
        
        # Update display
        if hasattr(self.app, 'update_radar_display'):
            self.app.update_radar_display(radar_msg)
            
        # Move to next frame
        self.current_frame = (self.current_frame + 1) % len(self.radar_frames)
        
    def get_radar_color(self, data):
        """Get color based on radar data."""
        if 'Clear' in data:
            return RGB_COLORS['green']
        elif 'Clouds' in data:
            return RGB_COLORS['gray']
        elif 'Rain' in data:
            return RGB_COLORS['blue']
        elif 'Storm' in data:
            return RGB_COLORS['red']
        else:
            return RGB_COLORS['white']
            
    def on_stop(self):
        """Clean up radar data."""
        self.radar_frames = []
        logger.info("Weather radar plugin stopped")