# Price-Action Trading Bot

This repository contains the source code for a modular, backtestable, and exchange-ready trading bot that operates exclusively on price action, chart patterns, and candlestick patterns. The bot is designed with a strong emphasis on risk management, situational awareness, and deterministic, backtestable strategies.

## Core Philosophy

- **Price-Action Only:** No traditional indicators (MAs, RSI, etc.). All decisions are based on price behavior (OHLC), structure, and time.
- **Playbook-Driven:** The bot only trades precisely defined and backtested setups.
- **Assume-Wrong Bias:** A defensive posture that prioritizes capital preservation, cuts losses quickly, and scales into confirmed winners.
- **Asymmetric Risk:** The system is designed to let profitable trades run (via trailing stops) while cutting losers at a predefined risk point, creating an asymmetric risk/reward profile.

## Features

This bot is a complete, end-to-end system with the following features:

#### 1. Data Handling
- Connects to the Alpaca API to fetch real historical OHLCV data for equities.
- A robust, Pydantic-based data model for all core objects (`Ohlcv`, `Signal`, `Trade`, `Position`).

#### 2. Market Analysis & Pattern Recognition
- **Market Regime Detection:** Analyzes price structure (swing highs/lows) to determine if the market is in an **Uptrend**, **Downtrend**, or **Ranging**.
- **Pattern Library:**
  - **Candlestick Patterns:** Bullish & Bearish Engulfing.
  - **Geometric Patterns:** AB=CD (Measured Moves).
  - **Harmonic Patterns:** Gartley "222".
- **Fibonacci Utilities:** Core functions to calculate key Fibonacci retracement and extension levels.

#### 3. Signal Generation & Filtering
- **Regime Filter:** The core strategy only takes trades that align with the detected market trend (longs in uptrends, shorts in downtrends).
- **Confluence Scorer:** Every potential trade is scored (0-100) based on a checklist of confirming factors (e.g., Fibonacci confluence, volume, candle strength). Only trades that pass a configurable minimum score are considered.

#### 4. Trade Execution & Management
- **Alpaca Integration:** Can submit paper trading orders directly to the Alpaca API.
- **Dynamic Position Sizing:** Automatically calculates trade size based on a configurable risk percentage of account equity.
- **Bracket Orders:** Submits entry orders with associated stop-loss and take-profit targets.
- **Dynamic Trailing Stops:** Once a trade is profitable by 1R, the system automatically trails the stop-loss to lock in profits while allowing the trade to run.
- **Scale-In Logic:** Can identify low-risk continuation patterns to add to existing winning positions.

#### 5. Risk Management
- **Per-Trade Risk:** Risk for each trade is strictly defined by the stop-loss placement.
- **Portfolio-Level Risk:**
  - **Max Open Positions:** Limits the number of concurrent trades.
  - **Max Daily Drawdown:** Halts all new trading for the day if the account equity drops by a configurable percentage.

#### 6. Backtesting Engine
- **Event-Driven:** A powerful backtester processes historical data day-by-day, simulating the entire trading workflow.
- **Performance Reporting:** At the end of a backtest, it generates a detailed report with key metrics like Net PnL, Win Rate, Profit Factor, and Average Win/Loss ratio.

#### 7. Code Quality
- **Unit Test Suite:** The entire codebase is covered by a comprehensive suite of unit tests using Python's `unittest` framework, with mocking for external services.
- **Modular Architecture:** The code is organized into logical, decoupled modules for data, patterns, execution, backtesting, and risk.

## How to Run a Backtest

1.  **Set Up API Keys:**
    -   The bot requires an Alpaca Paper Trading account.
    -   Set your API keys as environment variables:
        ```bash
        export ALPACA_API_KEY="YOUR_KEY"
        export ALPACA_SECRET_KEY="YOUR_SECRET_KEY"
        export ALPACA_BASE_URL="https://paper-api.alpaca.markets"
        ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    # (Note: A requirements.txt file would need to be created)
    # For now, install manually:
    pip install pydantic pyyaml pandas alpaca-trade-api python-dotenv
    ```

3.  **Configure the Backtest:**
    -   Open `configs/config.yaml`.
    -   Modify the `instruments` list, the date range in `run_backtest.py`, and any risk or pattern parameters you wish to test.

4.  **Run the Backtest:**
    ```bash
    python3 run_backtest.py
    ```
    The script will fetch the latest data, run the simulation, and print a detailed performance report to the console.

## Configuration (`configs/config.yaml`)

- **`account`**:
  - `equity`: The starting equity for the backtest.
  - `max_daily_loss_pct`: The max percentage of equity that can be lost in one day.
- **`risk`**:
  - `default_per_trade_risk_pct`: The percentage of total equity to risk on a single trade.
  - `max_open_positions`: The maximum number of trades allowed to be open at once.
  - `max_daily_drawdown_pct`: The master circuit-breaker; halts all new trading for the day if breached.
- **`instruments`**: A list of equity symbols to trade (e.g., "SPY", "QQQ").
- **`patterns`**:
  - `enable_*`: Feature flags to turn specific pattern detectors on or off.
  - `min_confluence_score`: The minimum score (0-100) a signal must have to be traded.
  - `*_tolerances`: Specific numerical tolerances for how "perfect" a pattern must be.
- **`execution`**:
  - `commission_per_trade`: A flat fee to simulate commission costs in the backtester.