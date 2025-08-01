import os
import time
from datetime import datetime
from trading_bot.core.config import load_config
from trading_bot.core.data_handler import fetch_historical_data, get_alpaca_api_client
from trading_bot.core.journal import log_trade
from trading_bot.strategies.strategy_library import find_patterns_for_day, find_add_on_signals
from trading_bot.execution.alpaca_executor import place_bracket_order
from alpaca_trade_api.rest import TimeFrame

def run_live_session():
    """
    The main entry point for running the bot in a live paper trading session.
    """
    print("--- Initializing Live Trading Session ---")

    # 1. Load Configuration
    try:
        config = load_config()
        print(f"Configuration loaded. Trading on: {config.instruments}")
    except FileNotFoundError:
        print("FATAL: config.yaml not found. Aborting.")
        return

    # 2. Initialize Alpaca API
    try:
        api = get_alpaca_api_client()
        account = api.get_account()
        print(f"Connected to Alpaca Paper Trading. Account Equity: ${account.equity}")
    except Exception as e:
        print(f"FATAL: Could not connect to Alpaca. Error: {e}. Aborting.")
        return

    # --- Main Trading Loop ---
    while True:
        try:
            print(f"\n--- New Run Cycle: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")

            # Get currently open positions from Alpaca
            open_positions = api.list_positions()
            open_position_symbols = [p.symbol for p in open_positions]

            # --- Portfolio Risk Checks ---
            if len(open_positions) >= config.risk.max_open_positions:
                print(f"Risk Warning: Max open positions ({config.risk.max_open_positions}) reached. No new trades will be opened.")

            # (A live daily drawdown check would be more complex and require tracking equity daily)

            for instrument in config.instruments:
                print(f"Analyzing {instrument}...")

                # Fetch latest data
                # Using a 200-day lookback for pattern analysis
                data = fetch_historical_data(instrument, TimeFrame.Day, "2022-01-01", datetime.now().strftime('%Y-%m-%d'))
                if not data:
                    print(f"Could not retrieve data for {instrument}. Skipping.")
                    continue

                if instrument in open_position_symbols:
                    print(f"Position already open for {instrument}. Checking for add-on signals...")
                    # In a real system, you'd get the position details to check for profitability
                    # For now, we'll just assume it could be profitable and look for signals
                    add_on_signal = find_add_on_signals("long", instrument, data) # Placeholder direction
                    if add_on_signal:
                        print(f"Found add-on signal for {instrument}! Submitting order...")
                        # place_bracket_order(add_on_signal, config, api) # This logic needs refinement for live

                # Only look for new trades if we are below the max position limit
                elif len(open_positions) < config.risk.max_open_positions:
                    signals = find_patterns_for_day(instrument, data, config)
                    if signals:
                        signal = signals[0] # Take the first valid signal
                        print(f"Found valid signal for {instrument}: {signal.pattern_name} ({signal.direction})")
                        order = place_bracket_order(signal, config, api)
                        if order:
                            reason = f"Live signal triggered by {signal.pattern_name} with score {signal.confluence_score}"
                            log_trade(signal, order, reason)

            print(f"--- Cycle Complete. Sleeping for 10 minutes... ---")
            time.sleep(600)

        except KeyboardInterrupt:
            print("\n--- User initiated shutdown. Exiting live session. ---")
            break
        except Exception as e:
            print(f"An unexpected error occurred in the main loop: {e}")
            print("Restarting loop after a short delay...")
            time.sleep(60)

if __name__ == '__main__':
    run_live_session()
