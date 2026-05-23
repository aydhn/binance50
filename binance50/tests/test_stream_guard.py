import pytest

from binance50.config.models import AppConfig
from binance50.core.exceptions import StreamConnectionDisabledError
from binance50.safety.stream_guard import (
    assert_real_stream_connect_allowed,
    build_stream_safety_report,
)


def test_stream_guard_blocks_real_connect():
    config = AppConfig()
    # Default is false
    assert config.streams.market_stream_real_connect_enabled is False
    with pytest.raises(StreamConnectionDisabledError):
        assert_real_stream_connect_allowed(config)


def test_stream_safety_report():
    config = AppConfig()
    rep = build_stream_safety_report(config)
    assert rep["status"] == "safe"
    assert "real_stream_disabled" in rep["reasons"]
