import pandas as pd
from typing import List
from ..core.models import Ohlcv

def load_csv_data(file_path: str) -> List[Ohlcv]:
    """
    Loads OHLCV data from a CSV file and converts it into a list of Ohlcv Pydantic models.

    Args:
        file_path (str): The path to the CSV file. The CSV should have columns:
                         'Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'.

    Returns:
        List[Ohlcv]: A list of Ohlcv data models.
    """
    try:
        df = pd.read_csv(file_path)

        # Ensure column names are in the expected format (lowercase)
        df.columns = [col.lower() for col in df.columns]

        # Convert timestamp column to datetime objects
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Convert DataFrame to a list of Pydantic models
        ohlcv_list = [Ohlcv(**row) for row in df.to_dict(orient='records')]

        return ohlcv_list

    except FileNotFoundError:
        print(f"Error: Data file not found at '{file_path}'")
        raise
    except Exception as e:
        print(f"An error occurred while loading data from '{file_path}': {e}")
        raise

# Example of how to use it (for testing)
if __name__ == '__main__':
    # Adjust the path depending on where you run the script from.
    # This assumes you run it from the root of the project.
    spy_data_path = 'data/SPY_1D.csv'
    btc_data_path = 'data/BTC-USD_1H.csv'

    print(f"--- Loading data for SPY from '{spy_data_path}' ---")
    try:
        spy_data = load_csv_data(spy_data_path)
        if spy_data:
            print(f"Successfully loaded {len(spy_data)} records.")
            print("First record:", spy_data[0])
            print("Last record:", spy_data[-1])
    except Exception as e:
        print(f"Failed to load SPY data.")

    print(f"\n--- Loading data for BTC from '{btc_data_path}' ---")
    try:
        btc_data = load_csv_data(btc_data_path)
        if btc_data:
            print(f"Successfully loaded {len(btc_data)} records.")
            print("First record:", btc_data[0])
            print("Last record:", btc_data[-1])
    except Exception as e:
        print(f"Failed to load BTC data.")
