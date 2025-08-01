import unittest
from trading_bot.patterns.gartley import find_gartley_patterns

class TestGartleyPattern(unittest.TestCase):

    def setUp(self):
        """Set up common configuration for tests."""
        self.mock_config = {
            "b_point_tolerance": 0.05,
            "d_point_tolerance": 0.05,
        }

    def test_bullish_gartley_detection(self):
        """Test the detection of a perfect bullish Gartley pattern."""
        # XA move is 10 points.
        X = (0, 100)
        A = (5, 110)
        # B is a 0.618 retracement of XA
        B = (8, 103.82) # 110 - (10 * 0.618)
        # C is some point between A and B
        C = (12, 108.0)
        # D is a 0.786 retracement of XA
        D = (16, 102.14) # 110 - (10 * 0.786)

        # We also need to satisfy the BC projection rule (1.272 - 1.618)
        # BC = 108 - 103.82 = 4.18
        # CD = 108 - 102.14 = 5.86
        # CD/BC = 5.86 / 4.18 = 1.40, which is valid.

        swing_lows = [X, B, D]
        swing_highs = [A, C]

        patterns = find_gartley_patterns(swing_highs, swing_lows, self.mock_config)

        self.assertEqual(len(patterns), 1)
        self.assertEqual(patterns[0].pattern_type, "bullish")
        self.assertEqual(patterns[0].D, D)

    def test_bearish_gartley_detection(self):
        """Test the detection of a perfect bearish Gartley pattern."""
        # XA move is 10 points.
        X = (0, 110)
        A = (5, 100)
        # B is a 0.618 retracement of XA
        B = (8, 106.18) # 100 + (10 * 0.618)
        # C is some point between A and B
        C = (12, 102.0)
        # D is a 0.786 retracement of XA
        D = (16, 107.86) # 100 + (10 * 0.786)

        # Check BC projection
        # BC = 106.18 - 102.0 = 4.18
        # CD = 107.86 - 102.0 = 5.86
        # CD/BC = 1.40, which is valid.

        swing_highs = [X, B, D]
        swing_lows = [A, C]

        patterns = find_gartley_patterns(swing_highs, swing_lows, self.mock_config)

        self.assertEqual(len(patterns), 1)
        self.assertEqual(patterns[0].pattern_type, "bearish")
        self.assertEqual(patterns[0].D, D)

    def test_invalid_b_point(self):
        """Test that a pattern with an invalid B-point is ignored."""
        X = (0, 100)
        A = (5, 110)
        # B is only a 0.500 retracement, outside the tolerance
        B = (8, 105.0)
        C = (12, 108.0)
        D = (16, 102.14)

        swing_lows = [X, B, D]
        swing_highs = [A, C]

        patterns = find_gartley_patterns(swing_highs, swing_lows, self.mock_config)
        self.assertEqual(len(patterns), 0)

if __name__ == '__main__':
    unittest.main()
