from datetime import datetime

import pytest

from binance50.config.models import AppConfig
from binance50.signals.engine import SignalEngine
from binance50.signals.models import SignalScoringRequest
from binance50.strategies.models import (
    SignalCandidate,
    StrategyCandidateStrength,
    StrategyDirection,
    StrategyExplanation,
    StrategyPluginType,
)


@pytest.fixture
def config():
    c = AppConfig()
    c.signals.cache_enabled = False  # disable real saving
    return c


@pytest.fixture
def engine(config):
    return SignalEngine(config)


@pytest.fixture
def candidates():
    dt = datetime.now()
    exp = StrategyExplanation(summary="test")
    return [
        SignalCandidate(
            candidate_id="c1",
            symbol="BTCUSDT",
            market_scope="spot",
            interval="1m",
            open_time=dt,
            plugin_name="plugin_a",
            plugin_type=StrategyPluginType.trend_following,
            direction=StrategyDirection.bullish,
            strength=StrategyCandidateStrength.medium,
            confidence=80.0,
            explanation=exp,
        ),
        SignalCandidate(
            candidate_id="c2",
            symbol="BTCUSDT",
            market_scope="spot",
            interval="1m",
            open_time=dt,
            plugin_name="plugin_b",
            plugin_type=StrategyPluginType.volume_confirmation,
            direction=StrategyDirection.bullish,
            strength=StrategyCandidateStrength.medium,
            confidence=80.0,
            explanation=exp,
        ),
    ]


def test_engine_run(engine, candidates):
    req = SignalScoringRequest(symbol="BTCUSDT", market_scope="spot", interval="1m")
    result = engine.run(candidates, req)

    assert result.success is True
    assert len(result.scored_candidates) == 2
    assert len(result.confluence_groups) == 1
    assert result.quality_report.status == "passed"
    assert result.metadata.input_candidate_count == 2
    assert result.metadata.scored_candidate_count == 2
    assert result.metadata.conflict_count == 0


def test_engine_run_with_empty(engine):
    req = SignalScoringRequest(symbol="BTCUSDT", market_scope="spot", interval="1m")
    result = engine.run([], req)
    # empty should succeed (if reject_empty is False, which is default)
    assert result.success is True
    assert result.metadata.input_candidate_count == 0
