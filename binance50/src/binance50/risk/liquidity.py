from typing import Any

from binance50.config.models import AppConfig
from binance50.risk.models import RiskComponent, RiskDimension, RiskSeverity


def check_spread_bps(spread_bps: float | None, config: AppConfig) -> RiskComponent:
    if spread_bps is None:
        passed = not config.risk.liquidity.reject_missing_liquidity_metadata
        return RiskComponent(
            dimension=RiskDimension.liquidity,
            passed=passed,
            severity=RiskSeverity.info if passed else RiskSeverity.blocked,
            reason="Missing spread metadata",
            metadata={},
        )
    penalty = 0.0
    passed = True
    severity = RiskSeverity.info
    reason = "Spread within limits"
    if spread_bps > config.risk.liquidity.max_spread_bps:
        passed = False
        severity = RiskSeverity.blocked
        reason = "Spread exceeds max allowed"
    elif spread_bps > config.risk.liquidity.warning_spread_bps:
        penalty = config.risk.liquidity.high_spread_penalty
        severity = RiskSeverity.warning
        reason = "High spread warning"
    return RiskComponent(
        dimension=RiskDimension.liquidity,
        raw_value=spread_bps,
        penalty=penalty,
        passed=passed,
        severity=severity,
        reason=reason,
        metadata={"spread_bps": spread_bps},
    )


def check_quote_volume(quote_volume: float | None, config: AppConfig) -> RiskComponent:
    if quote_volume is None:
        passed = not config.risk.liquidity.reject_missing_liquidity_metadata
        return RiskComponent(
            dimension=RiskDimension.liquidity,
            passed=passed,
            severity=RiskSeverity.info if passed else RiskSeverity.blocked,
            reason="Missing quote volume metadata",
            metadata={},
        )
    min_vol = config.risk.liquidity.min_quote_volume_24h_usdt
    passed = quote_volume >= min_vol
    return RiskComponent(
        dimension=RiskDimension.liquidity,
        raw_value=quote_volume,
        passed=passed,
        severity=RiskSeverity.info if passed else RiskSeverity.blocked,
        reason="Quote volume sufficient" if passed else "Quote volume below minimum",
        metadata={"min_vol": min_vol},
    )


def check_book_depth(depth_notional: float | None, config: AppConfig) -> RiskComponent:
    if depth_notional is None:
        passed = not config.risk.liquidity.reject_missing_liquidity_metadata
        return RiskComponent(
            dimension=RiskDimension.liquidity,
            passed=passed,
            severity=RiskSeverity.info if passed else RiskSeverity.blocked,
            reason="Missing book depth metadata",
            metadata={},
        )
    min_depth = config.risk.liquidity.min_book_depth_notional_usdt
    passed = depth_notional >= min_depth
    return RiskComponent(
        dimension=RiskDimension.liquidity,
        raw_value=depth_notional,
        passed=passed,
        severity=RiskSeverity.info if passed else RiskSeverity.blocked,
        reason="Book depth sufficient" if passed else "Book depth below minimum",
        metadata={"min_depth": min_depth},
    )


def compute_liquidity_risk(
    scored_signal: Any, universe_candidate_metadata: dict[str, Any] | None, config: AppConfig
) -> list[RiskComponent]:
    if not config.risk.liquidity.enabled:
        return []
    meta = universe_candidate_metadata or {}
    spread = meta.get("spread_bps")
    volume = meta.get("quote_volume_24h")
    depth = meta.get("book_depth_usdt")
    return [
        check_spread_bps(spread, config),
        check_quote_volume(volume, config),
        check_book_depth(depth, config),
    ]


def build_liquidity_risk_report(components: list[RiskComponent]) -> dict:
    return {"components": [c.model_dump() for c in components]}
