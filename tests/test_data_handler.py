import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from trading_bot.core.data_handler import fetch_historical_data
from trading_bot.core.models import Ohlcv
from alpaca_trade_api.rest import TimeFrame

class TestDataHandler(unittest.TestCase):

    @patch('trading_bot.core.data_handler.get_alpaca_api_client')
    def test_fetch_historical_data_success(self, mock_get_api_client):
        """Test successful fetching and parsing of data from a mocked API call."""

        # 1. Create a mock DataFrame that mimics the Alpaca API response
        mock_data = {
            'open': [100, 102],
            'high': [101, 103],
            'low': [99, 101],
            'close': [100.5, 102.5],
            'volume': [10000, 12000],
            'trade_count': [100, 120],
            'vwap': [100.2, 102.2]
        }
        mock_index = pd.to_datetime(['2023-01-01T09:30:00-04:00', '2023-01-02T09:30:00-04:00'])
        mock_df = pd.DataFrame(mock_data, index=mock_index)
        mock_df.index.name = 'timestamp' # This is the crucial fix

        # 2. Configure the mock API client
        mock_api_instance = MagicMock()
        mock_api_instance.get_bars.return_value.df = mock_df
        mock_get_api_client.return_value = mock_api_instance

        # 3. Call the function we are testing
        result = fetch_historical_data(
            symbol="SPY",
            timeframe=TimeFrame.Day,
            start_date="2023-01-01",
            end_date="2023-01-02"
        )

        # 4. Assert the results
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], Ohlcv)
        self.assertEqual(result[0].open, 100)
        self.assertEqual(result[1].close, 102.5)
        # Check that the timestamp is naive, as expected by our model
        self.assertIsNone(result[0].timestamp.tzinfo)

    @patch('trading_bot.core.data_handler.get_alpaca_api_client')
    def test_fetch_historical_data_api_error(self, mock_get_api_client):
        """Test that the function handles an API exception gracefully."""

        # Configure the mock to raise an exception
        mock_api_instance = MagicMock()
        mock_api_instance.get_bars.side_effect = Exception("API connection failed")
        mock_get_api_client.return_value = mock_api_instance

        # Call the function and assert it returns an empty list
        result = fetch_historical_data(
            symbol="FAIL",
            timeframe=TimeFrame.Day,
            start_date="2023-01-01",
            end_date="2023-01-02"
        )
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()
