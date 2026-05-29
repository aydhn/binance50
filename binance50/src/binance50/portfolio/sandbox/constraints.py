from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.concentration import PortfolioConcentrationReport
from binance50.portfolio.sandbox.correlation import PortfolioCorrelationReport
from binance50.portfolio.sandbox.exposure import PortfolioExposureReport
from binance50.portfolio.sandbox.models import PortfolioCandidateInput


class PortfolioConstraintResult(BaseModel):
    constraint_name: str
    passed: bool
    severity: str
    affected_candidate_ids: list[str] = Field(default_factory=list)
    message: str | None = None
    metadata: dict = Field(default_factory=dict)


def check_max_candidates(
    candidates: list[PortfolioCandidateInput], config: AppConfig
) -> PortfolioConstraintResult:
    limit = config.portfolio_sandbox.exposure.max_candidates_selected
    passed = len(candidates) <= limit
    return PortfolioConstraintResult(
        constraint_name="max_candidates_selected",
        passed=passed,
        severity="block",
        message=f"Candidate count {len(candidates)} exceeds limit {limit}" if not passed else None,
    )


def check_max_candidates_per_symbol(
    candidates: list[PortfolioCandidateInput], config: AppConfig
) -> PortfolioConstraintResult:
    limit = config.portfolio_sandbox.exposure.max_candidates_per_symbol
    counts = {}
    for c in candidates:
        counts[c.symbol] = counts.get(c.symbol, 0) + 1

    failed_syms = {s: c for s, c in counts.items() if c > limit}

    passed = len(failed_syms) == 0
    return PortfolioConstraintResult(
        constraint_name="max_candidates_per_symbol",
        passed=passed,
        severity="block",
        message=f"Symbols exceeding max candidates limit: {list(failed_syms.keys())}"
        if not passed
        else None,
    )


def check_max_candidates_same_direction(
    candidates: list[PortfolioCandidateInput], config: AppConfig
) -> PortfolioConstraintResult:
    limit = config.portfolio_sandbox.exposure.max_candidates_same_direction
    counts = {}
    for c in candidates:
        counts[c.direction] = counts.get(c.direction, 0) + 1

    failed_dirs = {d: c for d, c in counts.items() if c > limit}

    passed = len(failed_dirs) == 0
    return PortfolioConstraintResult(
        constraint_name="max_candidates_same_direction",
        passed=passed,
        severity="block",
        message=f"Directions exceeding max candidates limit: {list(failed_dirs.keys())}"
        if not passed
        else None,
    )


def check_exposure_constraints(
    exposure_report: PortfolioExposureReport, config: AppConfig
) -> list[PortfolioConstraintResult]:
    results = []
    if exposure_report.violations:
        results.append(
            PortfolioConstraintResult(
                constraint_name="exposure_limits",
                passed=False,
                severity="block",
                message="; ".join(exposure_report.violations),
            )
        )
    return results


def check_correlation_constraints(
    correlation_report: PortfolioCorrelationReport, config: AppConfig
) -> list[PortfolioConstraintResult]:
    results = []
    if correlation_report.blocked_correlation_pairs:
        results.append(
            PortfolioConstraintResult(
                constraint_name="correlation_block_limit",
                passed=False,
                severity="block",
                message=f"{len(correlation_report.blocked_correlation_pairs)} pairs blocked due to high correlation",
            )
        )
    return results


def check_concentration_constraints(
    concentration_report: PortfolioConcentrationReport, config: AppConfig
) -> list[PortfolioConstraintResult]:
    results = []
    if concentration_report.concentration_warnings:
        results.append(
            PortfolioConstraintResult(
                constraint_name="concentration_limits",
                passed=False,
                severity="penalty",
                message="; ".join(concentration_report.concentration_warnings),
            )
        )
    return results


def build_constraint_report(
    candidates: list[PortfolioCandidateInput],
    exposure_report: PortfolioExposureReport,
    correlation_report: PortfolioCorrelationReport,
    concentration_report: PortfolioConcentrationReport,
    config: AppConfig,
) -> list[PortfolioConstraintResult]:

    results = []
    results.append(check_max_candidates(candidates, config))
    results.append(check_max_candidates_per_symbol(candidates, config))
    results.append(check_max_candidates_same_direction(candidates, config))
    results.extend(check_exposure_constraints(exposure_report, config))
    results.extend(check_correlation_constraints(correlation_report, config))
    results.extend(check_concentration_constraints(concentration_report, config))

    return results
