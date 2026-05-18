from binance50.config.models import AppConfig
from binance50.core.enums import RuntimeEnvironment, TradingMode
from binance50.core.exceptions import InvalidTradingModeError


def check_mode_consistency(config: AppConfig) -> None:
    """Check consistency between trading mode and runtime environment."""
    mode = config.runtime.trading_mode
    env = config.runtime.environment

    # Paper mode is safe everywhere
    if mode == TradingMode.PAPER:
        return

    # Testnet mode needs testnet env
    if mode == TradingMode.TESTNET and env != RuntimeEnvironment.TESTNET:
        raise InvalidTradingModeError(
            f"Testnet trading mode requires testnet environment, got {env}"
        )

    # Demo mode needs demo env
    if mode == TradingMode.DEMO and env != RuntimeEnvironment.DEMO:
        raise InvalidTradingModeError(f"Demo trading mode requires demo environment, got {env}")

    # Live mode needs mainnet env
    if mode == TradingMode.LIVE and env != RuntimeEnvironment.MAINNET:
        raise InvalidTradingModeError(f"Live trading mode requires mainnet environment, got {env}")
