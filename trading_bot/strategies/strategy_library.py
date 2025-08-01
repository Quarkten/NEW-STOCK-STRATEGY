from typing import List
from ..core.models import Ohlcv, Signal
from ..core.config import Config
from ..patterns.market_regime import find_swing_points
from ..patterns.engulfing import find_engulfing_patterns
from ..patterns.abcd import find_abcd_patterns
from ..patterns.gartley import find_gartley_patterns

def find_patterns_for_day(
    instrument: str,
    data: List[Ohlcv],
    config: Config
) -> List[Signal]:
    """
    Runs all available pattern detectors on a given dataset and returns any signals.

    Args:
        instrument (str): The symbol being analyzed.
        data (List[Ohlcv]): The historical data for the instrument.
        config (Config): The application's configuration.

    Returns:
        List[Signal]: A list of signals found for the given day.
    """
    if not data:
        return []

    signals = []
    current_candle = data[-1]

    # --- 1. Engulfing Patterns ---
    if config.patterns.enable_engulfing:
        engulfing_patterns = find_engulfing_patterns(data[-2:]) # Only need last 2 candles
        if engulfing_patterns:
            pattern = engulfing_patterns[0]
            direction = "long" if pattern.pattern_type == "bullish" else "short"
            stop_loss = pattern.candle.low if direction == "long" else pattern.candle.high

            signals.append(Signal(
                instrument=instrument,
                timestamp=current_candle.timestamp,
                pattern_name="Engulfing",
                signal_type="entry",
                direction=direction,
                confluence_score=70, # Placeholder
                stop_loss=stop_loss,
                candle=current_candle
            ))

    # --- 2. Determine Market Regime ---
    swing_highs, swing_lows = find_swing_points(data, order=5)
    if len(swing_highs) < 2 or len(swing_lows) < 2:
        return signals # Not enough swings for regime or harmonic patterns

    from ..patterns.market_regime import detect_market_regime
    regime = detect_market_regime(swing_highs, swing_lows)

    # --- 3. Score and Filter Signals ---
    scored_signals = []
    from ..core.scorer import calculate_confluence_score
    for signal in signals:
        # First, filter by regime
        if (regime == "Uptrend" and signal.direction == "long") or \
           (regime == "Downtrend" and signal.direction == "short"):

            # If aligned with regime, calculate confluence score
            score = calculate_confluence_score(signal, data)
            signal.confluence_score = score

            # Only include signals that meet the minimum score
            if score >= config.patterns.min_confluence_score:
                scored_signals.append(signal)

    signals = scored_signals

    # Gartley Patterns
    if config.patterns.enable_abcd: # Assuming gartley uses abcd flag for now
        gartley_patterns = find_gartley_patterns(swing_highs, swing_lows, config.patterns.gartley.model_dump())
        # Logic to create a signal from a Gartley pattern would go here...

    # AB=CD Patterns
    if config.patterns.enable_abcd:
        abcd_patterns = find_abcd_patterns(swing_highs, swing_lows, config.patterns.abcd.model_dump())
        # Logic to create a signal from an AB=CD pattern would go here...

    return signals
