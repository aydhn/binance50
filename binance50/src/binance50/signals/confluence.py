from collections import defaultdict

from binance50.config.models import AppConfig
from binance50.signals.models import ConfluenceGroup, SignalScoreComponent
from binance50.signals.normalization import clamp_score
from binance50.strategies.models import SignalCandidate, StrategyDirection


class ConfluenceEngine:
    def __init__(self, config: AppConfig):
        self.config = config

    def assign_candidates_to_groups(self, candidates: list[SignalCandidate]) -> dict[str, list[SignalCandidate]]:
        groups = defaultdict(list)
        for c in candidates:
            if c.direction in (StrategyDirection.bullish, StrategyDirection.bearish):
                time_key = c.open_time.timestamp() * 1000 if hasattr(c.open_time, "timestamp") else c.open_time
                key = f"{c.market_scope}_{c.symbol}_{c.interval}_{int(time_key)}_{c.direction}"
                groups[key].append(c)
        return dict(groups)

    def detect_plugin_type_diversity(self, group_candidates: list[SignalCandidate]) -> dict[str, int]:
        types: dict[str, int] = defaultdict(int)
        for c in group_candidates:
            types[c.plugin_type.value] += 1
        return dict(types)

    def detect_confirmation_relationships(self, group_candidates: list[SignalCandidate]) -> dict[str, bool]:
        types = {c.plugin_type.value for c in group_candidates}

        has_trend = "trend_following" in types or "momentum_continuation" in types
        has_volume = "volume_confirmation" in types
        has_mtf = "mtf_confirmation" in types
        has_divergence = "divergence_candidate" in types
        has_pattern = "pattern_candidate" in types

        return {
            "trend_volume": has_trend and has_volume,
            "trend_mtf": has_trend and has_mtf,
            "divergence": has_divergence,
            "pattern": has_pattern
        }

    def build_confluence_groups(self, candidates: list[SignalCandidate], config: AppConfig) -> list[ConfluenceGroup]:
        if not config.signals.confluence.enabled:
            return []

        bar_groups = defaultdict(list)
        for c in candidates:
            if c.direction in (StrategyDirection.bullish, StrategyDirection.bearish):
                time_key = c.open_time.timestamp() * 1000 if hasattr(c.open_time, "timestamp") else c.open_time
                key = f"{c.market_scope}_{c.symbol}_{c.interval}_{int(time_key)}"
                bar_groups[key].append(c)

        confluence_groups = []
        directional_groups = self.assign_candidates_to_groups(candidates)

        for key, group_candidates in directional_groups.items():
            if not group_candidates:
                continue

            c0 = group_candidates[0]
            time_key = c0.open_time.timestamp() * 1000 if hasattr(c0.open_time, "timestamp") else c0.open_time
            bar_key = f"{c0.market_scope}_{c0.symbol}_{c0.interval}_{int(time_key)}"

            all_bar_candidates = bar_groups[bar_key]
            opposite_direction = StrategyDirection.bearish if c0.direction == StrategyDirection.bullish else StrategyDirection.bullish
            opposite_count = sum(1 for c in all_bar_candidates if c.direction == opposite_direction)

            plugin_names = list({c.plugin_name for c in group_candidates})
            plugin_types = list({c.plugin_type.value for c in group_candidates})

            confluence_score = 0.0
            if len(plugin_names) >= config.signals.confluence.min_plugins_for_confluence:
                base_bonus = min(
                    len(plugin_names) * config.signals.confluence.same_direction_bonus_per_plugin,
                    config.signals.confluence.max_same_direction_bonus
                )
                confluence_score += base_bonus

                if config.signals.confluence.require_distinct_plugin_types and len(plugin_types) > 1:
                    confluence_score += config.signals.confluence.plugin_type_diversity_bonus

            confluence_score = clamp_score(confluence_score, 0.0, config.signals.confluence.max_confluence_score)

            group = ConfluenceGroup(
                group_id=f"grp_{key}",
                symbol=c0.symbol,
                market_scope=c0.market_scope,
                interval=c0.interval,
                open_time=c0.open_time,
                direction=c0.direction,
                candidates=group_candidates,
                plugin_names=plugin_names,
                plugin_types=plugin_types,
                same_direction_count=len(group_candidates),
                opposite_direction_count=opposite_count,
                confluence_score=confluence_score,
                conflict_penalty=0.0,
            )
            confluence_groups.append(group)

        return confluence_groups

    def compute_confluence_score(self, group: ConfluenceGroup, config: AppConfig) -> SignalScoreComponent:
        if not config.signals.confluence.enabled or not group or group.same_direction_count < config.signals.confluence.min_plugins_for_confluence:
            return SignalScoreComponent(
                name="confluence", raw_value=0.0, normalized_value=0.0, weight=0.0, contribution=0.0, reason="Confluence conditions not met"
            )

        weight = config.signals.component_weights.get("confluence", 0.20)
        contribution = group.confluence_score * weight

        return SignalScoreComponent(
            name="confluence",
            raw_value=group.confluence_score,
            normalized_value=group.confluence_score,
            weight=weight,
            contribution=contribution,
            reason=f"Confluence from {group.same_direction_count} plugins of {len(group.plugin_types)} types",
            metadata={"same_direction_count": group.same_direction_count, "plugin_types": group.plugin_types}
        )

    def compute_confirmation_score(self, candidate: SignalCandidate, group: ConfluenceGroup, config: AppConfig) -> SignalScoreComponent:
        if not config.signals.confluence.enabled or not group:
            return SignalScoreComponent(
                name="confirmation", raw_value=0.0, normalized_value=0.0, weight=0.0, contribution=0.0, reason="No group for confirmation"
            )

        relationships = self.detect_confirmation_relationships(group.candidates)
        conf_score = 0.0
        reasons = []

        if relationships.get("trend_volume"):
            conf_score += config.signals.confluence.trend_volume_confirmation_bonus
            reasons.append("Trend+Volume")

        if relationships.get("trend_mtf"):
            conf_score += config.signals.confluence.mtf_confirmation_bonus
            reasons.append("Trend+MTF")

        if relationships.get("divergence") and candidate.plugin_type.value != "divergence_candidate":
             conf_score += config.signals.confluence.divergence_confirmation_bonus
             reasons.append("Divergence Supported")

        if relationships.get("pattern") and candidate.plugin_type.value != "pattern_candidate":
             conf_score += config.signals.confluence.pattern_confirmation_bonus
             reasons.append("Pattern Supported")

        conf_score = clamp_score(conf_score, 0.0, 100.0)
        weight = config.signals.component_weights.get("confirmation", 0.10)
        contribution = conf_score * weight

        return SignalScoreComponent(
            name="confirmation",
            raw_value=conf_score,
            normalized_value=conf_score,
            weight=weight,
            contribution=contribution,
            reason="Confirmed by: " + ", ".join(reasons) if reasons else "No specific confirmations",
            metadata=relationships
        )
