import os
from trading_bot.core.config import load_config
from trading_bot.core.data_handler import fetch_historical_data, get_alpaca_api_client
from trading_bot.core.journal import log_trade
from trading_bot.patterns.market_regime import find_swing_points
from trading_bot.patterns.engulfing import find_engulfing_patterns
from trading_bot.patterns.abcd import find_abcd_patterns
from trading_bot.patterns.gartley import find_gartley_patterns
from trading_bot.execution.alpaca_executor import place_bracket_order
from trading_bot.core.models import Signal
from alpaca_trade_api.rest import TimeFrame

def run_strategy():
    """
    The main entry point for the signal follower strategy.
    """
    print("--- Running Signal Follower Strategy ---")

    # 1. Load Configuration
    try:
        config = load_config()
        print("Configuration loaded successfully.")
    except FileNotFoundError:
        print("Error: config.yaml not found. Please ensure it exists in the /configs directory.")
        return

    # 2. Initialize Alpaca API
    try:
        api = get_alpaca_api_client()
        account = api.get_account()
        print(f"Connected to Alpaca. Account Equity: ${account.equity}")
    except ValueError as e:
        print(f"Error connecting to Alpaca: {e}")
        return

    # 3. Iterate through instruments and find signals
    for instrument in config.instruments:
        print(f"\n--- Analyzing {instrument} ---")

        # Fetch recent data (e.g., last 100 days)
        # In a real bot, this date range would be more dynamic
        data = fetch_historical_data(instrument, TimeFrame.Day, "2023-01-01", "2023-06-01")

        if not data:
            print(f"Could not retrieve data for {instrument}. Skipping.")
            continue

        # --- Run Pattern Detectors ---

        # A. Engulfing Patterns
        engulfing_patterns = find_engulfing_patterns(data)
        if engulfing_patterns:
            last_engulfing = engulfing_patterns[-1] # Focus on the most recent signal
            print(f"Found {last_engulfing.pattern_type.capitalize()} Engulfing pattern at {last_engulfing.candle.timestamp.date()}")

            # Create a signal
            direction = "long" if last_engulfing.pattern_type == "bullish" else "short"
            stop_loss = last_engulfing.candle.low if direction == "long" else last_engulfing.candle.high

            signal = Signal(
                instrument=instrument,
                timestamp=last_engulfing.candle.timestamp,
                pattern_name="Engulfing",
                signal_type="entry",
                direction=direction,
                confluence_score=70, # Placeholder score
                stop_loss=stop_loss,
                candle=last_engulfing.candle
            )

            # Execute and log the trade
            order = place_bracket_order(signal, config, api)
            if order:
                reason = f"Detected {last_engulfing.pattern_type} engulfing pattern."
                log_trade(signal, order, reason)

        # B. Harmonic and Geometric Patterns (require swing points)
        swing_highs, swing_lows = find_swing_points(data, order=5)

        if len(swing_highs) < 2 or len(swing_lows) < 2:
            print("Not enough swing points for harmonic patterns.")
            continue

        # Gartley Patterns
        gartley_patterns = find_gartley_patterns(swing_highs, swing_lows, config.patterns.gartley.model_dump())
        if gartley_patterns:
            print(f"Found {len(gartley_patterns)} Gartley patterns.")
            # Similar logic to execute on Gartley would go here...

        # AB=CD Patterns
        abcd_patterns = find_abcd_patterns(swing_highs, swing_lows, config.patterns.abcd.model_dump())
        if abcd_patterns:
            print(f"Found {len(abcd_patterns)} AB=CD patterns.")
            # Similar logic to execute on AB=CD would go here...

    print("\n--- Strategy run complete ---")

if __name__ == '__main__':
    # Set up environment variables for a local run if they are not already set
    # In a real deployment, these would be managed by the environment
    if "ALPACA_API_KEY" not in os.environ:
        print("Setting dummy Alpaca credentials for local test run.")
        os.environ["ALPACA_API_KEY"] = "DUMMY_KEY"
        os.environ["ALPACA_SECRET_KEY"] = "DUMMY_SECRET"

    run_strategy()
