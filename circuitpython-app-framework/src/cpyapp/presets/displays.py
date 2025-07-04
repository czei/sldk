"""
Data Display presets for financial, weather, and news information.

This module provides presets for displaying various types of data
like stock prices, cryptocurrency, weather, news, and transit info.
"""
from .base import ConfigurablePreset
from ..utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")


class StockTrackerPreset(ConfigurablePreset):
    """Display stock market prices and changes."""
    
    def __init__(self):
        super().__init__("stock_tracker", category="financial")
        
        self._config.update({
            'data_source': {
                'type': 'stock',
                'symbols': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA'],
                'api_key': None,  # User must provide
                'cache_ttl': 300  # 5 minute cache
            },
            'style': {
                'name': 'financial',
                'theme': 'stock_market',
                'colors': {
                    'positive': 'Green',
                    'negative': 'Red',
                    'neutral': 'White',
                    'background': 'Black'
                },
                'scroll_speed': 0.04,
                'show_arrows': True,  # ↑↓ for price changes
                'format': '{symbol}: ${price} {change_pct}%'
            },
            'board': 'auto',
            'metadata': {
                'name': 'stock_tracker',
                'description': 'Real-time stock market prices and changes',
                'tags': ['finance', 'stocks', 'market', 'investing']
            }
        })
        
        self.parameters = {
            'symbols': {
                'type': 'list',
                'default': ['AAPL', 'GOOGL', 'MSFT'],
                'description': 'Stock symbols to track'
            },
            'api_key': {
                'type': 'str',
                'required': True,
                'description': 'API key for stock data service'
            },
            'show_volume': {
                'type': 'bool',
                'default': False,
                'description': 'Show trading volume'
            }
        }
        
    def get_requirements(self):
        """Get requirements for this preset."""
        return {
            'api_key': 'Stock market API key required (e.g., Alpha Vantage, IEX Cloud)',
            'network': 'Internet connection required'
        }


class CryptoTrackerPreset(ConfigurablePreset):
    """Display cryptocurrency prices."""
    
    def __init__(self):
        super().__init__("crypto_tracker", category="financial")
        
        self._config.update({
            'data_source': {
                'type': 'url',
                'url': 'https://api.coinbase.com/v2/exchange-rates?currency=USD',
                'parser': 'json_path',
                'parser_config': {
                    'paths': {
                        'BTC': 'data.rates.BTC',
                        'ETH': 'data.rates.ETH',
                        'DOGE': 'data.rates.DOGE'
                    },
                    'format': '{name}: ${value}'
                },
                'cache_ttl': 60  # 1 minute cache
            },
            'style': {
                'name': 'crypto',
                'theme': 'digital',
                'colors': {
                    'BTC': 'Orange',
                    'ETH': 'Purple',
                    'default': 'Cyan',
                    'background': 'Black'
                },
                'scroll_speed': 0.035,
                'show_sparklines': True
            },
            'metadata': {
                'name': 'crypto_tracker',
                'description': 'Cryptocurrency prices in real-time',
                'tags': ['crypto', 'bitcoin', 'ethereum', 'finance']
            }
        })
        
        self.parameters = {
            'currencies': {
                'type': 'list',
                'default': ['BTC', 'ETH', 'DOGE'],
                'description': 'Cryptocurrencies to track'
            },
            'vs_currency': {
                'type': 'str',
                'default': 'USD',
                'description': 'Base currency for prices'
            }
        }


class WeatherStationPreset(ConfigurablePreset):
    """Display local weather information."""
    
    def __init__(self):
        super().__init__("weather_station", category="information")
        
        self._config.update({
            'data_source': {
                'type': 'weather',
                'location': None,  # User must provide
                'api_key': None,   # User must provide
                'units': 'imperial',
                'cache_ttl': 600   # 10 minute cache
            },
            'style': {
                'name': 'weather',
                'theme': 'climate',
                'colors': {
                    'sunny': 'Yellow',
                    'cloudy': 'Gray',
                    'rainy': 'Blue',
                    'snowy': 'White',
                    'temperature': 'Orange',
                    'background': 'DarkBlue'
                },
                'scroll_speed': 0.05,
                'show_icons': True,
                'format': '{temp}°F {condition} | {humidity}% humidity'
            },
            'metadata': {
                'name': 'weather_station',
                'description': 'Local weather conditions and forecast',
                'tags': ['weather', 'temperature', 'forecast', 'climate']
            }
        })
        
        self.parameters = {
            'location': {
                'type': 'str',
                'required': True,
                'description': 'City name or coordinates'
            },
            'api_key': {
                'type': 'str', 
                'required': True,
                'description': 'OpenWeatherMap API key'
            },
            'units': {
                'type': 'str',
                'default': 'imperial',
                'choices': ['imperial', 'metric'],
                'description': 'Temperature units'
            },
            'show_forecast': {
                'type': 'bool',
                'default': True,
                'description': 'Show 5-day forecast'
            }
        }
        
    def get_requirements(self):
        """Get requirements for this preset."""
        return {
            'api_key': 'OpenWeatherMap API key required',
            'location': 'City name or coordinates required',
            'network': 'Internet connection required'
        }


class NewsTickerPreset(ConfigurablePreset):
    """Display news headlines from RSS feeds."""
    
    def __init__(self):
        super().__init__("news_ticker", category="information")
        
        self._config.update({
            'data_source': {
                'type': 'url',
                'url': 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
                'parser': 'rss',
                'parser_config': {
                    'max_items': 10,
                    'format': '{title}'
                },
                'cache_ttl': 900  # 15 minute cache
            },
            'style': {
                'name': 'news',
                'theme': 'newspaper',
                'colors': {
                    'headline': 'White',
                    'breaking': 'Red',
                    'category': 'Yellow',
                    'background': 'Black'
                },
                'scroll_speed': 0.04,
                'separator': ' • '
            },
            'metadata': {
                'name': 'news_ticker',
                'description': 'Latest news headlines from major sources',
                'tags': ['news', 'headlines', 'current_events', 'rss']
            }
        })
        
        self.parameters = {
            'feed_url': {
                'type': 'str',
                'default': 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
                'description': 'RSS feed URL'
            },
            'max_items': {
                'type': 'int',
                'default': 10,
                'description': 'Maximum number of headlines'
            },
            'categories': {
                'type': 'list',
                'default': ['World', 'Technology', 'Business'],
                'description': 'News categories to include'
            }
        }


class SportsScoresPreset(ConfigurablePreset):
    """Display live sports scores."""
    
    def __init__(self):
        super().__init__("sports_scores", category="entertainment")
        
        self._config.update({
            'data_source': {
                'type': 'url',
                'url': 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard',
                'parser': 'json_path',
                'parser_config': {
                    'path': 'events',
                    'format': '{name}: {score}'
                },
                'cache_ttl': 60  # 1 minute cache during games
            },
            'style': {
                'name': 'sports',
                'theme': 'scoreboard',
                'colors': {
                    'home_team': 'Blue',
                    'away_team': 'Red',
                    'score': 'Yellow',
                    'final': 'Green',
                    'live': 'Orange',
                    'background': 'Black'
                },
                'scroll_speed': 0.045,
                'show_quarter': True
            },
            'metadata': {
                'name': 'sports_scores',
                'description': 'Live sports scores and updates',
                'tags': ['sports', 'scores', 'live', 'games']
            }
        })
        
        self.parameters = {
            'sport': {
                'type': 'str',
                'default': 'nfl',
                'choices': ['nfl', 'nba', 'mlb', 'nhl', 'soccer'],
                'description': 'Sport to track'
            },
            'teams': {
                'type': 'list',
                'default': [],
                'description': 'Specific teams to follow (empty for all)'
            }
        }


class TransitTrackerPreset(ConfigurablePreset):
    """Display public transit arrival times."""
    
    def __init__(self):
        super().__init__("transit_tracker", category="transportation")
        
        self._config.update({
            'data_source': {
                'type': 'function',
                'function': self._get_transit_data,  # Would need implementation
                'cache_ttl': 30  # 30 second cache
            },
            'style': {
                'name': 'transit',
                'theme': 'metro',
                'colors': {
                    'bus': 'Blue',
                    'train': 'Red',
                    'subway': 'Orange',
                    'arriving': 'Green',
                    'delayed': 'Yellow',
                    'background': 'Black'
                },
                'scroll_speed': 0.04,
                'show_route_colors': True
            },
            'metadata': {
                'name': 'transit_tracker',
                'description': 'Real-time public transit arrivals',
                'tags': ['transit', 'bus', 'train', 'transportation']
            }
        })
        
        self.parameters = {
            'agency': {
                'type': 'str',
                'required': True,
                'description': 'Transit agency (e.g., BART, MTA, CTA)'
            },
            'stops': {
                'type': 'list',
                'required': True,
                'description': 'Stop IDs to monitor'
            },
            'api_key': {
                'type': 'str',
                'description': 'API key if required by agency'
            }
        }
        
    def _get_transit_data(self):
        """Placeholder for transit data fetching."""
        # This would need actual implementation based on transit APIs
        return "Next Bus: 5 min | Train: 12 min"
        
    def get_requirements(self):
        """Get requirements for this preset."""
        return {
            'agency': 'Transit agency must be specified',
            'stops': 'Stop IDs must be provided',
            'api_key': 'May be required depending on agency',
            'network': 'Internet connection required'
        }


# Registry of all display presets
DISPLAY_PRESETS = {
    'stock_tracker': StockTrackerPreset,
    'crypto_tracker': CryptoTrackerPreset,
    'weather_station': WeatherStationPreset,
    'news_ticker': NewsTickerPreset,
    'sports_scores': SportsScoresPreset,
    'transit_tracker': TransitTrackerPreset
}


def get_display_preset(name):
    """
    Get a display preset by name.
    
    Args:
        name: Preset name
        
    Returns:
        Preset instance or None
    """
    preset_class = DISPLAY_PRESETS.get(name)
    if preset_class:
        return preset_class()
    return None