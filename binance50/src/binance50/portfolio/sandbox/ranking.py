from datetime import datetime

from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.concentration import compute_concentration_penalty
from binance50.portfolio.sandbox.diversification import compute_candidate_diversification_component
from binance50.portfolio.sandbox.explanations import build_candidate_selection_explanation
from binance50.portfolio.sandbox.models import (
    PortfolioCandidateInput,
    PortfolioCandidateScoreBreakdown,
    PortfolioCandidateStatus,
    PortfolioSandboxIntent,
    PortfolioSelectedSandboxCandidate,
)


class PortfolioCandidateRankingEngine:
    def __init__(self, config: AppConfig):
        self.config = config

    def clamp_score(self, value: float) -> float:
        r_config = self.config.portfolio_sandbox.ranking
        return max(r_config.score_clamp_min, min(r_config.score_clamp_max, value))

    def deterministic_tie_break(
        self, candidates: list[PortfolioSelectedSandboxCandidate]
    ) -> list[PortfolioSelectedSandboxCandidate]:
        # Sort by portfolio_score desc, then by candidate_id for stable tie-breaking
        return sorted(candidates, key=lambda c: (c.portfolio_score, c.candidate_id), reverse=True)

    def apply_correlation_penalty(self, candidate: PortfolioCandidateInput, context: dict) -> float:
        # Mock implementation. In a real system, you would look at the correlation report in the context.
        return 0.0

    def apply_concentration_penalty(
        self, candidate: PortfolioCandidateInput, context: dict
    ) -> float:
        return compute_concentration_penalty(candidate, context, self.config)

    def apply_diversification_bonus(
        self, candidate: PortfolioCandidateInput, context: dict
    ) -> float:
        return compute_candidate_diversification_component(candidate, context, self.config)

    def apply_liquidity_penalty(self, candidate: PortfolioCandidateInput, context: dict) -> float:
        if candidate.risk_context:
            return (
                candidate.risk_context.get("liquidity_risk", 0.0)
                * self.config.portfolio_sandbox.ranking.components.get(
                    "liquidity_penalty_weight", -0.05
                )
                * -1
            )  # Make positive since weight is negative
        return 0.0

    def apply_stale_penalty(self, candidate: PortfolioCandidateInput, context: dict) -> float:
        # Mock stale penalty
        return 0.0

    def compute_candidate_portfolio_score(
        self, candidate: PortfolioCandidateInput, context: dict
    ) -> PortfolioCandidateScoreBreakdown:
        r_config = self.config.portfolio_sandbox.ranking
        weights = r_config.components

        cq_component = (candidate.signal_score or 0.0) * weights.get(
            "candidate_quality_weight", 0.3
        )
        rq_component = (candidate.risk_score or 0.0) * weights.get("risk_quality_weight", 0.2)
        ml_component = (candidate.ml_blend_score or 0.0) * weights.get("ml_blend_weight", 0.2)

        div_bonus = self.apply_diversification_bonus(candidate, context) * weights.get(
            "diversification_weight", 0.1
        )
        corr_penalty = self.apply_correlation_penalty(candidate, context) * weights.get(
            "correlation_penalty_weight", -0.1
        )
        conc_penalty = self.apply_concentration_penalty(candidate, context) * weights.get(
            "concentration_penalty_weight", -0.1
        )
        liq_penalty = self.apply_liquidity_penalty(candidate, context) * weights.get(
            "liquidity_penalty_weight", -0.05
        )
        stale_penalty = self.apply_stale_penalty(candidate, context) * weights.get(
            "stale_candidate_penalty_weight", -0.05
        )

        raw_score = (
            cq_component
            + rq_component
            + ml_component
            + div_bonus
            + corr_penalty
            + conc_penalty
            + liq_penalty
            + stale_penalty
        )

        final_score = self.clamp_score(raw_score)

        return PortfolioCandidateScoreBreakdown(
            candidate_quality_component=cq_component,
            risk_quality_component=rq_component,
            ml_blend_component=ml_component,
            diversification_component=div_bonus,
            correlation_penalty=corr_penalty,
            concentration_penalty=conc_penalty,
            liquidity_penalty=liq_penalty,
            stale_candidate_penalty=stale_penalty,
            final_portfolio_score=final_score,
        )

    def rank_candidates(
        self, candidates: list[PortfolioCandidateInput], context: dict
    ) -> list[PortfolioSelectedSandboxCandidate]:
        if not self.config.portfolio_sandbox.ranking.enabled:
            return []

        ranked = []
        for cand in candidates:
            breakdown = self.compute_candidate_portfolio_score(cand, context)
            explanation = build_candidate_selection_explanation(cand, context, self.config)

            selected_cand = PortfolioSelectedSandboxCandidate(
                selected_id=f"sel_{cand.candidate_id}",
                candidate_id=cand.candidate_id,
                symbol=cand.symbol,
                market_scope=cand.market_scope,
                interval=cand.interval,
                open_time=cand.open_time,
                direction=cand.direction,
                rank=0,  # Will be set during selection
                selected=False,
                status=PortfolioCandidateStatus.eligible,
                intent=PortfolioSandboxIntent.sandbox_only,
                blocked_from_signal_engine=True,
                blocked_from_risk_engine=True,
                blocked_from_paper_engine=True,
                blocked_from_live_engine=True,
                blocked_from_execution=True,
                portfolio_score=breakdown.final_portfolio_score,
                score_breakdown=breakdown,
                hypothetical_notional_usdt=cand.hypothetical_notional_usdt or 0.0,
                hypothetical_exposure_pct=0.0,  # Filled in selection
                hypothetical_risk_budget_pct=0.0,  # Filled in selection
                explanation=explanation,
                created_at_utc=datetime.utcnow(),
            )
            ranked.append(selected_cand)

        return self.deterministic_tie_break(ranked)
