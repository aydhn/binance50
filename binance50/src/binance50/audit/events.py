import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from binance50.logging.redaction import redact_mapping


class AuditEventType(str, Enum):
    app_start = "app_start"
    app_stop = "app_stop"
    config_loaded = "config_loaded"
    safety_check_started = "safety_check_started"
    safety_check_passed = "safety_check_passed"
    safety_check_failed = "safety_check_failed"
    environment_selected = "environment_selected"
    connector_disabled = "connector_disabled"
    connector_enabled = "connector_enabled"
    secret_redacted = "secret_redacted"
    secret_leak_blocked = "secret_leak_blocked"
    error_captured = "error_captured"
    rate_limit_warning = "rate_limit_warning"
    binance_error_classified = "binance_error_classified"
    manual_action_required = "manual_action_required"
    future_trade_decision_placeholder = "future_trade_decision_placeholder"
    future_order_placeholder = "future_order_placeholder"
    future_risk_decision_placeholder = "future_risk_decision_placeholder"


@dataclass
class AuditEvent:
    event_type: AuditEventType | str
    component: str
    action: str
    status: str = "success"
    severity: str = "info"
    message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    error_code: str | None = None
    exception_class: str | None = None

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp_utc: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    correlation_id: str | None = None
    environment_profile: str | None = None
    trading_mode: str | None = None
    market_scope: str | None = None

    def __post_init__(self) -> None:
        # Ensure metadata is redacted
        if self.metadata:
            self.metadata = redact_mapping(self.metadata)
        if isinstance(self.event_type, AuditEventType):
            self.event_type = self.event_type.value

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp_utc": self.timestamp_utc,
            "severity": self.severity,
            "correlation_id": self.correlation_id,
            "environment_profile": self.environment_profile,
            "trading_mode": self.trading_mode,
            "market_scope": self.market_scope,
            "component": self.component,
            "action": self.action,
            "status": self.status,
            "message": self.message,
            "metadata": self.metadata,
            "error_code": self.error_code,
            "exception_class": self.exception_class,
        }
