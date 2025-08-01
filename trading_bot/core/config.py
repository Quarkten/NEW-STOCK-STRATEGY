import yaml
from typing import List, Literal
from pydantic import BaseModel, Field

# --- Nested Pydantic Models for Config Structure ---

class AccountSettings(BaseModel):
    equity: float = Field(..., gt=0, description="Starting account equity.")
    max_daily_loss_pct: float = Field(..., ge=0, lt=100, description="Max percentage of equity to lose in a day.")

class RiskSettings(BaseModel):
    default_per_trade_risk_pct: float = Field(..., ge=0, lt=100, description="Default risk per trade as a percentage of equity.")
    max_concurrent_exposure_pct: float = Field(..., ge=0, description="Max total exposure as a percentage of equity.")

class DoubleTopBottomSettings(BaseModel):
    price_similarity_threshold: float = Field(..., ge=0, description="Max percentage difference between the two tops/bottoms.")
    neckline_break_confirmation: float = Field(..., ge=0, description="Confirmation threshold for neckline break.")

class AbcdSettings(BaseModel):
    price_symmetry_tolerance: float = Field(..., ge=0)
    time_symmetry_tolerance: float = Field(..., ge=0)

class GartleySettings(BaseModel):
    b_point_tolerance: float = Field(..., ge=0)
    d_point_tolerance: float = Field(..., ge=0)

class PatternSettings(BaseModel):
    enable_double_top_bottom: bool
    enable_engulfing: bool
    enable_abcd: bool
    min_confluence_score: int = Field(..., ge=0, le=100, description="Minimum score to consider a signal valid.")
    double_top_bottom: DoubleTopBottomSettings
    abcd: AbcdSettings
    gartley: GartleySettings

class ExecutionSettings(BaseModel):
    broker: Literal["paper", "interactive_brokers", "binance"]
    slippage_pct: float = Field(..., ge=0, description="Slippage assumption for backtesting.")
    commission_per_trade: float = Field(..., ge=0, description="Fixed commission per trade.")

# --- Main Config Model ---

class Config(BaseModel):
    """
    Main configuration model that aggregates all settings.
    """
    account: AccountSettings
    risk: RiskSettings
    instruments: List[str]
    patterns: PatternSettings
    execution: ExecutionSettings

# --- Loader Function ---

def load_config(path: str = "configs/config.yaml") -> Config:
    """
    Loads the YAML configuration file from the given path,
    parses it, and returns a validated Config object.

    Args:
        path (str): The path to the configuration YAML file.

    Returns:
        Config: A Pydantic model instance with the loaded settings.
    """
    try:
        with open(path, 'r') as f:
            config_data = yaml.safe_load(f)
        return Config.model_validate(config_data)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at '{path}'")
        raise
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred while loading the config: {e}")
        raise

# Example of how to use it (optional, for testing)
if __name__ == '__main__':
    try:
        config = load_config()
        print("Configuration loaded successfully!")
        print("\nAccount Equity:", config.account.equity)
        print("Default Risk per Trade:", config.risk.default_per_trade_risk_pct, "%")
        print("Instruments:", config.instruments)
        print("Double Top/Bottom enabled:", config.patterns.enable_double_top_bottom)
        print("Min Confluence Score:", config.patterns.min_confluence_score)
    except Exception as e:
        print("Failed to load or validate configuration.")
