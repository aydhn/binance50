from dataclasses import dataclass
from datetime import datetime, timezone

from binance50.config.models import AppConfig
from binance50.core.exceptions import ExecutionQualityError
from .models import ExecutionSafetyRunResult


@dataclass
class ExecutionQualityIssue:
    issue_type: str
    severity: str
    intent_id: str
    message: str
    metadata: dict


@dataclass
class ExecutionQualityReport:
    status: str
    run_id: str
    intent_count: int
    safety_scan_count: int
    dry_run_count: int
    missing_safety_scan_count: int
    missing_source_trace_count: int
    missing_correlation_id_count: int
    missing_idempotency_key_count: int
    gateway_call_attempt_count: int
    credential_detected_count: int
    signed_payload_detected_count: int
    order_id_detected_count: int
    forbidden_state_count: int
    quantity_output_count: int
    leverage_output_count: int
    production_order_intent_count: int
    live_or_testnet_intent_count: int
    missing_hash_count: int
    issues: list[ExecutionQualityIssue]
    generated_at_utc: datetime


def detect_missing_safety_scans(result: ExecutionSafetyRunResult) -> int:
    return len(result.intents) - len(result.safety_scans)

def detect_missing_source_trace(result: ExecutionSafetyRunResult) -> int:
    return sum(1 for i in result.intents if not getattr(i, 'source_trace', None))

def detect_missing_correlation_ids(result: ExecutionSafetyRunResult) -> int:
    return sum(1 for i in result.intents if not getattr(i, 'correlation_id', None))

def detect_missing_idempotency_keys(result: ExecutionSafetyRunResult) -> int:
    return sum(1 for i in result.intents if not getattr(i, 'idempotency_key', None))

def detect_gateway_call_attempts(result: ExecutionSafetyRunResult) -> int:
    return sum(1 for s in result.safety_scans if s.gateway_call_attempt_detected)

def detect_credentials(result: ExecutionSafetyRunResult) -> int:
    return sum(1 for s in result.safety_scans if s.credential_detected)

def detect_signed_payloads(result: ExecutionSafetyRunResult) -> int:
    return sum(1 for s in result.safety_scans if s.signed_payload_detected)

def detect_order_ids(result: ExecutionSafetyRunResult) -> int:
    return sum(1 for s in result.safety_scans if s.order_id_detected)

def detect_forbidden_states(result: ExecutionSafetyRunResult) -> int:
    # Phase 28 allowed states
    allowed = ["draft_created", "safety_scanned", "rejected_by_guard", "blocked_by_kill_switch", "dry_run_validated", "archived"]
    return sum(1 for i in result.intents if i.status.value not in allowed)

def detect_quantity_outputs(result: ExecutionSafetyRunResult) -> int:
    return sum(1 for i in result.intents if i.quantity is not None)

def detect_leverage_outputs(result: ExecutionSafetyRunResult) -> int:
    return sum(1 for i in result.intents if "leverage" in getattr(i, 'metadata', {}))

def detect_production_order_intent(result: ExecutionSafetyRunResult) -> int:
    return sum(1 for i in result.intents if i.kind.value in ["paper_candidate", "testnet_candidate", "live_candidate"])

def detect_live_or_testnet_intent(result: ExecutionSafetyRunResult) -> int:
    return sum(1 for i in result.intents if i.mode.value in ["testnet_candidate", "live_candidate"])


def build_execution_quality_report(result: ExecutionSafetyRunResult, config: AppConfig) -> ExecutionQualityReport:
    issues = []

    missing_safety = detect_missing_safety_scans(result)
    gateway_attempts = detect_gateway_call_attempts(result)
    creds = detect_credentials(result)

    if missing_safety > 0:
        issues.append(ExecutionQualityIssue("missing_safety_scan", "critical", "multiple", f"{missing_safety} intents missing safety scans", {}))

    if creds > 0:
        issues.append(ExecutionQualityIssue("credential_detected", "critical", "multiple", f"{creds} credential leaks detected", {}))

    status = "passed" if len(issues) == 0 else "failed"

    return ExecutionQualityReport(
        status=status,
        run_id=result.run_id,
        intent_count=len(result.intents),
        safety_scan_count=len(result.safety_scans),
        dry_run_count=len(result.dry_run_results),
        missing_safety_scan_count=missing_safety,
        missing_source_trace_count=detect_missing_source_trace(result),
        missing_correlation_id_count=detect_missing_correlation_ids(result),
        missing_idempotency_key_count=detect_missing_idempotency_keys(result),
        gateway_call_attempt_count=gateway_attempts,
        credential_detected_count=creds,
        signed_payload_detected_count=detect_signed_payloads(result),
        order_id_detected_count=detect_order_ids(result),
        forbidden_state_count=detect_forbidden_states(result),
        quantity_output_count=detect_quantity_outputs(result),
        leverage_output_count=detect_leverage_outputs(result),
        production_order_intent_count=detect_production_order_intent(result),
        live_or_testnet_intent_count=detect_live_or_testnet_intent(result),
        missing_hash_count=0,
        issues=issues,
        generated_at_utc=datetime.now(timezone.utc)
    )

def assert_execution_quality_passed(report: ExecutionQualityReport, config: AppConfig) -> None:
    if report.status != "passed":
        raise ExecutionQualityError(f"Execution quality failed with {len(report.issues)} issues")

    q = config.execution.quality
    if q.reject_credential_detected and report.credential_detected_count > 0:
        raise ExecutionQualityError("Credentials detected in execution run.")
    if q.reject_gateway_call_attempt and report.gateway_call_attempt_count > 0:
        raise ExecutionQualityError("Gateway call attempts detected.")
    if q.reject_quantity_output and report.quantity_output_count > 0:
        raise ExecutionQualityError("Quantity output detected.")
    if q.reject_live_or_testnet_intent and report.live_or_testnet_intent_count > 0:
        raise ExecutionQualityError("Live or testnet intent detected.")
