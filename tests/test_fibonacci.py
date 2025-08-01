import unittest
from trading_bot.patterns.fibonacci import calculate_fib_levels

class TestFibonacci(unittest.TestCase):

    def test_calculate_fib_levels_uptrend(self):
        """Test Fibonacci levels for an uptrend swing (high=110, low=100)."""
        high = 110.0
        low = 100.0
        levels = calculate_fib_levels(high, low)

        # Test retracements (price pulling back from 110)
        self.assertAlmostEqual(levels['uptrend_retracements']['0.382'], 106.18)
        self.assertAlmostEqual(levels['uptrend_retracements']['0.500'], 105.0)
        self.assertAlmostEqual(levels['uptrend_retracements']['0.618'], 103.82)

        # Test extensions (price moving beyond 110)
        self.assertAlmostEqual(levels['uptrend_extensions']['1.272'], 112.72)
        self.assertAlmostEqual(levels['uptrend_extensions']['1.618'], 116.18)

    def test_calculate_fib_levels_downtrend(self):
        """Test Fibonacci levels for a downtrend swing (high=110, low=100)."""
        high = 110.0
        low = 100.0
        levels = calculate_fib_levels(high, low)

        # Test retracements (price pulling back from 100)
        self.assertAlmostEqual(levels['downtrend_retracements']['0.382'], 103.82)
        self.assertAlmostEqual(levels['downtrend_retracements']['0.500'], 105.0)
        self.assertAlmostEqual(levels['downtrend_retracements']['0.618'], 106.18)

        # Test extensions (price moving below 100)
        self.assertAlmostEqual(levels['downtrend_extensions']['1.272'], 97.28)
        self.assertAlmostEqual(levels['downtrend_extensions']['1.618'], 93.82)

    def test_invalid_input(self):
        """Test that an invalid input (high <= low) raises a ValueError."""
        with self.assertRaises(ValueError):
            calculate_fib_levels(100.0, 110.0)
        with self.assertRaises(ValueError):
            calculate_fib_levels(100.0, 100.0)

if __name__ == '__main__':
    unittest.main()
