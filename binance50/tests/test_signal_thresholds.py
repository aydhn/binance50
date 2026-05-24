import pytest

from binance50.config.models import AppConfig
from binance50.signals.models import SignalDecisionIntent
from binance50.signals.thresholds import (
    build_threshold_report,
    classify_signal_intent,
    passes_future_backtest_candidate_threshold,
    passes_research_candidate_threshold,
    passes_risk_review_threshold,
)


@pytest.fixture
def config():
    c = AppConfig()
    c.signals.thresholds.no_action_below = 40.0
    c.signals.thresholds.research_candidate_min = 50.0
    c.signals.thresholds.risk_review_min = 65.0
    c.signals.thresholds.future_backtest_candidate_min = 70.0
    return c


def test_passes_thresholds(config):
    assert not passes_research_candidate_threshold(49.0, config)
    assert passes_research_candidate_threshold(50.0, config)

    assert not passes_risk_review_threshold(64.0, config)
    assert passes_risk_review_threshold(65.0, config)

    assert not passes_future_backtest_candidate_threshold(69.0, config)
    assert passes_future_backtest_candidate_threshold(70.0, config)


def test_classify_signal_intent(config):
    assert classify_signal_intent(30.0, config) == SignalDecisionIntent.no_action
    assert classify_signal_intent(45.0, config) == SignalDecisionIntent.no_order  # >= 40, < 50
    assert classify_signal_intent(55.0, config) == SignalDecisionIntent.research_candidate
    assert classify_signal_intent(68.0, config) == SignalDecisionIntent.risk_review_candidate
    assert classify_signal_intent(80.0, config) == SignalDecisionIntent.future_backtest_candidate


def test_build_threshold_report(config):
    rep = build_threshold_report(config)
    assert rep["no_action_below"] == 40.0
    assert "warning" in rep
