import unittest
import os
from trading_bot.core.config import load_config, Config

class TestConfig(unittest.TestCase):

    def setUp(self):
        """Set up a dummy config file for testing."""
        self.config_path = "tests/test_config.yaml"
        with open(self.config_path, "w") as f:
            f.write("""
account:
  equity: 100000.0
  max_daily_loss_pct: 2.0

risk:
  default_per_trade_risk_pct: 1.0
  max_concurrent_exposure_pct: 5.0

instruments:
  - "SPY"
  - "QQQ"

patterns:
  enable_double_top_bottom: true
  enable_engulfing: true
  enable_abcd: true
  min_confluence_score: 60
  double_top_bottom:
    price_similarity_threshold: 0.01
    neckline_break_confirmation: 0.005
  abcd:
    price_symmetry_tolerance: 0.15
    time_symmetry_tolerance: 0.25
  gartley:
    b_point_tolerance: 0.05
    d_point_tolerance: 0.05

execution:
  broker: "paper"
  slippage_pct: 0.001
  commission_per_trade: 1.0
""")

    def tearDown(self):
        """Remove the dummy config file after tests."""
        os.remove(self.config_path)

    def test_load_config(self):
        """Test that the configuration loads correctly and returns a Config object."""
        config = load_config(path=self.config_path)

        # Check if the returned object is of the correct type
        self.assertIsInstance(config, Config)

        # Check a few values to ensure they were parsed correctly
        self.assertEqual(config.account.equity, 100000.0)
        self.assertEqual(config.risk.default_per_trade_risk_pct, 1.0)
        self.assertIn("SPY", config.instruments)
        self.assertEqual(config.patterns.gartley.b_point_tolerance, 0.05)
        self.assertEqual(config.execution.broker, "paper")

    def test_load_config_file_not_found(self):
        """Test that a FileNotFoundError is raised for a non-existent file."""
        with self.assertRaises(FileNotFoundError):
            load_config(path="non_existent_file.yaml")

if __name__ == '__main__':
    unittest.main()
