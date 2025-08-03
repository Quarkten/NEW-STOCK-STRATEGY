import os
import pandas as pd
from typing import List
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame
from .models import Ohlcv  # Adjusted import path

# --- Alpaca API Client ---

def get_alpaca_api_client():
    """Initializes and returns an Alpaca API client."""
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    base_url = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

    if not api_key or not secret_key:
        raise ValueError("Alpaca API Key and Secret Key must be set in the .env file.")
    
    api = tradeapi.REST(
        key_id=api_key,
        secret_key=secret_key,
        base_url=base_url,
        api_version='v2'
    )
    return api

# --- Data Fetching Functions ---

def fetch_historical_data(symbol: str, timeframe: TimeFrame, start_date: str, end_date: str) -> List[Ohlcv]:
    """
    Fetches historical OHLCV data from Alpaca and returns it as a list of Ohlcv models.
    """
    api = get_alpaca_api_client()
    try:
        bars = api.get_bars(symbol, timeframe, start_date, end_date, adjustment='raw').df
        # The Alpaca API returns a pandas DataFrame with a DatetimeIndex.
        # We reset the index to turn it into a column named 'timestamp'.
        bars.reset_index(inplace=True)

        # The 'timestamp' column is timezone-aware, so we make it naive for our model.
        bars['timestamp'] = bars['timestamp'].dt.tz_localize(None)
        bars.columns = [col.lower() for col in bars.columns]
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        bars = bars[required_columns]
        ohlcv_list = [Ohlcv(**row) for row in bars.to_dict(orient='records')]
        return ohlcv_list
    except Exception as e:
        print(f"An error occurred while fetching data for {symbol} from Alpaca: {e}")
        return []

# --- Test Block ---

if __name__ == '__main__':
    print("--- Testing Real-time Data Fetcher from Alpaca ---")
    symbol_to_fetch = "SPY"
    timeframe_to_fetch = TimeFrame.Day
    start_date_fetch = "2023-01-01"
    end_date_fetch = "2023-01-10"

    print(f"Fetching {timeframe_to_fetch.value} data for {symbol_to_fetch} from {start_date_fetch} to {end_date_fetch}...")

    try:
        historical_data = fetch_historical_data(
            symbol=symbol_to_fetch,
            timeframe=timeframe_to_fetch,
            start_date=start_date_fetch,
            end_date=end_date_fetch
        )
        if historical_data:
            print(f"Successfully loaded {len(historical_data)} records from Alpaca.")
            print("First record:", historical_data[0])
            print("Last record:", historical_data[-1])
        else:
            print("No data was returned from Alpaca.")
    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during testing: {e}")
