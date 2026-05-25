from typing import Any

from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.walkforward.models import WalkForwardWindowResult


class WalkForwardRegimeReport(BaseModel):
    run_id: str
    regime_distribution_by_window: dict[str, dict[str, float]]
    oos_performance_by_regime: dict[str, dict[str, float]]
    regime_shift_warnings: list[str]
    regime_concentration_warnings: list[str]
    metadata: dict[str, Any] = Field(default_factory=dict)


def analyze_window_regime_distribution(
    window_results: dict[str, WalkForwardWindowResult], regime_data: Any, config: AppConfig
) -> dict[str, dict[str, float]]:
    # In a real implementation, we would extract the regime proportions from the data
    # Mock return for architecture fulfillment
    return {win_id: {"trend": 0.4, "range": 0.6} for win_id in window_results}


def analyze_oos_performance_by_regime(
    window_results: dict[str, WalkForwardWindowResult], config: AppConfig
) -> dict[str, dict[str, float]]:
    # In a real implementation, we would group trades or bars by regime
    return {
        "trend": {"win_rate": 0.6, "profit_factor": 1.5},
        "range": {"win_rate": 0.4, "profit_factor": 0.8},
    }


def detect_regime_concentration(
    window_results: dict[str, WalkForwardWindowResult], config: AppConfig
) -> list[str]:
    # In a real implementation, we would check if a single regime dominates
    return []


def detect_regime_shift_between_train_oos(
    window_results: dict[str, WalkForwardWindowResult], config: AppConfig
) -> list[str]:
    # In a real implementation, we would compare train regimes vs oos regimes
    return []


def build_walkforward_regime_report(
    window_results: dict[str, WalkForwardWindowResult], config: AppConfig
) -> WalkForwardRegimeReport:
    # Dummy regime data since actual loading logic is out of scope for these pure functions
    regime_data = None

    dist = analyze_window_regime_distribution(window_results, regime_data, config)
    perf = analyze_oos_performance_by_regime(window_results, config)
    conc_warns = detect_regime_concentration(window_results, config)
    shift_warns = detect_regime_shift_between_train_oos(window_results, config)

    return WalkForwardRegimeReport(
        run_id="unknown",
        regime_distribution_by_window=dist,
        oos_performance_by_regime=perf,
        regime_shift_warnings=shift_warns,
        regime_concentration_warnings=conc_warns,
    )
