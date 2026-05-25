from typing import Any

from binance50.config.models import AppConfig
from binance50.walkforward.models import WalkForwardRunResult


def build_walkforward_run_summary(result: WalkForwardRunResult) -> dict[str, Any]:
    return {
        "run_id": result.run_id,
        "mode": result.mode,
        "success": result.success,
        "windows_completed": len(
            [w for w in result.window_results.values() if w.status == "completed"]
        ),
        "total_windows": len(result.windows),
    }


def build_window_table(result: WalkForwardRunResult, limit: int = 100) -> list[dict[str, Any]]:
    return [{"window_id": w.window_id, "status": w.status} for w in result.window_results.values()][
        :limit
    ]


def build_oos_metrics_table(result: WalkForwardRunResult) -> list[dict[str, Any]]:
    return [
        {"window_id": w.window_id, "metrics": w.oos_report.get("metrics", {})}
        for w in result.window_results.values()
        if w.oos_report
    ]


def build_stitched_oos_equity_report(result: WalkForwardRunResult) -> dict[str, Any]:
    return {}


def build_parameter_drift_report(result: WalkForwardRunResult) -> dict[str, Any]:
    return result.parameter_drift_summary or {}


def build_degradation_report(result: WalkForwardRunResult) -> dict[str, Any]:
    return result.degradation_summary or {}


def build_stability_report(result: WalkForwardRunResult) -> dict[str, Any]:
    return result.stability_report or {}


def build_regime_report(result: WalkForwardRunResult) -> dict[str, Any]:
    return result.regime_summary or {}


def build_robustness_report(result: WalkForwardRunResult) -> dict[str, Any]:
    return result.robustness_report or {}


def build_walkforward_health_report(config: AppConfig) -> dict[str, Any]:
    return {"status": "healthy" if config.walkforward.enabled else "disabled"}
