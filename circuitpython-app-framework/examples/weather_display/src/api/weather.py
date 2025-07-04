"""
Weather API Module

This module demonstrates how to extend the weather data source
with additional functionality specific to this application.
"""
from cpyapp.data_sources.weather import WeatherDataSource
from cpyapp.utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")


class ExtendedWeatherAPI(WeatherDataSource):
    """
    Extended weather API with additional features.
    
    This class adds theme park specific weather information
    and recommendations based on weather conditions.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize extended weather API."""
        super().__init__(*args, **kwargs)
        self.theme_park_mode = kwargs.get('theme_park_mode', True)
        
    def parse_data(self, raw_data):
        """Parse weather data with additional theme park info."""
        # Get base parsed data
        data = super().parse_data(raw_data)
        
        if not data or not self.theme_park_mode:
            return data
            
        # Add theme park recommendations
        data['theme_park_rating'] = self._calculate_park_rating(data)
        data['recommendations'] = self._get_recommendations(data)
        
        return data
        
    def _calculate_park_rating(self, weather_data):
        """
        Calculate theme park weather rating.
        
        Returns:
            dict: Rating from 1-5 stars with explanation
        """
        temp = weather_data.get('temperature', 70)
        humidity = weather_data.get('humidity', 50)
        wind_speed = weather_data.get('wind_speed', 0)
        condition = weather_data.get('condition', '').lower()
        
        # Start with perfect score
        rating = 5
        reasons = []
        
        # Temperature factors
        if temp > 95:
            rating -= 2
            reasons.append("Very hot")
        elif temp > 85:
            rating -= 1
            reasons.append("Hot")
        elif temp < 50:
            rating -= 2
            reasons.append("Cold")
        elif temp < 60:
            rating -= 1
            reasons.append("Cool")
            
        # Humidity factors
        if humidity > 80:
            rating -= 1
            reasons.append("High humidity")
        elif humidity > 90:
            rating -= 2
            reasons.append("Very humid")
            
        # Wind factors
        if wind_speed > 25:
            rating -= 2
            reasons.append("Very windy")
        elif wind_speed > 15:
            rating -= 1
            reasons.append("Windy")
            
        # Weather condition factors
        if 'rain' in condition:
            if 'heavy' in condition or 'thunderstorm' in condition:
                rating -= 3
                reasons.append("Heavy rain")
            else:
                rating -= 1
                reasons.append("Light rain")
        elif 'snow' in condition:
            rating -= 3
            reasons.append("Snow")
            
        # Ensure rating stays in bounds
        rating = max(1, min(5, rating))
        
        # Generate summary
        if rating == 5:
            summary = "Perfect theme park weather!"
        elif rating >= 4:
            summary = "Great day for the parks!"
        elif rating >= 3:
            summary = "Good park weather"
        elif rating >= 2:
            summary = "Challenging conditions"
        else:
            summary = "Consider indoor activities"
            
        return {
            'stars': rating,
            'summary': summary,
            'factors': reasons
        }
        
    def _get_recommendations(self, weather_data):
        """
        Get theme park recommendations based on weather.
        
        Returns:
            list: Recommendations for park visitors
        """
        recommendations = []
        
        temp = weather_data.get('temperature', 70)
        humidity = weather_data.get('humidity', 50)
        condition = weather_data.get('condition', '').lower()
        uv_index = weather_data.get('uv_index', 0)
        
        # Temperature recommendations
        if temp > 85:
            recommendations.append("Stay hydrated! 💧")
            recommendations.append("Take frequent breaks")
            if temp > 95:
                recommendations.append("Visit water rides")
                recommendations.append("Use indoor attractions")
                
        elif temp < 60:
            recommendations.append("Bring a jacket")
            if temp < 50:
                recommendations.append("Dress warmly")
                
        # Rain recommendations
        if 'rain' in condition:
            recommendations.append("Bring rain gear ☔")
            recommendations.append("Check indoor shows")
            if 'thunderstorm' in condition:
                recommendations.append("Monitor weather alerts")
                
        # Sun protection
        if condition in ['clear', 'sunny'] and temp > 70:
            recommendations.append("Use sunscreen ☀️")
            recommendations.append("Wear a hat")
            
        # Humidity recommendations
        if humidity > 80:
            recommendations.append("Expect slower pace")
            recommendations.append("Plan rest breaks")
            
        # General tips
        if weather_data.get('theme_park_rating', {}).get('stars', 5) >= 4:
            recommendations.append("Arrive early!")
            recommendations.append("Use FastPass/Lightning Lane")
            
        return recommendations
        
    def format_for_display(self, data):
        """Format weather data with theme park info."""
        messages = super().format_for_display(data)
        
        if not self.theme_park_mode or not data:
            return messages
            
        # Add theme park rating
        rating = data.get('theme_park_rating', {})
        if rating:
            stars = '⭐' * rating.get('stars', 0)
            messages.insert(2, {
                'type': 'scroll',
                'text': f"Park Rating: {stars}",
                'delay': 2
            })
            
            messages.insert(3, {
                'type': 'scroll',
                'text': rating.get('summary', ''),
                'delay': 2
            })
            
        # Add recommendations
        recommendations = data.get('recommendations', [])
        for rec in recommendations[:3]:  # Show top 3 recommendations
            messages.append({
                'type': 'scroll',
                'text': f"Tip: {rec}",
                'delay': 1.5
            })
            
        return messages


# Preset configurations for popular theme parks
THEME_PARK_WEATHER_CONFIGS = {
    'disney_world': {
        'location': {'lat': 28.3852, 'lon': -81.5639, 'name': 'Disney World'},
        'theme_park_mode': True,
        'units': 'imperial'
    },
    'disneyland': {
        'location': {'lat': 33.8121, 'lon': -117.9190, 'name': 'Disneyland'},
        'theme_park_mode': True,
        'units': 'imperial'
    },
    'universal_orlando': {
        'location': {'lat': 28.4752, 'lon': -81.4685, 'name': 'Universal Orlando'},
        'theme_park_mode': True,
        'units': 'imperial'
    },
    'universal_hollywood': {
        'location': {'lat': 34.1381, 'lon': -118.3534, 'name': 'Universal Hollywood'},
        'theme_park_mode': True,
        'units': 'imperial'
    }
}