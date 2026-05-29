from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.models import PortfolioSelectionRunResult


def build_portfolio_selection_summary(result: PortfolioSelectionRunResult) -> dict:
    return {
        "run_id": result.run_id,
        "status": result.status.value,
        "success": result.success,
        "input_count": len(result.input_candidates),
        "eligible_count": len(result.eligible_candidates),
        "selected_count": len(result.selected_candidates),
        "reproducibility_hash": result.reproducibility_report.get("output_hash")
        if result.reproducibility_report
        else None,
        "quality_status": result.quality_report.get("status", "unknown")
        if result.quality_report
        else "unknown",
    }


def build_input_candidate_table(candidates: list, limit: int = 100) -> list[dict]:
    return [c.model_dump(mode="json") for c in candidates[:limit]]


def build_selected_candidate_table(candidates: list, limit: int = 50) -> list[dict]:
    return [c.model_dump(mode="json") for c in candidates[:limit]]


def build_candidate_breakdown_report(candidate) -> dict:
    return candidate.score_breakdown.model_dump(mode="json")


def build_correlation_report_view(result: PortfolioSelectionRunResult) -> dict:
    return result.correlation_report if result.correlation_report else {}


def build_similarity_report_view(result: PortfolioSelectionRunResult) -> dict:
    return result.similarity_report if result.similarity_report else {}


def build_exposure_report_view(result: PortfolioSelectionRunResult) -> dict:
    return result.exposure_report if result.exposure_report else {}


def build_concentration_report_view(result: PortfolioSelectionRunResult) -> dict:
    return result.concentration_report if result.concentration_report else {}


def build_diversification_report_view(result: PortfolioSelectionRunResult) -> dict:
    return result.diversification_report if result.diversification_report else {}


def build_risk_budget_report_view(result: PortfolioSelectionRunResult) -> dict:
    return result.risk_budget_report if result.risk_budget_report else {}


def build_portfolio_sandbox_health_report(config: AppConfig) -> dict:
    return {
        "sandbox_enabled": config.portfolio_sandbox.enabled,
        "real_exchange_forbidden": config.portfolio_sandbox.real_exchange_forbidden,
        "allocation_production_forbidden": config.portfolio_sandbox.allocation_production_forbidden,
        "cache_enabled": config.portfolio_sandbox.cache_enabled,
        "correlation_enabled": config.portfolio_sandbox.correlation.enabled,
        "exposure_enabled": config.portfolio_sandbox.exposure.enabled,
        "optimizer_enabled": config.portfolio_sandbox.optimizer_skeleton.enabled,
        "status": "healthy",
    }
