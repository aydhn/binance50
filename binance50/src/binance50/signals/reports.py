from pathlib import Path
from typing import Any

from binance50.config.models import AppConfig
from binance50.signals.models import ConfluenceGroup, ScoredSignalCandidate, SignalScoringResult


def build_signal_run_summary(result: SignalScoringResult) -> dict[str, Any]:
    return {
        "status": "success" if result.success else "error",
        "error": result.error,
        "symbol": result.metadata.symbol,
        "interval": result.metadata.interval,
        "scored_count": result.metadata.scored_candidate_count,
        "rejected_count": result.metadata.rejected_candidate_count,
        "confluence_groups": result.metadata.confluence_group_count,
        "conflicts": result.metadata.conflict_count,
        "quality_status": result.quality_report.status if result.quality_report else "unknown",
        "generated_at": result.metadata.generated_at_utc
    }


def build_scored_signal_table(scored: list[ScoredSignalCandidate], limit: int = 50) -> list[dict[str, Any]]:
    table = []
    for s in scored[:limit]:
        table.append({
            "id": s.scored_signal_id[:10] + "...",
            "time": s.open_time,
            "dir": s.direction,
            "score": s.score,
            "tier": s.score_tier.value,
            "intent": s.intent.value,
            "plugin": s.plugin_name,
            "type": s.plugin_type,
            "conflicted": s.conflicted
        })
    return table


def build_confluence_group_report(groups: list[ConfluenceGroup]) -> dict[str, Any]:
    return {
        "group_count": len(groups),
        "avg_score": sum(g.confluence_score for g in groups) / max(1, len(groups)),
        "groups": [
            {
                "id": g.group_id[:10] + "...",
                "dir": g.direction,
                "score": g.confluence_score,
                "plugins": g.plugin_names,
                "types": g.plugin_types
            }
            for g in groups
        ]
    }


def build_conflict_summary_report(scored: list[ScoredSignalCandidate]) -> dict[str, Any]:
    conflicted = [s for s in scored if s.conflicted]
    return {
        "total_scored": len(scored),
        "total_conflicted": len(conflicted),
        "conflict_ratio": len(conflicted) / max(1, len(scored)),
        "reasons_summary": list({r for s in conflicted for r in s.conflict_reasons})
    }


def build_signal_threshold_report(config: AppConfig) -> dict[str, Any]:
    from binance50.signals.thresholds import build_threshold_report
    return build_threshold_report(config)


def build_signal_health_report(config: AppConfig) -> dict[str, Any]:
    return {
        "status": "ok" if config.signals.enabled else "disabled",
        "cache_dir_exists": Path(config.signals.cache_dir).exists() if config.signals.cache_enabled else False,
        "execution_forbidden": config.signals.execution_forbidden,
        "thresholds_deferred": config.signals.thresholds.execution_threshold_deferred,
        "plugin_weights_configured": len(config.signals.plugin_weights),
        "calibration_placeholder_active": config.signals.calibration.calibration_training_deferred
    }


def format_score_breakdown(scored: ScoredSignalCandidate) -> dict[str, Any]:
    from binance50.signals.explanations import build_score_breakdown_explanation
    if not scored.score_breakdown:
        return {}
    return build_score_breakdown_explanation(scored.score_breakdown)
