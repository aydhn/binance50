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


class VolumeConfirmationPlugin(StrategyPluginProtocol):
    name = "volume_confirmation"
    plugin_type = StrategyPluginType.volume_confirmation
    version = "1.0.0"
    description = "Volume confirmation candidate"

    @property
    def required_features(self) -> list[str]:
        return ["volu_obv", "volu_volume_sma_20", "volume"]

    @property
    def required_prefixes(self) -> list[str]:
        return []

    def is_enabled(self, config: AppConfig) -> bool:
        return config.strategies.plugins.volume_confirmation.enabled

    def validate_config(self, config: AppConfig) -> None:
        pass

    def validate_input(self, df: pd.DataFrame, config: AppConfig) -> None:
        pass

    def evaluate_row(self, row: pd.Series, context: StrategyContext) -> SignalCandidate | None:
        return None

    def evaluate(self, df: pd.DataFrame, context: StrategyContext) -> list[SignalCandidate]:
        candidates = []
        pcfg = context.config.strategies.plugins.volume_confirmation

        obv_diff = df.get("volu_obv", pd.Series(0, index=df.index)).diff()

        for i in range(1, len(df)):
            row = df.iloc[i]
            vol = row.get("volume", 0)
            vol_sma = row.get("volu_volume_sma_20", 0)
            obv_delta = obv_diff.iloc[i]

            vol_pass = not pcfg.require_volume_above_average or (
                vol > vol_sma * pcfg.volume_multiplier
            )

            if vol_pass and abs(obv_delta) > 0:
                direction = (
                    StrategyDirection.bullish if obv_delta > 0 else StrategyDirection.bearish
                )
                strength = StrategyCandidateStrength.weak
                confidence = 50.0

                from binance50.strategies.conditions import build_condition_evidence

                evidence = [
                    build_condition_evidence(
                        "volume_surge", "gt", vol_sma * pcfg.volume_multiplier, vol, True
                    ),
                    build_condition_evidence(
                        "obv_delta", "gt" if obv_delta > 0 else "lt", 0, obv_delta, True
                    ),
                ]

                explanation = StrategyExplanation(
                    summary=build_explanation_summary(self.name, direction, evidence)
                    + " Not a standalone trade signal.",
                    evidence=evidence,
                    passed_conditions=["volume_surge", "obv_delta"],
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
