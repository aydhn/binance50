from datetime import datetime

from binance50.config.models import AppConfig
from binance50.core.exceptions import PortfolioCandidateInputError
from binance50.portfolio.sandbox.models import PortfolioCandidateInput


class PortfolioCandidateLoader:
    def __init__(self, storage_manager=None):
        self.storage_manager = storage_manager

    def load_scored_signals(self, run_id: str, config: AppConfig) -> list[PortfolioCandidateInput]:
        # Implementation to load from scored signals
        return []

    def load_risk_assessments(
        self, run_id: str, config: AppConfig
    ) -> list[PortfolioCandidateInput]:
        # Implementation to load from risk assessments
        return []

    def load_ml_blended_candidates(
        self, run_id: str, config: AppConfig
    ) -> list[PortfolioCandidateInput]:
        # Implementation to load from ML blend
        return []

    def load_regime_context(self, run_id: str, config: AppConfig) -> dict:
        # Implementation to load regime contexts
        return {}

    def combine_candidate_sources(
        self,
        signals: list[PortfolioCandidateInput],
        risks: list[PortfolioCandidateInput],
        ml_blends: list[PortfolioCandidateInput],
        regimes: dict,
        config: AppConfig,
    ) -> list[PortfolioCandidateInput]:

        # Merge logic, naive implementation to merge on unique symbol-direction-time combination
        # For this sandbox, return a simple concatenation or merged representation
        combined = []
        combined.extend(signals)
        combined.extend(risks)
        combined.extend(ml_blends)

        return combined

    def validate_candidate_sources(
        self, candidates: list[PortfolioCandidateInput], config: AppConfig
    ) -> None:
        if not candidates and config.portfolio_sandbox.inputs.require_at_least_one_candidate_source:
            raise PortfolioCandidateInputError(
                "At least one candidate source is required, but none provided."
            )

        for cand in candidates:
            # Check execution fields
            if config.portfolio_sandbox.inputs.reject_execution_fields:
                if any(x in cand.metadata for x in ["order_id", "quantity", "leverage", "price"]):
                    raise PortfolioCandidateInputError("Execution fields detected in candidate")

            # Check intent
            if config.portfolio_sandbox.inputs.reject_live_paper_intent:
                intent = cand.metadata.get("intent", "research_only")
                if intent in ["live", "paper"]:
                    raise PortfolioCandidateInputError(
                        f"Candidate {cand.candidate_id} has forbidden intent: {intent}"
                    )

            if not cand.source_trace:
                raise PortfolioCandidateInputError(
                    f"Candidate {cand.candidate_id} missing source trace."
                )

    def build_loader_report(self, request, candidates, errors) -> dict:
        return {
            "request_id": request.request_id,
            "candidate_count": len(candidates),
            "errors": errors,
            "loaded_at_utc": datetime.utcnow().isoformat(),
        }
