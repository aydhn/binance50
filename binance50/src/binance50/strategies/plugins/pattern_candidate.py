from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.strategies.base import StrategyPluginProtocol
from binance50.strategies.candidates import build_signal_candidate
from binance50.strategies.context import StrategyContext
from binance50.strategies.explanations import build_explanation_summary
from binance50.strategies.models import (
    SignalCandidate,
    StrategyCandidateStrength,
    StrategyDirection,
    StrategyExplanation,
    StrategyPluginType,
)


class PatternCandidatePlugin(StrategyPluginProtocol):
    name = "pattern_candidate"
    plugin_type = StrategyPluginType.pattern_candidate
    version = "1.0.0"
    description = "Pattern skeleton candidate"

    @property
    def required_features(self) -> list[str]:
        return []

    @property
    def required_prefixes(self) -> list[str]:
        return ["pat_"]

    def is_enabled(self, config: AppConfig) -> bool:
        return config.strategies.plugins.pattern_candidate.enabled

    def validate_config(self, config: AppConfig) -> None:
        pass

    def validate_input(self, df: pd.DataFrame, config: AppConfig) -> None:
        pass

    def evaluate_row(self, row: pd.Series, context: StrategyContext) -> SignalCandidate | None:
        return None

    def evaluate(self, df: pd.DataFrame, context: StrategyContext) -> list[SignalCandidate]:
        candidates = []
        pcfg = context.config.strategies.plugins.pattern_candidate

        pat_cols = [c for c in df.columns if c.startswith("pat_")]

        for idx, row in df.iterrows():
            for c in pat_cols:
                val = row.get(c, 0)
                if pd.isna(val) or val == 0:
                    continue

                direction = StrategyDirection.bullish if val > 0 else StrategyDirection.bearish
                confidence = abs(val)

                if confidence < pcfg.min_pattern_confidence:
                    continue

                from binance50.strategies.conditions import build_condition_evidence

                evidence = [
                    build_condition_evidence(
                        c, "gte", pcfg.min_pattern_confidence, confidence, True
                    )
                ]

                explanation = StrategyExplanation(
                    summary=build_explanation_summary(self.name, direction, evidence)
                    + " Native skeleton patterns are only candidates.",
                    evidence=evidence,
                    passed_conditions=[c],
                )

                ot = row.get("open_time", context.now_ms)
                c_obj = build_signal_candidate(
                    context=context,
                    direction=direction,
                    strength=StrategyCandidateStrength.medium,
                    confidence=confidence,
                    explanation=explanation,
                    open_time=ot,
                    used_features=[c],
                )
                candidates.append(c_obj)

        return candidates

    def explain(self, candidate: SignalCandidate) -> StrategyExplanation:
        return candidate.explanation

    def health_check(self, config: AppConfig) -> dict[str, Any]:
        return {"status": "pass"}
