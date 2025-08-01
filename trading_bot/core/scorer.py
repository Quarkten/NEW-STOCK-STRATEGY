from typing import List
from .models import Signal, Ohlcv
from ..patterns.fibonacci import calculate_fib_levels

def calculate_confluence_score(signal: Signal, data: List[Ohlcv]) -> int:
    """
    Calculates a confluence score for a given signal based on a checklist of factors.

    Args:
        signal (Signal): The signal to score.
        data (List[Ohlcv]): The historical data leading up to the signal.

    Returns:
        int: A score from 0-100 representing the quality of the signal.
    """
    score = 0
    reasons = []

    # 1. Regime Alignment (This is already handled by the strategy filter,
    # but we can add points for it here as a baseline).
    # For now, we assume any signal passed to the scorer is already regime-aligned.
    score += 50
    reasons.append("Signal aligns with market regime")

    # 2. Fibonacci Confluence
    # Find the major swing high/low in the lookback period to draw fibs from
    if len(data) > 20: # Need enough data for a meaningful swing
        lookback_data = data[-20:] # Look at the last 20 bars
        major_high = max(c.high for c in lookback_data)
        major_low = min(c.low for c in lookback_data)

        fib_levels = calculate_fib_levels(major_high, major_low)

        entry_price = signal.candle.close

        # Check if entry is near a key retracement level
        if signal.direction == "long":
            for level in fib_levels['uptrend_retracements'].values():
                # Check if entry is within 0.5% of a fib level
                if abs(entry_price - level) / level < 0.005:
                    score += 20
                    reasons.append("Entry is near a key Fibonacci retracement level")
                    break
        else: # short
            for level in fib_levels['downtrend_retracements'].values():
                if abs(entry_price - level) / level < 0.005:
                    score += 20
                    reasons.append("Entry is near a key Fibonacci retracement level")
                    break

    # 3. Volume Confirmation
    # Check if the signal candle's volume is > 1.5x the average of the last 10 candles
    if len(data) > 10:
        avg_volume = sum(c.volume for c in data[-11:-1]) / 10
        if signal.candle.volume > avg_volume * 1.5:
            score += 15
            reasons.append("Signal confirmed by high volume")

    # 4. Candlestick Strength (simple example)
    # Give points if the candle closes in its top (for long) or bottom (for short) third
    body_range = abs(signal.candle.high - signal.candle.low)
    if body_range > 0:
        if signal.direction == "long" and (signal.candle.close - signal.candle.low) / body_range > 0.66:
            score += 15
            reasons.append("Strong bullish close on signal candle")
        elif signal.direction == "short" and (signal.candle.high - signal.candle.close) / body_range > 0.66:
            score += 15
            reasons.append("Strong bearish close on signal candle")

    print(f"Scoring for {signal.instrument} on {signal.timestamp.date()}:")
    print(f"  - Reasons: {', '.join(reasons)}")
    print(f"  - Final Score: {score}")

    return min(score, 100) # Cap the score at 100
