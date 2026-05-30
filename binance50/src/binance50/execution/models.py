from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any, Optional


class ExecutionMode(StrEnum):
    sandbox = "sandbox"
    paper_candidate = "paper_candidate"
    testnet_candidate = "testnet_candidate"
    live_candidate = "live_candidate"


class ExecutionIntentStatus(StrEnum):
    draft_created = "draft_created"
    safety_scanned = "safety_scanned"
    rejected_by_guard = "rejected_by_guard"
    blocked_by_kill_switch = "blocked_by_kill_switch"
    dry_run_validated = "dry_run_validated"
    archived = "archived"


class ExecutionIntentKind(StrEnum):
    hypothetical_review = "hypothetical_review"
    paper_candidate = "paper_candidate"
    testnet_candidate = "testnet_candidate"
    live_candidate = "live_candidate"


class ExecutionSide(StrEnum):
    buy = "buy"
    sell = "sell"
    flat = "flat"


class ExecutionSourceType(StrEnum):
    portfolio_construction_sandbox = "portfolio_construction_sandbox"
    portfolio_selection_sandbox = "portfolio_selection_sandbox"
    ml_blending_sandbox = "ml_blending_sandbox"
    risk_assessment = "risk_assessment"
    manual_review = "manual_review"


@dataclass
class ExecutionIntentDraft:
    intent_id: str
    mode: ExecutionMode
    kind: ExecutionIntentKind
    status: ExecutionIntentStatus
    source_type: ExecutionSourceType
    source_run_id: str
    source_candidate_id: str
    symbol: str
    market_scope: str
    interval: str
    side: ExecutionSide
    hypothetical_notional_usdt: Optional[Decimal]
    quantity: Optional[Decimal]
    price: Optional[Decimal]
    order_type: Optional[str]
    time_in_force: Optional[str]
    correlation_id: str
    idempotency_key: str
    source_trace: str
    safety_scan_id: Optional[str]
    explanation: str
    metadata: dict[str, Any]
    created_at_utc: datetime


@dataclass
class ExecutionSafetyScan:
    safety_scan_id: str
    intent_id: str
    passed: bool
    blocked: bool
    issues: list[str]
    credential_detected: bool
    signed_payload_detected: bool
    order_id_detected: bool
    forbidden_field_detected: bool
    gateway_call_attempt_detected: bool
    kill_switch_active: bool
    generated_at_utc: datetime
    metadata: dict[str, Any]


@dataclass
class ExecutionDryRunResult:
    dry_run_id: str
    intent_id: str
    passed: bool
    filter_validation_report: dict[str, Any]
    notional_validation_report: dict[str, Any]
    rounding_report: dict[str, Any]
    payload_safety_report: dict[str, Any]
    boundary_report: dict[str, Any]
    warnings: list[str]
    metadata: dict[str, Any]
    generated_at_utc: datetime


@dataclass
class ExecutionSafetyRunRequest:
    symbol: str
    market_scope: str
    interval: str
    portfolio_construction_run_id: str
    request_id: str
    correlation_id: str


@dataclass
class ExecutionSafetyRunResult:
    request: ExecutionSafetyRunRequest
    run_id: str
    intents: list[ExecutionIntentDraft]
    safety_scans: list[ExecutionSafetyScan]
    dry_run_results: list[ExecutionDryRunResult]
    boundary_report: dict[str, Any]
    kill_switch_report: dict[str, Any]
    circuit_breaker_report: dict[str, Any]
    quality_report: dict[str, Any]
    reproducibility_report: dict[str, Any]
    metadata: dict[str, Any]
    success: bool
    error: Optional[str]
