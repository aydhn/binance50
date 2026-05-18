from enum import StrEnum


class TradingMode(StrEnum):
    BACKTEST = "backtest"
    PAPER = "paper"
    TESTNET = "testnet"
    DEMO = "demo"
    LIVE = "live"


class MarketScope(StrEnum):
    SPOT = "spot"
    USDM_FUTURES = "usdm_futures"
    COINM_FUTURES = "coinm_futures"


class RuntimeEnvironment(StrEnum):
    LOCAL = "local"
    TESTNET = "testnet"
    DEMO = "demo"
    MAINNET = "mainnet"


class OrderIntent(StrEnum):
    OBSERVE_ONLY = "observe_only"
    SIMULATED = "simulated"
    TESTNET_ORDER = "testnet_order"
    LIVE_ORDER = "live_order"
