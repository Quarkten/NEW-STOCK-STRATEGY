from typing import Dict

def calculate_fib_levels(high: float, low: float) -> Dict[str, float]:
    """
    Calculates key Fibonacci retracement and extension levels based on a high and low price.

    Args:
        high (float): The high price of the swing.
        low (float): The low price of the swing.

    Returns:
        Dict[str, float]: A dictionary containing the calculated Fibonacci levels.
                          Keys are 'retracements' and 'extensions'.
    """
    if high <= low:
        raise ValueError("High must be greater than low to calculate Fibonacci levels.")

    price_range = high - low

    # Standard retracement levels
    retracements = {
        '0.236': high - (price_range * 0.236),
        '0.382': high - (price_range * 0.382),
        '0.500': high - (price_range * 0.500),
        '0.618': high - (price_range * 0.618),
        '0.786': high - (price_range * 0.786),
    }

    # Standard extension levels
    extensions = {
        '1.272': high + (price_range * 0.272),
        '1.618': high + (price_range * 0.618),
        '2.618': high + (price_range * 1.618),
    }

    # For downtrends, the calculation is reversed
    # We can provide both so the caller can choose based on trend context
    downtrend_retracements = {
        '0.236': low + (price_range * 0.236),
        '0.382': low + (price_range * 0.382),
        '0.500': low + (price_range * 0.500),
        '0.618': low + (price_range * 0.618),
        '0.786': low + (price_range * 0.786),
    }

    downtrend_extensions = {
        '1.272': low - (price_range * 0.272),
        '1.618': low - (price_range * 0.618),
        '2.618': low - (price_range * 1.618),
    }

    return {
        'uptrend_retracements': retracements,
        'uptrend_extensions': extensions,
        'downtrend_retracements': downtrend_retracements,
        'downtrend_extensions': downtrend_extensions,
    }

# --- Test Block ---
if __name__ == '__main__':
    print("--- Testing Fibonacci Level Calculation ---")

    test_high = 110.0
    test_low = 100.0

    print(f"Calculating levels for High={test_high}, Low={test_low}")

    try:
        levels = calculate_fib_levels(test_high, test_low)

        # Test uptrend retracements (price moving down from 110)
        assert abs(levels['uptrend_retracements']['0.500'] - 105.0) < 0.001, "Uptrend 50% retracement failed"
        print("Uptrend 50% retracement is:", round(levels['uptrend_retracements']['0.500'], 2))

        # Test uptrend extensions (price moving up from 110)
        assert abs(levels['uptrend_extensions']['1.618'] - 116.18) < 0.001, "Uptrend 1.618 extension failed"
        print("Uptrend 1.618 extension is:", round(levels['uptrend_extensions']['1.618'], 2))

        # Test downtrend retracements (price moving up from 100)
        assert abs(levels['downtrend_retracements']['0.382'] - 103.82) < 0.001, "Downtrend 38.2% retracement failed"
        print("Downtrend 38.2% retracement is:", round(levels['downtrend_retracements']['0.382'], 2))

        print("\nAll Fibonacci calculation tests passed successfully!")

    except ValueError as e:
        print(f"Test failed: {e}")
    except AssertionError as e:
        print(f"Test assertion failed: {e}")
