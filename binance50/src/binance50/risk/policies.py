from typing import Any

from binance50.config.models import AppConfig
from binance50.risk.limits import check_signal_score_threshold
from binance50.risk.models import (
    RiskAssessmentStatus,
    RiskBreakdown,
    RiskComponent,
    RiskIntent,
    RiskSeverity,
)


class RiskPolicyEngine:
    def evaluate_signal_policy(self, scored_signal: Any, config: AppConfig) -> list[RiskComponent]:
        components = []
        components.append(check_signal_score_threshold(scored_signal, config))
        return components

    def evaluate_regime_policy(
        self, scored_signal: Any, regime_context: dict[str, Any] | None, config: AppConfig
    ) -> list[RiskComponent]:
        return []

    def evaluate_market_policy(
        self, scored_signal: Any, market_context: dict[str, Any] | None, config: AppConfig
    ) -> list[RiskComponent]:
        return []

    def evaluate_operational_policy(self, config: AppConfig) -> list[RiskComponent]:
        return []

    def combine_components(
        self, components: list[RiskComponent], config: AppConfig, base_score: float = 0.0
    ) -> RiskBreakdown:
        total_penalty = sum(c.penalty for c in components)
        total_bonus = sum(c.bonus for c in components)
        warnings = [c.reason for c in components if c.severity == RiskSeverity.warning]
        blocks = [
            c.reason for c in components if c.severity == RiskSeverity.blocked or not c.passed
        ]
        final_score = base_score - total_penalty + total_bonus
        if config.risk.decision.score_clamp:
            final_score = max(0.0, min(config.risk.decision.max_risk_score, final_score))
        return RiskBreakdown(
            components=components,
            base_score=base_score,
            total_penalty=total_penalty,
            total_bonus=total_bonus,
            final_risk_score=final_score,
            warnings=warnings,
            blocking_reasons=blocks,
        )

    def classify_assessment_status(
        self, breakdown: RiskBreakdown, scored_signal: Any, config: AppConfig
    ) -> tuple[RiskAssessmentStatus, RiskIntent]:
        if breakdown.blocking_reasons:
            return RiskAssessmentStatus.blocked_by_policy, RiskIntent.no_order
        score = breakdown.final_risk_score
        dec_cfg = config.risk.decision
        if score < dec_cfg.reject_below_score:
            return RiskAssessmentStatus.rejected_by_risk, RiskIntent.no_order
        elif score >= dec_cfg.approved_for_paper_review_min_score:
            return RiskAssessmentStatus.approved_for_paper_review, RiskIntent.paper_review_candidate
        elif score >= dec_cfg.approved_for_future_backtest_min_score:
            return (
                RiskAssessmentStatus.approved_for_future_backtest,
                RiskIntent.future_backtest_candidate,
            )
        elif score >= dec_cfg.needs_review_min_score:
            return RiskAssessmentStatus.needs_review, RiskIntent.risk_review
        return RiskAssessmentStatus.rejected_by_risk, RiskIntent.no_order
