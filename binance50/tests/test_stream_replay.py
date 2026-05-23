from binance50.config.models import AppConfig
from binance50.core.enums import MarketScope
from binance50.streams.replay import StreamReplayEngine


def test_stream_replay():
    config = AppConfig()
    engine = StreamReplayEngine(config)
    res = engine.replay_fixture_sequence(
        ["spot_kline_btcusdt_1m_closed.json"], MarketScope.SPOT, speed_multiplier=1.0
    )
    assert res.event_count == 1
    assert res.speed_multiplier == 1.0
