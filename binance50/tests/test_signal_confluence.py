import pytest
from datetime import datetime
from binance50.config.models import AppConfig
from binance50.signals.confluence import ConfluenceEngine
from binance50.strategies.models import SignalCandidate, StrategyDirection, StrategyCandidateStrength, StrategyPluginType, StrategyExplanation

@pytest.fixture
def config():
    return AppConfig()

@pytest.fixture
def engine(config):
    return ConfluenceEngine(config)

@pytest.fixture
def candidates():
    dt = datetime.now()
    exp = StrategyExplanation(summary="test")
    return [
        SignalCandidate(
            candidate_id="c1", symbol="BTCUSDT", market_scope="spot", interval="1m",
            open_time=dt, plugin_name="plugin_a", plugin_type=StrategyPluginType.trend_following,
            direction=StrategyDirection.bullish, strength=StrategyCandidateStrength.medium,
            confidence=80.0, explanation=exp
        ),
        SignalCandidate(
            candidate_id="c2", symbol="BTCUSDT", market_scope="spot", interval="1m",
            open_time=dt, plugin_name="plugin_b", plugin_type=StrategyPluginType.volume_confirmation,
            direction=StrategyDirection.bullish, strength=StrategyCandidateStrength.medium,
            confidence=80.0, explanation=exp
        ),
        SignalCandidate(
            candidate_id="c3", symbol="BTCUSDT", market_scope="spot", interval="1m",
            open_time=dt, plugin_name="plugin_c", plugin_type=StrategyPluginType.divergence_candidate,
            direction=StrategyDirection.bearish, strength=StrategyCandidateStrength.medium,
            confidence=80.0, explanation=exp
        )
    ]

def test_build_confluence_groups(engine, config, candidates):
    groups = engine.build_confluence_groups(candidates, config)
    assert len(groups) == 2 # One for bullish, one for bearish

    bullish_group = next(g for g in groups if g.direction == StrategyDirection.bullish)
    assert bullish_group.same_direction_count == 2
    assert bullish_group.opposite_direction_count == 1
    # score = (2 * 5.0 base) + 5.0 (diversity) = 15.0
    assert bullish_group.confluence_score == 15.0

def test_compute_confluence_score(engine, config, candidates):
    groups = engine.build_confluence_groups(candidates, config)
    bullish_group = next(g for g in groups if g.direction == StrategyDirection.bullish)
    comp = engine.compute_confluence_score(bullish_group, config)
    # raw_score 15.0 * 0.2 weight = 3.0
    assert comp.raw_value == 15.0
    assert comp.contribution == 3.0

def test_compute_confirmation_score(engine, config, candidates):
    groups = engine.build_confluence_groups(candidates, config)
    bullish_group = next(g for g in groups if g.direction == StrategyDirection.bullish)

    # Has trend and volume
    comp = engine.compute_confirmation_score(candidates[0], bullish_group, config)
    # Trend+Volume bonus = 5.0 -> raw = 5.0
    # weight = 0.1 -> contribution = 0.5
    assert comp.raw_value == 5.0
    assert comp.contribution == 0.5
