import pytest
from pydantic import ValidationError

from binance50.strategies.models import (
    SignalCandidate,
    StrategyCandidateStrength,
    StrategyDirection,
    StrategyExplanation,
    StrategyPluginType,
)


def test_signal_candidate_bounds():
    exp = StrategyExplanation(summary="test")
    # Valid
    SignalCandidate(
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
        explanation=exp,
    )

    # Invalid confidence
    with pytest.raises(ValidationError):
        SignalCandidate(
            candidate_id="1",
            symbol="BTC",
            market_scope="spot",
            interval="1m",
            open_time=100,
            plugin_name="test",
            plugin_type=StrategyPluginType.trend_following,
            direction=StrategyDirection.bullish,
            strength=StrategyCandidateStrength.weak,
            confidence=150.0,
            explanation=exp,
        )


def test_signal_candidate_no_execution_fields():
    exp = StrategyExplanation(summary="test")
    c = SignalCandidate(
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
        explanation=exp,
    )
    assert not hasattr(c, "order_id")
    assert not hasattr(c, "quantity")
