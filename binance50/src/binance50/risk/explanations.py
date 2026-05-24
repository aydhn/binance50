from typing import Any

from binance50.config.models import AppConfig
from binance50.risk.models import RiskAssessmentStatus, RiskBreakdown


def explain_blocking_reasons(breakdown: RiskBreakdown) -> str:
    if not breakdown.blocking_reasons:
        return ""
    return "Blocked due to: " + "; ".join(breakdown.blocking_reasons)


def explain_risk_status(status: RiskAssessmentStatus) -> str:
    mapping = {
        RiskAssessmentStatus.approved_for_future_backtest: "Candidate approved for future backtest review.",
        RiskAssessmentStatus.approved_for_paper_review: "Candidate approved for paper trading review.",
        RiskAssessmentStatus.needs_review: "Candidate requires manual risk review.",
        RiskAssessmentStatus.rejected_by_risk: "Candidate rejected due to insufficient risk score.",
        RiskAssessmentStatus.blocked_by_policy: "Candidate blocked by risk policy.",
        RiskAssessmentStatus.no_action: "No risk action taken.",
    }
    return mapping.get(status, "Unknown status.")


def build_risk_breakdown_explanation(breakdown: RiskBreakdown) -> dict[str, Any]:
    return {
        "final_score": breakdown.final_risk_score,
        "base_score": breakdown.base_score,
        "penalties": breakdown.total_penalty,
        "bonuses": breakdown.total_bonus,
        "warnings": breakdown.warnings,
        "blocks": breakdown.blocking_reasons,
    }


def build_risk_explanation(status: RiskAssessmentStatus, breakdown: RiskBreakdown) -> str:
    parts = [explain_risk_status(status)]
    blocks = explain_blocking_reasons(breakdown)
    if blocks:
        parts.append(blocks)
    if breakdown.warnings:
        parts.append(f"Warnings: {len(breakdown.warnings)}")
    return " ".join(parts)


def validate_risk_explanation(text: str, config: AppConfig) -> None:
    order_words = ["buy", "sell", "order", "execute", "long", "short", "position"]
    text_lower = text.lower()
    for w in order_words:
        if w in text_lower:
            if config.risk.quality.reject_order_like_language:
                raise ValueError(f"Risk explanation contains order-like language: {w}")
