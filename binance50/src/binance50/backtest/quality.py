from typing import Any

from pydantic import BaseModel

from .models import BacktestRunResult


class BacktestQualityIssue(BaseModel):
    issue_type: str
    severity: str
    event_id: str | None = None
    trade_id: str | None = None
    message: str
    metadata: dict[str, Any] | None = None


class BacktestQualityReport(BaseModel):
    status: str
    event_count: int
    fill_count: int
    position_count: int
    trade_count: int
    equity_point_count: int
    invalid_equity_count: int
    negative_cash_count: int
    same_bar_fill_count: int
    lookahead_issue_count: int
    missing_explanation_count: int
    metric_nan_inf_count: int
    execution_field_count: int
    issues: list[BacktestQualityIssue]
    generated_at_utc: str


def build_backtest_quality_report(result: BacktestRunResult, config) -> BacktestQualityReport:
    # Stub
    return BacktestQualityReport(
        status="PASS",
        event_count=0,
        fill_count=0,
        position_count=0,
        trade_count=0,
        equity_point_count=0,
        invalid_equity_count=0,
        negative_cash_count=0,
        same_bar_fill_count=0,
        lookahead_issue_count=0,
        missing_explanation_count=0,
        metric_nan_inf_count=0,
        execution_field_count=0,
        issues=[],
        generated_at_utc="2024-01-01T00:00:00Z",
    )


def detect_same_bar_fills(result: BacktestRunResult, config):
    pass


def detect_invalid_equity_curve(result: BacktestRunResult):
    pass


def detect_negative_cash(result: BacktestRunResult):
    pass


def detect_unmatched_positions(result: BacktestRunResult):
    pass


def detect_fill_without_event(result: BacktestRunResult):
    pass


def detect_missing_explanations(result: BacktestRunResult):
    pass


def detect_metric_nan_inf(result: BacktestRunResult):
    pass


def detect_execution_fields(result: BacktestRunResult):
    pass


def assert_backtest_quality_passed(report: BacktestQualityReport, config):
    pass
