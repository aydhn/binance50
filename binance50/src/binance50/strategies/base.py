from typing import Any, Protocol, runtime_checkable

import pandas as pd

from binance50.config.models import AppConfig
from binance50.strategies.context import StrategyContext
from binance50.strategies.models import SignalCandidate, StrategyExplanation, StrategyPluginType


@runtime_checkable
class StrategyPluginProtocol(Protocol):
    name: str
    plugin_type: StrategyPluginType
    version: str
    required_features: list[str]
    required_prefixes: list[str]
    description: str

    def is_enabled(self, config: AppConfig) -> bool: ...

    def validate_config(self, config: AppConfig) -> None: ...

    def validate_input(self, df: pd.DataFrame, config: AppConfig) -> None: ...

    def evaluate_row(self, row: pd.Series, context: StrategyContext) -> SignalCandidate | None: ...

    def evaluate(self, df: pd.DataFrame, context: StrategyContext) -> list[SignalCandidate]: ...

    def explain(self, candidate: SignalCandidate) -> StrategyExplanation: ...

    def health_check(self, config: AppConfig) -> dict[str, Any]: ...
