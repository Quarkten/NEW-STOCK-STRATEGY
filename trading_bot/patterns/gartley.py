from typing import List, Optional, Dict
from pydantic import BaseModel
from ..core.models import Ohlcv
from .market_regime import SwingPoint

class GartleyPattern(BaseModel):
    """Represents a detected Gartley pattern."""
    X: SwingPoint
    A: SwingPoint
    B: SwingPoint
    C: SwingPoint
    D: SwingPoint
    pattern_type: str  # "bullish" or "bearish"

def find_gartley_patterns(
    swing_highs: List[SwingPoint],
    swing_lows: List[SwingPoint],
    config: Dict
) -> List[GartleyPattern]:
    """
    Identifies Gartley "222" patterns from a list of swing points.
    """
    patterns = []

    # Combine and sort all swing points by index
    all_swings = sorted(swing_highs + swing_lows, key=lambda x: x[0])

    if len(all_swings) < 5:
        return []

    # A Bullish Gartley starts with a low (X) followed by a high (A)
    # X-A-B-C-D sequence is Low-High-Low-High-Low
    for i in range(len(all_swings) - 4):
        X, A, B, C, D = all_swings[i:i+5]

        # Check structure: Bullish Gartley is Low-High-Low-High-Low
        if not (X in swing_lows and A in swing_highs and B in swing_lows and C in swing_highs and D in swing_lows):
            continue

        # --- Fibonacci Ratio Checks for Bullish Gartley ---
        xa_move = A[1] - X[1]
        ab_move = A[1] - B[1]
        bc_move = C[1] - B[1]
        cd_move = C[1] - D[1]

        # 1. B point must be ~0.618 retracement of XA
        b_retracement = ab_move / xa_move
        if not (0.618 - config['b_point_tolerance'] <= b_retracement <= 0.618 + config['b_point_tolerance']):
            continue

        # 2. D point must be ~0.786 retracement of XA
        ad_move = D[1] - A[1] # This will be negative
        d_retracement = (A[1] - D[1]) / xa_move
        if not (0.786 - config['d_point_tolerance'] <= d_retracement <= 0.786 + config['d_point_tolerance']):
            continue

        # 3. BC projection: CD leg is typically 1.272 to 1.618 of BC
        cd_bc_projection = cd_move / bc_move
        if not (1.272 <= cd_bc_projection <= 1.618):
            continue

        patterns.append(GartleyPattern(X=X, A=A, B=B, C=C, D=D, pattern_type="bullish"))

    # A Bearish Gartley starts with a high (X) followed by a low (A)
    # X-A-B-C-D sequence is High-Low-High-Low-High
    for i in range(len(all_swings) - 4):
        X, A, B, C, D = all_swings[i:i+5]

        if not (X in swing_highs and A in swing_lows and B in swing_highs and C in swing_lows and D in swing_highs):
            continue

        xa_move = X[1] - A[1]
        ab_move = B[1] - A[1]
        bc_move = B[1] - C[1]
        cd_move = D[1] - C[1]

        b_retracement = ab_move / xa_move
        if not (0.618 - config['b_point_tolerance'] <= b_retracement <= 0.618 + config['b_point_tolerance']):
            continue

        d_retracement = (D[1] - A[1]) / xa_move
        if not (0.786 - config['d_point_tolerance'] <= d_retracement <= 0.786 + config['d_point_tolerance']):
            continue

        cd_bc_projection = cd_move / bc_move
        if not (1.272 <= cd_bc_projection <= 1.618):
            continue

        patterns.append(GartleyPattern(X=X, A=A, B=B, C=C, D=D, pattern_type="bearish"))

    return patterns

# --- Test Block ---
if __name__ == '__main__':
    print("--- Testing Gartley Pattern Detection ---")

    # Create perfect swing points for a Bullish Gartley
    X = (0, 100)
    A = (5, 110)
    # B should be at 100 + (110-100)*0.382 = 103.82 (since B is a 0.618 retracement from A)
    B = (8, 103.82)
    # Adjust C to make the BC projection valid
    C = (12, 108.02)
    # D should be at 100 + (110-100)*0.214 = 102.14 (since D is a 0.786 retracement from A)
    D = (16, 102.14)

    mock_swing_lows = [X, B, D]
    mock_swing_highs = [A, C]

    mock_config = {"b_point_tolerance": 0.05, "d_point_tolerance": 0.05}

    detected = find_gartley_patterns(mock_swing_highs, mock_swing_lows, mock_config)

    print(f"Detected {len(detected)} patterns.")

    if detected:
        pattern = detected[0]
        print("Pattern Type:", pattern.pattern_type)
        print("X:", pattern.X)
        print("A:", pattern.A)
        print("B:", pattern.B)
        print("C:", pattern.C)
        print("D:", pattern.D)
        assert pattern.pattern_type == "bullish"
        print("\nTest passed for Bullish Gartley detection.")
    else:
        print("\nNo Gartley patterns detected.")
