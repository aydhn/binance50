import uuid

from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.concentration import build_concentration_report
from binance50.portfolio.sandbox.correlation import build_correlation_report
from binance50.portfolio.sandbox.deduplication import (
    deduplicate_candidates,
)
from binance50.portfolio.sandbox.diversification import build_diversification_report
from binance50.portfolio.sandbox.eligibility import (
    filter_eligible_candidates,
)
from binance50.portfolio.sandbox.exposure import build_exposure_report
from binance50.portfolio.sandbox.loaders import PortfolioCandidateLoader
from binance50.portfolio.sandbox.models import (
    PortfolioSandboxStatus,
    PortfolioSelectionRunRequest,
    PortfolioSelectionRunResult,
)
from binance50.portfolio.sandbox.normalization import normalize_candidate_scores
from binance50.portfolio.sandbox.optimizer_skeleton import run_optional_optimizer_skeleton
from binance50.portfolio.sandbox.quality import (
    assert_portfolio_sandbox_quality_passed,
    build_portfolio_sandbox_quality_report,
)
from binance50.portfolio.sandbox.ranking import PortfolioCandidateRankingEngine
from binance50.portfolio.sandbox.reproducibility import build_portfolio_reproducibility_report
from binance50.portfolio.sandbox.risk_budget import build_risk_budget_report
from binance50.portfolio.sandbox.selection import select_top_candidates
from binance50.portfolio.sandbox.similarity import build_similarity_report


class PortfolioCandidateSelectionRunner:
    def __init__(self, config: AppConfig, storage_manager=None):
        self.config = config
        self.storage_manager = storage_manager
        self.loader = PortfolioCandidateLoader(storage_manager)
        self.ranking_engine = PortfolioCandidateRankingEngine(config)

    def load_inputs(self, request: PortfolioSelectionRunRequest) -> list:
        # Mock load from request context or storage
        # Signals
        signals = (
            self.loader.load_scored_signals(request.scored_signal_run_id, self.config)
            if request.scored_signal_run_id
            else []
        )
        risks = (
            self.loader.load_risk_assessments(request.risk_run_id, self.config)
            if request.risk_run_id
            else []
        )
        blends = (
            self.loader.load_ml_blended_candidates(request.ml_blending_run_id, self.config)
            if request.ml_blending_run_id
            else []
        )

        regimes = (
            self.loader.load_regime_context(request.regime_run_id, self.config)
            if request.regime_run_id
            else {}
        )

        candidates = self.loader.combine_candidate_sources(
            signals, risks, blends, regimes, self.config
        )
        self.loader.validate_candidate_sources(candidates, self.config)

        return candidates

    def run(self, request: PortfolioSelectionRunRequest) -> PortfolioSelectionRunResult:
        run_id = f"port_sel_{uuid.uuid4().hex[:8]}"

        result = PortfolioSelectionRunResult(
            request=request, run_id=run_id, status=PortfolioSandboxStatus.running
        )

        try:
            # Load
            inputs = self.load_inputs(request)
            result.input_candidates = inputs

            # Normalize
            normalized = normalize_candidate_scores(inputs, self.config)

            # Deduplicate
            deduped = deduplicate_candidates(normalized, self.config)

            # Eligibility
            eligible, rejected = filter_eligible_candidates(deduped, self.config)
            result.eligible_candidates = eligible
            result.rejected_candidates = rejected

            # Market data mock for correlation
            market_data = {}

            # Build Context Reports
            corr_rep = build_correlation_report(eligible, market_data, self.config)
            result.correlation_report = corr_rep.model_dump(mode="json")

            sim_rep = build_similarity_report(eligible, self.config)
            result.similarity_report = sim_rep.model_dump(mode="json")

            exp_rep = build_exposure_report(eligible, self.config)
            result.exposure_report = exp_rep.model_dump(mode="json")

            conc_rep = build_concentration_report(eligible, self.config)
            result.concentration_report = conc_rep.model_dump(mode="json")

            div_rep = build_diversification_report(eligible, result.correlation_report, self.config)
            result.diversification_report = div_rep.model_dump(mode="json")

            budget_rep = build_risk_budget_report(eligible, self.config)
            result.risk_budget_report = budget_rep.model_dump(mode="json")

            context = {
                "correlation": result.correlation_report,
                "similarity": result.similarity_report,
                "exposure": result.exposure_report,
                "concentration": result.concentration_report,
                "diversification": result.diversification_report,
                "risk_budget": result.risk_budget_report,
            }

            # Rank
            ranked = self.ranking_engine.rank_candidates(eligible, context)

            # Select
            selected = select_top_candidates(ranked, self.config)
            result.selected_candidates = selected

            # Optimizer Skeleton
            opt_rep = run_optional_optimizer_skeleton(selected, context, self.config)
            result.optimizer_skeleton_report = opt_rep.model_dump(mode="json")

            # Reproducibility
            rep_report = build_portfolio_reproducibility_report(result, self.config)
            result.reproducibility_report = rep_report

            # Quality
            q_report = build_portfolio_sandbox_quality_report(result, self.config)
            result.quality_report = q_report.model_dump(mode="json")
            assert_portfolio_sandbox_quality_passed(q_report, self.config)

            result.status = PortfolioSandboxStatus.completed
            result.success = True

        except Exception as e:
            result.status = PortfolioSandboxStatus.failed
            result.error = str(e)

        return result

    def run_latest_sandbox(
        self, symbol: str, market_scope: str, interval: str
    ) -> PortfolioSelectionRunResult:
        req = PortfolioSelectionRunRequest(
            symbol=symbol, market_scope=market_scope, interval=interval
        )
        return self.run(req)
