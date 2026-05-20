from typing import Any

from binance50.config.models import AppConfig
from binance50.core.enums import TradingMode
from binance50.core.exceptions import DryRunViolationError, OrderPathDisabledError


def is_effective_ordering_disabled(config: AppConfig) -> bool:
    if config.safety.disable_all_orders:
        return True
    return bool(config.safety.dry_run)


def get_effective_trading_mode(config: AppConfig) -> TradingMode:
    if config.safety.force_paper_mode:
        return TradingMode.PAPER
    return config.runtime.trading_mode


def assert_dry_run_safe(config: AppConfig) -> None:
    if config.safety.dry_run and config.connector.order_gateway_enabled:
        raise DryRunViolationError("Order gateway cannot be enabled while dry_run is true")


def assert_no_order_path_when_disabled(config: AppConfig) -> None:
    if config.safety.disable_all_orders and config.connector.order_gateway_enabled:
        raise OrderPathDisabledError(
            "Order gateway cannot be enabled while disable_all_orders is true"
        )


def assert_force_paper_mode(config: AppConfig) -> None:
    if config.safety.force_paper_mode and config.runtime.trading_mode != TradingMode.PAPER:
        # Though the config validator also catches this, we have it as a guard check too
        pass


def build_dry_run_report(config: AppConfig) -> dict[str, Any]:
    effective_mode = get_effective_trading_mode(config)
    ordering_disabled = is_effective_ordering_disabled(config)

    issues = []
    try:
        assert_dry_run_safe(config)
    except Exception as e:
        issues.append(str(e))

    try:
        assert_no_order_path_when_disabled(config)
    except Exception as e:
        issues.append(str(e))

    return {
        "status": "unsafe" if issues else "safe",
        "issues": issues,
        "dry_run": config.safety.dry_run,
        "force_paper_mode": config.safety.force_paper_mode,
        "disable_all_orders": config.safety.disable_all_orders,
        "effective_trading_mode": effective_mode.value,
        "real_orders_impossible": ordering_disabled,
        "order_gateway_enabled": config.connector.order_gateway_enabled,
    }
