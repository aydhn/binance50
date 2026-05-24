from datetime import datetime

import pytest

from binance50.config.models import AppConfig
from binance50.signals.models import SignalScoreComponent
from binance50.signals.scoring import SignalScoringEngine
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
    return c


@pytest.fixture
def engine(config):
    return SignalScoringEngine(config)


@pytest.fixture
def candidate():
    dt = datetime.now()
    exp = StrategyExplanation(summary="test")
    return SignalCandidate(
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
    )


def test_reject_candidate(engine, candidate):
    scored = engine.reject_candidate(candidate, "Test rejection")
    assert scored.status.value == "rejected"
    assert scored.intent.value == "no_action"
    assert scored.score == 0.0
    assert scored.explanation == "Test rejection"


def test_build_score_breakdown(engine, candidate):
    components = [
        SignalScoreComponent(
            name="c1",
            raw_value=50.0,
            normalized_value=50.0,
            weight=1.0,
            contribution=50.0,
            reason="r1",
        ),
        SignalScoreComponent(
            name="c2",
            raw_value=10.0,
            normalized_value=10.0,
            weight=-1.0,
            contribution=-10.0,
            reason="r2",
        ),
    ]
    bd = engine.build_score_breakdown(candidate, components)
    assert bd.subtotal_before_penalties == 50.0
    assert bd.total_penalty == 10.0
    assert bd.final_score == 40.0
    assert bd.score_tier.value in ["medium", "low"]


def test_compute_final_score(engine, config):
    components = [
        SignalScoreComponent(
            name="c1",
            raw_value=60.0,
            normalized_value=60.0,
            weight=1.0,
            contribution=60.0,
            reason="r1",
        ),
        SignalScoreComponent(
            name="c2",
            raw_value=50.0,
            normalized_value=50.0,
            weight=1.0,
            contribution=50.0,
            reason="r2",
        ),
    ]
    # Sum is 110, should clamp to 100
    assert engine.compute_final_score(components, config) == 100.0


def test_score_candidate_full(engine, candidate):
    # This invokes all the components
    scored = engine.score_candidate(
        candidate,
        group=None,
        conflicts=[],
        current_open_time=int(candidate.open_time.timestamp() * 1000) + 1,
    )
    assert scored.status.value == "scored_candidate"
    assert scored.score > 0.0
    assert scored.score_breakdown is not None
    assert len(scored.score_breakdown.components) == 7
    assert scored.explanation is not None
    assert "Candidate c1" in scored.explanation


def test_score_candidates(engine, candidate):
    candidates = [candidate]
    results = engine.score_candidates(candidates)
    assert len(results) == 1
    assert results[0].score > 0.0
