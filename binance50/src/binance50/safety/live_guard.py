import os

from binance50.config.models import AppConfig
from binance50.core.enums import RuntimeEnvironment, TradingMode
from binance50.core.exceptions import LiveTradingBlockedError


def check_live_trading_guard(config: AppConfig) -> None:
    """Check if live trading is allowed and fully confirmed."""
    if config.runtime.trading_mode == TradingMode.LIVE:
        if not config.safety.enable_live_trading:
            raise LiveTradingBlockedError(
                "Live trading requested but safety.enable_live_trading is false"
            )

        if not config.safety.confirm_live_trading:
            raise LiveTradingBlockedError(
                "Live trading requested but safety.confirm_live_trading is false"
            )

        if config.runtime.environment != RuntimeEnvironment.MAINNET:
            raise LiveTradingBlockedError(
                f"Live trading requires mainnet environment, got {config.runtime.environment}"
            )

        # Extra layer: check explicitly for an env var flag
        if os.environ.get("LIVE_ALLOWED", "false").lower() != "true":
            raise LiveTradingBlockedError(
                "Live trading blocked: LIVE_ALLOWED environment variable is not set to true. "
                "This is a required multi-layer protection."
            )
