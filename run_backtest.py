import os
from trading_bot.core.config import load_config
from trading_bot.core.data_handler import fetch_historical_data
from trading_bot.backtesting.engine import Backtester
from alpaca_trade_api.rest import TimeFrame

def main():
    """
    The main entry point for running a backtest.
    """
    print("--- Initializing Backtest Runner ---")

    # 1. Set up environment (ensure API keys are available)
    # In a real deployment, this would be managed by the environment, not the script
    if "ALPACA_API_KEY" not in os.environ:
        print("API keys not found in environment. Please set them before running.")
        # For this example, we'll try to proceed if a local .env file exists
        from dotenv import load_dotenv
        if os.path.exists('.env'):
            print("Found .env file, loading keys...")
            load_dotenv()
        else:
            return

    # 2. Load Configuration
    try:
        config = load_config()
        print(f"Loaded configuration for instruments: {config.instruments}")
    except FileNotFoundError:
        print("Error: config.yaml not found.")
        return

    # 3. Fetch Historical Data for all instruments
    all_data = {}
    for instrument in config.instruments:
        print(f"Fetching historical data for {instrument}...")
        # Using a fixed range for this example backtest
        data = fetch_historical_data(instrument, TimeFrame.Day, "2022-01-01", "2023-01-01")
        if data:
            all_data[instrument] = data
            print(f"Successfully fetched {len(data)} bars for {instrument}.")
        else:
            print(f"Could not fetch data for {instrument}. It will be excluded from this backtest.")

    if not all_data:
        print("No data fetched. Aborting backtest.")
        return

    # 4. Initialize and Run the Backtester
    backtester = Backtester(data=all_data, config=config)
    backtester.run()

if __name__ == '__main__':
    main()
