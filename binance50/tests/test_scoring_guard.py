from datetime import datetime

import pytest

from binance50.config.models import AppConfig
from binance50.safety.scoring_guard import (
    assert_no_execution_threshold,
    assert_scored_signals_safe,
    assert_signal_config_safe,
    build_signal_scoring_safety_report,
)
from binance50.signals.models import (
    ScoredSignalCandidate,
    ScoredSignalStatus,
    SignalDecisionIntent,
    SignalScoreBreakdown,
    SignalScoreTier,
)


@pytest.fixture
def config():
    c = AppConfig()
    return c


@pytest.fixture
def scored():
    bd = SignalScoreBreakdown(
        components=[],
        subtotal_before_penalties=50.0,
        total_penalty=0.0,
        final_score=50.0,
        score_tier=SignalScoreTier.medium,
    )
    return ScoredSignalCandidate(
        scored_signal_id="s1",
        source_candidate_id="c1",
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        open_time=datetime.now(),
        direction="bullish",
        status=ScoredSignalStatus.scored_candidate,
        intent=SignalDecisionIntent.research_candidate,
        score=50.0,
        score_tier=SignalScoreTier.medium,
        confidence=80.0,
        plugin_name="plugin_a",
        plugin_type="trend_following",
        strategy_strength="medium",
        score_breakdown=bd,
        explanation="Safe explanation",
    )


def test_assert_signal_config_safe_defaults(config):
    assert_signal_config_safe(config)


def test_assert_signal_config_safe_failures(config):
    config.signals.execution_forbidden = False
    from binance50.core.exceptions import SignalConfigError

    with pytest.raises(SignalConfigError):
        assert_signal_config_safe(config)


def test_assert_no_execution_threshold(config):
    assert_no_execution_threshold(config)
    config.signals.thresholds.execution_threshold_deferred = False
    from binance50.core.exceptions import ExecutionThresholdForbiddenError

    with pytest.raises(ExecutionThresholdForbiddenError):
        assert_no_execution_threshold(config)


def test_assert_scored_signals_safe(scored, config):
    assert_scored_signals_safe([scored], config)

    # Test intent failure
    from binance50.core.exceptions import (
        ExecutionObjectDetectedError,
        SignalValidationError,
    )

    # In Pydantic Enum you can't simply inject random strings if validated but we can mock or construct
    bad_scored = scored.model_construct(intent="execution_buy")
    with pytest.raises(SignalValidationError):
        assert_scored_signals_safe([bad_scored], config)

    # Test execution field
    bad_scored2 = scored.model_copy(update={"metadata": {"order_id": "12345"}})
    with pytest.raises(ExecutionObjectDetectedError):
        assert_scored_signals_safe([bad_scored2], config)


def test_build_signal_scoring_safety_report(config):
    report = build_signal_scoring_safety_report(config)
    assert report["config_safe"] is True
    assert report["no_execution_threshold"] is True
    assert len(report["errors"]) == 0
