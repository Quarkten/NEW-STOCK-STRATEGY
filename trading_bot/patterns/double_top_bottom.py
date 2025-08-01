from typing import List, Optional, Dict
from pydantic import BaseModel
from ..core.models import Ohlcv, Signal
from .market_regime import SwingPoint

class DoubleTopBottomPattern(BaseModel):
    """Represents a detected Double Top or Double Bottom pattern."""
    peak1: SwingPoint
    peak2: SwingPoint
    neckline: SwingPoint
    pattern_type: str # "double_top" or "double_bottom"

def find_double_top_bottom_patterns(
    swing_highs: List[SwingPoint],
    swing_lows: List[SwingPoint],
    data: List[Ohlcv],
    config: Dict
) -> List[Signal]:
    """
    Identifies Double Top and Double Bottom patterns.
    A signal is generated upon a confirmed break of the neckline.
    """
    signals = []

    # --- Find Double Tops (M shape) ---
    if len(swing_highs) >= 2 and len(swing_lows) >= 1:
        for i in range(len(swing_highs) - 1):
            peak1 = swing_highs[i]
            peak2 = swing_highs[i+1]

            # Find the intervening swing low (the neckline)
            neckline_low = next((low for low in swing_lows if peak1[0] < low[0] < peak2[0]), None)
            if not neckline_low:
                continue

            # Check for price similarity between the two peaks
            price_diff = abs(peak1[1] - peak2[1]) / peak1[1]
            if price_diff <= config['price_similarity_threshold']:
                # We have a potential Double Top. Now, we need to watch for a neckline break.
                # Start searching for the break from the bar after the second peak.
                signal_found = False
                for j in range(peak2[0] + 1, len(data)):
                    if data[j].close < neckline_low[1]:
                        signals.append(Signal(
                            instrument="",
                            timestamp=data[j].timestamp,
                            pattern_name="Double Top",
                            signal_type="entry",
                            direction="short",
                            confluence_score=0,
                            stop_loss=max(peak1[1], peak2[1]),
                            candle=data[j]
                        ))
                        signal_found = True
                        break
                if signal_found:
                    break
    # --- Find Double Bottoms (W shape) ---
    if len(swing_lows) >= 2 and len(swing_highs) >= 1:
        for i in range(len(swing_lows) - 1):
            peak1 = swing_lows[i]
            peak2 = swing_lows[i+1]

            neckline_high = next((high for high in swing_highs if peak1[0] < high[0] < peak2[0]), None)
            if not neckline_high:
                continue

            price_diff = abs(peak1[1] - peak2[1]) / peak1[1]
            if price_diff <= config['price_similarity_threshold']:
                signal_found = False
                for j in range(peak2[0] + 1, len(data)):
                    if data[j].close > neckline_high[1]:
                        signals.append(Signal(
                            instrument="",
                            timestamp=data[j].timestamp,
                            pattern_name="Double Bottom",
                            signal_type="entry",
                            direction="long",
                            confluence_score=0,
                            stop_loss=min(peak1[1], peak2[1]),
                            candle=data[j]
                        ))
                        signal_found = True
                        break
                if signal_found:
                    break

    return signals
