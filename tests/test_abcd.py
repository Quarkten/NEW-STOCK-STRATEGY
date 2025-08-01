import unittest
from trading_bot.patterns.abcd import find_abcd_patterns

class TestAbcdPattern(unittest.TestCase):

    def setUp(self):
        """Set up common configuration for tests."""
        self.mock_config = {
            "price_symmetry_tolerance": 0.15,
            "time_symmetry_tolerance": 0.25,
        }

    def test_bullish_abcd_detection(self):
        """Test the detection of a bullish AB=CD pattern."""
        # A=100, B=110. C is a 0.618 retracement of AB.
        A = (0, 100.0)
        B = (5, 110.0)
        C = (10, 103.82) # 110 - (10 * 0.618)

        swing_lows = [A, C]
        swing_highs = [B]

        patterns = find_abcd_patterns(swing_highs, swing_lows, self.mock_config)

        self.assertEqual(len(patterns), 1)
        self.assertEqual(patterns[0].pattern_type, "bullish")
        self.assertEqual(patterns[0].A, A)
        self.assertEqual(patterns[0].C, C)
        # Check D projection: C + (B-A) = 103.82 + 10 = 113.82
        self.assertAlmostEqual(patterns[0].D[1], 113.82)

    def test_bearish_abcd_detection(self):
        """Test the detection of a bearish AB=CD pattern."""
        # A=110, B=100. C is a 0.786 retracement of AB.
        A = (0, 110.0)
        B = (5, 100.0)
        C = (10, 107.86) # 100 + (10 * 0.786)

        swing_highs = [A, C]
        swing_lows = [B]

        patterns = find_abcd_patterns(swing_highs, swing_lows, self.mock_config)

        self.assertEqual(len(patterns), 1)
        self.assertEqual(patterns[0].pattern_type, "bearish")
        self.assertEqual(patterns[0].A, A)
        self.assertEqual(patterns[0].C, C)
        # Check D projection: C - (A-B) = 107.86 - 10 = 97.86
        self.assertAlmostEqual(patterns[0].D[1], 97.86)

    def test_invalid_retracement(self):
        """Test that a pattern with an invalid C-point retracement is ignored."""
        # C is only a 0.382 retracement, which is outside our accepted 0.618-0.786 range
        A = (0, 100.0)
        B = (5, 110.0)
        C = (10, 106.18) # 110 - (10 * 0.382)

        swing_lows = [A, C]
        swing_highs = [B]

        patterns = find_abcd_patterns(swing_highs, swing_lows, self.mock_config)
        self.assertEqual(len(patterns), 0)

if __name__ == '__main__':
    unittest.main()
