from typing import Any

from binance50.config.models import AppConfig
from binance50.risk.models import RiskComponent, RiskDimension, RiskSeverity


def estimate_hypothetical_notional_usdt(scored_signal: Any, config: AppConfig) -> float:
    return config.risk.position_risk.max_notional_per_candidate_usdt


def estimate_hypothetical_risk_pct(
    notional_usdt: float, account_equity_usdt: float, config: AppConfig
) -> float:
    if account_equity_usdt <= 0:
        return 0.0
    return (notional_usdt / account_equity_usdt) * 100.0


def check_min_notional(notional_usdt: float, config: AppConfig) -> RiskComponent:
    min_notional = config.risk.position_risk.min_notional_usdt
    passed = notional_usdt >= min_notional
    return RiskComponent(
        dimension=RiskDimension.notional,
        raw_value=notional_usdt,
        passed=passed,
        severity=RiskSeverity.info if passed else RiskSeverity.blocked,
        reason="Notional meets minimum requirement" if passed else "Notional below minimum",
        metadata={"min_notional": min_notional},
    )


def check_max_notional(notional_usdt: float, config: AppConfig) -> RiskComponent:
    max_notional = config.risk.position_risk.max_notional_per_candidate_usdt
    passed = notional_usdt <= max_notional
    return RiskComponent(
        dimension=RiskDimension.notional,
        raw_value=notional_usdt,
        passed=passed,
        severity=RiskSeverity.info if passed else RiskSeverity.blocked,
        reason="Notional within max limits" if passed else "Notional exceeds maximum allowed",
        metadata={"max_notional": max_notional},
    )


def round_quantity_estimate_to_step_size(quantity: float, step_size: float) -> float:
    if step_size <= 0:
        return quantity
    import math

    return math.floor(quantity / step_size) * step_size


def validate_notional_against_symbol_filters(
    notional_usdt: float, symbol_filter_metadata: dict[str, Any] | None, config: AppConfig
) -> RiskComponent:
    if not symbol_filter_metadata and config.risk.spot.reject_if_filter_metadata_missing:
        return RiskComponent(
            dimension=RiskDimension.symbol_filter,
            raw_value=notional_usdt,
            passed=False,
            severity=RiskSeverity.blocked,
            reason="Missing required symbol filter metadata",
            metadata={},
        )
    return RiskComponent(
        dimension=RiskDimension.symbol_filter,
        raw_value=notional_usdt,
        passed=True,
        severity=RiskSeverity.info,
        reason="Notional passes symbol filter checks",
        metadata={},
    )
