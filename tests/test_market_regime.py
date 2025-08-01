import unittest
from trading_bot.patterns.market_regime import detect_market_regime

class TestMarketRegimeLogic(unittest.TestCase):

    def test_detect_uptrend(self):
        """Test regime detection with ideal uptrend swing points."""
        swing_highs = [(5, 110), (10, 120)]  # Higher High
        swing_lows = [(2, 100), (8, 105)]   # Higher Low
        regime = detect_market_regime(swing_highs, swing_lows)
        self.assertEqual(regime, "Uptrend")

    def test_detect_downtrend(self):
        """Test regime detection with ideal downtrend swing points."""
        swing_highs = [(5, 120), (10, 110)]  # Lower High
        swing_lows = [(2, 105), (8, 100)]   # Lower Low
        regime = detect_market_regime(swing_highs, swing_lows)
        self.assertEqual(regime, "Downtrend")

    def test_detect_ranging_equal_highs(self):
        """Test regime detection with equal highs."""
        swing_highs = [(5, 120), (10, 120)]
        swing_lows = [(2, 100), (8, 105)] # Higher low
        regime = detect_market_regime(swing_highs, swing_lows)
        self.assertEqual(regime, "Ranging")

    def test_detect_ranging_equal_lows(self):
        """Test regime detection with equal lows."""
        swing_highs = [(5, 110), (10, 120)] # Higher high
        swing_lows = [(2, 100), (8, 100)]
        regime = detect_market_regime(swing_highs, swing_lows)
        self.assertEqual(regime, "Ranging")

    def test_detect_ranging_conflicting(self):
        """Test regime detection with conflicting signals (higher high, lower low)."""
        swing_highs = [(5, 110), (10, 120)] # Higher high
        swing_lows = [(2, 105), (8, 100)]   # Lower low
        regime = detect_market_regime(swing_highs, swing_lows)
        self.assertEqual(regime, "Ranging")

    def test_not_enough_data(self):
        """Test that 'Ranging' is returned when there are not enough swing points."""
        swing_highs = [(0, 110)]
        swing_lows = [(1, 100)]
        regime = detect_market_regime(swing_highs, swing_lows)
        self.assertEqual(regime, "Ranging")

# We can add a separate test class for the find_swing_points function if needed,
# but for now, we confirm the core regime logic is sound.

if __name__ == '__main__':
    unittest.main()
