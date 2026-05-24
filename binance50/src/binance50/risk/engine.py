from typing import Any

from binance50.config.models import AppConfig
from binance50.risk.decisions import build_risk_assessment
from binance50.risk.explanations import build_risk_explanation
from binance50.risk.models import (
    RiskAssessment,
    RiskAssessmentStatus,
    RiskRunRequest,
    RiskRunResult,
)
from binance50.risk.notional import (
    estimate_hypothetical_notional_usdt,
    estimate_hypothetical_risk_pct,
)
from binance50.risk.policies import RiskPolicyEngine


class RiskEngine:
    def __init__(self, config: AppConfig, policy_engine: RiskPolicyEngine | None = None):
        self.config = config
        self.policy_engine = policy_engine or RiskPolicyEngine()

    def run(
        self, scored_signals: list[Any], regimes: list[Any] | None, request: RiskRunRequest
    ) -> RiskRunResult:
        result = RiskRunResult(request=request)
        if not self.config.risk.enabled:
            result.error = "Risk engine is disabled."
            result.success = False
            return result
        for signal in scored_signals:
            regime_ctx = self.match_regime_context(signal, regimes) if regimes else None
            assessment = self.assess_single(signal, regime_ctx)
            if assessment.blocked or assessment.status == RiskAssessmentStatus.rejected_by_risk:
                result.rejected_assessments.append(assessment)
            else:
                result.assessments.append(assessment)
        return result

    def assess_single(
        self, scored_signal: Any, regime_context: dict[str, Any] | None = None
    ) -> RiskAssessment:
        components = []
        components.extend(self.policy_engine.evaluate_signal_policy(scored_signal, self.config))
        components.extend(
            self.policy_engine.evaluate_regime_policy(scored_signal, regime_context, self.config)
        )
        base_score = getattr(scored_signal, "final_score", 0.0)
        breakdown = self.policy_engine.combine_components(components, self.config, base_score)
        status, intent = self.policy_engine.classify_assessment_status(
            breakdown, scored_signal, self.config
        )
        explanation = build_risk_explanation(status, breakdown)
        notional = estimate_hypothetical_notional_usdt(scored_signal, self.config)
        risk_pct = estimate_hypothetical_risk_pct(
            notional, self.config.risk.account.simulated_account_equity_usdt, self.config
        )
        return build_risk_assessment(
            scored_signal=scored_signal,
            status=status,
            intent=intent,
            breakdown=breakdown,
            explanation=explanation,
            regime_context=regime_context,
            notional_usdt=notional,
            risk_pct=risk_pct,
        )

    def match_regime_context(self, scored_signal: Any, regimes: list[Any]) -> dict[str, Any] | None:
        return None
