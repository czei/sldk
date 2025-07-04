"""
Display plugin for stock ticker.
"""
import time
from cpyapp.core.plugin import DisplayPlugin
from cpyapp.utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")


class StockTickerPlugin(DisplayPlugin):
    """Plugin for displaying stock prices."""
    
    def __init__(self):
        super().__init__("StockTicker")
        
    def get_messages(self, stock_data):
        """
        Get display messages from stock data.
        
        Args:
            stock_data: Dictionary of stock information
            
        Returns:
            List of message dictionaries
        """
        messages = []
        
        if not stock_data:
            messages.append({
                'type': 'scroll',
                'text': 'No stock data available',
                'delay': 3
            })
            return messages
            
        # Market status message
        market_status = self._get_market_status()
        messages.append({
            'type': 'static',
            'text': f"Market: {market_status}",
            'duration': 2
        })
        
        # Stock price messages
        for symbol, data in stock_data.items():
            stock_messages = self._get_stock_messages(data)
            messages.extend(stock_messages)
            
        return messages
        
    def _get_stock_messages(self, stock_info):
        """Get messages for a single stock."""
        messages = []
        
        symbol = stock_info['symbol']
        price = stock_info['price']
        change = stock_info['change']
        change_percent = stock_info['change_percent']
        
        # Format price
        if price >= 1000:
            price_str = f"${price:,.0f}"
        else:
            price_str = f"${price:.2f}"
            
        # Format change
        change_sign = "+" if float(change) >= 0 else ""
        change_str = f"{change_sign}{change:.2f}"
        
        # Stock symbol and price
        messages.append({
            'type': 'static',
            'text': f"{symbol}: {price_str}",
            'duration': 2
        })
        
        # Change information
        messages.append({
            'type': 'static', 
            'text': f"{change_str} ({change_percent}%)",
            'duration': 2
        })
        
        return messages
        
    def _get_market_status(self):
        """
        Determine if market is open based on current time.
        Simplified version - doesn't account for holidays.
        """
        import time
        
        # Get current time (this is simplified and doesn't handle timezones properly)
        current_time = time.localtime()
        weekday = current_time.tm_wday  # 0 = Monday, 6 = Sunday
        hour = current_time.tm_hour
        
        # Market is closed on weekends
        if weekday >= 5:  # Saturday or Sunday
            return "CLOSED"
            
        # Market hours: 9:30 AM to 4:00 PM EST (simplified)
        if 9 <= hour < 16:
            return "OPEN"
        else:
            return "CLOSED"
            
    def get_colors(self):
        """Get stock ticker color scheme."""
        return {
            'symbol': (255, 255, 255),       # White
            'price': (255, 255, 0),          # Yellow
            'gain': (0, 255, 0),             # Green
            'loss': (255, 0, 0),             # Red
            'market_open': (0, 255, 0),      # Green
            'market_closed': (255, 0, 0),    # Red
        }