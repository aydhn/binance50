from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import ConfigError
from binance50.safety.live_guard import check_live_trading_guard
from binance50.safety.mode_guard import check_mode_consistency, validate_connector_flags


def validate_environment_matrix(config: AppConfig) -> None:
    """Validate the complete environment matrix."""
    validate_selected_profile(config)


def validate_selected_profile(config: AppConfig) -> None:
    """Validate the selected environment profile."""
    # This implicitly checks basic profile constraints via Pydantic model_validators
    _ = config.selected_environment_profile

    assert_no_real_orders_in_paper(config)
    assert_no_orders_in_readonly(config)

    check_mode_consistency(config)
    check_live_trading_guard(config)
    validate_connector_flags(config)


def assert_no_real_orders_in_paper(config: AppConfig) -> None:
    """Assert that paper modes do not allow real orders."""
    profile = config.selected_environment_profile
    if profile.is_paper and profile.allows_real_orders:
        raise ConfigError(f"Paper profile {profile.profile_name} cannot allow real orders.")


def assert_no_orders_in_readonly(config: AppConfig) -> None:
    """Assert that readonly modes do not allow real orders."""
    profile = config.selected_environment_profile
    if profile.permission_level.value == "read_only" and profile.supports_order_placement:
        raise ConfigError(
            f"Read-only profile {profile.profile_name} cannot support order placement."
        )


def build_environment_safety_report(config: AppConfig) -> dict[str, Any]:
    """Build a comprehensive safety report of the environment."""
    profile = config.selected_environment_profile

    blocking_reasons = []

    try:
        validate_environment_matrix(config)
    except Exception as e:
        blocking_reasons.append(str(e))

    safety_status = "unsafe" if blocking_reasons else "safe"
    if not blocking_reasons and profile.is_paper:
        safety_status = "safe: paper mode, real orders disabled"

    return {
        "selected_profile": profile.profile_name.value,
        "trading_mode": config.runtime.trading_mode.value,
        "market_scope": config.runtime.market_scope.value,
        "account_domain": config.runtime.account_domain.value,
        "is_testnet": profile.is_testnet,
        "is_mainnet": profile.is_mainnet,
        "is_paper": profile.is_paper,
        "is_live": profile.is_live,
        "allows_real_orders": profile.allows_real_orders,
        "connector_enabled": config.connector.connection_enabled,
        "order_gateway_enabled": config.connector.order_gateway_enabled,
        "websocket_enabled": config.connector.websocket_enabled,
        "safety_status": safety_status,
        "blocking_reasons": blocking_reasons,
    }
