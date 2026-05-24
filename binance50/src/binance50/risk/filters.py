from typing import Any

from binance50.config.models import AppConfig
from binance50.risk.models import RiskComponent, RiskDimension, RiskSeverity


def extract_risk_relevant_filters(symbol_metadata: dict[str, Any]) -> dict[str, Any]:
    relevant_keys = [
        "PRICE_FILTER",
        "LOT_SIZE",
        "MARKET_LOT_SIZE",
        "MIN_NOTIONAL",
        "NOTIONAL",
        "PERCENT_PRICE",
        "PERCENT_PRICE_BY_SIDE",
    ]
    filters = symbol_metadata.get("filters", [])
    extracted = {}
    for f in filters:
        if isinstance(f, dict) and f.get("filterType") in relevant_keys:
            extracted[f["filterType"]] = f
    return extracted


def check_price_filter_metadata(
    symbol_metadata: dict[str, Any] | None, config: AppConfig
) -> RiskComponent:
    passed = True
    if not symbol_metadata and config.risk.spot.require_price_filter_check:
        passed = False
    return RiskComponent(
        dimension=RiskDimension.symbol_filter,
        passed=passed,
        severity=RiskSeverity.info if passed else RiskSeverity.blocked,
        reason="Price filter metadata available" if passed else "Missing price filter metadata",
        metadata={"filter": "PRICE_FILTER"},
    )


def check_lot_size_metadata(
    symbol_metadata: dict[str, Any] | None, config: AppConfig
) -> RiskComponent:
    passed = True
    if not symbol_metadata and config.risk.spot.require_lot_size_check:
        passed = False
    return RiskComponent(
        dimension=RiskDimension.symbol_filter,
        passed=passed,
        severity=RiskSeverity.info if passed else RiskSeverity.blocked,
        reason="Lot size metadata available" if passed else "Missing lot size metadata",
        metadata={"filter": "LOT_SIZE"},
    )


def check_min_notional_metadata(
    symbol_metadata: dict[str, Any] | None, config: AppConfig
) -> RiskComponent:
    passed = True
    if not symbol_metadata and config.risk.spot.require_min_notional_check:
        passed = False
    return RiskComponent(
        dimension=RiskDimension.symbol_filter,
        passed=passed,
        severity=RiskSeverity.info if passed else RiskSeverity.blocked,
        reason="Min notional metadata available" if passed else "Missing min notional metadata",
        metadata={"filter": "MIN_NOTIONAL/NOTIONAL"},
    )


def check_symbol_filter_readiness(
    symbol_metadata: dict[str, Any] | None, config: AppConfig
) -> list[RiskComponent]:
    return [
        check_price_filter_metadata(symbol_metadata, config),
        check_lot_size_metadata(symbol_metadata, config),
        check_min_notional_metadata(symbol_metadata, config),
    ]


def build_symbol_filter_risk_report(symbol_metadata: dict[str, Any] | None) -> dict:
    if not symbol_metadata:
        return {"status": "missing", "filters": {}}
    return {"status": "available", "filters": extract_risk_relevant_filters(symbol_metadata)}
