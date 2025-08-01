import unittest
from datetime import datetime, timedelta
from trading_bot.core.models import Ohlcv
from trading_bot.patterns.double_top_bottom import find_double_top_bottom_patterns

class TestDoubleTopBottom(unittest.TestCase):

    def setUp(self):
        """Set up common config and data structures."""
        self.mock_config = {"price_similarity_threshold": 0.01}

        # --- Data for Double Top (M shape) ---
        self.dt_swing_highs = [(2, 110.0), (6, 109.9)] # Two highs at similar prices
        self.dt_swing_lows = [(4, 105.0)] # Intervening low (neckline)
        self.dt_data = [
            Ohlcv(timestamp=datetime(2023,1,1)+timedelta(days=i), open=108, high=112, low=107, close=108) for i in range(8)
        ]
        # Manually set the key candle values
        self.dt_data[2].high = 110.0
        self.dt_data[4].low = 105.0
        self.dt_data[6].high = 109.9
        self.dt_data[7].close = 104.0 # The unambiguous candle that breaks the neckline

        # --- Data for Double Bottom (W shape) ---
        self.db_swing_lows = [(2, 100.0), (6, 100.1)]
        self.db_swing_highs = [(4, 105.0)]
        self.db_data = [
            Ohlcv(timestamp=datetime(2023,1,1)+timedelta(days=i), open=102, high=104, low=101, close=102) for i in range(8)
        ]
        self.db_data[2].low = 100.0
        self.db_data[4].high = 105.0
        self.db_data[6].low = 100.1
        self.db_data[7].close = 106.0 # The unambiguous candle that breaks the neckline

    def test_detect_double_top(self):
        """Test that a Double Top pattern is correctly identified."""
        signals = find_double_top_bottom_patterns(self.dt_swing_highs, self.dt_swing_lows, self.dt_data, self.mock_config)
        self.assertEqual(len(signals), 1)
        signal = signals[0]
        self.assertEqual(signal.pattern_name, "Double Top")
        self.assertEqual(signal.direction, "short")
        self.assertEqual(signal.stop_loss, 110.0)
        self.assertEqual(signal.candle.close, 104.0)

    def test_detect_double_bottom(self):
        """Test that a Double Bottom pattern is correctly identified."""
        signals = find_double_top_bottom_patterns(self.db_swing_highs, self.db_swing_lows, self.db_data, self.mock_config)
        self.assertEqual(len(signals), 1)
        signal = signals[0]
        self.assertEqual(signal.pattern_name, "Double Bottom")
        self.assertEqual(signal.direction, "long")
        self.assertEqual(signal.stop_loss, 100.0)
        self.assertEqual(signal.candle.close, 106.0)

    def test_no_pattern_dissimilar_peaks(self):
        """Test that no pattern is found if peaks are not similar in price."""
        dissimilar_highs = [(2, 110.0), (6, 112.0)] # > 1% difference
        signals = find_double_top_bottom_patterns(dissimilar_highs, self.dt_swing_lows, self.dt_data, self.mock_config)
        self.assertEqual(len(signals), 0)

if __name__ == '__main__':
    unittest.main()
