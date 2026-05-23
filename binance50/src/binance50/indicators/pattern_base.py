import pandas as pd
from typing import List, Dict, Any, Protocol
from pydantic import BaseModel
from enum import StrEnum
from binance50.config.models import AppConfig

class PatternDirection(StrEnum):
    bullish = "bullish"
    bearish = "bearish"
    neutral = "neutral"
    unknown = "unknown"

class PatternCandidate(BaseModel):
    pattern_name: str
    symbol: str
    interval: str
    open_time: pd.Timestamp
    direction: PatternDirection
    strength: float
    source: str
    confidence: float
    metadata: Dict[str, Any] = {}
    warnings: List[str] = []

    class Config:
        arbitrary_types_allowed = True

class IndicatorContext(BaseModel):
    config: AppConfig
    symbol: str
    interval: str

class PatternDetectorProtocol(Protocol):
    @property
    def name(self) -> str:
        ...

    def is_available(self) -> bool:
        ...

    def detect(self, df: pd.DataFrame, context: IndicatorContext) -> List[PatternCandidate]:
        ...
