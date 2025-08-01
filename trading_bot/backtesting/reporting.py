from typing import List
import pandas as pd
from ..core.models import Trade

def generate_report(trades: List[Trade], initial_equity: float, final_equity: float):
    """
    Generates and prints a detailed performance report from a list of trades.
    """
    if not trades:
        print("No trades were made. No report to generate.")
        return

    wins = [t for t in trades if t.pnl is not None and t.pnl > 0]
    losses = [t for t in trades if t.pnl is not None and t.pnl < 0]

    total_trades = len(trades)
    win_rate = (len(wins) / total_trades) * 100 if total_trades > 0 else 0

    total_pnl = final_equity - initial_equity

    # --- Calculate Profit Factor and Averages ---
    total_profit = sum(t.pnl for t in wins)
    total_loss = abs(sum(t.pnl for t in losses))

    profit_factor = total_profit / total_loss if total_loss > 0 else 999

    avg_win = total_profit / len(wins) if wins else 0
    avg_loss = total_loss / len(losses) if losses else 0

    avg_win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 999

    # --- Print Report ---
    print("\n--- Backtest Performance Report ---")
    print("="*40)
    print(f"Initial Equity:       ${initial_equity:,.2f}")
    print(f"Final Equity:         ${final_equity:,.2f}")
    print(f"Net PnL:              ${total_pnl:,.2f}")
    print("-"*40)
    print(f"Total Trades:         {total_trades}")
    print(f"Win Rate:             {win_rate:.2f}%")
    print(f"Profit Factor:        {profit_factor:.2f}")
    print(f"Avg Win / Avg Loss:   {avg_win_loss_ratio:.2f}")
    print(f"Average Win:          ${avg_win:,.2f}")
    print(f"Average Loss:         ${avg_loss:,.2f}")
    print("="*40)

# --- Test Block ---
if __name__ == '__main__':
    from datetime import datetime
    print("--- Testing Reporting Module ---")

    mock_trades = [
        Trade(trade_id="1", instrument="A", direction="long", entry_timestamp=datetime.now(), entry_price=100, size=10, status="closed", pnl=50.0),
        Trade(trade_id="2", instrument="B", direction="long", entry_timestamp=datetime.now(), entry_price=100, size=10, status="closed", pnl=-25.0),
        Trade(trade_id="3", instrument="C", direction="long", entry_timestamp=datetime.now(), entry_price=100, size=10, status="closed", pnl=100.0),
        Trade(trade_id="4", instrument="D", direction="long", entry_timestamp=datetime.now(), entry_price=100, size=10, status="closed", pnl=-30.0),
    ]

    generate_report(mock_trades, 10000, 10095)
    # Expected:
    # PnL = 95
    # Wins = 2, Losses = 2, Win Rate = 50%
    # Total Profit = 150, Total Loss = 55
    # Profit Factor = 150 / 55 = 2.72
    # Avg Win = 75, Avg Loss = 27.5
    # Avg W/L Ratio = 75 / 27.5 = 2.72
    print("\nTest report generated. Please verify the numbers manually.")
