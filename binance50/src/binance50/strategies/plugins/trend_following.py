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


class TrendFollowingPlugin(StrategyPluginProtocol):
    name = "trend_following"
    plugin_type = StrategyPluginType.trend_following
    version = "1.0.0"
    description = "Trend following strategy using EMAs and ADX"

    @property
    def required_features(self) -> list[str]:
        return ["trend_ema_20", "trend_ema_50", "trend_ema_200", "trend_adx_14"]

    @property
    def required_prefixes(self) -> list[str]:
        return []

    def is_enabled(self, config: AppConfig) -> bool:
        return config.strategies.plugins.trend_following.enabled

    def validate_config(self, config: AppConfig) -> None:
        pass

    def validate_input(self, df: pd.DataFrame, config: AppConfig) -> None:
        pass

    def evaluate_row(self, row: pd.Series, context: StrategyContext) -> SignalCandidate | None:
        return None  # Batch evaluate used

    def evaluate(self, df: pd.DataFrame, context: StrategyContext) -> list[SignalCandidate]:
        candidates = []
        pcfg = context.config.strategies.plugins.trend_following

        for _idx, row in df.iterrows():
            close = row.get("close", 0)
            ema20 = row.get(pcfg.ema_fast, 0)
            ema50 = row.get(pcfg.ema_mid, 0)
            ema200 = row.get(pcfg.ema_slow, 0)
            adx = row.get("trend_adx_14", 0)

            # Bullish rules
            bullish_pass = ema20 > ema50 > ema200 and close > ema20 and adx >= pcfg.min_adx

            # Bearish rules
            bearish_pass = ema20 < ema50 < ema200 and close < ema20 and adx >= pcfg.min_adx

            if bullish_pass or bearish_pass:
                direction = StrategyDirection.bullish if bullish_pass else StrategyDirection.bearish
                strength = (
                    StrategyCandidateStrength.strong
                    if adx >= pcfg.strong_adx
                    else StrategyCandidateStrength.medium
                )

                # simplistic confidence
                confidence = min(100.0, max(0.0, 50.0 + (adx - pcfg.min_adx) * 2.0))

                from binance50.strategies.conditions import build_condition_evidence

                evidence = [
                    build_condition_evidence("ema_alignment", "eq", True, True, True),
                    build_condition_evidence(
                        "close_vs_ema20", "gt" if bullish_pass else "lt", ema20, close, True
                    ),
                    build_condition_evidence("adx", "gte", pcfg.min_adx, adx, True),
                ]

                explanation = StrategyExplanation(
                    summary=build_explanation_summary(self.name, direction, evidence),
                    evidence=evidence,
                    passed_conditions=["ema_alignment", "close_vs_ema20", "adx"],
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
