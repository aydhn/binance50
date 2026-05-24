import hashlib
from datetime import datetime
from typing import Any

from binance50.risk.models import RiskAssessment, RiskAssessmentStatus, RiskBreakdown, RiskIntent


def _generate_assessment_id(scored_signal_id: str, symbol: str, open_time: datetime) -> str:
    seed = f"{scored_signal_id}_{symbol}_{open_time.isoformat()}".encode()
    return hashlib.md5(seed).hexdigest()


def build_risk_assessment(
    scored_signal: Any,
    status: RiskAssessmentStatus,
    intent: RiskIntent,
    breakdown: RiskBreakdown,
    explanation: str,
    regime_context: dict[str, Any] | None = None,
    notional_usdt: float | None = None,
    risk_pct: float | None = None,
) -> RiskAssessment:
    tier = (
        "high"
        if status
        in [
            RiskAssessmentStatus.approved_for_paper_review,
            RiskAssessmentStatus.approved_for_future_backtest,
        ]
        else ("medium" if status == RiskAssessmentStatus.needs_review else "low")
    )
    return RiskAssessment(
        assessment_id=_generate_assessment_id(
            scored_signal.id, scored_signal.symbol, scored_signal.open_time
        ),
        source_scored_signal_id=scored_signal.id,
        symbol=scored_signal.symbol,
        market_scope=scored_signal.market_scope,
        interval=scored_signal.interval,
        open_time=scored_signal.open_time,
        close_time=scored_signal.close_time,
        direction=scored_signal.direction,
        status=status,
        intent=intent,
        final_risk_score=breakdown.final_risk_score,
        risk_tier=tier,
        approved=status
        in [
            RiskAssessmentStatus.approved_for_paper_review,
            RiskAssessmentStatus.approved_for_future_backtest,
        ],
        blocked=status == RiskAssessmentStatus.blocked_by_policy,
        needs_review=status == RiskAssessmentStatus.needs_review,
        breakdown=breakdown,
        explanation=explanation,
        regime_context=regime_context,
        signal_snapshot=None,
        hypothetical_notional_usdt=notional_usdt,
        hypothetical_risk_pct=risk_pct,
        metadata={},
    )


def reject_by_risk(
    scored_signal: Any, breakdown: RiskBreakdown, explanation: str
) -> RiskAssessment:
    return build_risk_assessment(
        scored_signal,
        RiskAssessmentStatus.rejected_by_risk,
        RiskIntent.no_order,
        breakdown,
        explanation,
    )


def block_by_policy(
    scored_signal: Any, breakdown: RiskBreakdown, explanation: str
) -> RiskAssessment:
    return build_risk_assessment(
        scored_signal,
        RiskAssessmentStatus.blocked_by_policy,
        RiskIntent.no_order,
        breakdown,
        explanation,
    )


def needs_review_assessment(
    scored_signal: Any, breakdown: RiskBreakdown, explanation: str
) -> RiskAssessment:
    return build_risk_assessment(
        scored_signal,
        RiskAssessmentStatus.needs_review,
        RiskIntent.risk_review,
        breakdown,
        explanation,
    )


def approve_for_future_backtest(
    scored_signal: Any, breakdown: RiskBreakdown, explanation: str
) -> RiskAssessment:
    return build_risk_assessment(
        scored_signal,
        RiskAssessmentStatus.approved_for_future_backtest,
        RiskIntent.future_backtest_candidate,
        breakdown,
        explanation,
    )


def approve_for_paper_review(
    scored_signal: Any, breakdown: RiskBreakdown, explanation: str
) -> RiskAssessment:
    return build_risk_assessment(
        scored_signal,
        RiskAssessmentStatus.approved_for_paper_review,
        RiskIntent.paper_review_candidate,
        breakdown,
        explanation,
    )
