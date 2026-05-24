from datetime import datetime

import pytest

from binance50.config.models import AppConfig
from binance50.risk.engine import RiskEngine
from binance50.risk.models import RiskAssessmentStatus, RiskRunRequest


@pytest.fixture
def test_config():
    return AppConfig()


class DummyScoredSignal:
    def __init__(self, score):
        self.final_score = score
        self.id = "sig1"
        self.symbol = "BTCUSDT"
        self.market_scope = "spot"
        self.interval = "1m"
        self.open_time = datetime.utcnow()
        self.close_time = datetime.utcnow()
        self.direction = "bullish"


def test_risk_engine_run(test_config):
    engine = RiskEngine(test_config)
    req = RiskRunRequest(symbol="BTCUSDT")

    # Test with a passing score
    sig_pass = DummyScoredSignal(80.0)
    res_pass = engine.run([sig_pass], None, req)

    assert res_pass.success is True
    assert len(res_pass.assessments) == 1
    assert res_pass.assessments[0].status == RiskAssessmentStatus.approved_for_paper_review
    assert res_pass.assessments[0].hypothetical_notional_usdt is not None

    # Test with a failing score
    sig_fail = DummyScoredSignal(30.0)
    res_fail = engine.run([sig_fail], None, req)

    assert len(res_fail.rejected_assessments) == 1
    assert res_fail.rejected_assessments[0].status == RiskAssessmentStatus.blocked_by_policy


def test_risk_engine_disabled(test_config):
    test_config.risk.enabled = False
    engine = RiskEngine(test_config)
    res = engine.run([], None, RiskRunRequest())
    assert res.success is False
    assert res.error == "Risk engine is disabled."
