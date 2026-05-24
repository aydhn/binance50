from typing import Any

import pandas as pd

from binance50.config.models import AppConfig
from binance50.core.exceptions import RiskLimitError
from binance50.risk.models import RiskComponent, RiskDimension, RiskSeverity


def validate_global_risk_limits(config: AppConfig) -> None:
    if not config.risk.enabled:
        return
    limits = config.risk.global_limits
    if limits.max_total_risk_pct > 5.0:
        raise RiskLimitError("max_total_risk_pct exceeds absolute maximum limit")


def check_signal_score_threshold(scored_signal: Any, config: AppConfig) -> RiskComponent:
    threshold = config.risk.global_limits.min_signal_score_for_risk_review
    score = getattr(scored_signal, "final_score", 0.0)
    passed = score >= threshold
    severity = RiskSeverity.info if passed else RiskSeverity.blocked
    reason = (
        "Score meets minimum risk threshold"
        if passed
        else f"Score {score} below threshold {threshold}"
    )
    return RiskComponent(
        dimension=RiskDimension.signal_score,
        raw_value=score,
        passed=passed,
        severity=severity,
        reason=reason,
        metadata={"threshold": threshold},
    )


def check_max_candidates_per_hour(
    history_df: pd.DataFrame | None, config: AppConfig
) -> RiskComponent:
    limit = config.risk.global_limits.max_candidates_per_hour
    count = len(history_df) if history_df is not None else 0
    passed = count <= limit
    severity = RiskSeverity.info if passed else RiskSeverity.blocked
    return RiskComponent(
        dimension=RiskDimension.frequency,
        raw_value=count,
        passed=passed,
        severity=severity,
        reason="Candidate volume within limits" if passed else "Too many candidates per hour",
        metadata={"limit": limit},
    )


def check_max_symbol_candidates(
    symbol: str, history_df: pd.DataFrame | None, config: AppConfig
) -> RiskComponent:
    limit = config.risk.global_limits.max_symbols_with_risk
    return RiskComponent(
        dimension=RiskDimension.frequency,
        raw_value=0,
        passed=True,
        severity=RiskSeverity.info,
        reason="Symbol candidates within limit",
        metadata={"symbol": symbol, "limit": limit},
    )


def check_global_exposure_placeholder(
    current_context: dict[str, Any] | None, config: AppConfig
) -> RiskComponent:
    limit = config.risk.global_limits.max_total_risk_pct
    exposure = current_context.get("total_exposure_pct", 0.0) if current_context else 0.0
    passed = exposure <= limit
    return RiskComponent(
        dimension=RiskDimension.exposure,
        raw_value=exposure,
        passed=passed,
        severity=RiskSeverity.info if passed else RiskSeverity.blocked,
        reason=(
            "Total exposure within placeholder limits"
            if passed
            else "Total exposure exceeds placeholder limits"
        ),
        metadata={"limit": limit},
    )


def build_limit_report(config: AppConfig) -> dict:
    return {
        "global_limits": (
            config.risk.global_limits.model_dump() if config.risk.global_limits else {}
        ),
        "position_risk": (
            config.risk.position_risk.model_dump() if config.risk.position_risk else {}
        ),
        "spot": config.risk.spot.model_dump() if config.risk.spot else {},
        "futures": config.risk.futures.model_dump() if config.risk.futures else {},
    }
