import datetime
from typing import Any

from binance50.config.models import AppConfig
from binance50.signals.conflicts import SignalConflict, compute_conflict_penalty
from binance50.signals.confluence import ConfluenceEngine, ConfluenceGroup
from binance50.signals.explanations import build_score_breakdown_explanation, build_score_explanation
from binance50.signals.freshness import compute_freshness_component
from binance50.signals.models import (
    ScoredSignalCandidate,
    ScoredSignalStatus,
    SignalDecisionIntent,
    SignalScoreBreakdown,
    SignalScoreComponent,
)
from binance50.signals.normalization import clamp_score, score_to_tier
from binance50.signals.thresholds import classify_signal_intent
from binance50.signals.weighting import SignalWeightingEngine
from binance50.strategies.models import SignalCandidate, StrategyCandidateStatus


class SignalScoringEngine:
    def __init__(self, config: AppConfig, weighting_engine: SignalWeightingEngine | None = None, confluence_engine: ConfluenceEngine | None = None):
        self.config = config
        self.weighting_engine = weighting_engine or SignalWeightingEngine()
        self.confluence_engine = confluence_engine or ConfluenceEngine(config)

    def reject_candidate(self, candidate: SignalCandidate, reason: str) -> ScoredSignalCandidate:
        return ScoredSignalCandidate(
            scored_signal_id=f"scored_{candidate.candidate_id}",
            source_candidate_id=candidate.candidate_id,
            symbol=candidate.symbol,
            market_scope=candidate.market_scope,
            interval=candidate.interval,
            open_time=candidate.open_time,
            close_time=candidate.close_time,
            direction=candidate.direction.value,
            status=ScoredSignalStatus.rejected,
            intent=SignalDecisionIntent.no_action,
            score=0.0,
            score_tier=score_to_tier(0.0, self.config),
            confidence=candidate.confidence,
            plugin_name=candidate.plugin_name,
            plugin_type=candidate.plugin_type.value,
            strategy_strength=candidate.strength.value,
            explanation=reason,
            source_candidate=candidate
        )

    def build_score_breakdown(self, candidate: SignalCandidate, components: list[SignalScoreComponent]) -> SignalScoreBreakdown:
        subtotal = 0.0
        total_penalty = 0.0

        for comp in components:
            if comp.contribution < 0:
                total_penalty += abs(comp.contribution)
            else:
                subtotal += comp.contribution

        final_score = self.compute_final_score(components, self.config)
        tier = score_to_tier(final_score, self.config)

        return SignalScoreBreakdown(
            components=components,
            subtotal_before_penalties=subtotal,
            total_penalty=total_penalty,
            final_score=final_score,
            score_tier=tier
        )

    def compute_final_score(self, components: list[SignalScoreComponent], config: AppConfig) -> float:
        total = sum(c.contribution for c in components)

        if config.signals.scoring.round_scores_decimals >= 0:
            total = round(total, config.signals.scoring.round_scores_decimals)

        return clamp_score(total, config.signals.scoring.min_score, config.signals.scoring.max_score)

    def score_candidate(self, candidate: SignalCandidate, group: ConfluenceGroup | None, conflicts: list[SignalConflict], current_open_time: int | None = None) -> ScoredSignalCandidate:
        if candidate.status in (StrategyCandidateStatus.rejected, StrategyCandidateStatus.warning):
            return self.reject_candidate(candidate, f"Candidate was previously {candidate.status.value}")

        if candidate.direction == "no_action":
            return self.reject_candidate(candidate, "Candidate direction is no_action")

        open_ts = candidate.open_time.timestamp() * 1000 if isinstance(candidate.open_time, datetime.datetime) else candidate.open_time
        curr_time = current_open_time or int(open_ts)

        conf_comp = self.weighting_engine.compute_component_contribution(
            "candidate_confidence", candidate.confidence, self.config, "Raw strategy confidence"
        )

        plugin_comp = self.weighting_engine.compute_plugin_weighted_score(candidate, self.config)

        confluence_comp = self.confluence_engine.compute_confluence_score(group, self.config) if group else self.weighting_engine.compute_component_contribution(
            "confluence", 0.0, self.config, "No confluence group"
        )

        conf_comp_bonus = self.confluence_engine.compute_confirmation_score(candidate, group, self.config) if group else self.weighting_engine.compute_component_contribution(
            "confirmation", 0.0, self.config, "No confirmation group"
        )

        freshness_comp = compute_freshness_component(candidate, curr_time, candidate.interval, self.config)

        quality_comp = self.weighting_engine.compute_component_contribution(
            "data_quality", 100.0, self.config, "Base data quality"
        )

        conflict_comp = compute_conflict_penalty(candidate, conflicts, self.config)

        components = [conf_comp, plugin_comp, confluence_comp, conf_comp_bonus, freshness_comp, quality_comp, conflict_comp]

        breakdown = self.build_score_breakdown(candidate, components)

        status = ScoredSignalStatus.scored_candidate
        if conflict_comp.contribution < 0:
            status = ScoredSignalStatus.conflicted
        if freshness_comp.normalized_value == 0:
            status = ScoredSignalStatus.expired

        intent = classify_signal_intent(breakdown.final_score, self.config)

        scored = ScoredSignalCandidate(
            scored_signal_id=f"scored_{candidate.candidate_id}",
            source_candidate_id=candidate.candidate_id,
            symbol=candidate.symbol,
            market_scope=candidate.market_scope,
            interval=candidate.interval,
            open_time=candidate.open_time,
            close_time=candidate.close_time,
            direction=candidate.direction.value,
            status=status,
            intent=intent,
            score=breakdown.final_score,
            score_tier=breakdown.score_tier,
            confidence=candidate.confidence,
            plugin_name=candidate.plugin_name,
            plugin_type=candidate.plugin_type.value,
            strategy_strength=candidate.strength.value,
            score_breakdown=breakdown,
            confluence_group_id=group.group_id if group else None,
            conflicted=(conflict_comp.contribution < 0),
            conflict_reasons=[conflict_comp.reason] if conflict_comp.contribution < 0 else [],
            expired=(freshness_comp.normalized_value == 0),
            source_candidate=candidate
        )

        explanation = build_score_explanation(scored)

        return scored.model_copy(update={"explanation": explanation})

    def score_candidates(self, candidates: list[SignalCandidate], current_open_time: int | None = None) -> list[ScoredSignalCandidate]:
        from binance50.signals.conflicts import detect_opposite_direction_conflicts, detect_same_plugin_conflicts

        if current_open_time is None and candidates:
            open_times = []
            for c in candidates:
                ts = c.open_time.timestamp() * 1000 if isinstance(c.open_time, datetime.datetime) else c.open_time
                open_times.append(int(ts))
            current_open_time = max(open_times) + 1

        confluence_groups = self.confluence_engine.build_confluence_groups(candidates, self.config)

        candidate_groups: dict[str, ConfluenceGroup | None] = {}
        for group in confluence_groups:
            for c in group.candidates:
                candidate_groups[c.candidate_id] = group

        opposite_conflicts = detect_opposite_direction_conflicts(candidates, self.config)
        same_plugin_conflicts = detect_same_plugin_conflicts(candidates, self.config)
        all_conflicts = opposite_conflicts + same_plugin_conflicts

        scored_results = []
        for c in candidates:
            c_group = candidate_groups.get(c.candidate_id, None)
            scored = self.score_candidate(c, c_group, all_conflicts, current_open_time)
            scored_results.append(scored)

        return scored_results
