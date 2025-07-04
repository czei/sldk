# Stock Ticker Display

A real-time stock price display application built with the CircuitPython Application Framework.

## Features

- 📈 **Real-time Stock Prices**: Displays current stock prices and changes
- 🎨 **Color Coding**: Green for gains, red for losses
- 🔄 **Auto Updates**: Refreshes data every 5 minutes
- ⚙️ **Configurable**: Set your own watchlist of stock symbols
- 🏢 **Market Status**: Shows if market is open or closed

## Configuration

Edit `settings.json` to configure your watchlist:
```json
{
  "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"],
  "update_interval": 300,
  "show_percentage": true,
  "brightness_scale": "0.5"
}
```

## API Data Source

Stock data provided by Alpha Vantage API (free tier available).
Get your API key at: https://www.alphavantage.co/support/#api-key

Add your API key to `secrets.py`:
```python
secrets = {
    "ssid": "Your_WiFi_SSID", 
    "password": "Your_WiFi_Password",
    "alpha_vantage_key": "YOUR_API_KEY_HERE"
}
```

## Example Display Output

```
Market: OPEN
AAPL: $150.25 +2.5%
GOOGL: $2,785.50 -1.2%
MSFT: $334.75 +0.8%
```

## Installation

1. Copy framework files to CIRCUITPY drive
2. Copy this example to your device
3. Configure WiFi and API credentials
4. Set your stock watchlist in settings.json