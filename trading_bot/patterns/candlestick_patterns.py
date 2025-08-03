from typing import List, Optional
from ..core.models import Ohlcv
from ..core.patterns import Pattern

def find_bullish_engulfing(data: List[Ohlcv]) -> Optional[Pattern]:
    """Identifies a Bullish Engulfing pattern."""
    if len(data) < 2:
        return None
    
    last_candle = data[-1]
    prev_candle = data[-2]

    if prev_candle.close < prev_candle.open and \
       last_candle.close > last_candle.open and \
       last_candle.close > prev_candle.open and \
       last_candle.open < prev_candle.close:
        return Pattern(pattern_type="bullish", pattern_name="Bullish Engulfing", candle=last_candle)
    return None

def find_morning_star(data: List[Ohlcv]) -> Optional[Pattern]:
    """Identifies a Morning Star pattern."""
    if len(data) < 3:
        return None

    c1, c2, c3 = data[-3], data[-2], data[-1]

    if c1.close < c1.open and \
       abs(c2.close - c2.open) < (c2.high - c2.low) * 0.3 and \
       c3.close > c3.open and \
       c3.close > (c1.open + c1.close) / 2:
        return Pattern(pattern_type="bullish", pattern_name="Morning Star", candle=c3)
    return None

def find_hammer(data: List[Ohlcv]) -> Optional[Pattern]:
    """Identifies a Hammer pattern."""
    if len(data) < 1:
        return None
    
    candle = data[-1]
    body_size = abs(candle.close - candle.open)
    lower_wick = candle.open - candle.low if candle.close > candle.open else candle.close - candle.low
    upper_wick = candle.high - candle.close if candle.close > candle.open else candle.high - candle.open

    if lower_wick > 2 * body_size and upper_wick < body_size:
        return Pattern(pattern_type="bullish", pattern_name="Hammer", candle=candle)
    return None

def find_three_white_soldiers(data: List[Ohlcv]) -> Optional[Pattern]:
    """Identifies a Three White Soldiers pattern."""
    if len(data) < 3:
        return None

    c1, c2, c3 = data[-3], data[-2], data[-1]

    if c1.close > c1.open and c2.close > c2.open and c3.close > c3.open and \
       c2.open > c1.open and c2.open < c1.close and \
       c3.open > c2.open and c3.open < c2.close and \
       c2.close > c1.close and c3.close > c2.close:
        return Pattern(pattern_type="bullish", pattern_name="Three White Soldiers", candle=c3)
    return None

def find_piercing_line(data: List[Ohlcv]) -> Optional[Pattern]:
    """Identifies a Piercing Line pattern."""
    if len(data) < 2:
        return None

    c1, c2 = data[-2], data[-1]

    if c1.close < c1.open and c2.close > c2.open and \
       c2.open < c1.low and c2.close > (c1.open + c1.close) / 2 and \
       c2.close < c1.open:
        return Pattern(pattern_type="bullish", pattern_name="Piercing Line", candle=c2)
    return None
