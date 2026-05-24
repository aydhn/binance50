from datetime import UTC, datetime

import pytest

from binance50.config.models import AppConfig
from binance50.signals.freshness import (
    compute_candidate_age_bars,
    compute_freshness_component,
    compute_freshness_multiplier,
    is_candidate_expired,
)
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
    c.signals.freshness.stale_score_multiplier = 0.5
    c.signals.freshness.expired_score_multiplier = 0.0
    c.signals.freshness.current_bar_multiplier = 1.0
    c.signals.component_weights["freshness"] = 0.05
    return c


@pytest.fixture
def candidate():
    dt = int(datetime.now(UTC).timestamp() * 1000)
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
        expiry_bars=3,
    )


def test_compute_candidate_age_bars(candidate):
    ts = candidate.open_time
    assert compute_candidate_age_bars(candidate, ts, "1m") == 0
    assert compute_candidate_age_bars(candidate, ts + 60000, "1m") == 1
    assert compute_candidate_age_bars(candidate, ts + 120000, "1m") == 2


def test_is_candidate_expired(candidate, config):
    ts = candidate.open_time
    assert not is_candidate_expired(candidate, ts, "1m", config)
    assert not is_candidate_expired(candidate, ts + 180000, "1m", config)  # 3 bars = not expired
    assert is_candidate_expired(candidate, ts + 240000, "1m", config)  # 4 bars = expired


def test_compute_freshness_multiplier(candidate, config):
    ts = candidate.open_time
    assert compute_freshness_multiplier(candidate, ts, "1m", config) == 1.0
    assert compute_freshness_multiplier(candidate, ts + 240000, "1m", config) == 0.0  # expired

    # 1 bar old out of 3 = 1.0 - (0.5/3)*1 = ~0.833
    val = compute_freshness_multiplier(candidate, ts + 60000, "1m", config)
    assert abs(val - 0.8333) < 0.01


def test_compute_freshness_component(candidate, config):
    ts = candidate.open_time
    comp = compute_freshness_component(candidate, ts + 60000, "1m", config)
    assert comp.name == "freshness"
    # val ~0.8333 * 100 = 83.33 * 0.05 = ~4.16
    assert abs(comp.raw_value - 83.33) < 0.1
    assert abs(comp.contribution - 4.16) < 0.1
