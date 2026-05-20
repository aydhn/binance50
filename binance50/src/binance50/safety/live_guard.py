from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import LiveTradingBlockedError
from binance50.security.live_unlock import get_live_unlock_status


def assert_live_trading_allowed(config: AppConfig) -> None:
    """
    Validate that all conditions for live trading are met.
    Raises LiveTradingBlockedError if any condition fails.
    """
    profile = config.selected_environment_profile

    # 1. Profile must be live and mainnet
    if not profile.is_live:
        raise LiveTradingBlockedError("Selected profile is not marked as live")
    if not profile.is_mainnet:
        raise LiveTradingBlockedError("Selected profile is not a mainnet profile")
    if not profile.allows_real_orders:
        raise LiveTradingBlockedError("Selected profile does not allow real orders")

    # 2. Cannot be a readonly profile
    if profile.profile_name.value.endswith("_readonly"):
        raise LiveTradingBlockedError("Readonly profile cannot be used for live trading")

    # 3. Safety flags must allow it
    if config.safety.dry_run:
        raise LiveTradingBlockedError("Live trading blocked: dry_run is true")
    if config.safety.force_paper_mode:
        raise LiveTradingBlockedError("Live trading blocked: force_paper_mode is true")
    if config.safety.disable_all_orders:
        raise LiveTradingBlockedError("Live trading blocked: disable_all_orders is true")
    if not config.safety.allow_live_orders:
        raise LiveTradingBlockedError("Live trading blocked: allow_live_orders is false")
    if not config.safety.enable_live_trading:
        raise LiveTradingBlockedError("Live trading blocked: enable_live_trading is false")
    if not config.safety.confirm_live_trading:
        raise LiveTradingBlockedError("Live trading blocked: confirm_live_trading is false")

    # 4. Live Unlock phrases
    unlock_status = get_live_unlock_status(config)
    if unlock_status["requires_manual_unlock"] and not unlock_status["unlock_phrase_present"]:
        raise LiveTradingBlockedError(
            "Live trading blocked: manual unlock phrase missing or incorrect"
        )
    if unlock_status["requires_mainnet_confirmation"] and not unlock_status["risk_ack_present"]:
        raise LiveTradingBlockedError(
            "Live trading blocked: risk acknowledgement missing or incorrect"
        )

    # 5. Connector must be enabled
    if not config.connector.connection_enabled:
        raise LiveTradingBlockedError("Live trading blocked: connection_enabled is false")
    if not config.connector.order_gateway_enabled:
        raise LiveTradingBlockedError("Live trading blocked: order_gateway_enabled is false")

    # 6. Credentials and Permissions
    creds = config.credentials.binance
    has_key = creds.api_key is not None and creds.api_key.get_secret_value() != ""
    has_secret = creds.api_secret is not None and creds.api_secret.get_secret_value() != ""

    if not (has_key and has_secret):
        raise LiveTradingBlockedError("Live trading blocked: API key or secret missing")

    if profile.market_scope.value == "spot" and not creds.permission_spot_trade:
        raise LiveTradingBlockedError("Live trading blocked: spot trade permission required")
    if profile.market_scope.value == "usdm_futures" and not creds.permission_futures_trade:
        raise LiveTradingBlockedError("Live trading blocked: futures trade permission required")


def build_live_guard_report(config: AppConfig) -> dict[str, Any]:
    """Build a detailed report of live trading guard status without throwing exceptions."""
    blocking_reasons = []

    try:
        assert_live_trading_allowed(config)
    except LiveTradingBlockedError as e:
        blocking_reasons.append(str(e))
    except Exception as e:
        blocking_reasons.append(f"Unexpected error in live guard: {str(e)}")

    is_blocked = len(blocking_reasons) > 0

    return {
        "live_trading_blocked": is_blocked,
        "blocking_reasons": blocking_reasons,
    }
