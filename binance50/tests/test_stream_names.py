import pytest

from binance50.connectors.stream_names import (
    build_agg_trade_stream,
    build_book_ticker_stream,
    build_combined_stream_path,
    build_depth_stream,
    build_kline_stream,
    build_raw_stream_path,
    build_trade_stream,
    classify_usdm_stream_route,
    normalize_symbol_for_stream,
)


def test_normalize_symbol() -> None:
    assert normalize_symbol_for_stream("BTCUSDT") == "btcusdt"

    with pytest.raises(ValueError):
        normalize_symbol_for_stream("")

    with pytest.raises(ValueError):
        normalize_symbol_for_stream("BTC/USDT")


def test_build_streams() -> None:
    assert build_kline_stream("BTCUSDT", "1m") == "btcusdt@kline_1m"
    assert build_trade_stream("BTCUSDT") == "btcusdt@trade"
    assert build_agg_trade_stream("BTCUSDT") == "btcusdt@aggTrade"
    assert build_book_ticker_stream("BTCUSDT") == "btcusdt@bookTicker"
    assert build_depth_stream("BTCUSDT", 100) == "btcusdt@depth@100ms"


def test_build_streams_invalid_args() -> None:
    with pytest.raises(ValueError):
        build_kline_stream("BTCUSDT", "invalid")

    with pytest.raises(ValueError):
        build_depth_stream("BTCUSDT", 50)


def test_combined_and_raw_paths() -> None:
    assert build_raw_stream_path("btcusdt@trade") == "/ws/btcusdt@trade"
    assert (
        build_combined_stream_path(["btcusdt@trade", "ethusdt@trade"])
        == "/stream?streams=btcusdt@trade/ethusdt@trade"
    )


def test_usdm_classification() -> None:
    assert classify_usdm_stream_route("btcusdt@trade") == "market"
    assert classify_usdm_stream_route("unknown") == "public"
