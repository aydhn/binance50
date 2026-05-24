from datetime import datetime

import pytest

from binance50.config.models import AppConfig
from binance50.risk.exposure import (
    ExposureSnapshot,
    build_simulated_exposure_snapshot,
    check_correlated_candidates_placeholder,
    check_symbol_exposure,
    check_total_exposure,
)
from binance50.risk.models import RiskAssessment, RiskAssessmentStatus, RiskBreakdown, RiskIntent


@pytest.fixture
def test_config():
    return AppConfig()


def test_build_simulated_exposure_snapshot(test_config):
    a1 = RiskAssessment(
        assessment_id="1",
        source_scored_signal_id="s1",
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        open_time=datetime.utcnow(),
        close_time=datetime.utcnow(),
        direction="bullish",
        status=RiskAssessmentStatus.needs_review,
        intent=RiskIntent.risk_review,
        final_risk_score=60.0,
        risk_tier="low",
        approved=False,
        blocked=False,
        needs_review=True,
        breakdown=RiskBreakdown(),
        explanation="test",
        hypothetical_risk_pct=1.0,
    )
    a2 = RiskAssessment(
        assessment_id="2",
        source_scored_signal_id="s2",
        symbol="BTCUSDT",
        market_scope="spot",
        interval="1m",
        open_time=datetime.utcnow(),
        close_time=datetime.utcnow(),
        direction="bullish",
        status=RiskAssessmentStatus.needs_review,
        intent=RiskIntent.risk_review,
        final_risk_score=60.0,
        risk_tier="low",
        approved=False,
        blocked=False,
        needs_review=True,
        breakdown=RiskBreakdown(),
        explanation="test",
        hypothetical_risk_pct=2.0,
    )
    snapshot = build_simulated_exposure_snapshot([a1, a2], test_config)
    assert snapshot.total_exposure_pct == 3.0
    assert snapshot.symbol_exposure_pct["BTCUSDT"] == 3.0
    assert snapshot.open_risk_candidates == 2


def test_exposure_checks(test_config):
    test_config.risk.position_risk.max_symbol_exposure_pct = 2.0
    test_config.risk.position_risk.max_total_exposure_pct = 5.0
    test_config.risk.global_limits.max_correlated_candidates = 1

    snapshot = ExposureSnapshot(
        total_exposure_pct=6.0, symbol_exposure_pct={"BTCUSDT": 3.0}, correlated_candidates=2
    )

    comp_sym = check_symbol_exposure(snapshot, "BTCUSDT", test_config)
    assert comp_sym.passed is False

    comp_tot = check_total_exposure(snapshot, test_config)
    assert comp_tot.passed is False

    comp_corr = check_correlated_candidates_placeholder(snapshot, test_config)
    assert comp_corr.passed is False
