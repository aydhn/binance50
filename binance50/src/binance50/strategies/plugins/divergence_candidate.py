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


class DivergenceCandidatePlugin(StrategyPluginProtocol):
    name = "divergence_candidate"
    plugin_type = StrategyPluginType.divergence_candidate
    version = "1.0.0"
    description = "Divergence strategy candidate"

    @property
    def required_features(self) -> list[str]:
        return []

    @property
    def required_prefixes(self) -> list[str]:
        return ["div_"]

    def is_enabled(self, config: AppConfig) -> bool:
        return config.strategies.plugins.divergence_candidate.enabled

    def validate_config(self, config: AppConfig) -> None:
        pass

    def validate_input(self, df: pd.DataFrame, config: AppConfig) -> None:
        pass

    def evaluate_row(self, row: pd.Series, context: StrategyContext) -> SignalCandidate | None:
        return None

    def evaluate(self, df: pd.DataFrame, context: StrategyContext) -> list[SignalCandidate]:
        candidates = []
        pcfg = context.config.strategies.plugins.divergence_candidate

        div_cols = [c for c in df.columns if c.startswith("div_") and "score" in c]

        for _idx, row in df.iterrows():
            for c in div_cols:
                score = row.get(c, 0)
                if pd.isna(score) or score < pcfg.min_divergence_score:
                    continue

                is_bullish = "bullish" in c
                is_hidden = "hidden" in c

                if is_hidden and not pcfg.accept_hidden:
                    continue
                if not is_hidden and not pcfg.accept_regular:
                    continue

                direction = StrategyDirection.bullish if is_bullish else StrategyDirection.bearish

                from binance50.strategies.conditions import build_condition_evidence

                evidence = [
                    build_condition_evidence(c, "gte", pcfg.min_divergence_score, score, True)
                ]

                explanation = StrategyExplanation(
                    summary=build_explanation_summary(self.name, direction, evidence)
                    + " Warning: Divergence signals may repaint depending on v2 config. Trade signals are not generated.",
                    evidence=evidence,
                    passed_conditions=["divergence_detected"],
                )

                ot = row.get("open_time", context.now_ms)
                c_obj = build_signal_candidate(
                    context=context,
                    direction=direction,
                    strength=StrategyCandidateStrength.medium,
                    confidence=min(100.0, score),
                    explanation=explanation,
                    open_time=ot,
                    used_features=[c],
                    metadata={"hidden": is_hidden, "repainting_risk": True},
                )
                candidates.append(c_obj)

        return candidates

    def explain(self, candidate: SignalCandidate) -> StrategyExplanation:
        return candidate.explanation

    def health_check(self, config: AppConfig) -> dict[str, Any]:
        return {"status": "pass"}
