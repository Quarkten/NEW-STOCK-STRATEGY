from typing import List, Dict
from ..core.models import Ohlcv, Signal, Trade, Position
from ..core.config import Config
from ..execution.alpaca_executor import calculate_position_size

class BacktestAccount:
    """Represents the state of a simulated trading account."""
    def __init__(self, initial_equity: float):
        self.equity = initial_equity
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[Trade] = []
        self.equity_curve: List[float] = [initial_equity]

    def update_equity(self, new_equity: float):
        self.equity = new_equity

class Backtester:
    """
    An event-driven backtester for evaluating trading strategies on historical data.
    """
    def __init__(self, data: Dict[str, List[Ohlcv]], config: Config):
        self.data = data
        self.config = config
        self.account = BacktestAccount(config.account.equity)
        self.timestamps = self._get_master_timestamp_list()

    def _get_master_timestamp_list(self):
        """Creates a master list of all unique hourly timestamps across all data feeds."""
        all_timestamps = set()
        for symbol_data in self.data.values():
            for candle in symbol_data['hourly']:
                all_timestamps.add(candle.timestamp)
        return sorted(list(all_timestamps))

    def run(self):
        """
        Runs the backtest simulation over the entire historical data period.
        """
        print("--- Starting Backtest ---")

        # Get a master list of unique days, not hours
        self.dates = sorted(list(set(c.timestamp.date() for s_data in self.data.values() for c in s_data['daily'])))

        for date in self.dates:
            # Get all hourly candles for the current day
            hourly_candles_for_day = {
                symbol: [c for c in self.data[symbol]['hourly'] if c.timestamp.date() == date]
                for symbol in self.data.keys()
            }

            # Loop through the hours of the day
            for hour in range(24): # Simplistic loop, a real system would use market hours
                for symbol in self.data.keys():
                    current_hourly_candle = next((c for c in hourly_candles_for_day[symbol] if c.timestamp.hour == hour), None)
                    if not current_hourly_candle:
                        continue

                    # Get all data up to the current point in time
                    daily_data_to_date = [c for c in self.data[symbol]['daily'] if c.timestamp.date() <= date]
                    hourly_data_to_date = [c for c in self.data[symbol]['hourly'] if c.timestamp <= current_hourly_candle.timestamp]

                    # --- 1. Check for SL/TP on open positions ---
                    if symbol in self.account.positions:
                        self._check_for_exit(symbol, current_hourly_candle)

                    # --- 2. Run strategy logic ---
                    from ..strategies.strategy_library import find_signals
                    if symbol not in self.account.positions:
                        signals = find_signals(instrument=symbol, daily_data=daily_data_to_date, hourly_data=hourly_data_to_date, config=self.config)
                        if signals:
                            self._execute_signal(signals[0], current_hourly_candle)

            # --- Mark-to-Market at the end of the day ---
            unrealized_pnl = 0
            for position in self.account.positions.values():
                latest_candle_for_pos = next((c for c in reversed(self.data[position.instrument]['daily']) if c.timestamp.date() <= date), None)
                if latest_candle_for_pos:
                    position.update_pnl(latest_candle_for_pos.close)
                    unrealized_pnl += position.unrealized_pnl

            current_portfolio_value = self.account.equity + unrealized_pnl
            self.account.equity_curve.append(current_portfolio_value)

        print("--- Backtest Complete ---")
        self.generate_report()

    def _execute_signal(self, signal: Signal, candle: Ohlcv):
        """Simulates the execution of a trade signal."""

        entry_price = candle.close
        commission = self.config.execution.commission_per_trade

        # Use the equity at the start of the day for position sizing to avoid compounding unrealized PnL
        equity_for_sizing = next((e for e in reversed(self.account.equity_curve)), self.account.equity)

        qty = calculate_position_size(
            account_equity=equity_for_sizing,
            risk_per_trade_pct=self.config.risk.default_per_trade_risk_pct,
            entry_price=entry_price,
            stop_loss_price=signal.stop_loss
        )

        if qty <= 0:
            return

        # Create the trade record
        trade = Trade(
            trade_id=f"trade_{len(self.account.trade_history)+1}",
            instrument=signal.instrument,
            direction=signal.direction,
            entry_timestamp=candle.timestamp,
            entry_price=entry_price,
            stop_loss_price=signal.stop_loss,
            size=qty,
            status="open"
        )

        # Deduct commission and add trade to history
        self.account.equity -= commission
        self.account.trade_history.append(trade)

        # --- Update or Create Position ---
        if signal.signal_type == "add":
            if signal.instrument in self.account.positions:
                position = self.account.positions[signal.instrument]

                # Recalculate average entry price
                new_total_size = position.size + qty
                new_total_cost = (position.average_entry_price * position.size) + (entry_price * qty)
                position.average_entry_price = new_total_cost / new_total_size
                position.size = new_total_size

                print(f"{candle.timestamp.date()}: ADDED TO {signal.direction.upper()} "
                      f"{signal.instrument} @ {entry_price:.2f} (New Size: {new_total_size:.4f})")
            else:
                # Should not happen, but handle gracefully
                print("Warning: Received 'add' signal but no open position found. Ignoring.")

        elif signal.signal_type == "entry":
            self.account.positions[signal.instrument] = Position(
                instrument=signal.instrument,
                direction=signal.direction,
                size=qty,
                average_entry_price=entry_price
            )
            print(f"{candle.timestamp.date()}: EXECUTED {signal.direction.upper()} "
                  f"{signal.instrument} @ {entry_price:.2f} (Qty: {qty:.4f})")

    def _check_for_exit(self, symbol: str, candle: Ohlcv):
        """Checks if an open position should be closed due to SL/TP."""
        position = self.account.positions[symbol]

        # Find the open trade corresponding to this position
        open_trade = next((t for t in self.account.trade_history if t.instrument == symbol and t.status == "open"), None)
        if not open_trade:
            return # Should not happen if position exists

        exit_price = 0
        exit_reason = ""

        # --- Trailing Stop-Loss Logic ---
        initial_risk = abs(open_trade.entry_price - open_trade.stop_loss_price)
        current_pnl_per_share = candle.close - open_trade.entry_price if position.direction == "long" else open_trade.entry_price - candle.close

        # Use a trailing stop once the trade is profitable by at least 1R
        if current_pnl_per_share >= initial_risk:
            # Get the recent hourly data to determine the trailing stop
            recent_hourly_data = self.data[symbol]['hourly']
            if len(recent_hourly_data) < 4: return # Not enough data to trail

            # Trail stop below the low of the last 3 candles for a long
            if position.direction == "long":
                new_stop = min(c.low for c in recent_hourly_data[-4:-1])
                if new_stop > open_trade.stop_loss_price:
                    open_trade.stop_loss_price = new_stop
            # Trail stop above the high of the last 3 candles for a short
            else: # short
                new_stop = max(c.high for c in recent_hourly_data[-4:-1])
                if new_stop < open_trade.stop_loss_price:
                    open_trade.stop_loss_price = new_stop

        # --- Check for Exit ---
        stop_loss_price = open_trade.stop_loss_price
        if position.direction == "long" and candle.low <= stop_loss_price:
            exit_price = stop_loss_price
            exit_reason = "Trailing Stop" if current_pnl_per_share > 0 else "Stop-Loss"
        elif position.direction == "short" and candle.high >= stop_loss_price:
            exit_price = stop_loss_price
            exit_reason = "Trailing Stop" if current_pnl_per_share > 0 else "Stop-Loss"

        if exit_price > 0:
            # Close the trade
            open_trade.close_trade(timestamp=candle.timestamp, price=exit_price)
            self.account.update_equity(self.account.equity + open_trade.pnl)
            del self.account.positions[symbol]
            print(f"{candle.timestamp.date()}: EXIT {position.direction.upper()} "
                  f"{symbol} @ {exit_price:.2f} for {exit_reason}. PnL: ${open_trade.pnl:.2f}")

    def generate_report(self):
        """Generates and prints a summary of the backtest performance."""
        from .reporting import generate_report
        generate_report(
            trades=self.account.trade_history,
            equity_curve=self.account.equity_curve,
            initial_equity=self.config.account.equity
        )

if __name__ == '__main__':
    from datetime import datetime
    from ..core.config import Config, AccountSettings, RiskSettings, PatternSettings, DoubleTopBottomSettings, AbcdSettings, GartleySettings, ExecutionSettings

    print("--- Testing Backtester Engine ---")

    # 1. Create Dummy Config
    dummy_config = Config(
        account=AccountSettings(equity=100000, max_daily_loss_pct=2.0),
        risk=RiskSettings(default_per_trade_risk_pct=1.0, max_concurrent_exposure_pct=5.0),
        instruments=["DUMMY"],
        patterns=PatternSettings(enable_double_top_bottom=True, enable_engulfing=True, enable_abcd=True, min_confluence_score=60, double_top_bottom=DoubleTopBottomSettings(price_similarity_threshold=0.01, neckline_break_confirmation=0.005), abcd=AbcdSettings(price_symmetry_tolerance=0.15, time_symmetry_tolerance=0.25), gartley=GartleySettings(b_point_tolerance=0.05, d_point_tolerance=0.05)),
        execution=ExecutionSettings(broker="paper", slippage_pct=0.0, commission_per_trade=1.0)
    )

    # 2. Create Dummy Data
    dummy_data = {
        "DUMMY": [
            Ohlcv(timestamp=datetime(2023,1,1), open=100, high=102, low=98, close=101),
            Ohlcv(timestamp=datetime(2023,1,2), open=101, high=103, low=99, close=102),
            Ohlcv(timestamp=datetime(2023,1,3), open=102, high=104, low=100, close=103),
            Ohlcv(timestamp=datetime(2023,1,4), open=103, high=105, low=101, close=104),
            Ohlcv(timestamp=datetime(2023,1,5), open=104, high=106, low=102, close=105), # Signal day
            Ohlcv(timestamp=datetime(2023,1,6), open=105, high=107, low=103, close=106),
            Ohlcv(timestamp=datetime(2023,1,7), open=106, high=108, low=101, close=107), # Stop-loss hit day (low is 101, SL is 102)
        ]
    }

    # 3. Run Backtest
    backtester = Backtester(data=dummy_data, config=dummy_config)
    backtester.run()

    # 4. Assert Results
    account_state = backtester.account
    final_trade = account_state.trade_history[0]

    print(f"\nFinal assertion: Found {len(account_state.trade_history)} trades.")
    assert len(account_state.trade_history) == 1, "Test failed: Should have executed exactly one trade."
    assert final_trade.status == "closed", "Test failed: Trade should have been closed."
    assert final_trade.pnl is not None, "Test failed: PnL should be calculated."
    # Entry=105, SL=102. Risk per share = 3. Qty = (100k*1%)/3 = 333.33. PnL = (102-105)*333.33 = -999.99
    # Equity = 100k - 1 (comm) - 999.99 = 98999.01
    assert abs(account_state.equity - 98999.01) < 0.01, f"Test failed: Final equity is {account_state.equity}"
    print("Backtester engine test passed successfully!")
