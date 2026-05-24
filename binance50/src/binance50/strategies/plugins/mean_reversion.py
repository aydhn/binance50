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


class MeanReversionPlugin(StrategyPluginProtocol):
    name = "mean_reversion"
    plugin_type = StrategyPluginType.mean_reversion
    version = "1.0.0"
    description = "Mean reversion strategy candidate"

    @property
    def required_features(self) -> list[str]:
        return ["mom_rsi_14", "vol_bb_lower_20_2", "vol_bb_upper_20_2"]

    @property
    def required_prefixes(self) -> list[str]:
        return []

    def is_enabled(self, config: AppConfig) -> bool:
        return config.strategies.plugins.mean_reversion.enabled

    def validate_config(self, config: AppConfig) -> None:
        pass

    def validate_input(self, df: pd.DataFrame, config: AppConfig) -> None:
        pass

    def evaluate_row(self, row: pd.Series, context: StrategyContext) -> SignalCandidate | None:
        return None

    def evaluate(self, df: pd.DataFrame, context: StrategyContext) -> list[SignalCandidate]:
        candidates = []
        pcfg = context.config.strategies.plugins.mean_reversion

        for _idx, row in df.iterrows():
            close = row.get("close", 0)
            rsi = row.get("mom_rsi_14", 50)
            bb_low = row.get("vol_bb_lower_20_2", 0)
            bb_high = row.get("vol_bb_upper_20_2", 0)

            bullish_pass = rsi <= pcfg.rsi_oversold and (
                not pcfg.require_bollinger_touch or close <= bb_low
            )
            bearish_pass = rsi >= pcfg.rsi_overbought and (
                not pcfg.require_bollinger_touch or close >= bb_high
            )

            if bullish_pass or bearish_pass:
                direction = StrategyDirection.bullish if bullish_pass else StrategyDirection.bearish
                strength = StrategyCandidateStrength.medium

                dist = abs(rsi - 50)
                confidence = min(100.0, max(0.0, dist * 2.0))

                from binance50.strategies.conditions import build_condition_evidence

                evidence = [
                    build_condition_evidence(
                        "mom_rsi_14",
                        "lte" if bullish_pass else "gte",
                        pcfg.rsi_oversold if bullish_pass else pcfg.rsi_overbought,
                        rsi,
                        True,
                    ),
                    build_condition_evidence(
                        "bb_touch",
                        "lte" if bullish_pass else "gte",
                        bb_low if bullish_pass else bb_high,
                        close,
                        True,
                    ),
                ]

                explanation = StrategyExplanation(
                    summary=build_explanation_summary(self.name, direction, evidence)
                    + " Note: mean reversion candidate only.",
                    evidence=evidence,
                    passed_conditions=["rsi_extreme", "bb_touch"],
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
