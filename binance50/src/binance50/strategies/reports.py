from typing import Any

from binance50.config.models import AppConfig
from binance50.strategies.candidates import detect_conflicting_candidates
from binance50.strategies.models import SignalCandidate, StrategyRunResult
from binance50.strategies.registry import StrategyRegistry


def build_strategy_run_summary(result: StrategyRunResult) -> dict[str, Any]:
    return {
        "request_id": result.request.request_id,
        "symbol": result.request.symbol,
        "interval": result.request.interval,
        "success": result.success,
        "error": result.error,
        "candidates": len(result.candidates),
        "rejected": len(result.rejected_candidates),
        "plugins_run": result.metadata.plugin_count,
        "warnings": result.metadata.warnings,
        "generated_at": result.metadata.generated_at_utc,
    }


def build_plugin_report(
    plugin: Any, candidates: list[SignalCandidate], errors: list[str]
) -> dict[str, Any]:
    return {
        "plugin_name": plugin.name,
        "version": plugin.version,
        "candidates_generated": len(candidates),
        "errors": errors,
    }


def build_candidate_table(candidates: list[SignalCandidate]) -> list[dict[str, Any]]:
    table = []
    for c in candidates:
        table.append(
            {
                "time": c.open_time,
                "plugin": c.plugin_name,
                "direction": c.direction.value,
                "strength": c.strength.value,
                "confidence": round(c.confidence, 2),
                "summary": c.explanation.summary if c.explanation else "",
            }
        )
    return table


def build_conflict_report(candidates: list[SignalCandidate]) -> dict[str, Any]:
    conflicts = detect_conflicting_candidates(candidates)
    return {"conflict_count": len(conflicts), "details": conflicts}


def build_strategy_health_report(config: AppConfig, registry: StrategyRegistry) -> dict[str, Any]:
    return {
        "config_safe": config.strategies.execution_forbidden
        and config.strategies.order_creation_forbidden,
        "registry_health": registry.health_report(config),
    }


def format_candidate_preview(
    candidates: list[SignalCandidate], limit: int = 20
) -> list[dict[str, Any]]:
    return build_candidate_table(candidates[:limit])
