from datetime import datetime
from alpaca_trade_api.entity import Order
from .models import Signal

def log_trade(
    signal: Signal,
    order: Order,
    reason: str,
    journal_file: str = "trading_journal.md"
):
    """
    Logs the details of a trade to a Markdown file.

    Args:
        signal (Signal): The signal that triggered the trade.
        order (Order): The order object returned by the Alpaca API.
        reason (str): A human-readable reason for taking the trade.
        journal_file (str): The path to the journal file.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = f"""
### Trade Executed: {signal.instrument} ({signal.direction.upper()})

- **Timestamp:** {timestamp}
- **Instrument:** {signal.instrument}
- **Direction:** {signal.direction.upper()}
- **Pattern:** {signal.pattern_name}
- **Reason:** {reason}

**Order Details:**
- **Alpaca Order ID:** `{order.id}`
- **Quantity:** `{order.qty}`
- **Type:** `{order.order_type}`
- **Status:** `{order.status}`

**Risk Management:**
- **Entry Price (Approx):** `{order.filled_avg_price or 'N/A (Market Order)'}`
- **Stop Loss:** `{signal.stop_loss}`

---
"""

    try:
        with open(journal_file, "a") as f:
            f.write(log_entry)
        print(f"Trade for {signal.instrument} logged successfully to {journal_file}.")
    except IOError as e:
        print(f"Error: Could not write to journal file {journal_file}: {e}")

# --- Test Block ---
if __name__ == '__main__':
    print("--- Testing Journal Logger ---")

    # Create mock objects for testing
    mock_signal = Signal(
        instrument="TSLA",
        timestamp="2023-01-01T12:00:00",
        pattern_name="Bullish Engulfing",
        signal_type="entry",
        direction="long",
        confluence_score=75,
        stop_loss=200.0
    )

    # A mock Order object needs to have the attributes our function uses
    class MockOrder:
        def __init__(self, id, qty, order_type, status, filled_avg_price):
            self.id = id
            self.qty = qty
            self.order_type = order_type
            self.status = status
            self.filled_avg_price = filled_avg_price

    mock_order_obj = MockOrder(
        id="mock_order_id_456",
        qty="15.5",
        order_type="market",
        status="accepted",
        filled_avg_price=None
    )

    test_journal_file = "test_journal.md"

    # Clean up old test file if it exists
    import os
    if os.path.exists(test_journal_file):
        os.remove(test_journal_file)

    log_trade(mock_signal, mock_order_obj, "Signal confirmed by high volume.", journal_file=test_journal_file)

    # Verify the file was created and has content
    assert os.path.exists(test_journal_file)
    with open(test_journal_file, "r") as f:
        content = f.read()
        assert "TSLA (LONG)" in content
        assert "mock_order_id_456" in content

    print("\nJournal test passed. Check the content of 'test_journal.md'.")
    os.remove(test_journal_file) # Clean up
