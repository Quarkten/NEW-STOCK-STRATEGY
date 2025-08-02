import os
from typing import Optional
from alpaca_trade_api.rest import REST, TimeFrame
from alpaca_trade_api.entity import Order
from ..core.models import Signal
from ..core.config import Config

def get_alpaca_api() -> REST:
    """Initializes and returns the Alpaca REST API client."""
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    base_url = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

    if not api_key or not secret_key:
        raise ValueError("Alpaca API credentials must be set as environment variables.")

    return REST(key_id=api_key, secret_key=secret_key, base_url=base_url, api_version='v2')

def calculate_position_size(account_equity: float, base_risk_pct: float, entry_price: float, stop_loss_price: float, confluence_score: int) -> float:
    """
    Calculates the number of shares to trade based on risk parameters and signal conviction.
    """
    # Adjust risk based on confluence score
    if confluence_score > 85:
        adjusted_risk_pct = base_risk_pct * 1.5
    elif confluence_score > 70:
        adjusted_risk_pct = base_risk_pct
    else:
        adjusted_risk_pct = base_risk_pct * 0.5

    risk_amount = account_equity * (adjusted_risk_pct / 100.0)
    risk_per_share = abs(entry_price - stop_loss_price)

    if risk_per_share <= 0:
        return 0.0

    quantity = risk_amount / risk_per_share
    return round(quantity, 4)

def place_bracket_order(
    signal: Signal,
    config: Config,
    api: REST
) -> Optional[Order]:
    """
    Places a bracket order (entry, take-profit, stop-loss) on Alpaca.

    Args:
        signal (Signal): The trading signal containing direction, symbol, etc.
        config (Config): The application's configuration object.
        api (REST): The authenticated Alpaca API client.

    Returns:
        Optional[Order]: The Alpaca Order entity if successful, otherwise None.
    """
    try:
        # 1. Get current account information and price
        account = api.get_account()
        # Use the close of the signal candle as the estimated entry price
        entry_price = signal.candle.close

        if not signal.stop_loss:
            print("Error: Signal must have a stop_loss price to place a bracket order.")
            return None

        # 2. Calculate position size
        quantity = calculate_position_size(
            account_equity=float(account.equity),
            base_risk_pct=config.risk.default_per_trade_risk_pct,
            entry_price=entry_price,
            stop_loss_price=signal.stop_loss,
            confluence_score=signal.confluence_score
        )

        if quantity <= 0:
            print(f"Calculated quantity is {quantity}. Order not placed.")
            return None

        # 3. Define the bracket order parameters
        side = 'buy' if signal.direction == 'long' else 'sell'

        # Calculate take profit based on a 2:1 reward:risk ratio and add buffers
        risk_per_share = abs(entry_price - signal.stop_loss)
        # Use a more substantial buffer, e.g., 0.05% of the price
        price_buffer = entry_price * 0.0005

        if side == 'buy':
            stop_loss_price = signal.stop_loss - price_buffer
            take_profit_price = entry_price + (2 * risk_per_share)
        else: # side == 'sell'
            stop_loss_price = signal.stop_loss + price_buffer
            take_profit_price = entry_price - (2 * risk_per_share)

        order_data = {
            "symbol": signal.instrument,
            "qty": quantity,
            "side": side,
            "type": "market",
            "time_in_force": "day", # Use 'day' for fractional shares
            "order_class": "bracket",
            "stop_loss": {
                "stop_price": round(stop_loss_price, 2)
            },
            "take_profit": {
                "limit_price": round(take_profit_price, 2)
            }
        }

        print(f"Placing order: {order_data}")
        order = api.submit_order(**order_data)
        print(f"Successfully placed order: {order.id}")
        return order

    except Exception as e:
        print(f"An error occurred while placing order for {signal.instrument}: {e}")
        return None
