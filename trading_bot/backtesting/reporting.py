from typing import List
import pandas as pd
from ..core.models import Trade

import numpy as np
import matplotlib.pyplot as plt

def generate_report(trades: List[Trade], equity_curve: List[float], initial_equity: float):
    """
    Generates, prints, and plots a detailed performance report.
    """
    if not trades:
        print("No trades were made. No report to generate.")
        return

    final_equity = equity_curve[-1]

    # --- Basic Stats ---
    wins = [t for t in trades if t.pnl is not None and t.pnl > 0]
    losses = [t for t in trades if t.pnl is not None and t.pnl < 0]
    total_trades = len(trades)
    win_rate = (len(wins) / total_trades) * 100 if total_trades > 0 else 0
    total_pnl = final_equity - initial_equity
    total_profit = sum(t.pnl for t in wins)
    total_loss = abs(sum(t.pnl for t in losses))
    profit_factor = total_profit / total_loss if total_loss > 0 else 999
    avg_win = total_profit / len(wins) if wins else 0
    avg_loss = total_loss / len(losses) if losses else 0
    avg_win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 999

    # --- Advanced Metrics ---
    returns = pd.Series(equity_curve).pct_change().dropna()
    sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std() if returns.std() > 0 else 0

    # Max Drawdown
    peak = pd.Series(equity_curve).expanding(min_periods=1).max()
    drawdown = (pd.Series(equity_curve) - peak) / peak
    max_drawdown = drawdown.min() * 100

    # --- Print Report ---
    print("\n--- Backtest Performance Report ---")
    print("="*40)
    print(f"Initial Equity:       ${initial_equity:,.2f}")
    print(f"Final Equity:         ${final_equity:,.2f}")
    print(f"Net PnL:              ${total_pnl:,.2f} ({total_pnl/initial_equity:.2%})")
    print("-"*40)
    print(f"Total Trades:         {total_trades}")
    print(f"Win Rate:             {win_rate:.2f}%")
    print(f"Profit Factor:        {profit_factor:.2f}")
    print(f"Avg Win / Avg Loss:   {avg_win_loss_ratio:.2f}")
    print(f"Average Win:          ${avg_win:,.2f}")
    print(f"Average Loss:         ${avg_loss:,.2f}")
    print("-"*40)
    print(f"Sharpe Ratio:         {sharpe_ratio:.2f}")
    print(f"Max Drawdown:         {max_drawdown:.2f}%")
    print("="*40)

    # --- Generate Plot ---
    plt.figure(figsize=(12, 6))
    plt.plot(equity_curve)
    plt.title('Portfolio Equity Curve')
    plt.xlabel('Days')
    plt.ylabel('Equity ($)')
    plt.grid(True)
    plt.savefig('equity_curve.png')
    print("Equity curve plot saved to equity_curve.png")

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
