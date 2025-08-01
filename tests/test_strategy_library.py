import unittest
from datetime import datetime
from trading_bot.core.models import Ohlcv
from trading_bot.strategies.strategy_library import find_add_on_signals

class TestStrategyLibrary(unittest.TestCase):

    def test_find_add_on_signal_bullish(self):
        """Test that an add-on signal is found for a profitable long position."""
        # Create data where the last two candles form a bullish engulfing pattern
        mock_data = [
            Ohlcv(timestamp=datetime(2023,1,1), open=102, high=103, low=100, close=101),
            Ohlcv(timestamp=datetime(2023,1,2), open=100, high=104, low=99, close=103)
        ]

        signal = find_add_on_signals(
            position_direction="long",
            instrument="TEST",
            data=mock_data
        )

        self.assertIsNotNone(signal)
        self.assertEqual(signal.signal_type, "add")
        self.assertEqual(signal.direction, "long")

    def test_no_add_on_signal_wrong_direction(self):
        """Test that no signal is found if the pattern is counter-trend."""
        # Bullish engulfing pattern, but we have a short position
        mock_data = [
            Ohlcv(timestamp=datetime(2023,1,1), open=102, high=103, low=100, close=101),
            Ohlcv(timestamp=datetime(2023,1,2), open=100, high=104, low=99, close=103)
        ]

        signal = find_add_on_signals(
            position_direction="short",
            instrument="TEST",
            data=mock_data
        )

        self.assertIsNone(signal)

if __name__ == '__main__':
    unittest.main()
