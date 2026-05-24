import pytest

from binance50.config.models import AppConfig
from binance50.risk.models import (
    RiskAssessmentStatus,
    RiskComponent,
    RiskDimension,
    RiskIntent,
    RiskSeverity,
)
from binance50.risk.policies import RiskPolicyEngine


@pytest.fixture
def policy_engine():
    return RiskPolicyEngine()


@pytest.fixture
def test_config():
    return AppConfig()


class DummyScoredSignal:
    def __init__(self, score):
        self.final_score = score
        self.id = "test"
        self.symbol = "BTCUSDT"
        from datetime import datetime

        self.open_time = datetime.utcnow()


def test_combine_components(policy_engine, test_config):
    components = [
        RiskComponent(dimension=RiskDimension.signal_score, passed=True, reason="Pass"),
        RiskComponent(
            dimension=RiskDimension.volatility,
            penalty=10.0,
            passed=True,
            severity=RiskSeverity.warning,
            reason="Vol penalty",
        ),
        RiskComponent(
            dimension=RiskDimension.liquidity, bonus=5.0, passed=True, reason="Liq bonus"
        ),
    ]
    breakdown = policy_engine.combine_components(components, test_config, base_score=70.0)
    assert breakdown.total_penalty == 10.0
    assert breakdown.total_bonus == 5.0
    assert breakdown.final_risk_score == 65.0
    assert len(breakdown.warnings) == 1


def test_classify_assessment_status(policy_engine, test_config):
    # Blocked
    components_blocked = [
        RiskComponent(
            dimension=RiskDimension.leverage,
            passed=False,
            severity=RiskSeverity.blocked,
            reason="Leverage blocked",
        )
    ]
    breakdown_blocked = policy_engine.combine_components(components_blocked, test_config, 80.0)
    status, intent = policy_engine.classify_assessment_status(
        breakdown_blocked, DummyScoredSignal(80.0), test_config
    )
    assert status == RiskAssessmentStatus.blocked_by_policy
    assert intent == RiskIntent.no_order

    # Approved paper
    breakdown_paper = policy_engine.combine_components([], test_config, 85.0)
    status, intent = policy_engine.classify_assessment_status(
        breakdown_paper, DummyScoredSignal(85.0), test_config
    )
    assert status == RiskAssessmentStatus.approved_for_paper_review
    assert intent == RiskIntent.paper_review_candidate
