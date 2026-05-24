from datetime import datetime

import pytest

from binance50.config.models import AppConfig
from binance50.signals.weighting import SignalWeightingEngine
from binance50.strategies.models import (
    SignalCandidate,
    StrategyCandidateStrength,
    StrategyDirection,
    StrategyPluginType,
)


@pytest.fixture
def config():
    c = AppConfig()
    c.signals.plugin_weights["test_plugin"] = 1.2
    c.signals.component_weights["test_comp"] = 0.5
    return c


@pytest.fixture
def weighting_engine():
    return SignalWeightingEngine()


def test_get_plugin_weight_known(config, weighting_engine):
    assert weighting_engine.get_plugin_weight("test_plugin", "trend_following", config) == 1.2


def test_get_plugin_weight_unknown_type(config, weighting_engine):
    # fallback to plugin type
    assert weighting_engine.get_plugin_weight("unknown", "trend_following", config) == 1.0


def test_get_component_weight(config, weighting_engine):
    assert weighting_engine.get_component_weight("test_comp", config) == 0.5
    # negative fallback to 0.0 unless conflict_penalty
    config.signals.component_weights["invalid_neg"] = -0.5
    assert weighting_engine.get_component_weight("invalid_neg", config) == 0.0
    assert weighting_engine.get_component_weight("conflict_penalty", config) == -0.2


def test_compute_plugin_weighted_score(config, weighting_engine):
    cand = SignalCandidate(
        candidate_id="c1",
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        open_time=datetime.now(),
        plugin_name="test_plugin",
        plugin_type=StrategyPluginType.trend_following,
        direction=StrategyDirection.bullish,
        strength=StrategyCandidateStrength.medium,
        confidence=80.0,
        explanation={
            "summary": "test"
        },  # mock dict, it gets validated usually but bypassing strict validation here
    )

    # We need to properly mock explanation for Pydantic
    from binance50.strategies.models import StrategyExplanation

    cand = cand.model_copy(update={"explanation": StrategyExplanation(summary="test")})

    comp = weighting_engine.compute_plugin_weighted_score(cand, config)
    assert comp.name == "plugin_weighted_score"
    assert comp.weight == 1.2
    assert comp.contribution == 80.0 * 1.2
