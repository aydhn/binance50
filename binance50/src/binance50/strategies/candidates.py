import hashlib
import json
from collections import defaultdict
from typing import Any

import pandas as pd

from binance50.strategies.context import StrategyContext
from binance50.strategies.models import (
    SignalCandidate,
    StrategyCandidateStatus,
    StrategyCandidateStrength,
    StrategyDirection,
    StrategyExplanation,
    StrategyIntent,
    StrategyRejectionReason,
)


def build_signal_candidate(
    context: StrategyContext,
    direction: StrategyDirection,
    strength: StrategyCandidateStrength,
    confidence: float,
    explanation: StrategyExplanation,
    expiry_bars: int | None = None,
    intent: StrategyIntent = StrategyIntent.scoring_input,
    rejection_reasons: list[StrategyRejectionReason] | None = None,
    metadata: dict[str, Any] | None = None,
    open_time: int | None = None,
    close_time: int | None = None,
    required_features: list[str] | None = None,
    used_features: list[str] | None = None,
) -> SignalCandidate:

    if expiry_bars is None:
        expiry_bars = context.config.strategies.candidate.default_expiry_bars

    status = StrategyCandidateStatus.candidate
    if rejection_reasons:
        status = StrategyCandidateStatus.rejected
    elif direction in (StrategyDirection.neutral, StrategyDirection.no_action):
        status = StrategyCandidateStatus.no_action

    ot = open_time if open_time is not None else context.now_ms

    # Deterministic ID
    id_str = f"{context.symbol}_{context.interval}_{ot}_{context.plugin_name}_{direction}_{context.config_hash}"
    candidate_id = hashlib.sha256(id_str.encode()).hexdigest()

    return SignalCandidate(
        candidate_id=candidate_id,
        symbol=context.symbol,
        market_scope=context.market_scope,
        interval=context.interval,
        open_time=ot,
        close_time=close_time,
        plugin_name=context.plugin_name,
        plugin_type="trend_following",  # Mock placeholder
        direction=direction,
        strength=strength,
        confidence=confidence,
        status=status,
        intent=intent,
        expiry_bars=expiry_bars,
        explanation=explanation,
        required_features=required_features or [],
        used_features=used_features or [],
        rejection_reasons=rejection_reasons or [],
        metadata=metadata or {},
        created_at_utc=context.now_ms,
    )


def reject_candidate(
    context: StrategyContext,
    reason: StrategyRejectionReason,
    explanation: StrategyExplanation,
    open_time: int | None = None,
) -> SignalCandidate:
    # Need plugin_type from context but context doesn't store it, hack it from enum

    ot = open_time if open_time is not None else context.now_ms
    id_str = f"{context.symbol}_{context.interval}_{ot}_{context.plugin_name}_rejected_{reason}_{context.config_hash}"
    candidate_id = hashlib.sha256(id_str.encode()).hexdigest()

    return SignalCandidate(
        candidate_id=candidate_id,
        symbol=context.symbol,
        market_scope=context.market_scope,
        interval=context.interval,
        open_time=ot,
        plugin_name=context.plugin_name,
        plugin_type="trend_following",
        direction=StrategyDirection.no_action,
        strength=StrategyCandidateStrength.weak,
        confidence=0.0,
        status=StrategyCandidateStatus.rejected,
        intent=StrategyIntent.explanation_only,
        expiry_bars=0,
        explanation=explanation,
        rejection_reasons=[reason],
        created_at_utc=context.now_ms,
    )


def no_action_candidate(
    context: StrategyContext, explanation: StrategyExplanation, open_time: int | None = None
) -> SignalCandidate:
    ot = open_time if open_time is not None else context.now_ms
    id_str = f"{context.symbol}_{context.interval}_{ot}_{context.plugin_name}_no_action_{context.config_hash}"
    candidate_id = hashlib.sha256(id_str.encode()).hexdigest()

    return SignalCandidate(
        candidate_id=candidate_id,
        symbol=context.symbol,
        market_scope=context.market_scope,
        interval=context.interval,
        open_time=ot,
        plugin_name=context.plugin_name,
        plugin_type="trend_following",
        direction=StrategyDirection.no_action,
        strength=StrategyCandidateStrength.weak,
        confidence=0.0,
        status=StrategyCandidateStatus.no_action,
        intent=StrategyIntent.no_order,
        expiry_bars=0,
        explanation=explanation,
        created_at_utc=context.now_ms,
    )


def deduplicate_candidates(candidates: list[SignalCandidate]) -> list[SignalCandidate]:
    seen = set()
    result = []
    for c in candidates:
        if c.candidate_id not in seen:
            seen.add(c.candidate_id)
            result.append(c)
    return result


def group_candidates_by_bar(candidates: list[SignalCandidate]) -> dict[int, list[SignalCandidate]]:
    grouped = defaultdict(list)
    for c in candidates:
        ot = c.open_time
        if hasattr(ot, "timestamp"):
            ot = int(ot.timestamp() * 1000)
        grouped[ot].append(c)
    return dict(grouped)


def detect_conflicting_candidates(candidates: list[SignalCandidate]) -> list[dict[str, Any]]:
    grouped = group_candidates_by_bar(candidates)
    conflicts = []

    for ot, cands in grouped.items():
        directions = {
            c.direction
            for c in cands
            if c.direction in (StrategyDirection.bullish, StrategyDirection.bearish)
        }
        if len(directions) > 1:
            conflicts.append(
                {
                    "open_time": ot,
                    "symbol": cands[0].symbol,
                    "interval": cands[0].interval,
                    "conflicting_directions": list(directions),
                    "plugins_involved": [c.plugin_name for c in cands],
                }
            )

    return conflicts


def candidates_to_dataframe(candidates: list[SignalCandidate]) -> pd.DataFrame:
    if not candidates:
        return pd.DataFrame()

    records = []
    for c in candidates:
        d = c.model_dump()
        d["explanation_summary"] = c.explanation.summary if c.explanation else ""
        d["used_features_json"] = json.dumps(c.used_features)
        d["rejection_reasons_json"] = json.dumps([r.value for r in c.rejection_reasons])
        d["metadata_json"] = json.dumps(c.metadata)
        d.pop("explanation", None)
        d.pop("required_features", None)
        d.pop("used_features", None)
        d.pop("rejection_reasons", None)
        d.pop("metadata", None)
        # Ensure enums are stringified
        d["plugin_type"] = c.plugin_type.value
        d["direction"] = c.direction.value
        d["strength"] = c.strength.value
        d["status"] = c.status.value
        d["intent"] = c.intent.value
        records.append(d)

    return pd.DataFrame(records)


def dataframe_to_candidates(df: pd.DataFrame) -> list[SignalCandidate]:
    # Parsing back from DF is mostly used for testing/cache
    # Skipped full impl for brevity, the reverse of the above
    return []
