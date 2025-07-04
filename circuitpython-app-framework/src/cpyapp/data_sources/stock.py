"""
Stock Data Source for financial market data.

This module provides a data source for fetching stock prices and
market data from various APIs including Alpha Vantage.
"""
import json
import random
try:
    from typing import Dict, Any, Optional, List
except ImportError:
    # CircuitPython doesn't have typing
    pass

from .base import HttpDataSource
from ..utils.error_handler import ErrorHandler

# Initialize logger
logger = ErrorHandler("error_log")


class StockDataSource(HttpDataSource):
    """
    Data source for stock market data.
    
    This class provides access to stock prices and market data
    from various APIs, with Alpha Vantage as the primary source.
    """
    
    # Popular stock symbol presets
    PRESETS = {
        'tech': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META'],
        'faang': ['META', 'AAPL', 'AMZN', 'NFLX', 'GOOGL'],
        'dow': ['AAPL', 'MSFT', 'JPM', 'JNJ', 'WMT'],
        'crypto': ['BTC-USD', 'ETH-USD', 'BNB-USD'],
        'meme': ['GME', 'AMC', 'BB', 'BBBY'],
        'ev': ['TSLA', 'RIVN', 'LCID', 'F', 'GM'],
        'finance': ['JPM', 'BAC', 'WFC', 'GS', 'MS'],
    }
    
    # API providers
    PROVIDERS = {
        'alpha_vantage': {
            'base_url': 'https://www.alphavantage.co/query',
            'requires_key': True,
            'rate_limit': 5.0,  # 5 seconds between requests (free tier)
        },
        'mock': {
            'base_url': None,
            'requires_key': False,
            'rate_limit': 0.1,
        }
    }
    
    def __init__(self, symbols=None, preset=None, provider='alpha_vantage', api_key=None, **kwargs):
        """
        Initialize stock data source.
        
        Args:
            symbols: List of stock symbols or single symbol
            preset: Preset name (e.g., 'tech', 'faang')
            provider: API provider ('alpha_vantage' or 'mock')
            api_key: API key for the provider
            **kwargs: Additional arguments passed to HttpDataSource
        """
        # Use preset if provided
        if preset and preset in self.PRESETS:
            symbols = self.PRESETS[preset]
            
        # Ensure symbols is a list
        if isinstance(symbols, str):
            symbols = [symbols]
        elif symbols is None:
            symbols = self.PRESETS['tech'][:3]  # Default to top 3 tech stocks
            logger.info("No symbols specified, defaulting to AAPL, GOOGL, MSFT")
            
        # Store configuration
        self.symbols = symbols
        self.provider = provider
        self.api_key = api_key
        self.provider_config = self.PROVIDERS.get(provider, self.PROVIDERS['mock'])
        
        # Check for API key if required
        if self.provider_config['requires_key'] and not api_key:
            # Try to load from secrets
            try:
                from ..utils.url_utils import load_credentials
                credentials = load_credentials()
                self.api_key = credentials.get('alpha_vantage_key', '')
            except Exception:
                logger.warning(f"{provider} requires API key but none provided, using mock data")
                self.provider = 'mock'
                self.provider_config = self.PROVIDERS['mock']
                
        # Set rate limit based on provider
        rate_limit = kwargs.pop('rate_limit', self.provider_config['rate_limit'])
        
        super().__init__("Stock", url=None, rate_limit=rate_limit, **kwargs)
        
    async def _fetch_data(self):
        """Fetch stock data."""
        stock_data = {}
        
        if self.provider == 'mock':
            return self._get_mock_data()
            
        # Fetch real data for each symbol
        for symbol in self.symbols:
            try:
                data = await self._fetch_symbol_data(symbol)
                if data:
                    stock_data[symbol] = data
            except Exception as e:
                logger.error(e, f"Failed to fetch data for {symbol}")
                
        return stock_data
        
    async def _fetch_symbol_data(self, symbol):
        """Fetch data for a single symbol."""
        if self.provider == 'alpha_vantage':
            return await self._fetch_alpha_vantage(symbol)
        else:
            return None
            
    async def _fetch_alpha_vantage(self, symbol):
        """Fetch data from Alpha Vantage API."""
        self.url = f"{self.provider_config['base_url']}?function=GLOBAL_QUOTE&symbol={symbol}&apikey={self.api_key}"
        
        response_data = await super()._fetch_data()
        
        if not response_data or 'Global Quote' not in response_data:
            logger.error(None, f"Invalid Alpha Vantage response for {symbol}")
            return None
            
        quote = response_data['Global Quote']
        
        return {
            'symbol': symbol,
            'price': float(quote.get('05. price', 0)),
            'change': float(quote.get('09. change', 0)),
            'change_percent': quote.get('10. change percent', '0%').replace('%', ''),
            'volume': int(quote.get('06. volume', 0)),
            'high': float(quote.get('03. high', 0)),
            'low': float(quote.get('04. low', 0)),
            'open': float(quote.get('02. open', 0)),
            'previous_close': float(quote.get('08. previous close', 0))
        }
        
    def _get_mock_data(self):
        """Generate mock stock data for testing."""
        mock_data = {}
        
        base_prices = {
            'AAPL': 150.0,
            'GOOGL': 2785.0,
            'MSFT': 334.0,
            'TSLA': 800.0,
            'AMZN': 3200.0,
            'META': 475.0,
            'NFLX': 600.0,
            'JPM': 150.0,
            'BAC': 35.0,
            'WFC': 45.0,
            'GME': 25.0,
            'AMC': 5.0,
            'BTC-USD': 45000.0,
            'ETH-USD': 3000.0,
        }
        
        for symbol in self.symbols:
            base_price = base_prices.get(symbol, 100.0)
            
            # Generate realistic variations
            change_percent = random.uniform(-5.0, 5.0)
            change = base_price * (change_percent / 100)
            price = base_price + change
            
            # Calculate high/low with some variance
            daily_variance = base_price * 0.02  # 2% daily range
            high = price + random.uniform(0, daily_variance)
            low = price - random.uniform(0, daily_variance)
            
            mock_data[symbol] = {
                'symbol': symbol,
                'price': round(price, 2),
                'change': round(change, 2),
                'change_percent': f"{change_percent:.2f}",
                'volume': random.randint(1000000, 50000000),
                'high': round(high, 2),
                'low': round(low, 2),
                'open': round(base_price + random.uniform(-daily_variance/2, daily_variance/2), 2),
                'previous_close': round(base_price, 2)
            }
            
        return mock_data
        
    def parse_data(self, raw_data):
        """Parse stock data into standard format."""
        # Data is already in the correct format
        return raw_data
        
    def format_for_display(self, data):
        """Format stock data for display."""
        messages = []
        
        if not data:
            return [{
                'type': 'scroll',
                'text': 'No stock data available',
                'delay': 2
            }]
            
        # Sort by change percentage
        sorted_stocks = sorted(
            data.items(),
            key=lambda x: float(x[1]['change_percent']),
            reverse=True
        )
        
        # Market summary
        gainers = sum(1 for _, stock in sorted_stocks if float(stock['change_percent']) > 0)
        losers = sum(1 for _, stock in sorted_stocks if float(stock['change_percent']) < 0)
        
        messages.append({
            'type': 'scroll',
            'text': f"=== MARKET UPDATE: {gainers}↑ {losers}↓ ===",
            'delay': 3
        })
        
        # Individual stocks
        for symbol, stock in sorted_stocks:
            change = stock['change']
            change_pct = float(stock['change_percent'])
            arrow = '↑' if change > 0 else '↓' if change < 0 else '→'
            color = 'green' if change > 0 else 'red' if change < 0 else 'white'
            
            # Format price based on value
            price = stock['price']
            if price >= 1000:
                price_str = f"${price:,.0f}"
            elif price >= 100:
                price_str = f"${price:.1f}"
            else:
                price_str = f"${price:.2f}"
                
            messages.append({
                'type': 'scroll',
                'text': f"{symbol}: {price_str} {arrow}{abs(change_pct):.1f}%",
                'delay': 2,
                'color': color  # Optional color hint for the display
            })
            
            # Add volume info for significant movers
            if abs(change_pct) > 3.0:
                volume_m = stock['volume'] / 1_000_000
                messages.append({
                    'type': 'scroll',
                    'text': f"  Vol: {volume_m:.1f}M | H: ${stock['high']:.2f} L: ${stock['low']:.2f}",
                    'delay': 1.5
                })
                
        return messages
        
    def get_stock_price(self, symbol):
        """
        Get current price for a specific stock symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Current price, or None if not found
        """
        if hasattr(self, '_cache') and self._cache:
            return self._cache.get(symbol, {}).get('price')
        return None
        
    def get_market_summary(self):
        """
        Get a summary of the current market state.
        
        Returns:
            Dictionary with market summary statistics
        """
        if not hasattr(self, '_cache') or not self._cache:
            return None
            
        total_stocks = len(self._cache)
        gainers = sum(1 for stock in self._cache.values() if stock['change'] > 0)
        losers = sum(1 for stock in self._cache.values() if stock['change'] < 0)
        unchanged = total_stocks - gainers - losers
        
        total_volume = sum(stock['volume'] for stock in self._cache.values())
        avg_change_pct = sum(float(stock['change_percent']) for stock in self._cache.values()) / total_stocks if total_stocks > 0 else 0
        
        return {
            'total_stocks': total_stocks,
            'gainers': gainers,
            'losers': losers,
            'unchanged': unchanged,
            'total_volume': total_volume,
            'average_change_percent': avg_change_pct,
            'market_trend': 'bullish' if gainers > losers else 'bearish' if losers > gainers else 'neutral'
        }