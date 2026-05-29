import datetime
from typing import Any

from pydantic import BaseModel, Field

from binance50.config.models import AppConfig
from binance50.core.exceptions import PortfolioConstructionQualityError
from binance50.portfolio.construction.models import (
    PortfolioConstructionRunResult,
)


class PortfolioConstructionQualityIssue(BaseModel):
    issue_type: str
    severity: str
    allocation_item_id: str
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)

class PortfolioConstructionQualityReport(BaseModel):
    status: str
    run_id: str
    candidate_count: int
    allocation_item_count: int
    methods_tested_count: int
    missing_breakdown_count: int = 0
    missing_explanation_count: int = 0
    weight_out_of_range_count: int = 0
    weight_sum_invalid_count: int = 0
    non_finite_covariance_count: int = 0
    non_finite_volatility_count: int = 0
    nan_inf_output_count: int = 0
    missing_hash_count: int = 0
    forward_return_issue_count: int = 0
    future_column_issue_count: int = 0
    quantity_output_count: int = 0
    order_like_output_count: int = 0
    production_allocation_intent_count: int = 0
    live_or_paper_intent_count: int = 0
    high_portfolio_volatility_warning_count: int = 0
    high_concentration_warning_count: int = 0
    dominant_risk_contributor_warning_count: int = 0
    issues: list[PortfolioConstructionQualityIssue] = Field(default_factory=list)
    generated_at_utc: str = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC).isoformat())

def build_portfolio_construction_quality_report(result: PortfolioConstructionRunResult, config: AppConfig) -> PortfolioConstructionQualityReport:
    report = PortfolioConstructionQualityReport(
        status="running",
        run_id=result.run_id,
        candidate_count=len(result.selected_candidates),
        allocation_item_count=len(result.selected_sandbox_allocation) if result.selected_sandbox_allocation else 0,
        methods_tested_count=len(result.allocation_methods_tested)
    )

    detect_missing_explanations(result, report)
    detect_weight_out_of_range(result, report)
    detect_weight_sum_invalid(result, report)
    detect_non_finite_covariance(result, report)
    detect_non_finite_volatility(result, report)
    detect_quantity_output(result, report)
    detect_order_like_output(result, report)
    detect_production_allocation_intent(result, report)
    detect_live_or_paper_intent(result, report)

    if result.constraint_report:
        for c_res in result.constraint_report.get("results", []):
            if c_res.get("severity") == "warning":
                 if c_res.get("constraint_name") == "portfolio_volatility":
                     report.high_portfolio_volatility_warning_count += 1
                     report.issues.append(PortfolioConstructionQualityIssue(issue_type="high_portfolio_volatility", severity="warning", allocation_item_id="portfolio", message=c_res.get("message", "High portfolio volatility")))
                 elif c_res.get("constraint_name") == "concentration":
                     report.high_concentration_warning_count += 1

    if result.risk_contribution_report and result.risk_contribution_report.get("dominant_risk_contributor_warning"):
        report.dominant_risk_contributor_warning_count += 1
        report.issues.append(PortfolioConstructionQualityIssue(issue_type="dominant_risk_contributor", severity="warning", allocation_item_id="portfolio", message="A single asset dominates the portfolio risk."))

    error_issues = [i for i in report.issues if i.severity == "error"]
    report.status = "failed" if error_issues else "passed"

    return report

def detect_missing_explanations(result: PortfolioConstructionRunResult, report: PortfolioConstructionQualityReport):
    if not result.selected_sandbox_allocation: return
    for item in result.selected_sandbox_allocation:
        if not item.explanation:
            report.missing_explanation_count += 1
            report.issues.append(PortfolioConstructionQualityIssue(issue_type="missing_explanation", severity="error", allocation_item_id=item.allocation_item_id, message="Allocation item is missing required explanation."))

def detect_weight_out_of_range(result: PortfolioConstructionRunResult, report: PortfolioConstructionQualityReport):
    if not result.selected_sandbox_allocation: return
    for item in result.selected_sandbox_allocation:
        if item.sandbox_weight < 0 or item.sandbox_weight > 1.0:
            report.weight_out_of_range_count += 1
            report.issues.append(PortfolioConstructionQualityIssue(issue_type="weight_out_of_range", severity="error", allocation_item_id=item.allocation_item_id, message=f"Weight {item.sandbox_weight} is outside [0, 1] range."))

def detect_weight_sum_invalid(result: PortfolioConstructionRunResult, report: PortfolioConstructionQualityReport):
    if not result.selected_sandbox_allocation: return
    total_w = sum(item.sandbox_weight for item in result.selected_sandbox_allocation)
    if total_w > 1.0001:
        report.weight_sum_invalid_count += 1
        report.issues.append(PortfolioConstructionQualityIssue(issue_type="weight_sum_invalid", severity="error", allocation_item_id="portfolio", message=f"Total weight {total_w} exceeds 1.0."))

def detect_non_finite_covariance(result: PortfolioConstructionRunResult, report: PortfolioConstructionQualityReport):
    if result.covariance_report and result.covariance_report.get("non_finite_count", 0) > 0:
        report.non_finite_covariance_count += 1
        report.issues.append(PortfolioConstructionQualityIssue(issue_type="non_finite_covariance", severity="error", allocation_item_id="portfolio", message="Covariance matrix contains non-finite values."))

def detect_non_finite_volatility(result: PortfolioConstructionRunResult, report: PortfolioConstructionQualityReport):
    if result.volatility_report:
        for symbol, vol in result.volatility_report.get("symbol_volatilities", {}).items():
             import numpy as np
             if not np.isfinite(vol):
                 report.non_finite_volatility_count += 1
                 report.issues.append(PortfolioConstructionQualityIssue(issue_type="non_finite_volatility", severity="error", allocation_item_id=symbol, message="Volatility estimate is not finite."))

def detect_quantity_output(result: PortfolioConstructionRunResult, report: PortfolioConstructionQualityReport):
    if not result.selected_sandbox_allocation: return
    for item in result.selected_sandbox_allocation:
         if hasattr(item, "quantity") or "quantity" in item.model_dump():
             report.quantity_output_count += 1
             report.issues.append(PortfolioConstructionQualityIssue(issue_type="quantity_output_forbidden", severity="error", allocation_item_id=item.allocation_item_id, message="Allocation item contains forbidden quantity output."))

def detect_order_like_output(result: PortfolioConstructionRunResult, report: PortfolioConstructionQualityReport):
    if not result.selected_sandbox_allocation: return
    forbidden = ["buy", "sell", "order", "execute"]
    for item in result.selected_sandbox_allocation:
         exp = (item.explanation or "").lower()
         for f in forbidden:
             if f" {f} " in f" {exp} ":
                 report.order_like_output_count += 1
                 report.issues.append(PortfolioConstructionQualityIssue(issue_type="order_like_output_forbidden", severity="error", allocation_item_id=item.allocation_item_id, message=f"Explanation contains forbidden order-like word '{f}'."))

def detect_production_allocation_intent(result: PortfolioConstructionRunResult, report: PortfolioConstructionQualityReport):
    if not result.selected_sandbox_allocation: return
    for item in result.selected_sandbox_allocation:
         if "production allocation" in (item.explanation or "").lower() or "position sizing" in (item.explanation or "").lower():
             report.production_allocation_intent_count += 1
             report.issues.append(PortfolioConstructionQualityIssue(issue_type="production_allocation_intent", severity="error", allocation_item_id=item.allocation_item_id, message="Explanation implies production allocation intent."))

def detect_live_or_paper_intent(result: PortfolioConstructionRunResult, report: PortfolioConstructionQualityReport):
    if not result.selected_sandbox_allocation: return
    for item in result.selected_sandbox_allocation:
         intent = item.intent.value if hasattr(item.intent, "value") else str(item.intent)
         if intent in ("live", "paper"):
             report.live_or_paper_intent_count += 1
             report.issues.append(PortfolioConstructionQualityIssue(issue_type="live_or_paper_intent", severity="error", allocation_item_id=item.allocation_item_id, message=f"Item intent is {intent}, which is forbidden in sandbox."))

def assert_portfolio_construction_quality_passed(report: PortfolioConstructionQualityReport, config: AppConfig) -> None:
    if report.status == "failed":
        errors = [i.message for i in report.issues if i.severity == "error"]
        raise PortfolioConstructionQualityError(f"Quality checks failed: {errors[0]} (and {len(errors)-1} more).")
