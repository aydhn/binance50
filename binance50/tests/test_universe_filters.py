from binance50.config.models import UniverseConfig
from binance50.core.enums import MarketScope
from binance50.universe.blacklist import SymbolListPolicy
from binance50.universe.filters import (
    evaluate_symbol_metadata,
    is_leveraged_token_symbol,
    is_stablecoin_pair,
)
from binance50.universe.models import SymbolMetadata, SymbolRejectionReason, SymbolStatus


def test_is_stablecoin_pair():
    assert is_stablecoin_pair("USDC", "USDT")
    assert is_stablecoin_pair("BUSD", "TRY")
    assert not is_stablecoin_pair("BTC", "USDT")


def test_is_leveraged_token():
    assert is_leveraged_token_symbol("BTCUPUSDT")
    assert is_leveraged_token_symbol("BTCDOWNUSDT")
    assert is_leveraged_token_symbol("ETHBULLUSDT")
    assert is_leveraged_token_symbol("ETHBEARUSDT")
    assert not is_leveraged_token_symbol("BTCUSDT")


def test_evaluate_symbol_metadata():
    c = UniverseConfig()
    bl = SymbolListPolicy()
    wl = SymbolListPolicy()

    m = SymbolMetadata(
        symbol="BTCUSDT",
        base_asset="BTC",
        quote_asset="USDT",
        status=SymbolStatus.HALT,
        market_scope=MarketScope.SPOT,
    )

    reasons, _ = evaluate_symbol_metadata(m, c, bl, wl)
    assert SymbolRejectionReason.NOT_TRADING in reasons
    assert SymbolRejectionReason.MISSING_FILTERS in reasons  # because it has no filters

    m.status = SymbolStatus.TRADING
    m.quote_asset = "BTC"
    reasons, _ = evaluate_symbol_metadata(m, c, bl, wl)
    assert SymbolRejectionReason.QUOTE_ASSET_NOT_ALLOWED in reasons

    m.quote_asset = "USDT"
    bl.symbols = ["BTCUSDT"]
    reasons, _ = evaluate_symbol_metadata(m, c, bl, wl)
    assert SymbolRejectionReason.BLACKLISTED in reasons

    bl.symbols = []
    m.base_asset = "USDC"
    reasons, _ = evaluate_symbol_metadata(m, c, bl, wl)
    assert SymbolRejectionReason.STABLECOIN_PAIR in reasons

    m.base_asset = "BTCUP"
    m.symbol = "BTCUPUSDT"
    reasons, _ = evaluate_symbol_metadata(m, c, bl, wl)
    assert SymbolRejectionReason.LEVERAGED_TOKEN in reasons
