from binance50.config.models import AppConfig
from binance50.core.enums import MarketScope
from binance50.streams.simulator import StreamSimulator


def test_stream_simulator():
    config = AppConfig()
    sim = StreamSimulator(config)
    res = sim.simulate_from_fixtures(["spot_kline_btcusdt_1m_closed.json"], MarketScope.SPOT)
    assert res.event_count >= 1
    assert res.accepted_count >= 1
    assert res.invalid_count == 0


def test_stream_simulator_invalid():
    config = AppConfig()
    sim = StreamSimulator(config)
    res = sim.simulate_from_fixtures(["stream_bad_missing_fields.json"], MarketScope.SPOT)
    assert res.event_count >= 1
    assert res.accepted_count == 0
    assert res.invalid_count == 1
