from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.portfolio.sandbox.models import PortfolioCandidateInput


class PortfolioExposureReport(BaseModel):
    run_id: str
    total_hypothetical_exposure_usdt: float
    total_hypothetical_exposure_pct: float
    exposure_by_symbol: dict[str, float] = Field(default_factory=dict)
    exposure_by_direction: dict[str, float] = Field(default_factory=dict)
    exposure_by_interval: dict[str, float] = Field(default_factory=dict)
    max_symbol_exposure_pct: float
    max_directional_exposure_pct: float
    violations: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


def compute_candidate_hypothetical_exposure(
    candidate: PortfolioCandidateInput, config: AppConfig
) -> dict:
    e_config = config.portfolio_sandbox.exposure

    # Base notional
    notional = e_config.default_candidate_notional_usdt

    # Optionally override from risk
    if (
        e_config.use_risk_hypothetical_notional_if_available
        and candidate.hypothetical_notional_usdt is not None
    ):
        notional = candidate.hypothetical_notional_usdt

    candidate.hypothetical_notional_usdt = notional
    pct = (
        (notional / e_config.starting_equity_usdt) * 100.0
        if e_config.starting_equity_usdt > 0
        else 0.0
    )

    return {
        "candidate_id": candidate.candidate_id,
        "symbol": candidate.symbol,
        "direction": candidate.direction,
        "notional": notional,
        "pct": pct,
    }


def check_symbol_exposure(
    exposure_by_symbol: dict, total_equity: float, config: AppConfig
) -> list[str]:
    violations = []
    limit_pct = config.portfolio_sandbox.exposure.max_symbol_hypothetical_exposure_pct
    for sym, val in exposure_by_symbol.items():
        pct = (val / total_equity) * 100.0 if total_equity > 0 else 0.0
        if pct > limit_pct:
            violations.append(f"Symbol {sym} exposure ({pct:.2f}%) exceeds limit ({limit_pct}%)")
    return violations


def check_directional_exposure(
    exposure_by_dir: dict, total_equity: float, config: AppConfig
) -> list[str]:
    violations = []
    limit_pct = config.portfolio_sandbox.exposure.max_directional_exposure_pct
    for d, val in exposure_by_dir.items():
        pct = (val / total_equity) * 100.0 if total_equity > 0 else 0.0
        if pct > limit_pct:
            violations.append(f"Direction {d} exposure ({pct:.2f}%) exceeds limit ({limit_pct}%)")
    return violations


def check_interval_exposure(
    candidates: list[PortfolioCandidateInput], config: AppConfig
) -> list[str]:
    # Placeholder for interval exposure checks
    return []


def compute_total_exposure(
    candidates: list[PortfolioCandidateInput], config: AppConfig
) -> PortfolioExposureReport:
    e_config = config.portfolio_sandbox.exposure
    equity = e_config.starting_equity_usdt

    report = PortfolioExposureReport(
        run_id="unknown",
        total_hypothetical_exposure_usdt=0.0,
        total_hypothetical_exposure_pct=0.0,
        max_symbol_exposure_pct=0.0,
        max_directional_exposure_pct=0.0,
    )

    if not e_config.enabled:
        return report

    for cand in candidates:
        exp = compute_candidate_hypothetical_exposure(cand, config)
        notional = exp["notional"]

        report.total_hypothetical_exposure_usdt += notional
        report.exposure_by_symbol[cand.symbol] = (
            report.exposure_by_symbol.get(cand.symbol, 0.0) + notional
        )
        report.exposure_by_direction[cand.direction] = (
            report.exposure_by_direction.get(cand.direction, 0.0) + notional
        )
        report.exposure_by_interval[cand.interval] = (
            report.exposure_by_interval.get(cand.interval, 0.0) + notional
        )

    report.total_hypothetical_exposure_pct = (
        (report.total_hypothetical_exposure_usdt / equity) * 100.0 if equity > 0 else 0.0
    )

    if report.exposure_by_symbol:
        max_sym_val = max(report.exposure_by_symbol.values())
        report.max_symbol_exposure_pct = (max_sym_val / equity) * 100.0 if equity > 0 else 0.0

    if report.exposure_by_direction:
        max_dir_val = max(report.exposure_by_direction.values())
        report.max_directional_exposure_pct = (max_dir_val / equity) * 100.0 if equity > 0 else 0.0

    # Check violations
    if report.total_hypothetical_exposure_pct > e_config.max_total_hypothetical_exposure_pct:
        report.violations.append(
            f"Total exposure ({report.total_hypothetical_exposure_pct:.2f}%) exceeds limit ({e_config.max_total_hypothetical_exposure_pct}%)"
        )

    report.violations.extend(check_symbol_exposure(report.exposure_by_symbol, equity, config))
    report.violations.extend(
        check_directional_exposure(report.exposure_by_direction, equity, config)
    )

    return report


def build_exposure_report(
    candidates: list[PortfolioCandidateInput], config: AppConfig
) -> PortfolioExposureReport:
    return compute_total_exposure(candidates, config)
