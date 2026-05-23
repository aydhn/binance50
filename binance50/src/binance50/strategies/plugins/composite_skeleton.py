from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.strategies.base import StrategyPluginProtocol
from binance50.strategies.context import StrategyContext
from binance50.strategies.models import (
    SignalCandidate,
    StrategyExplanation,
    StrategyPluginType,
)


class CompositeSkeletonPlugin(StrategyPluginProtocol):
    name = "composite_skeleton"
    plugin_type = StrategyPluginType.composite_skeleton
    version = "1.0.0"
    description = "Composite rule aggregator skeleton (defers scoring to Phase 14)"

    @property
    def required_features(self) -> list[str]:
        return []

    @property
    def required_prefixes(self) -> list[str]:
        return []

    def is_enabled(self, config: AppConfig) -> bool:
        return config.strategies.plugins.composite_skeleton.enabled

    def validate_config(self, config: AppConfig) -> None:
        if not config.strategies.plugins.composite_skeleton.final_signal_scoring_deferred:
            raise ValueError("Composite final_signal_scoring_deferred must be true in Phase 13")

    def validate_input(self, df: pd.DataFrame, config: AppConfig) -> None:
        pass

    def evaluate_row(self, row: pd.Series, context: StrategyContext) -> SignalCandidate | None:
        return None

    def evaluate(self, df: pd.DataFrame, context: StrategyContext) -> list[SignalCandidate]:
        # The composite aggregator in Phase 13 does not actually re-evaluate feature rows.
        # It sits here as a placeholder for Phase 14, where it will take other plugin outputs.
        # For this Phase, we just return an empty list or a mock summary if we had access to previous plugin outputs.

        # We can't access other plugin outputs within evaluate (they are run in parallel by engine)
        # The engine will group them later. For now, it returns empty.
        return []

    def explain(self, candidate: SignalCandidate) -> StrategyExplanation:
        return candidate.explanation

    def health_check(self, config: AppConfig) -> dict[str, Any]:
        return {"status": "pass"}
