import unittest
from unittest.mock import patch, MagicMock
from trading_bot.core.models import Signal
from trading_bot.core.config import load_config
from trading_bot.execution.alpaca_executor import calculate_position_size, place_bracket_order

class TestAlpacaExecutor(unittest.TestCase):

    def setUp(self):
        """Load a sample config for testing."""
        # This will fail if the main config.yaml is not present, but for now it's ok
        # A better approach would be to create a dummy config like in test_config.py
        try:
            self.config = load_config()
        except FileNotFoundError:
            # Create a dummy config if the main one doesn't exist
            from trading_bot.core.config import Config, AccountSettings, RiskSettings, PatternSettings, DoubleTopBottomSettings, AbcdSettings, GartleySettings, ExecutionSettings
            self.config = Config(
                account=AccountSettings(equity=50000, max_daily_loss_pct=2.0),
                risk=RiskSettings(default_per_trade_risk_pct=1.0, max_concurrent_exposure_pct=5.0),
                instruments=["DUMMY"],
                patterns=PatternSettings(enable_double_top_bottom=True, enable_engulfing=True, enable_abcd=True, min_confluence_score=60, double_top_bottom=DoubleTopBottomSettings(price_similarity_threshold=0.01, neckline_break_confirmation=0.005), abcd=AbcdSettings(price_symmetry_tolerance=0.15, time_symmetry_tolerance=0.25), gartley=GartleySettings(b_point_tolerance=0.05, d_point_tolerance=0.05)),
                execution=ExecutionSettings(broker="paper", slippage_pct=0.001, commission_per_trade=1.0)
            )

    def test_calculate_position_size(self):
        """Test the position sizing calculation."""
        size = calculate_position_size(
            account_equity=100000.0,
            risk_per_trade_pct=1.0,  # Risking $1000
            entry_price=150.0,
            stop_loss_price=140.0  # $10 risk per share
        )
        # Expected size = $1000 / $10 = 100 shares
        self.assertEqual(size, 100.0)

    @patch('trading_bot.execution.alpaca_executor.REST')
    def test_place_bracket_order_long(self, mock_api_class):
        """Test that a long bracket order is submitted with the correct parameters."""
        mock_api = MagicMock()

        # Mock the return values for the API calls
        mock_account = MagicMock()
        mock_account.equity = "100000"
        mock_api.get_account.return_value = mock_account

        mock_trade = MagicMock()
        mock_trade.price = 150.0
        mock_api.get_latest_trade.return_value = mock_trade

        mock_order = MagicMock()
        mock_order.id = "test_order_id_123"
        mock_api.submit_order.return_value = mock_order

        from trading_bot.core.models import Ohlcv
        mock_candle = Ohlcv(timestamp="2023-01-01T09:30:00", open=148, high=151, low=147, close=150)

        signal = Signal(
            instrument="SPY",
            timestamp="2023-01-01T10:00:00",
            pattern_name="test_pattern",
            signal_type="entry",
            direction="long",
            confluence_score=80,
            stop_loss=140.0,
            candle=mock_candle
        )

        result_order = place_bracket_order(signal, self.config, mock_api)

        self.assertIsNotNone(result_order)
        self.assertEqual(result_order.id, "test_order_id_123")

        # Assert that submit_order was called once with the correct arguments
        mock_api.submit_order.assert_called_once()
        call_args = mock_api.submit_order.call_args[1]

        self.assertEqual(call_args['symbol'], "SPY")
        self.assertEqual(call_args['side'], "buy")
        self.assertEqual(call_args['qty'], 100) # Based on test_calculate_position_size
        self.assertEqual(call_args['order_class'], "bracket")
        self.assertAlmostEqual(call_args['stop_loss']['stop_price'], 139.93)
        self.assertAlmostEqual(call_args['take_profit']['limit_price'], 170.0) # Entry + 2*Risk

if __name__ == '__main__':
    unittest.main()
