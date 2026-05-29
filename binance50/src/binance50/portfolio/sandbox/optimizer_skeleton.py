from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.core.exceptions import PortfolioOptimizerSkeletonError
from binance50.portfolio.sandbox.models import PortfolioCandidateInput


class PortfolioOptimizerSkeletonReport(BaseModel):
    enabled: bool
    scipy_available: bool
    used_for_selection: bool
    method: str
    objective_description: str
    constraints: dict = Field(default_factory=dict)
    sandbox_weights: dict[str, float] = Field(default_factory=dict)
    success: bool
    warnings: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


def check_scipy_availability() -> dict:
    try:
        import scipy

        return {"available": True, "version": scipy.__version__}
    except ImportError:
        return {"available": False, "version": None}


def explain_optimizer_skeleton(config: AppConfig) -> dict:
    return {
        "description": "Optional constrained optimizer skeleton for portfolio allocation.",
        "status": "Sandbox weights only. No production allocation. No real position sizing.",
    }


def validate_optimizer_output_sandbox_only(
    report: PortfolioOptimizerSkeletonReport, config: AppConfig
) -> None:
    if config.portfolio_sandbox.optimizer_skeleton.production_allocation_forbidden:
        if (
            report.used_for_selection
            and config.portfolio_sandbox.optimizer_skeleton.default_enabled_for_selection
        ):
            raise PortfolioOptimizerSkeletonError(
                "Optimizer skeleton cannot be default enabled for selection in production allocation forbidden mode"
            )


def build_optimizer_problem_skeleton(
    candidates: list[PortfolioCandidateInput], context: dict, config: AppConfig
) -> dict:
    return {
        "num_candidates": len(candidates),
        "objective": "maximize_portfolio_score",
        "constraints": config.portfolio_sandbox.optimizer_skeleton.constraints,
    }


def run_optional_optimizer_skeleton(
    candidates: list[PortfolioCandidateInput], context: dict, config: AppConfig
) -> PortfolioOptimizerSkeletonReport:
    o_config = config.portfolio_sandbox.optimizer_skeleton

    report = PortfolioOptimizerSkeletonReport(
        enabled=o_config.enabled,
        scipy_available=False,
        used_for_selection=o_config.default_enabled_for_selection,
        method=o_config.method,
        objective_description="Maximize weighted portfolio score under correlation and exposure constraints",
        constraints=o_config.constraints,
        success=False,
    )

    if not o_config.enabled or not candidates:
        return report

    scipy_info = check_scipy_availability()
    report.scipy_available = scipy_info["available"]

    if not report.scipy_available:
        if o_config.fail_if_scipy_missing:
            raise PortfolioOptimizerSkeletonError("SciPy is required but not available")
        report.warnings.append("SciPy not available. Skipping optimization.")
        return report

    # Skeleton logic: just return equal weights for demonstration
    weights = {c.candidate_id: 1.0 / len(candidates) for c in candidates}
    report.sandbox_weights = weights
    report.success = True

    validate_optimizer_output_sandbox_only(report, config)

    return report
