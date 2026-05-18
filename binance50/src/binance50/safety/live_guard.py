import os

from binance50.config.models import AppConfig
from binance50.core.enums import TradingMode
from binance50.core.exceptions import LiveTradingBlockedError


def check_live_trading_guard(config: AppConfig) -> None:
    """Check if live trading is allowed and fully confirmed."""
    profile = config.selected_environment_profile

    if profile.is_live or config.runtime.trading_mode == TradingMode.LIVE:
        if config.runtime.trading_mode != TradingMode.LIVE:
            raise LiveTradingBlockedError("Live profile requires TradingMode.LIVE")

        if not profile.is_live:
            raise LiveTradingBlockedError("TradingMode.LIVE requires a live profile")

        if not profile.is_mainnet:
            raise LiveTradingBlockedError("Live trading requires a mainnet profile")

        if not profile.allows_real_orders:
            raise LiveTradingBlockedError("Live trading profile must allow real orders")

        if not profile.requires_live_guard:
            raise LiveTradingBlockedError("Live trading profile must require live guard")

        if not config.safety.allow_live_orders:
            raise LiveTradingBlockedError("safety.allow_live_orders must be true")

        if not config.safety.enable_live_trading:
            raise LiveTradingBlockedError("safety.enable_live_trading must be true")

        if not config.safety.confirm_live_trading:
            raise LiveTradingBlockedError("safety.confirm_live_trading must be true")

        if os.environ.get("BINANCE50_LIVE_UNLOCK") != "I_UNDERSTAND_REAL_MONEY_RISK":
            raise LiveTradingBlockedError(
                "BINANCE50_LIVE_UNLOCK environment variable must be set "
                "to 'I_UNDERSTAND_REAL_MONEY_RISK'"
            )

        if not config.connector.order_gateway_enabled:
            raise LiveTradingBlockedError(
                "connector.order_gateway_enabled must be true for live trading"
            )
