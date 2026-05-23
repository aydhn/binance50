import pytest

from binance50.config.models import AppConfig
from binance50.core.enums import MarketScope
from binance50.streams.event_types import StreamType
from binance50.streams.subscription import build_subscribe_payload, build_subscription_plan


def test_build_subscription_plan():
    config = AppConfig()
    plan = build_subscription_plan(
        symbols=["BTCUSDT", "ETHUSDT"],
        stream_types=[StreamType.kline, StreamType.book_ticker],
        market_scope=MarketScope.SPOT,
        config=config,
        interval="1m",
    )
    assert len(plan.subscriptions) == 4
    assert plan.use_combined is True
    assert plan.combined_path is not None
    assert "btcusdt@kline_1m" in plan.combined_path

    payload = build_subscribe_payload(plan.subscriptions)
    assert payload["method"] == "SUBSCRIBE"
    assert len(payload["params"]) == 4


def test_max_symbols_limit():
    config = AppConfig()
    config.streams.max_symbols_per_stream_plan = 2
    with pytest.raises(ValueError):
        build_subscription_plan(
            ["BTCUSDT", "ETHUSDT", "BNBUSDT"], [StreamType.kline], MarketScope.SPOT, config
        )
