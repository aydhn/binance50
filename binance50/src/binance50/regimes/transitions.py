from typing import Any

import pandas as pd
from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.regimes.models import MarketRegime, RegimeClassification, RegimeFamily


class RegimeTransitionEvent(BaseModel):
    transition_id: str
    symbol: str
    market_scope: str
    interval: str
    open_time: int
    from_regime: MarketRegime
    to_regime: MarketRegime
    from_family: RegimeFamily
    to_family: RegimeFamily
    confidence_before: float
    confidence_after: float
    stability_before: float
    stability_after: float
    transition_type: str
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


def classify_transition_type(prev: RegimeClassification, curr: RegimeClassification) -> str:
    if prev.family == curr.family:
        return "intra_family"
    if prev.regime == MarketRegime.unknown or curr.regime == MarketRegime.unknown:
        return "to_from_unknown"
    return "cross_family"


def compute_transition_intensity(prev: RegimeClassification, curr: RegimeClassification) -> float:
    if (prev.regime == MarketRegime.trend_up and curr.regime == MarketRegime.trend_down) or (
        prev.regime == MarketRegime.trend_down and curr.regime == MarketRegime.trend_up
    ):
        return 1.0
    return 0.5


def detect_regime_transitions(
    classifications: list[RegimeClassification], config: AppConfig
) -> list[RegimeTransitionEvent]:
    if not config.regimes.transitions.enabled:
        return []
    events = []
    for i in range(1, len(classifications)):
        prev = classifications[i - 1]
        curr = classifications[i]
        if prev.regime != curr.regime:
            t_type = classify_transition_type(prev, curr)
            event = RegimeTransitionEvent(
                transition_id=f"{curr.symbol}_{curr.open_time}",
                symbol=curr.symbol,
                market_scope=curr.market_scope,
                interval=curr.interval,
                open_time=curr.open_time,
                from_regime=prev.regime,
                to_regime=curr.regime,
                from_family=prev.family,
                to_family=curr.family,
                confidence_before=prev.confidence,
                confidence_after=curr.confidence,
                stability_before=prev.stability_score or 0.0,
                stability_after=curr.stability_score or 0.0,
                transition_type=t_type,
            )
            events.append(event)
    return events


def add_transition_flags(
    classifications: list[RegimeClassification],
    transitions: list[RegimeTransitionEvent],
    config: AppConfig,
) -> list[RegimeClassification]:
    if not config.regimes.transitions.mark_transition_bars:
        return classifications
    t_times = {t.open_time for t in transitions}
    for c in classifications:
        if c.open_time in t_times:
            c.is_transition = True
    return classifications


def transitions_to_dataframe(events: list[RegimeTransitionEvent]) -> pd.DataFrame:
    return pd.DataFrame([e.model_dump() for e in events])
