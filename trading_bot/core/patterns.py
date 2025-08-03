from pydantic import BaseModel
from .models import Ohlcv

class Pattern(BaseModel):
    """Represents a detected pattern."""
    pattern_type: str
    pattern_name: str
    candle: Ohlcv
