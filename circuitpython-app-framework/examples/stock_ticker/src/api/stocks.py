"""
Stock API service for fetching real-time stock data.
"""
import asyncio
import json
from cpyapp.utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")


class StockAPI:
    """API service for fetching stock data."""
    
    def __init__(self, http_client, settings_manager):
        """Initialize stock API service."""
        self.http_client = http_client
        self.settings_manager = settings_manager
        self.api_key = None
        self.stocks = {}
        
    async def initialize(self):
        """Initialize the stock API service."""
        # Get API key from secrets
        try:
            from cpyapp.utils.url_utils import load_credentials
            credentials = load_credentials()
            self.api_key = credentials.get('alpha_vantage_key', '')
            
            if not self.api_key:
                logger.error(None, "Alpha Vantage API key not found in secrets.py")
                logger.info("Please add 'alpha_vantage_key' to your secrets.py file")
                
        except Exception as e:
            logger.error(e, "Error loading API credentials")
            
    async def get_stock_prices(self):
        """
        Fetch current stock prices for configured symbols.
        
        Returns:
            Dictionary of stock data
        """
        symbols = self.settings_manager.get("symbols", ["AAPL", "GOOGL", "MSFT"])
        stock_data = {}
        
        if not self.api_key:
            # Return mock data if no API key
            logger.info("Using mock stock data (no API key)")
            return self._get_mock_data(symbols)
            
        # Fetch data for each symbol
        for symbol in symbols:
            try:
                data = await self._fetch_stock_data(symbol)
                if data:
                    stock_data[symbol] = data
            except Exception as e:
                logger.error(e, f"Error fetching data for {symbol}")
                
        return stock_data
        
    async def _fetch_stock_data(self, symbol):
        """Fetch data for a single stock symbol."""
        # Alpha Vantage Global Quote endpoint
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={self.api_key}"
        
        try:
            response = await self.http_client.get(url)
            
            if not response or response.status_code != 200:
                logger.error(None, f"Failed to fetch data for {symbol}")
                return None
                
            data = response.json()
            
            # Parse Alpha Vantage response
            if "Global Quote" in data:
                quote = data["Global Quote"]
                return {
                    'symbol': symbol,
                    'price': float(quote.get('05. price', 0)),
                    'change': float(quote.get('09. change', 0)),
                    'change_percent': quote.get('10. change percent', '0%').replace('%', ''),
                    'volume': int(quote.get('06. volume', 0))
                }
            else:
                logger.error(None, f"Unexpected API response format for {symbol}")
                return None
                
        except Exception as e:
            logger.error(e, f"Error parsing stock data for {symbol}")
            return None
            
    def _get_mock_data(self, symbols):
        """Generate mock stock data for testing."""
        import random
        
        mock_data = {}
        base_prices = {
            'AAPL': 150.0,
            'GOOGL': 2785.0,
            'MSFT': 334.0,
            'TSLA': 800.0,
            'AMZN': 3200.0
        }
        
        for symbol in symbols:
            base_price = base_prices.get(symbol, 100.0)
            change_percent = random.uniform(-5.0, 5.0)
            change = base_price * (change_percent / 100)
            price = base_price + change
            
            mock_data[symbol] = {
                'symbol': symbol,
                'price': round(price, 2),
                'change': round(change, 2),
                'change_percent': f"{change_percent:.1f}",
                'volume': random.randint(1000000, 50000000)
            }
            
        return mock_data