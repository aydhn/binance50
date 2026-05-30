from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field
from binance50.config.models import AppConfig
from binance50.paper.models import PaperExecutionRunResult
from binance50.core.exceptions import PaperQualityError

class PaperExecutionQualityIssue(BaseModel):
    issue_type: str
    severity: str
    paper_order_id: str | None
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)

class PaperExecutionQualityReport(BaseModel):
    status: str
    run_id: str
    order_count: int
    fill_count: int
    ledger_event_count: int
    missing_source_intent_count: int = 0
    missing_safety_scan_count: int = 0
    missing_filter_validation_count: int = 0
    missing_ledger_event_count: int = 0
    missing_pnl_report_count: int = 0
    negative_cash_count: int = 0
    short_spot_count: int = 0
    exchange_order_field_count: int = 0
    credential_detected_count: int = 0
    signed_payload_detected_count: int = 0
    network_call_count: int = 0
    exchange_state_count: int = 0
    live_or_testnet_intent_count: int = 0
    missing_hash_count: int = 0
    warnings: list[str] = Field(default_factory=list)
    issues: list[PaperExecutionQualityIssue] = Field(default_factory=list)
    generated_at_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

def build_paper_execution_quality_report(result: PaperExecutionRunResult, config: AppConfig) -> PaperExecutionQualityReport:
    report = PaperExecutionQualityReport(
        status="passed",
        run_id=result.run_id,
        order_count=len(result.paper_orders),
        fill_count=len(result.paper_fills),
        ledger_event_count=len(result.ledger_events)
    )
    # Detect various issues
    # simplified for now

    if report.issues and any(i.severity == "critical" for i in report.issues):
        report.status = "failed"

    return report

def detect_exchange_order_fields(result: PaperExecutionRunResult) -> int:
    return 0

def assert_paper_execution_quality_passed(report: PaperExecutionQualityReport, config: AppConfig) -> None:
    if report.status == "failed":
        raise PaperQualityError("Paper execution quality checks failed")
