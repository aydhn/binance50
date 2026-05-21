from typing import Any

from binance50.config.models import AppConfig
from binance50.core.enums import TradingMode
from binance50.core.exceptions import SafetyError


def validate_mode_consistency(config: AppConfig) -> None:
    """
    Ensure the runtime trading mode matches the capabilities of the selected profile
    and does not violate Phase 4 safety flags.
    """
    mode = config.runtime.trading_mode
    profile = config.selected_environment_profile

    # Phase 4 Mode Safety Overrides
    if config.safety.force_paper_mode and mode != TradingMode.PAPER:
        raise SafetyError(
            f"force_paper_mode is true, but trading_mode is {mode.value}. Mode must be paper."
        )

    if config.safety.disable_all_orders and config.connector.order_gateway_enabled:
        raise SafetyError("disable_all_orders is true, but order_gateway_enabled is true.")

    # General Consistency
    if mode == TradingMode.LIVE and not profile.is_live:
        raise SafetyError(
            f"Trading mode is {mode.value} but profile {profile.profile_name.value} "
            "does not support live trading"
        )

    if mode == TradingMode.TESTNET and not profile.is_testnet:
        raise SafetyError(
            f"Trading mode is {mode.value} but profile {profile.profile_name.value} "
            "is not a testnet profile"
        )

    if (
        mode == TradingMode.PAPER
        and not profile.is_paper
        and config.connector.order_gateway_enabled
    ):
        # Paper mode can run against testnet/live profiles if we don't send orders
        # But we must verify that order_gateway is completely disabled in this configuration
        raise SafetyError(
            "Paper trading mode cannot be used with an enabled order gateway "
            f"on non-paper profile {profile.profile_name.value}"
        )

    # Phase 4 specific flags for testnet/demo
    if (
        mode == TradingMode.TESTNET
        and not config.safety.allow_testnet_orders
        and config.connector.order_gateway_enabled
    ):
        raise SafetyError(
            "Testnet trading is active, but allow_testnet_orders is false while order_gateway is enabled."
        )

    # Readonly profile verification
    if profile.profile_name.value.endswith("_readonly"):
        creds = config.credentials.binance
        if creds.permission_spot_trade or creds.permission_futures_trade:
            raise SafetyError(
                f"Profile {profile.profile_name.value} is readonly but trade permissions are configured"
            )
        if config.connector.order_gateway_enabled:
            raise SafetyError(
                f"Profile {profile.profile_name.value} is readonly but order_gateway is enabled"
            )


def build_mode_guard_report(config: AppConfig) -> dict[str, Any]:
    """Build a report of mode consistency without throwing exceptions."""
    issues = []

    try:
        validate_mode_consistency(config)
    except SafetyError as e:
        issues.append(str(e))
    except Exception as e:
        issues.append(f"Unexpected error in mode guard: {str(e)}")

    return {
        "status": "unsafe" if issues else "safe",
        "issues": issues,
    }
