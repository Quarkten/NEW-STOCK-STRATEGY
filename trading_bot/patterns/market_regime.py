from typing import List, Tuple, Literal
from ..core.models import Ohlcv

# Type alias for a swing point: (index, price)
SwingPoint = Tuple[int, float]

def find_swing_points(data: List[Ohlcv], order: int = 5) -> Tuple[List[SwingPoint], List[SwingPoint]]:
    """
    Identifies swing highs and lows in a list of OHLCV data.

    A swing high is a candle's high that is higher than the 'order' candles before and after it.
    A swing low is a candle's low that is lower than the 'order' candles before and after it.

    Args:
        data (List[Ohlcv]): A list of OHLCV data.
        order (int): The number of candles on each side to check for a swing point.

    Returns:
        Tuple[List[SwingPoint], List[SwingPoint]]: A tuple containing a list of swing highs
                                                   and a list of swing lows.
    """
    swing_highs: List[SwingPoint] = []
    swing_lows: List[SwingPoint] = []

    # We cannot determine swing points for candles at the very beginning or end of the data
    for i in range(order, len(data) - order):
        is_swing_high = True
        is_swing_low = True

        # Check for swing high
        for j in range(1, order + 1):
            if data[i].high < data[i-j].high or data[i].high < data[i+j].high:
                is_swing_high = False
                break
        if is_swing_high:
            swing_highs.append((i, data[i].high))

        # Check for swing low
        for j in range(1, order + 1):
            if data[i].low > data[i-j].low or data[i].low > data[i+j].low:
                is_swing_low = False
                break
        if is_swing_low:
            swing_lows.append((i, data[i].low))

    return swing_highs, swing_lows

def detect_market_regime(
    swing_highs: List[SwingPoint],
    swing_lows: List[SwingPoint]
) -> Literal["Uptrend", "Downtrend", "Ranging"]:
    """
    Detects the market regime based on the last few swing points.

    Args:
        swing_highs (List[SwingPoint]): List of swing highs.
        swing_lows (List[SwingPoint]): List of swing lows.

    Returns:
        Literal["Uptrend", "Downtrend", "Ranging"]: The detected market regime.
    """
    if len(swing_highs) < 2 or len(swing_lows) < 2:
        return "Ranging" # Not enough data to determine a trend

    # Get the last two swing highs and lows
    last_high = swing_highs[-1][1]
    prev_high = swing_highs[-2][1]
    last_low = swing_lows[-1][1]
    prev_low = swing_lows[-2][1]

    # Check for uptrend: higher highs and higher lows
    if last_high > prev_high and last_low > prev_low:
        return "Uptrend"
    # Check for downtrend: lower highs and lower lows
    elif last_high < prev_high and last_low < prev_low:
        return "Downtrend"
    else:
        return "Ranging"

from datetime import datetime, timedelta

# --- Test Block ---

if __name__ == '__main__':
    print("--- Testing Market Regime Detection ---")

    # Helper to create a list of timestamps
    start_time = datetime(2023, 1, 1)
    timestamps = [start_time + timedelta(days=i) for i in range(16)]

    # Create a more realistic sample data set for testing with clear swing points
    test_data: List[Ohlcv] = [
        # Dummy bars for padding at the start
        Ohlcv(timestamp=timestamps[0], open=100, high=100, low=100, close=100),
        Ohlcv(timestamp=timestamps[1], open=100, high=100, low=100, close=100),
        # A clear swing low
        Ohlcv(timestamp=timestamps[2], open=105, high=106, low=100, close=101), # idx 2
        Ohlcv(timestamp=timestamps[3], open=101, high=104, low=101, close=103),
        Ohlcv(timestamp=timestamps[4], open=103, high=105, low=102, close=104),
        # A clear swing high
        Ohlcv(timestamp=timestamps[5], open=110, high=115, low=109, close=112), # idx 5
        Ohlcv(timestamp=timestamps[6], open=112, high=114, low=110, close=111),
        Ohlcv(timestamp=timestamps[7], open=111, high=112, low=108, close=109),
        # A clear higher low
        Ohlcv(timestamp=timestamps[8], open=109, high=110, low=105, close=107), # idx 8
        Ohlcv(timestamp=timestamps[9], open=107, high=109, low=106, close=108),
        Ohlcv(timestamp=timestamps[10], open=108, high=111, low=107, close=110),
        # A clear higher high
        Ohlcv(timestamp=timestamps[11], open=120, high=125, low=119, close=122), # idx 11
        Ohlcv(timestamp=timestamps[12], open=122, high=124, low=120, close=121),
        Ohlcv(timestamp=timestamps[13], open=121, high=123, low=119, close=120),
        # Dummy bars for padding at the end
        Ohlcv(timestamp=timestamps[14], open=100, high=100, low=100, close=100),
        Ohlcv(timestamp=timestamps[15], open=100, high=100, low=100, close=100),
    ]

    # Use a smaller order for this denser data
    swing_highs, swing_lows = find_swing_points(test_data, order=2)

    print(f"Found {len(swing_highs)} swing highs: {swing_highs}")
    print(f"Found {len(swing_lows)} swing lows: {swing_lows}")

    if len(swing_highs) >= 2 and len(swing_lows) >= 2:
        regime = detect_market_regime(swing_highs, swing_lows)
        print(f"\nDetected Market Regime: {regime}")
        assert regime == "Uptrend", f"Expected 'Uptrend' but got '{regime}'"
        print("Test passed for Uptrend detection.")
    else:
        print("\nNot enough swing points found to detect a regime.")
