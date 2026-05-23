from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from binance50.config.models import AppConfig
from binance50.signals.models import ScoredSignalCandidate, SignalScoreComponent
from binance50.strategies.models import SignalCandidate, StrategyDirection


class SignalConflict(BaseModel):
    model_config = ConfigDict(frozen=True)

    conflict_id: str
    symbol: str
    market_scope: str
    interval: str
    open_time: int
    bullish_candidate_ids: list[str] = Field(default_factory=list)
    bearish_candidate_ids: list[str] = Field(default_factory=list)
    same_plugin_conflicts: bool = False
    severity: str
    penalty: float
    reasons: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


def group_candidates_by_symbol_interval_time(candidates: list[SignalCandidate]) -> dict[str, list[SignalCandidate]]:
    groups: dict[str, list[SignalCandidate]] = {}
    for c in candidates:
        time_key = c.open_time.timestamp() * 1000 if hasattr(c.open_time, "timestamp") else c.open_time
        key = f"{c.market_scope}_{c.symbol}_{c.interval}_{int(time_key)}"
        if key not in groups:
            groups[key] = []
        groups[key].append(c)
    return groups


def detect_opposite_direction_conflicts(candidates: list[SignalCandidate], config: AppConfig) -> list[SignalConflict]:
    if not config.signals.conflicts.enabled or not config.signals.conflicts.detect_opposite_direction_same_bar:
        return []

    conflicts = []
    groups = group_candidates_by_symbol_interval_time(candidates)

    for key, group in groups.items():
        bullish = [c for c in group if c.direction == StrategyDirection.bullish]
        bearish = [c for c in group if c.direction == StrategyDirection.bearish]

        if bullish and bearish:
            bullish_ids = [c.candidate_id for c in bullish]
            bearish_ids = [c.candidate_id for c in bearish]

            time_key = bullish[0].open_time.timestamp() * 1000 if hasattr(bullish[0].open_time, "timestamp") else bullish[0].open_time

            conflict = SignalConflict(
                conflict_id=f"conf_{key}",
                symbol=bullish[0].symbol,
                market_scope=bullish[0].market_scope,
                interval=bullish[0].interval,
                open_time=int(time_key),
                bullish_candidate_ids=bullish_ids,
                bearish_candidate_ids=bearish_ids,
                severity="high",
                penalty=config.signals.conflicts.bearish_bullish_conflict_penalty,
                reasons=[f"Opposite direction signals detected on same bar ({len(bullish)} bullish, {len(bearish)} bearish)"]
            )
            conflicts.append(conflict)

    return conflicts


def detect_same_plugin_conflicts(candidates: list[SignalCandidate], config: AppConfig) -> list[SignalConflict]:
    if not config.signals.conflicts.enabled or not config.signals.conflicts.detect_same_plugin_opposite_direction:
        return []

    conflicts = []
    groups = group_candidates_by_symbol_interval_time(candidates)

    for key, group in groups.items():
        plugin_directions: dict[str, set[StrategyDirection]] = {}
        for c in group:
            if c.direction in (StrategyDirection.bullish, StrategyDirection.bearish):
                if c.plugin_name not in plugin_directions:
                    plugin_directions[c.plugin_name] = set()
                plugin_directions[c.plugin_name].add(c.direction)

        conflicting_plugins = [p for p, d in plugin_directions.items() if len(d) > 1]

        if conflicting_plugins:
            bullish = [c for c in group if c.plugin_name in conflicting_plugins and c.direction == StrategyDirection.bullish]
            bearish = [c for c in group if c.plugin_name in conflicting_plugins and c.direction == StrategyDirection.bearish]

            time_key = group[0].open_time.timestamp() * 1000 if hasattr(group[0].open_time, "timestamp") else group[0].open_time

            conflict = SignalConflict(
                conflict_id=f"conf_same_plugin_{key}",
                symbol=group[0].symbol,
                market_scope=group[0].market_scope,
                interval=group[0].interval,
                open_time=int(time_key),
                bullish_candidate_ids=[c.candidate_id for c in bullish],
                bearish_candidate_ids=[c.candidate_id for c in bearish],
                same_plugin_conflicts=True,
                severity="critical",
                penalty=config.signals.conflicts.same_plugin_conflict_penalty,
                reasons=[f"Plugin(s) {', '.join(conflicting_plugins)} generated opposite signals on the same bar"]
            )
            conflicts.append(conflict)

    return conflicts


def compute_conflict_penalty(candidate: SignalCandidate, conflicts: list[SignalConflict], config: AppConfig) -> SignalScoreComponent:
    if not config.signals.conflicts.enabled or candidate.direction not in (StrategyDirection.bullish, StrategyDirection.bearish):
        return SignalScoreComponent(
            name="conflict_penalty", raw_value=0.0, normalized_value=0.0, weight=0.0, contribution=0.0, reason="No conflict penalty applicable"
        )

    total_penalty = 0.0
    reasons = []

    for conflict in conflicts:
        if candidate.candidate_id in conflict.bullish_candidate_ids or candidate.candidate_id in conflict.bearish_candidate_ids:
            total_penalty += conflict.penalty
            reasons.extend(conflict.reasons)

    capped_penalty = min(total_penalty, config.signals.conflicts.max_conflict_penalty)
    weight = config.signals.component_weights.get("conflict_penalty", -0.20)
    contribution = capped_penalty * weight

    return SignalScoreComponent(
        name="conflict_penalty",
        raw_value=capped_penalty,
        normalized_value=capped_penalty,
        weight=weight,
        contribution=contribution,
        reason=" | ".join(reasons) if reasons else "No conflicts",
        metadata={"total_unbounded_penalty": total_penalty}
    )


def mark_conflicted_scored_candidates(scored: list[ScoredSignalCandidate], conflicts: list[SignalConflict]) -> list[ScoredSignalCandidate]:
    conflicted_ids: dict[str, list[str]] = {}
    for c in conflicts:
        for cid in c.bullish_candidate_ids + c.bearish_candidate_ids:
            if cid not in conflicted_ids:
                conflicted_ids[cid] = []
            conflicted_ids[cid].extend(c.reasons)

    result = []
    for s in scored:
        if s.source_candidate_id in conflicted_ids:
            updated = s.model_copy(update={
                "conflicted": True,
                "conflict_reasons": list(set(conflicted_ids[s.source_candidate_id]))
            })
            result.append(updated)
        else:
            result.append(s)

    return result
