from pathlib import Path
from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import (
    MarketDataFetchDisabledError,
    SafetyError,
    UnsupportedIntervalError,
)
from binance50.market_data.fetch_plan import OHLCVFetchPlan


def assert_market_data_config_safe(config: AppConfig) -> None:
    if config.market_data.real_fetch_enabled:
        raise SafetyError(
            "market_data.real_fetch_enabled is True. Blocked by Phase 8 safety default."
        )


def assert_real_fetch_allowed(config: AppConfig) -> None:
    if not config.market_data.real_fetch_enabled:
        raise MarketDataFetchDisabledError("market_data.real_fetch_enabled is False")

    if not config.network.real_network_enabled:
        raise MarketDataFetchDisabledError("network.real_network_enabled is False")

    if not config.connector.connection_enabled:
        raise MarketDataFetchDisabledError("connector.connection_enabled is False")


def assert_symbol_interval_allowed(symbol: str, interval: str, config: AppConfig) -> None:
    if not symbol.isalnum() or len(symbol) < 3 or len(symbol) > 20:
        raise SafetyError(f"Invalid symbol format: {symbol}")

    if interval not in config.market_data.allowed_intervals:
        raise UnsupportedIntervalError(f"Interval {interval} is not in allowed_intervals")


def assert_fetch_plan_safe(plan: OHLCVFetchPlan, config: AppConfig) -> None:
    assert_symbol_interval_allowed(plan.symbol, plan.interval, config)

    if plan.total_expected_requests > 500:
        raise SafetyError(
            f"Fetch plan is too long. Requested {plan.total_expected_requests} chunks. Max allowed is 500."
        )


def assert_cache_path_safe(path: Path, config: AppConfig) -> None:
    try:
        resolved = path.resolve()
        # Ensure it is within the project root
        project_root = Path(__file__).parent.parent.parent.parent.resolve()
        if project_root not in resolved.parents and resolved != project_root:
            raise SafetyError(f"Cache path {path} resolves outside of project root")
    except Exception as e:
        if isinstance(e, SafetyError):
            raise
        raise SafetyError(f"Could not resolve safe cache path: {e}")


def build_market_data_safety_report(config: AppConfig) -> dict[str, Any]:
    issues = []
    status = "safe"

    try:
        assert_market_data_config_safe(config)
    except SafetyError as e:
        issues.append(str(e))
        status = "unsafe"

    try:
        assert_real_fetch_allowed(config)
    except MarketDataFetchDisabledError:
        pass  # Expected default

    return {
        "status": status,
        "real_fetch_disabled": not config.market_data.real_fetch_enabled,
        "network_enabled": config.network.real_network_enabled,
        "connector_enabled": config.connector.connection_enabled,
        "issues": issues,
    }
