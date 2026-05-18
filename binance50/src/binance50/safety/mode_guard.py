import logging

from binance50.config.models import AppConfig
from binance50.core.enums import TradingMode
from binance50.core.exceptions import ConfigError, InvalidTradingModeError

logger = logging.getLogger(__name__)


def check_mode_consistency(config: AppConfig) -> None:
    """Check consistency between trading mode and runtime environment."""
    # Keep for backward compatibility with existing tests
    validate_environment_profile_consistency(config)


def validate_environment_profile_consistency(config: AppConfig) -> None:
    """Validate that the selected profile is consistent with the runtime trading mode."""
    mode = config.runtime.trading_mode
    profile = config.selected_environment_profile

    # Testnet mode needs testnet env profile
    if mode == TradingMode.TESTNET and not profile.is_testnet:
        raise InvalidTradingModeError(
            f"Testnet trading mode requires testnet profile, got {profile.profile_name}"
        )

    # Demo mode is considered paper mode for validation
    if mode == TradingMode.DEMO and not profile.is_testnet:
        raise InvalidTradingModeError(
            f"Demo trading mode requires testnet profile, got {profile.profile_name}"
        )

    # Live mode needs mainnet env
    if mode == TradingMode.LIVE and not profile.is_mainnet:
        raise InvalidTradingModeError(
            f"Live trading mode requires mainnet profile, got {profile.profile_name}"
        )

    # Live mode needs live profile
    if mode == TradingMode.LIVE and not profile.is_live:
        raise InvalidTradingModeError(
            f"Live trading mode requires live profile, got {profile.profile_name}"
        )

    # Testnet profile with Live mode
    if profile.is_testnet and mode == TradingMode.LIVE:
        raise InvalidTradingModeError(
            f"Testnet profile {profile.profile_name} cannot be used with live trading mode"
        )

    # Live profile with Paper mode
    if profile.is_live and mode in (TradingMode.PAPER, TradingMode.BACKTEST):
        raise InvalidTradingModeError(
            f"Live profile {profile.profile_name} cannot be used with paper/backtest trading mode"
        )


def validate_connector_flags(config: AppConfig) -> None:
    """Validate connector flags against the selected profile."""
    if not config.connector.connection_enabled:
        logger.info(
            "Connector is disabled globally via connection_enabled=false. "
            "No connections will be made."
        )
        return

    if config.connector.order_gateway_enabled:
        assert_order_gateway_allowed(config)


def assert_order_gateway_allowed(config: AppConfig) -> None:
    """Assert that the order gateway is allowed for the current profile."""
    profile = config.selected_environment_profile
    if not profile.supports_order_placement:
        raise ConfigError(
            f"Profile {profile.profile_name} does not support order placement, "
            "but order_gateway_enabled is true."
        )
    if profile.is_paper:
        raise ConfigError(
            f"Paper profile {profile.profile_name} does not support order placement, "
            "but order_gateway_enabled is true."
        )
