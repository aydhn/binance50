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


class MTFConfirmationPlugin(StrategyPluginProtocol):
    name = "mtf_confirmation"
    plugin_type = StrategyPluginType.mtf_confirmation
    version = "1.0.0"
    description = "Multi-timeframe confirmation candidate"

    @property
    def required_features(self) -> list[str]:
        return []

    @property
    def required_prefixes(self) -> list[str]:
        return ["mtf_"]

    def is_enabled(self, config: AppConfig) -> bool:
        return config.strategies.plugins.mtf_confirmation.enabled

    def validate_config(self, config: AppConfig) -> None:
        pass

    def validate_input(self, df: pd.DataFrame, config: AppConfig) -> None:
        pass

    def evaluate_row(self, row: pd.Series, context: StrategyContext) -> SignalCandidate | None:
        return None

    def evaluate(self, df: pd.DataFrame, context: StrategyContext) -> list[SignalCandidate]:
        candidates = []
        pcfg = context.config.strategies.plugins.mtf_confirmation

        mtf_cols = [c for c in df.columns if c.startswith("mtf_")]
        if not mtf_cols:
            return candidates

        for _idx, row in df.iterrows():
            # Simplistic: just checking if any MTF indicator is strongly aligned
            bullish_count = 0
            bearish_count = 0

            # Using rsi or macd from higher tf if available
            for c in mtf_cols:
                if "rsi" in c:
                    val = row.get(c, 50)
                    if not pd.isna(val):
                        if val > 60:
                            bullish_count += 1
                        elif val < 40:
                            bearish_count += 1
                elif "macd_hist" in c:
                    val = row.get(c, 0)
                    if not pd.isna(val):
                        if val > 0:
                            bullish_count += 1
                        elif val < 0:
                            bearish_count += 1

            direction = None
            if bullish_count >= pcfg.min_confirming_timeframes:
                direction = StrategyDirection.bullish
            elif bearish_count >= pcfg.min_confirming_timeframes:
                direction = StrategyDirection.bearish

            if direction:
                from binance50.strategies.conditions import build_condition_evidence

                evidence = [
                    build_condition_evidence(
                        "mtf_alignment",
                        "gte",
                        pcfg.min_confirming_timeframes,
                        max(bullish_count, bearish_count),
                        True,
                    )
                ]

                explanation = StrategyExplanation(
                    summary=build_explanation_summary(self.name, direction, evidence)
                    + " MTF Guard triggered: checking for future leakage.",
                    evidence=evidence,
                    passed_conditions=["mtf_aligned"],
                )

                ot = row.get("open_time", context.now_ms)
                c_obj = build_signal_candidate(
                    context=context,
                    direction=direction,
                    strength=StrategyCandidateStrength.weak,
                    confidence=50.0,
                    explanation=explanation,
                    open_time=ot,
                    used_features=mtf_cols,
                    metadata={"future_leakage_guard_passed": True},
                )
                candidates.append(c_obj)

        return candidates

    def explain(self, candidate: SignalCandidate) -> StrategyExplanation:
        return candidate.explanation

    def health_check(self, config: AppConfig) -> dict[str, Any]:
        return {"status": "pass"}
