# Price-Action Trading Bot

This repository contains the source code for a modular, backtestable, and exchange-ready trading bot that operates exclusively on price action, chart patterns, and candlestick patterns. The bot is designed with a strong emphasis on risk management, situational awareness, and deterministic, backtestable strategies.

## Core Philosophy

- **Price-Action Only:** No traditional indicators (MAs, RSI, etc.). All decisions are based on price behavior (OHLC), structure, and time.
- **Playbook-Driven:** The bot only trades precisely defined and backtested setups.
- **Assume-Wrong Bias:** A defensive posture that prioritizes capital preservation, cuts losses quickly, and scales into confirmed winners.

## Current Features

The foundational infrastructure for the bot has been established. The following components are now in place:

- **Modular Project Structure:** The codebase is organized into a clean, scalable architecture with distinct modules for core logic, data handling, pattern detection, risk management, and execution.
- **Core Data Models:** Robust, type-safe Pydantic models for essential data structures like `Ohlcv`, `Trade`, `Position`, and `Signal`.
- **Configuration Management:** A centralized configuration system using a `config.yaml` file allows for easy management of settings for the account, risk parameters, instruments, and strategies.
- **CSV Data Handler:** A data module capable of loading historical OHLCV data from CSV files, which serves as the foundation for the backtesting engine.

## Getting Started

### 1. Installation

Install the required Python packages:

```bash
pip install pydantic pyyaml pandas
```

### 2. Configuration

Modify the `configs/config.yaml` file to set up your desired parameters for account equity, risk, and target instruments.

### 3. Running a Module

You can test the functionality of the core modules by running them directly. For example, to test the data handler, first ensure you have sample data in the `data/` directory, then run:

```bash
python3 -m trading_bot.data.data_handler
```

This will load the sample data and print the first and last records.