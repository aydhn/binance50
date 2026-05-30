from datetime import datetime, timezone
from typing import Any

from binance50.config.models import AppConfig
from binance50.core.exceptions import ExecutionPayloadSafetyError

from .models import ExecutionSafetyScan


def detect_api_credentials(payload: dict[str, Any]) -> list[str]:
    violations = []
    str_payload = str(payload).lower()
    if "api_key" in str_payload or "apikey" in str_payload:
        violations.append("API key detected")
    if "secret" in str_payload and ("key" in str_payload or "api" in str_payload):
        violations.append("Secret detected")
    if "listenkey" in str_payload or "listen_key" in str_payload:
        violations.append("Listen key detected")
    return violations


def detect_signed_payload(payload: dict[str, Any]) -> list[str]:
    violations = []
    str_payload = str(payload).lower()
    if "signature" in str_payload:
        violations.append("Signature field detected")
    if "timestamp" in str_payload and "signature" in str_payload:
        violations.append("Timestamped signed payload detected")
    return violations


def detect_order_identifiers(payload: dict[str, Any]) -> list[str]:
    violations = []
    str_payload = str(payload).lower()
    for field in ["orderid", "order_id", "clientorderid", "client_order_id", "exchangeorderid", "exchange_order_id", "newclientorderid", "origclientorderid"]:
        if field in str_payload:
            violations.append(f"Exchange order identifier '{field}' detected")
    return violations


def detect_exchange_endpoint_references(payload: dict[str, Any]) -> list[str]:
    violations = []
    str_payload = str(payload).lower()
    for ref in ["/api/v3/order", "/api/v3/order/test", "submit_order", "live_order", "testnet_order", "paper_order", "raw_http_request"]:
        if ref in str_payload:
            violations.append(f"Exchange endpoint reference '{ref}' detected")
    return violations


def detect_order_like_fields(payload: dict[str, Any]) -> list[str]:
    violations = []
    # Not purely order-like on their own, but in a raw payload check context:
    if "quantity" in payload or "qty" in payload:
         violations.append("Quantity field detected")
    if "leverage" in payload:
         violations.append("Leverage field detected")
    if "stopLoss" in payload or "stop_loss" in payload:
         violations.append("Stop loss field detected")
    if "takeProfit" in payload or "take_profit" in payload:
         violations.append("Take profit field detected")
    return violations


def scan_payload_for_forbidden_fields(payload: dict[str, Any], intent_id: str, config: AppConfig) -> ExecutionSafetyScan:
    conf = config.execution.payload_safety
    if not conf.enabled:
        return ExecutionSafetyScan(
            safety_scan_id=f"scan_{intent_id}",
            intent_id=intent_id,
            passed=True,
            blocked=False,
            issues=[],
            credential_detected=False,
            signed_payload_detected=False,
            order_id_detected=False,
            forbidden_field_detected=False,
            gateway_call_attempt_detected=False,
            kill_switch_active=config.execution.kill_switch.global_kill_switch_default_on,
            generated_at_utc=datetime.now(timezone.utc),
            metadata={}
        )

    credentials = detect_api_credentials(payload) if conf.reject_api_key or conf.reject_secret or conf.reject_listen_key else []
    signed = detect_signed_payload(payload) if conf.reject_signature or conf.reject_timestamp_signed_payload else []
    identifiers = detect_order_identifiers(payload) if conf.reject_order_id or conf.reject_client_order_id or conf.reject_exchange_order_id else []
    endpoints = detect_exchange_endpoint_references(payload) if conf.reject_submit_endpoint or conf.reject_binance_order_endpoint else []
    order_fields = detect_order_like_fields(payload) if conf.reject_real_order else []

    all_issues = credentials + signed + identifiers + endpoints + order_fields

    passed = len(all_issues) == 0

    return ExecutionSafetyScan(
        safety_scan_id=f"scan_{intent_id}",
        intent_id=intent_id,
        passed=passed,
        blocked=not passed,
        issues=all_issues,
        credential_detected=len(credentials) > 0,
        signed_payload_detected=len(signed) > 0,
        order_id_detected=len(identifiers) > 0,
        forbidden_field_detected=len(order_fields) > 0,
        gateway_call_attempt_detected=len(endpoints) > 0,
        kill_switch_active=config.execution.kill_switch.global_kill_switch_default_on,
        generated_at_utc=datetime.now(timezone.utc),
        metadata={}
    )


def assert_payload_safe(payload: dict[str, Any], config: AppConfig) -> None:
    scan = scan_payload_for_forbidden_fields(payload, "adhoc", config)
    if not scan.passed:
        raise ExecutionPayloadSafetyError(f"Payload safety validation failed: {', '.join(scan.issues)}")
