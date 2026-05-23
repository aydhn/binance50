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


class MomentumContinuationPlugin(StrategyPluginProtocol):
    name = "momentum_continuation"
    plugin_type = StrategyPluginType.momentum_continuation
    version = "1.0.0"
    description = "Momentum continuation strategy candidate"

    @property
    def required_features(self) -> list[str]:
        return ["mom_rsi_14", "trend_macd_hist_12_26_9", "mom_roc_10"]

    @property
    def required_prefixes(self) -> list[str]:
        return []

    def is_enabled(self, config: AppConfig) -> bool:
        return config.strategies.plugins.momentum_continuation.enabled

    def validate_config(self, config: AppConfig) -> None:
        pass

    def validate_input(self, df: pd.DataFrame, config: AppConfig) -> None:
        pass

    def evaluate_row(self, row: pd.Series, context: StrategyContext) -> SignalCandidate | None:
        return None

    def evaluate(self, df: pd.DataFrame, context: StrategyContext) -> list[SignalCandidate]:
        candidates = []
        pcfg = context.config.strategies.plugins.momentum_continuation

        for idx, row in df.iterrows():
            rsi = row.get("mom_rsi_14", 50)
            macd_hist = row.get("trend_macd_hist_12_26_9", 0)
            roc = row.get("mom_roc_10", 0)

            bullish_pass = (
                rsi > pcfg.rsi_min
                and roc > pcfg.roc_min
                and (not pcfg.require_macd_hist_positive_for_bullish or macd_hist > 0)
            )

            bearish_pass = (
                rsi < (100 - pcfg.rsi_min)
                and roc < -pcfg.roc_min
                and (not pcfg.require_macd_hist_negative_for_bearish or macd_hist < 0)
            )

            if bullish_pass or bearish_pass:
                direction = StrategyDirection.bullish if bullish_pass else StrategyDirection.bearish
                strength = StrategyCandidateStrength.medium

                confidence = min(100.0, max(0.0, abs(roc) * 10.0 + 50.0))

                from binance50.strategies.conditions import build_condition_evidence

                evidence = [
                    build_condition_evidence(
                        "mom_rsi_14",
                        "gt" if bullish_pass else "lt",
                        pcfg.rsi_min if bullish_pass else (100 - pcfg.rsi_min),
                        rsi,
                        True,
                    ),
                    build_condition_evidence(
                        "mom_roc_10",
                        "gt" if bullish_pass else "lt",
                        pcfg.roc_min if bullish_pass else -pcfg.roc_min,
                        roc,
                        True,
                    ),
                ]

                explanation = StrategyExplanation(
                    summary=build_explanation_summary(self.name, direction, evidence),
                    evidence=evidence,
                    passed_conditions=["momentum_aligned"],
                )

                ot = row.get("open_time", context.now_ms)
                c = build_signal_candidate(
                    context=context,
                    direction=direction,
                    strength=strength,
                    confidence=confidence,
                    explanation=explanation,
                    open_time=ot,
                    used_features=self.required_features,
                )
                candidates.append(c)

        return candidates

    def explain(self, candidate: SignalCandidate) -> StrategyExplanation:
        return candidate.explanation

    def health_check(self, config: AppConfig) -> dict[str, Any]:
        return {"status": "pass"}
