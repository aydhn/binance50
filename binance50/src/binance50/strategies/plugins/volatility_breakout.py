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


class VolatilityBreakoutPlugin(StrategyPluginProtocol):
    name = "volatility_breakout"
    plugin_type = StrategyPluginType.volatility_breakout
    version = "1.0.0"
    description = "Volatility breakout strategy candidate"

    @property
    def required_features(self) -> list[str]:
        return ["vol_atr_14", "vol_donchian_high_20", "vol_donchian_low_20"]

    @property
    def required_prefixes(self) -> list[str]:
        return []

    def is_enabled(self, config: AppConfig) -> bool:
        return config.strategies.plugins.volatility_breakout.enabled

    def validate_config(self, config: AppConfig) -> None:
        pass

    def validate_input(self, df: pd.DataFrame, config: AppConfig) -> None:
        pass

    def evaluate_row(self, row: pd.Series, context: StrategyContext) -> SignalCandidate | None:
        return None

    def evaluate(self, df: pd.DataFrame, context: StrategyContext) -> list[SignalCandidate]:
        candidates = []
        pcfg = context.config.strategies.plugins.volatility_breakout

        for idx, row in df.iterrows():
            close = row.get("close", 0)
            atr = row.get("vol_atr_14", 0)
            donchian_h = row.get("vol_donchian_high_20", 0)
            donchian_l = row.get("vol_donchian_low_20", 0)

            if pcfg.require_atr_positive and atr <= 0:
                continue

            buffer = atr * pcfg.breakout_buffer_atr

            bullish_pass = close > (donchian_h + buffer)
            bearish_pass = close < (donchian_l - buffer)

            if bullish_pass or bearish_pass:
                direction = StrategyDirection.bullish if bullish_pass else StrategyDirection.bearish
                strength = StrategyCandidateStrength.strong

                confidence = 60.0  # simple default

                from binance50.strategies.conditions import build_condition_evidence

                evidence = [
                    build_condition_evidence(
                        "breakout",
                        "gt" if bullish_pass else "lt",
                        donchian_h + buffer if bullish_pass else donchian_l - buffer,
                        close,
                        True,
                    )
                ]

                explanation = StrategyExplanation(
                    summary=build_explanation_summary(self.name, direction, evidence)
                    + " Breakout candidate only.",
                    evidence=evidence,
                    passed_conditions=["breakout"],
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
