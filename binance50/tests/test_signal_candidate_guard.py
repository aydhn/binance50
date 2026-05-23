import pytest

from binance50.config.models import AppConfig
from binance50.core.exceptions import ActionableLanguageDetectedError
from binance50.safety.signal_candidate_guard import assert_candidate_safe
from binance50.strategies.models import (
    SignalCandidate,
    StrategyCandidateStrength,
    StrategyDirection,
    StrategyExplanation,
    StrategyIntent,
    StrategyPluginType,
)


def test_candidate_language_guard():
    config = AppConfig()
    exp_safe = StrategyExplanation(summary="RSI oversold candidate")
    c_safe = SignalCandidate(
        candidate_id="1",
        symbol="BTC",
        market_scope="spot",
        interval="1m",
        open_time=100,
        plugin_name="test",
        plugin_type=StrategyPluginType.trend_following,
        direction=StrategyDirection.bullish,
        strength=StrategyCandidateStrength.weak,
        confidence=50.0,
        explanation=exp_safe,
        intent=StrategyIntent.no_order,
    )
    assert_candidate_safe(c_safe, config)

    exp_unsafe = StrategyExplanation(summary="buy now")
    c_unsafe = SignalCandidate(
        candidate_id="1",
        symbol="BTC",
        market_scope="spot",
        interval="1m",
        open_time=100,
        plugin_name="test",
        plugin_type=StrategyPluginType.trend_following,
        direction=StrategyDirection.bullish,
        strength=StrategyCandidateStrength.weak,
        confidence=50.0,
        explanation=exp_unsafe,
        intent=StrategyIntent.no_order,
    )
    with pytest.raises(ActionableLanguageDetectedError):
        assert_candidate_safe(c_unsafe, config)
