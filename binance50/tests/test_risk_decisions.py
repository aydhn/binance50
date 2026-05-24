from datetime import datetime

from binance50.risk.datasets import dataframe_to_risk_assessments, risk_assessments_to_dataframe
from binance50.risk.decisions import (
    approve_for_future_backtest,
    approve_for_paper_review,
    block_by_policy,
    needs_review_assessment,
    reject_by_risk,
)
from binance50.risk.models import RiskAssessmentStatus, RiskBreakdown, RiskIntent


class DummyScoredSignal:
    def __init__(self):
        self.id = "test"
        self.symbol = "BTCUSDT"
        self.market_scope = "spot"
        self.interval = "1m"
        self.open_time = datetime.utcnow()
        self.close_time = datetime.utcnow()
        self.direction = "bullish"
        self.final_score = 80.0


def test_decision_helpers():
    sig = DummyScoredSignal()
    breakdown = RiskBreakdown(final_risk_score=80.0)

    a_fb = approve_for_future_backtest(sig, breakdown, "Test")
    assert a_fb.status == RiskAssessmentStatus.approved_for_future_backtest
    assert a_fb.intent == RiskIntent.future_backtest_candidate
    assert a_fb.approved is True

    a_pr = approve_for_paper_review(sig, breakdown, "Test")
    assert a_pr.status == RiskAssessmentStatus.approved_for_paper_review
    assert a_pr.intent == RiskIntent.paper_review_candidate
    assert a_pr.approved is True

    a_nr = needs_review_assessment(sig, breakdown, "Test")
    assert a_nr.status == RiskAssessmentStatus.needs_review
    assert a_nr.needs_review is True

    a_rej = reject_by_risk(sig, breakdown, "Test")
    assert a_rej.status == RiskAssessmentStatus.rejected_by_risk

    a_blk = block_by_policy(sig, breakdown, "Test")
    assert a_blk.status == RiskAssessmentStatus.blocked_by_policy
    assert a_blk.blocked is True


def test_dataframe_roundtrip():
    sig = DummyScoredSignal()
    a = approve_for_paper_review(sig, RiskBreakdown(final_risk_score=90.0), "Great")

    df = risk_assessments_to_dataframe([a])
    assert len(df) == 1
    assert (
        "explanation_json" not in df.columns
    )  # Native fields aren't JSON encoded unless requested, wait, the mapper does that
    assert "breakdown_json" in df.columns

    rehydrated = dataframe_to_risk_assessments(df)
    assert len(rehydrated) == 1
    assert rehydrated[0].status == RiskAssessmentStatus.approved_for_paper_review
    assert rehydrated[0].breakdown.final_risk_score == 90.0
