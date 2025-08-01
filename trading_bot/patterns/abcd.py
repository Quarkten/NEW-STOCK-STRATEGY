from typing import List, Optional, Dict
from pydantic import BaseModel
from ..core.models import Ohlcv
from .market_regime import SwingPoint

class ABCDPattern(BaseModel):
    """Represents a detected AB=CD pattern."""
    A: SwingPoint
    B: SwingPoint
    C: SwingPoint
    D: SwingPoint
    pattern_type: str # "bullish" or "bearish"

def find_abcd_patterns(
    swing_highs: List[SwingPoint],
    swing_lows: List[SwingPoint],
    config: Dict
) -> List[ABCDPattern]:
    """
    Identifies AB=CD patterns from a list of swing points.

    Args:
        swing_highs (List[SwingPoint]): A list of swing high points.
        swing_lows (List[SwingPoint]): A list of swing low points.
        config (Dict): The pattern configuration dictionary.

    Returns:
        List[ABCDPattern]: A list of detected AB=CD patterns.
    """
    patterns = []

    # For a bullish AB=CD, the structure is Low(A) -> High(B) -> Low(C) -> High(D)
    # So we need at least two swing lows and one swing high in between
    for i in range(len(swing_lows) - 1):
        for j in range(len(swing_highs)):
            # Ensure B is between A and C
            if swing_lows[i][0] < swing_highs[j][0] < swing_lows[i+1][0]:
                A = swing_lows[i]
                B = swing_highs[j]
                C = swing_lows[i+1]

                # Basic validation: C must be higher than A
                if C[1] <= A[1]:
                    continue

                # --- Calculate legs and check symmetry ---
                ab_price_range = B[1] - A[1]
                bc_price_range = B[1] - C[1]

                # Project D point
                d_price_projection = C[1] + ab_price_range

                # Check C retracement of AB (typically 0.618 to 0.786)
                c_retracement = bc_price_range / ab_price_range
                if not (0.618 <= c_retracement <= 0.786):
                    continue

                # In a real system, we would project D and wait for a reversal signal there.
                # For backtesting, we can search for a D that completes the pattern.
                # Here, we will just create a theoretical D for the pattern structure.
                # A more advanced implementation would search for the next swing high.
                D_projected = (C[0] + (B[0] - A[0]), d_price_projection)

                patterns.append(ABCDPattern(A=A, B=B, C=C, D=D_projected, pattern_type="bullish"))

    # A bearish AB=CD is High(A) -> Low(B) -> High(C) -> Low(D)
    for i in range(len(swing_highs) - 1):
        for j in range(len(swing_lows)):
            if swing_highs[i][0] < swing_lows[j][0] < swing_highs[i+1][0]:
                A = swing_highs[i]
                B = swing_lows[j]
                C = swing_highs[i+1]

                if C[1] >= A[1]:
                    continue

                ab_price_range = A[1] - B[1]
                bc_price_range = C[1] - B[1]
                d_price_projection = C[1] - ab_price_range

                c_retracement = bc_price_range / ab_price_range
                if not (0.618 <= c_retracement <= 0.786):
                    continue

                D_projected = (C[0] + (B[0] - A[0]), d_price_projection)
                patterns.append(ABCDPattern(A=A, B=B, C=C, D=D_projected, pattern_type="bearish"))

    return patterns

# --- Test Block ---
if __name__ == '__main__':
    print("--- Testing AB=CD Pattern Detection ---")

    # Sample swing points for a bullish AB=CD
    test_swing_lows = [(0, 100.0), (10, 105.0)] # A and C
    test_swing_highs = [(5, 110.0)] # B

    # C is at 50% retracement of AB, which is not in the 0.618-0.786 range
    # Let's adjust C to be at a 0.618 retracement
    # AB range = 10. C should be at 110 - (10 * 0.618) = 103.82
    test_swing_lows[1] = (10, 103.82)

    mock_config = {
        "price_symmetry_tolerance": 0.15,
        "time_symmetry_tolerance": 0.25,
    }

    detected_patterns = find_abcd_patterns(test_swing_highs, test_swing_lows, mock_config)

    print(f"Detected {len(detected_patterns)} patterns.")

    if detected_patterns:
        pattern = detected_patterns[0]
        print("Pattern Type:", pattern.pattern_type)
        print("A:", pattern.A)
        print("B:", pattern.B)
        print("C:", pattern.C)
        print("Projected D:", pattern.D)

        # Verify the projection
        # D should be at C + (B-A) = 103.82 + (110-100) = 113.82
        assert abs(pattern.D[1] - 113.82) < 0.01, "D point projection is incorrect."
        assert pattern.pattern_type == "bullish"
        print("\nTest passed for bullish AB=CD detection.")
    else:
        print("\nNo patterns detected.")
