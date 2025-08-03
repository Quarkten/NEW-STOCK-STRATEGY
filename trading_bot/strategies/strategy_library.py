from typing import List, Optional
from ..core.models import Ohlcv, Signal
from ..core.config import Config
from ..core.patterns import Pattern
from ..patterns.market_regime import find_swing_points
from ..patterns.engulfing import find_engulfing_patterns
from ..patterns.abcd import find_abcd_patterns
from ..patterns.gartley import find_gartley_patterns
from ..patterns.candlestick_patterns import find_bullish_engulfing, find_morning_star, find_hammer, find_three_white_soldiers, find_piercing_line
from ..patterns.chart_patterns import find_cup_and_handle, find_inverse_head_and_shoulders, find_falling_wedge, find_bull_flag, find_ascending_triangle

def find_all_patterns(data: List[Ohlcv]) -> List[Pattern]:
    """Finds all available patterns in the given data."""
    patterns = []
    
    # Candlestick patterns
    patterns.append(find_bullish_engulfing(data))
    patterns.append(find_morning_star(data))
    patterns.append(find_hammer(data))
    patterns.append(find_three_white_soldiers(data))
    patterns.append(find_piercing_line(data))
    
    # Chart patterns
    patterns.append(find_cup_and_handle(data))
    patterns.append(find_inverse_head_and_shoulders(data))
    patterns.append(find_falling_wedge(data))
    patterns.append(find_bull_flag(data))
    patterns.append(find_ascending_triangle(data))
    
    return [p for p in patterns if p is not None]

def find_signals(
    instrument: str,
    daily_data: List[Ohlcv],
    hourly_data: List[Ohlcv],
    config: Config
) -> List[Signal]:
    """
    Runs all available pattern detectors on the hourly data, filtered by the daily trend.
    """
    if len(daily_data) < 20 or len(hourly_data) < 2: # Need enough data for context
        return []

    # 1. Determine Major Trend from Daily Data
    from ..patterns.market_regime import find_swing_points, detect_market_regime
    daily_swing_highs, daily_swing_lows = find_swing_points(daily_data, order=10)
    if len(daily_swing_highs) < 2 or len(daily_swing_lows) < 2:
        return []
    major_trend = detect_market_regime(daily_swing_highs, daily_swing_lows)

    if major_trend == "Ranging":
        return [] # Only trade in clear daily trends

    # 2. Look for Entry Patterns on Hourly Data
    signals = []
    current_hourly_candle = hourly_data[-1]

    # Engulfing Patterns on Hourly Chart
    if config.patterns.enable_engulfing:
        patterns = find_all_patterns(hourly_data)
        for pattern in patterns:
            direction = "long" if pattern.pattern_type == "bullish" else "short"

            # 3. Check for Alignment
            if major_trend == "Uptrend" and direction == "long":

                stop_loss = pattern.candle.low if direction == "long" else pattern.candle.high
                signal = Signal(
                    instrument=instrument,
                    timestamp=current_hourly_candle.timestamp,
                    pattern_name=f"H1 {pattern.pattern_name} ({major_trend})",
                    signal_type="entry",
                    direction=direction,
                    confluence_score=0, # Will be scored later
                    stop_loss=stop_loss,
                    candle=current_hourly_candle
                )
                signals.append(signal)

    # (Other pattern detectors like AB=CD, Gartley would be called here on the hourly data)

    # 4. Score and filter the final signals
    # (Scoring logic can also be enhanced with MTF context)
    # ...

    return signals

def find_add_on_signals(
    position_direction: str,
    instrument: str,
    data: List[Ohlcv]
) -> Optional[Signal]:
    """
    Looks for low-risk continuation patterns to add to an existing profitable position.

    Args:
        position_direction (str): The direction of the open position ('long' or 'short').
        instrument (str): The symbol being analyzed.
        data (List[Ohlcv]): The historical data for the instrument.

    Returns:
        Optional[Signal]: An 'add' signal if a valid continuation pattern is found.
    """
    if len(data) < 2:
        return None

    # Simple continuation signal: A small engulfing pattern in the direction of the trend
    engulfing_patterns = find_engulfing_patterns(data[-2:])
    if not engulfing_patterns:
        return None

    pattern = engulfing_patterns[0]
    current_candle = data[-1]

    # If we are long, look for a bullish continuation
    if position_direction == "long" and pattern.pattern_type == "bullish":
        return Signal(
            instrument=instrument,
            timestamp=current_candle.timestamp,
            pattern_name="Engulfing Add-on",
            signal_type="add",
            direction="long",
            confluence_score=80, # High score as it's with a winning trade
            stop_loss=current_candle.low,
            candle=current_candle
        )
    

    return None
