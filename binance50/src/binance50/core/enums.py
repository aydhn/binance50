from enum import StrEnum


class ExchangeName(StrEnum):
    BINANCE = "binance"


class AccountDomain(StrEnum):
    SPOT = "spot"
    USDM_FUTURES = "usdm_futures"
    COINM_FUTURES = "coinm_futures"


class EnvironmentProfileName(StrEnum):
    LOCAL_PAPER_SPOT = "local_paper_spot"
    LOCAL_PAPER_USDM_FUTURES = "local_paper_usdm_futures"
    SPOT_TESTNET = "spot_testnet"
    USDM_FUTURES_TESTNET = "usdm_futures_testnet"
    SPOT_MAINNET_READONLY = "spot_mainnet_readonly"
    USDM_FUTURES_MAINNET_READONLY = "usdm_futures_mainnet_readonly"
    SPOT_MAINNET_LIVE = "spot_mainnet_live"
    USDM_FUTURES_MAINNET_LIVE = "usdm_futures_mainnet_live"
    COINM_FUTURES_PLACEHOLDER = "coinm_futures_placeholder"


class EndpointRole(StrEnum):
    REST_PRIMARY = "rest_primary"
    REST_FALLBACK = "rest_fallback"
    WEBSOCKET_MARKET = "websocket_market"
    WEBSOCKET_USER = "websocket_user"


class PermissionLevel(StrEnum):
    NO_CREDENTIALS = "no_credentials"
    READ_ONLY = "read_only"
    TEST_ORDER = "test_order"
    LIVE_ORDER = "live_order"


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
