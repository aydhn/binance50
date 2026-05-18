class Binance50Error(Exception):
    """Base exception for binance50."""

    pass


class ConfigError(Binance50Error):
    """Configuration related errors."""

    pass


class SafetyError(Binance50Error):
    """Safety and guard related errors."""

    pass


class SecretLeakError(SafetyError):
    """Secret leak related errors."""

    pass


class LiveTradingBlockedError(SafetyError):
    """Live trading is blocked."""

    pass


class InvalidTradingModeError(SafetyError):
    """Invalid trading mode."""

    pass
