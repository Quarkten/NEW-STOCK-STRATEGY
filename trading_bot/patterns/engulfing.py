from typing import List
from pydantic import BaseModel
from ..core.models import Ohlcv

class EngulfingPattern(BaseModel):
    """Represents a detected Engulfing pattern."""
    index: int
    pattern_type: str  # "bullish" or "bearish"
    candle: Ohlcv

def find_engulfing_patterns(data: List[Ohlcv]) -> List[EngulfingPattern]:
    """
    Identifies Bullish and Bearish Engulfing patterns in a list of OHLCV data.

    Args:
        data (List[Ohlcv]): A list of OHLCV data, ordered by time.

    Returns:
        List[EngulfingPattern]: A list of detected engulfing patterns.
    """
    patterns = []
    if len(data) < 2:
        return patterns

    for i in range(1, len(data)):
        prev_candle = data[i-1]
        curr_candle = data[i]

        prev_body_size = abs(prev_candle.close - prev_candle.open)
        curr_body_size = abs(curr_candle.close - curr_candle.open)

        # --- Check for Bullish Engulfing ---
        # 1. Previous candle must be bearish (close < open).
        # 2. Current candle must be bullish (close > open).
        # 3. Current candle's body must engulf the previous candle's body.
        is_bullish_engulfing = (
            prev_candle.close < prev_candle.open and
            curr_candle.close > curr_candle.open and
            curr_candle.open < prev_candle.close and
            curr_candle.close > prev_candle.open
        )
        if is_bullish_engulfing:
            patterns.append(EngulfingPattern(
                index=i,
                pattern_type="bullish",
                candle=curr_candle
            ))

        # --- Check for Bearish Engulfing ---
        # 1. Previous candle must be bullish (close > open).
        # 2. Current candle must be bearish (close < open).
        # 3. Current candle's body must engulf the previous candle's body.
        is_bearish_engulfing = (
            prev_candle.close > prev_candle.open and
            curr_candle.close < curr_candle.open and
            curr_candle.open > prev_candle.close and
            curr_candle.close < prev_candle.open
        )
        if is_bearish_engulfing:
            patterns.append(EngulfingPattern(
                index=i,
                pattern_type="bearish",
                candle=curr_candle
            ))

    return patterns

# --- Test Block ---
if __name__ == '__main__':
    from datetime import datetime, timedelta
    print("--- Testing Engulfing Pattern Detection ---")

    # Bullish Engulfing Data
    bullish_data = [
        Ohlcv(timestamp=datetime(2023,1,1), open=102, high=103, low=100, close=101), # Bearish candle
        Ohlcv(timestamp=datetime(2023,1,2), open=100, high=104, low=99, close=103)   # Bullish, engulfs prior
    ]

    # Bearish Engulfing Data
    bearish_data = [
        Ohlcv(timestamp=datetime(2023,1,1), open=100, high=103, low=99, close=102), # Bullish candle
        Ohlcv(timestamp=datetime(2023,1,2), open=103, high=104, low=99, close=99)   # Bearish, engulfs prior
    ]

    bullish_patterns = find_engulfing_patterns(bullish_data)
    print(f"Found {len(bullish_patterns)} bullish patterns.")
    assert len(bullish_patterns) == 1
    assert bullish_patterns[0].pattern_type == "bullish"
    print("Bullish Engulfing test passed.")

    bearish_patterns = find_engulfing_patterns(bearish_data)
    print(f"Found {len(bearish_patterns)} bearish patterns.")
    assert len(bearish_patterns) == 1
    assert bearish_patterns[0].pattern_type == "bearish"
    print("Bearish Engulfing test passed.")

    print("\nAll Engulfing pattern tests passed successfully!")
